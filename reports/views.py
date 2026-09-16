from datetime import datetime, time
from django.db.models import Count, F, Sum, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sales.models import Sale, SaleItem


def date_range(request):
    start = request.query_params.get("start")
    end = request.query_params.get("end")
    if not start or not end:
        return None, None

    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
    except ValueError:
        return None, None

    tz = timezone.get_current_timezone()
    return (
        timezone.make_aware(datetime.combine(start_date, time.min), tz),
        timezone.make_aware(datetime.combine(end_date, time.max), tz),
    )


class SalesGeneralReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start, end = date_range(request)
        if not start:
            return Response({"detail": "Informe start e end no formato YYYY-MM-DD."}, status=400)

        queryset = Sale.objects.filter(
            status=Sale.Status.COMPLETED,
            completed_at__range=(start, end),
        )
        if request.user.role == "CASHIER":
            queryset = queryset.filter(cashier=request.user)

        summary = queryset.aggregate(
            total_sales=Count("id"),
            revenue=Coalesce(Sum("total"), 0),
        )
        return Response({
            "periodo": {"inicio": start.date(), "fim": end.date()},
            "total_vendas": summary["total_sales"],
            "faturamento": summary["revenue"],
        })


class SalesProductReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start, end = date_range(request)
        if not start:
            return Response({"detail": "Informe start e end no formato YYYY-MM-DD."}, status=400)

        queryset = SaleItem.objects.filter(
            sale__status=Sale.Status.COMPLETED,
            sale__completed_at__range=(start, end),
        )
        if request.user.role == "CASHIER":
            queryset = queryset.filter(sale__cashier=request.user)

        subtotal_expression = ExpressionWrapper(
            F("quantity") * F("unit_price"),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        )

        rows = queryset.values(
            "product_id", "product__barcode", "product__name"
        ).annotate(
            quantidade=Sum("quantity"),
            faturamento=Sum(subtotal_expression),
            vendas=Count("sale", distinct=True),
        ).order_by("-faturamento")

        return Response({
            "periodo": {"inicio": start.date(), "fim": end.date()},
            "produtos": list(rows),
        })
