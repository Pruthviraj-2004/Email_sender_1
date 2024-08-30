from django.urls import path

from .views import AddEmployeeResponseView, AddEmployeeView, ControlPanelView, CreateEmployeeEventResponseView, CreateOrganizationEventView, EmployeeDeleteView, EmployeeEventResponseView, EmployeeEventResponsesView, EmployeeExportView, EmployeeListView, EmployeeResponseView, EmployeeResponsesView, FilterEmployeeResponses, ManageWorking, ManageWorkingDays, OrganizationEventListView, SelectMonthYearView, SendConfirmationEmail, SendCustomEmailsToAllEmployees, SendCustomEmailsYesNoToAllEmployees, SendEmailsToAllEmployees, SendEventSummaryEmail, SendSummaryEmail, UploadFileView, ViewEmployeeResponseByEmployee, ViewEmployeeResponses, ViewEventResponses, ViewResponsesByMonth

urlpatterns = [
    path('send-email/<int:employee_id>/', SendConfirmationEmail.as_view(), name='send_email'),
    path('send-emails-to-all/', SendEmailsToAllEmployees.as_view(), name='send_emails_to_all'),
    path('response/<int:employee_id>/<str:response_value>/', EmployeeResponseView.as_view(), name='employee_response'),
    path('control-panel/', ControlPanelView.as_view(), name='control_panel'),
    path('employees/', EmployeeListView.as_view(), name='employee_list'),
    path('employee-responses/', EmployeeResponsesView.as_view(), name='employee_responses'),
    path('add-employee/', AddEmployeeView.as_view(), name='add_employee'),
    path('add-employee-response/', AddEmployeeResponseView.as_view(), name='add_employee_response'),
    path('view-responses/', ViewEmployeeResponses.as_view(), name='view_responses'),
    path('view-responses-by-employee/', ViewEmployeeResponseByEmployee.as_view(), name='view_responses_by_employee'),
    path('filter-responses/', FilterEmployeeResponses.as_view(), name='filter_responses'),    
    path('view-responses-month/', ViewResponsesByMonth.as_view(), name='view_responses_month'),
    path('manage-working-days/', ManageWorkingDays.as_view(), name='manage_working_days'),

    path('manage-working/<int:year>/<int:month>/', ManageWorking.as_view(), name='manage_working'),
    path('select-month-year/', SelectMonthYearView.as_view(), name='select_month_year'),

    path('upload-file/', UploadFileView.as_view(), name='upload_file'),
    path('export-employees/', EmployeeExportView.as_view(), name='employee_export'),

    path('employee/delete/<int:user_id>/', EmployeeDeleteView.as_view(), name='employee_delete'),

    path('send-custom-yes-no-emails/', SendCustomEmailsYesNoToAllEmployees.as_view(), name='send_custom_yes_no_emails'),
    path('send-custom-emails/', SendCustomEmailsToAllEmployees.as_view(), name='send_custom_emails'),
    path('send-summary-email/', SendSummaryEmail.as_view(), name='send_summary_email'),
    
    path('events/', OrganizationEventListView.as_view(), name='organization_events'),
    path('event-responses/', EmployeeEventResponsesView.as_view(), name='employee_event_responses'),
    path('create-event/', CreateOrganizationEventView.as_view(), name='create_event'),
    path('create-employee-response/', CreateEmployeeEventResponseView.as_view(), name='create_employee_response'),
    path('view-event-responses/', ViewEventResponses.as_view(), name='view_event_responses'),
    path('send-event-summary-email/', SendEventSummaryEmail.as_view(), name='send_event_summary_email'),

    path('employee/<int:employee_id>/event/<int:event_id>/response/<str:response_value>/', EmployeeEventResponseView.as_view(), name='employee_event_response'),

]