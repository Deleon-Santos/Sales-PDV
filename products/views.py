from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsManagerOrAdmin, IsCashierOrAbove
from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsCashierOrAbove]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAuthenticated(), IsManagerOrAdmin()]
        return [IsAuthenticated(), IsCashierOrAbove()]
