from django.urls import path
from .views import SalesGeneralReportView, SalesProductReportView

urlpatterns = [
    path("vendas/", SalesGeneralReportView.as_view(), name="relatorio-vendas"),
    path("produtos/", SalesProductReportView.as_view(), name="relatorio-produtos"),
]
