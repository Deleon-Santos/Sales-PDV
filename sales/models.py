from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from products.models import Product


class Sale(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Aberta"
        COMPLETED = "COMPLETED", "Finalizada"
        CANCELED = "CANCELED", "Cancelada"

    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Dinheiro"
        DEBIT = "DEBIT", "Débito"
        CREDIT = "CREDIT", "Crédito"
        PIX = "PIX", "PIX"

    cashier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sales",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    payment_method = models.CharField(
        max_length=20, choices=PaymentMethod.choices, blank=True
    )
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["created_at", "status"])]

    def __str__(self):
        return f"Venda #{self.pk}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="sale_items")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["sale", "product"],
                name="unique_product_per_sale",
            )
        ]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
