from django.core.management.base import BaseCommand
from core.models import User
from products.models import Product


class Command(BaseCommand):
    help = "Cria usuários e produtos para demonstração."

    def handle(self, *args, **options):
        users = [
            ("admin@caixa.local", "admin", "Admin@12345", User.Role.ADMIN, True, True),
            ("gerente@caixa.local", "gerente", "Gerente@12345", User.Role.MANAGER, True, False),
            ("caixa@caixa.local", "caixa", "Caixa@12345", User.Role.CASHIER, True, False),
        ]

        for email, username, password, role, staff, superuser in users:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "role": role,
                    "is_staff": staff,
                    "is_superuser": superuser,
                },
            )
            if created:
                user.set_password(password)
                user.save()

        demo_products = [
            ("7891000000011", "Arroz 5kg", "25.90", 100),
            ("7891000000012", "Feijão 1kg", "8.50", 120),
            ("7891000000013", "Leite 1L", "5.49", 200),
            ("7891000000014", "Café 500g", "16.90", 80),
        ]

        for barcode, name, price, stock in demo_products:
            Product.objects.get_or_create(
                barcode=barcode,
                defaults={"name": name, "price": price, "stock": stock},
            )

        self.stdout.write(self.style.SUCCESS("Dados de demonstração criados."))
