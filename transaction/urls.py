from django.urls import path, include
from rest_framework import routers

from transaction import views

router = routers.DefaultRouter()
router.register(r"transaction", views.TransactionViewSet, basename="transaction")

urlpatterns = [
    path("", include(router.urls)),
]
