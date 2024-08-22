from django.urls import path

from .views import AddEmployeeResponseView, AddEmployeeView, ControlPanelView, EmployeeResponseView, FilterEmployeeResponses, SendConfirmationEmail, SendEmailsToAllEmployees, ViewEmployeeResponseByEmployee, ViewEmployeeResponses

urlpatterns = [
    path('send-email/<int:employee_id>/', SendConfirmationEmail.as_view(), name='send_email'),
    path('send-emails-to-all/', SendEmailsToAllEmployees.as_view(), name='send_emails_to_all'),
    path('response/<int:employee_id>/<str:response_value>/', EmployeeResponseView.as_view(), name='employee_response'),
    path('control-panel/', ControlPanelView.as_view(), name='control_panel'),
    path('add-employee/', AddEmployeeView.as_view(), name='add_employee'),
    path('add-employee-response/', AddEmployeeResponseView.as_view(), name='add_employee_response'),
    path('view-responses/', ViewEmployeeResponses.as_view(), name='view_responses'),
    path('view-responses-by-employee/', ViewEmployeeResponseByEmployee.as_view(), name='view_responses_by_employee'),
    path('filter-responses/', FilterEmployeeResponses.as_view(), name='filter_responses'),    
]