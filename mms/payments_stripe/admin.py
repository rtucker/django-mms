from django.contrib import admin

from .models import Customer, Charge

admin.site.register(Customer)
admin.site.register(Charge)
