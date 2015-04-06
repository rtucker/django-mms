from django.contrib import admin

from .models import LedgerAccount, LedgerEntry, PaymentMethod

admin.site.register(LedgerEntry)
admin.site.register(PaymentMethod)


@admin.register(LedgerAccount)
class LedgerAccountAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'balance', 'account_type', 'account_balance')
