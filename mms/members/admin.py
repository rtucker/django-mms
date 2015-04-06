from django.contrib import admin

from .models import MembershipLevel, Member

admin.site.register(MembershipLevel)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'membership', 'billing_up_to_date', 'balance')
