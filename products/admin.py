from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("barcode", "name", "price", "stock", "active")
    search_fields = ("barcode", "name")
    list_filter = ("active",)
