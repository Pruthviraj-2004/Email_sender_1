from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import OrganizationEvent, Employee, EmployeeEventResponse, EmployeeResponse

class EmployeeResource(resources.ModelResource):
    name_email = fields.Field(
        attribute='name_email',
        column_name='Name and Email',
        readonly=True
    )

    class Meta:
        model = Employee
        fields = ('user_id', 'name', 'email', 'name_email')
        export_order = ('user_id', 'name', 'email', 'name_email')
        import_id_fields = ['user_id']
        skip_unchanged = True
        report_skipped = False
        use_natural_foreign_keys = True

    def dehydrate_name_email(self, employee):
        """
        Custom method to create a combined representation of the name and email for export.
        """
        return f"{employee.name} <{employee.email}>"

    def before_import_row(self, row, **kwargs):
        """
        Optional method to handle data before importing, such as data cleanup or validation.
        """
        if 'id' in row:
            row['user_id'] = row.pop('id')

class EmployeeResponseResource(resources.ModelResource):
    employee = fields.Field(
        column_name='Employee Name',
        attribute='employee',
        widget=ForeignKeyWidget(Employee, 'name')
    )

    class Meta:
        model = EmployeeResponse
        fields = ('employee', 'date', 'response')
        export_order = ('employee', 'date', 'response')
        import_id_fields = ['employee', 'date']
        skip_unchanged = True
        report_skipped = False
        use_natural_foreign_keys = False 

class OrganizationEventResource(resources.ModelResource):
    class Meta:
        model = OrganizationEvent
        fields = ('event_id', 'name', 'date')
        export_order = ('event_id', 'name', 'date')
        import_id_fields = ['event_id']
        skip_unchanged = True
        report_skipped = False

class EmployeeEventResponseResource(resources.ModelResource):
    event = fields.Field(
        column_name='Event Name',
        attribute='event',
        widget=ForeignKeyWidget(OrganizationEvent, 'name')
    )
    employee = fields.Field(
        column_name='Employee Name',
        attribute='employee',
        widget=ForeignKeyWidget(Employee, 'name')
    )

    class Meta:
        model = EmployeeEventResponse
        fields = ('employee', 'event', 'date', 'response')
        export_order = ('employee', 'event', 'date', 'response')
        import_id_fields = ['employee', 'event', 'date']
        skip_unchanged = True
        report_skipped = False
        use_natural_foreign_keys = True
