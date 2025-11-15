from django.contrib import admin
from transaction.models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("vendor", "customer", "amount", "created_at", "updated_at")
    search_fields = ("vendor", "customer")
    list_filter = ("created_at", "updated_at")
