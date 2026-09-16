from rest_framework.routers import DefaultRouter
from .views import SaleItemViewSet

router = DefaultRouter()
router.register("", SaleItemViewSet, basename="item-venda")
urlpatterns = router.urls
