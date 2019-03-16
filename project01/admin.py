from django.contrib import admin
from project01.models import LSOCProfile

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm


class LSOCProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'description', 'permissions')

    def permissions(self, object):
        if object.lsoc_permissions == '*':
            return 'FULL ACCESS'
        else:
            return object.lsoc_permissions


admin.site.register(LSOCProfile, LSOCProfileAdmin)
admin.site.site_header = 'LSOC Administration'
