from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import User, AttendanceResponse

class UserResource(resources.ModelResource):
    # Adding a custom field to show something custom like concatenation of name and email if needed
    name_email = fields.Field(
        attribute='name_email', 
        column_name='Name and Email',
        readonly=True  # This field will be used only for export and not for import
    )

    class Meta:
        model = User
        fields = ('user_id', 'name', 'email', 'name_email')  # Including the custom field in exports
        export_order = ('user_id', 'name', 'email', 'name_email')
        import_id_fields = ['user_id']
        skip_unchanged = True
        report_skipped = False
        use_natural_foreign_keys = True

    def dehydrate_name_email(self, user):
        """
        Custom method to create a combined representation of the name and email for export.
        """
        return f"{user.name} <{user.email}>"

    def before_import_row(self, row, **kwargs):
        """
        Optional method to handle data before importing, such as data cleanup or validation.
        """
        if 'id' in row:
            row['user_id'] = row.pop('id')


class AttendanceResponseResource(resources.ModelResource):
    # This widget will use the email field of the User model to link records.
    user = fields.Field(
        column_name='User Email',  # Make sure this exactly matches your CSV header for the user's email
        attribute='user',
        widget=ForeignKeyWidget(User, 'email')
    )

    class Meta:
        model = AttendanceResponse
        fields = ('user', 'date', 'response')  # 'user__name' changed to 'user' for simplicity in import/export
        export_order = ('user', 'date', 'response')
        import_id_fields = ['user', 'date']  # Assuming you are identifying records by 'user' and 'date'
        skip_unchanged = True
        report_skipped = False
        use_natural_foreign_keys = True

    def dehydrate_user(self, attendance_response):
        # Returns the email of the user for the export file.
        return attendance_response.user.email if attendance_response.user else ''

    def before_import_row(self, row, **kwargs):
        # Ensures user is fetched by email and handles missing or incorrect emails.
        user_email = row.get('User Email')
        if user_email:
            user = User.objects.filter(email=user_email).first()
            if not user:
                raise ValueError(f"User with email {user_email} not found")
            row['user'] = user
        else:
            raise ValueError("User Email is missing or blank in the CSV file")
