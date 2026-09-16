from rest_framework.routers import DefaultRouter
from .views import SaleViewSet

router = DefaultRouter()
router.register("", SaleViewSet, basename="venda")
urlpatterns = router.urls
