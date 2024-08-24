# admin.py

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Employee, EmployeeResponse, WorkingDays
from .resources import EmployeeResource, EmployeeResponseResource

@admin.register(Employee)
class EmployeeAdmin(ImportExportModelAdmin):
    resource_class = EmployeeResource
    list_display = ('user_id', 'name', 'get_decrypted_email')
    list_filter = ('name', )
    search_fields = ('name', 'email')

    def get_decrypted_email(self, obj):
        # Decrypts the email for display in the admin; this assumes decryption is automatic
        return obj.email
    get_decrypted_email.short_description = "Email"

@admin.register(EmployeeResponse)
class EmployeeResponseAdmin(ImportExportModelAdmin):
    resource_class = EmployeeResponseResource
    list_display = ('employee', 'date', 'response')
    list_filter = ('employee', 'date', 'response')
    search_fields = ('employee__name', 'employee__email')

@admin.register(WorkingDays)
class WorkingDaysAdmin(admin.ModelAdmin):
    list_display = ['month', 'year', 'days']

