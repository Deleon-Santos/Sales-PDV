from rest_framework import serializers
from .models import Sale, SaleItem


class SaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = SaleItem
        fields = (
            "id", "sale", "product", "product_name",
            "quantity", "unit_price", "subtotal"
        )
        read_only_fields = ("unit_price", "subtotal", "product_name")


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    cashier_name = serializers.CharField(source="cashier.username", read_only=True)

    class Meta:
        model = Sale
        fields = (
            "id", "cashier", "cashier_name", "status",
            "payment_method", "total", "created_at",
            "completed_at", "items",
        )
        read_only_fields = (
            "cashier", "status", "total", "created_at",
            "completed_at", "items",
        )
