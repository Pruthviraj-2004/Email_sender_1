from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Employee, EmployeeResponse

class EmployeeResource(resources.ModelResource):
    # Adding a custom field to show something custom like concatenation of name and email if needed
    name_email = fields.Field(
        attribute='name_email',
        column_name='Name and Email',
        readonly=True  # This field will be used only for export and not for import
    )

    class Meta:
        model = Employee
        fields = ('user_id', 'name', 'email', 'name_email')  # Including the custom field in exports
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
    # This widget will use the email field of the Employee model to link records.
    employee = fields.Field(
        column_name='Employee Email',  # Make sure this exactly matches your CSV header for the employee's email
        attribute='employee',
        widget=ForeignKeyWidget(Employee, 'email')
    )

    class Meta:
        model = EmployeeResponse
        fields = ('employee', 'date', 'response')  # 'employee__name' changed to 'employee' for simplicity in import/export
        export_order = ('employee', 'date', 'response')
        import_id_fields = ['employee', 'date']  # Assuming you are identifying records by 'employee' and 'date'
        skip_unchanged = True
        report_skipped = False
        use_natural_foreign_keys = True

    def dehydrate_employee(self, employee_response):
        # Returns the email of the employee for the export file.
        return employee_response.employee.email if employee_response.employee else ''

    def before_import_row(self, row, **kwargs):
        # Ensures employee is fetched by email and handles missing or incorrect emails.
        employee_email = row.get('Employee Email')
        if employee_email:
            employee = Employee.objects.filter(email=employee_email).first()
            if not employee:
                raise ValueError(f"Employee with email {employee_email} not found")
            row['employee'] = employee
        else:
            raise ValueError("Employee Email is missing or blank in the CSV file")
