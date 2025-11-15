from django.urls import path

from customer.views import increase_credit

urlpatterns = [
    path("increase-credit/", increase_credit),
]
