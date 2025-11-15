from django.urls import path

from vendor.views import submit_request, approve_request

urlpatterns = [
    path("submit-request/", submit_request),
    path("approve-request/", approve_request),
]
