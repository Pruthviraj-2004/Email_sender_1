# admin.py

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import User, AttendanceResponse
from .resources import UserResource, AttendanceResponseResource

@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    resource_class = UserResource
    list_display = ('user_id', 'name', 'email')
    list_filter = ('name', )
    search_fields = ('name', 'email')

@admin.register(AttendanceResponse)
class AttendanceResponseAdmin(ImportExportModelAdmin):
    resource_class = AttendanceResponseResource
    list_display = ('user', 'date', 'response')
    list_filter = ('user', 'date', 'response')
    search_fields = ('user__name', 'user__email')
