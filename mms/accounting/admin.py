from django.contrib import admin

from .models import LedgerAccount, LedgerEntry, PaymentMethod

admin.site.register(LedgerAccount)
admin.site.register(LedgerEntry)
admin.site.register(PaymentMethod)