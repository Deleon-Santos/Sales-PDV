from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from .models import Sale, SaleItem
from products.models import Product


@transaction.atomic
def add_item(sale: Sale, product: Product, quantity: int) -> SaleItem:
    if sale.status != Sale.Status.OPEN:
        raise ValidationError("Somente vendas abertas podem receber itens.")

    if quantity <= 0:
        raise ValidationError("A quantidade deve ser maior que zero.")

    product = Product.objects.select_for_update().get(pk=product.pk)

    existing = SaleItem.objects.filter(sale=sale, product=product).first()
    new_quantity = quantity + (existing.quantity if existing else 0)

    if product.stock < new_quantity:
        raise ValidationError("Estoque insuficiente.")

    item = existing or SaleItem(sale=sale, product=product)
    item.quantity = new_quantity
    item.unit_price = product.price
    item.subtotal = product.price * Decimal(new_quantity)
    item.save()

    sale.total = sum(
        (row.subtotal for row in sale.items.all()),
        Decimal("0.00"),
    )
    sale.save(update_fields=["total"])
    return item


@transaction.atomic
def complete_sale(sale: Sale, payment_method: str) -> Sale:
    if sale.status != Sale.Status.OPEN:
        raise ValidationError("A venda não está aberta.")

    items = list(sale.items.select_related("product").all())
    if not items:
        raise ValidationError("A venda precisa possuir pelo menos um item.")

    for item in items:
        product = Product.objects.select_for_update().get(pk=item.product_id)
        if product.stock < item.quantity:
            raise ValidationError(
                f"Estoque insuficiente para {product.name}."
            )
        product.stock -= item.quantity
        product.save(update_fields=["stock"])

    sale.payment_method = payment_method
    sale.status = Sale.Status.COMPLETED
    sale.completed_at = timezone.now()
    sale.save(update_fields=["payment_method", "status", "completed_at"])
    return sale


@transaction.atomic
def cancel_sale(sale: Sale) -> Sale:
    if sale.status == Sale.Status.CANCELED:
        raise ValidationError("A venda já está cancelada.")

    if sale.status == Sale.Status.COMPLETED:
        for item in sale.items.all():
            product = Product.objects.select_for_update().get(pk=item.product_id)
            product.stock += item.quantity
            product.save(update_fields=["stock"])

    sale.status = Sale.Status.CANCELED
    sale.save(update_fields=["status"])
    return sale
