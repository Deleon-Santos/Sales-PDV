from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsManagerOrAdmin
from products.models import Product
from receipts.pdf import build_receipt_pdf
from .models import Sale, SaleItem
from .serializers import SaleSerializer, SaleItemSerializer
from .services import add_item, cancel_sale, complete_sale


class SaleViewSet(viewsets.ModelViewSet):
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Sale.objects.select_related("cashier").prefetch_related(
            "items__product"
        )
        if self.request.user.role in {"ADMIN", "MANAGER"}:
            return queryset
        return queryset.filter(cashier=self.request.user)

    def perform_create(self, serializer):
        serializer.save(cashier=self.request.user)

    def destroy(self, request, *args, **kwargs):
        sale = self.get_object()
        if sale.status != Sale.Status.OPEN:
            return Response(
                {"detail": "Somente vendas abertas podem ser excluídas."},
                status=status.HTTP_409_CONFLICT,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def finalizar(self, request, pk=None):
        sale = self.get_object()
        payment_method = request.data.get("payment_method")
        if payment_method not in dict(Sale.PaymentMethod.choices):
            return Response(
                {"detail": "Forma de pagamento inválida."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        sale = complete_sale(sale, payment_method)
        return Response(SaleSerializer(sale).data)

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        sale = self.get_object()
        if sale.status == Sale.Status.COMPLETED and request.user.role not in {
            "ADMIN", "MANAGER"
        }:
            return Response(
                {"detail": "Somente gerente ou administrador pode cancelar venda finalizada."},
                status=status.HTTP_403_FORBIDDEN,
            )
        sale = cancel_sale(sale)
        return Response(SaleSerializer(sale).data)

    @action(detail=True, methods=["get"], url_path="cupom")
    def cupom(self, request, pk=None):
        sale = self.get_object()
        return build_receipt_pdf(sale)


class SaleItemViewSet(viewsets.ModelViewSet):
    serializer_class = SaleItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = SaleItem.objects.select_related("sale", "product")
        if self.request.user.role in {"ADMIN", "MANAGER"}:
            return queryset
        return queryset.filter(sale__cashier=self.request.user)

    def create(self, request, *args, **kwargs):
        sale = get_object_or_404(Sale, pk=request.data.get("sale"))
        product = get_object_or_404(Product, pk=request.data.get("product"))
        if sale.cashier_id != request.user.id and request.user.role not in {"ADMIN", "MANAGER"}:
            return Response({"detail": "Sem permissão."}, status=403)
        item = add_item(sale, product, int(request.data.get("quantity", 0)))
        return Response(self.get_serializer(item).data, status=201)

    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Itens devem ser ajustados pela regra de negócio da venda."},
            status=405,
        )

    def destroy(self, request, *args, **kwargs):
        item = self.get_object()
        if item.sale.status != Sale.Status.OPEN:
            return Response(
                {"detail": "Somente itens de vendas abertas podem ser removidos."},
                status=409,
            )
        sale = item.sale
        item.delete()
        sale.total = sum(
            (row.subtotal for row in sale.items.all()),
            Decimal("0.00"),
        )
        sale.save(update_fields=["total"])
        return Response(status=204)
