# admin.py

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import OrganizationEvent, Employee, EmployeeEventResponse, EmployeeResponse, WorkingDays
from .resources import EmployeeEventResponseResource, EmployeeResource, EmployeeResponseResource, OrganizationEventResource

@admin.register(Employee)
class EmployeeAdmin(ImportExportModelAdmin):
    resource_class = EmployeeResource
    list_display = ('user_id', 'name', 'get_decrypted_email', 'created_at', 'updated_at')
    list_filter = ('name', )
    search_fields = ('name', 'email')

    def get_decrypted_email(self, obj):
        # Decrypts the email for display in the admin; this assumes decryption is automatic
        return obj.email
    get_decrypted_email.short_description = "Email"

@admin.register(EmployeeResponse)
class EmployeeResponseAdmin(ImportExportModelAdmin):
    resource_class = EmployeeResponseResource
    list_display = ('employee', 'date', 'response', 'created_at', 'updated_at')
    list_filter = ('employee', 'date', 'response')
    search_fields = ('employee__name', 'employee__email')

@admin.register(WorkingDays)
class WorkingDaysAdmin(ImportExportModelAdmin):
    list_display = ['month', 'year', 'days', 'created_at', 'updated_at']

@admin.register(OrganizationEvent)
class OrganizationEventAdmin(admin.ModelAdmin):
    resource_class = OrganizationEventResource
    list_display = ('event_id', 'name', 'date', 'created_at', 'updated_at')
    search_fields = ('event_id', 'name')
    list_filter = ('date',)

@admin.register(EmployeeEventResponse)
class EmployeeEventResponseAdmin(ImportExportModelAdmin):
    resource_class = EmployeeEventResponseResource
    list_display = ('employee', 'event', 'date', 'response', 'created_at', 'updated_at')
    search_fields = ('employee__name', 'event__name', 'response')
    list_filter = ('date', 'response')