from import_export import resources
from import_export.fields import Field
from .models import User, AttendanceResponse

class UserResource(resources.ModelResource):
    class Meta:
        model = User
        # specify fields to be exported/imported or use 'fields = '__all__''
        fields = ('user_id', 'name', 'email')
        export_order = ('user_id', 'name', 'email')

class AttendanceResponseResource(resources.ModelResource):
    # Adding a custom field to show related user's email in export
    user_email = Field(attribute='user__email', column_name='User Email')

    class Meta:
        model = AttendanceResponse
        # including the custom field in exports
        fields = ('user__name', 'user_email', 'date', 'response')
        export_order = ('user__name', 'user_email', 'date', 'response')

    def dehydrate_user_email(self, attendance_response):
        # This method is to handle the representation of the user email in the export file.
        return attendance_response.user.email
