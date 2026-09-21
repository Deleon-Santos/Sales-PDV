from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


def api_root(request):
    return JsonResponse({"message": "Bem-vindo à API do Sales-PDV", "status": "online"})

urlpatterns = [
    path("", api_root),
    path("admin/", admin.site.urls),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/usuarios/", include("core.urls")),
    path("api/produtos/", include("products.urls")),
    path("api/vendas/", include("sales.urls")),
    path("api/relatorios/", include("reports.urls")),
    path("api/itens-venda/", include("sales.item_urls")),
]
