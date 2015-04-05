from django.contrib import admin

from .models import MembershipLevel, Member

admin.site.register(MembershipLevel)
admin.site.register(Member)