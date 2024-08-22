from django.urls import path
from .views import AttendanceResponseView, add_response, add_user, control_panel, filter_responses, index, send_emails, send_emails_to_all_users, view_responses, view_user_responses

urlpatterns = [
    # path('send-mail', views.index),
    path('send-mail/<int:user_id>/', index, name='send_mail'),
    path('confirm/response/<int:user_id>/<str:response_value>/', AttendanceResponseView.as_view(), name='confirm_response'),
    path('add-user/', add_user, name='add_user'),
    path('add-response/', add_response, name='add_response'),
    path('view-responses/', view_responses, name='view_responses'),
    path('control-panel/', control_panel, name='control_panel'),
    path('send-emails/', send_emails, name='send_emails'),
    path('view-user-responses/', view_user_responses, name='view_user_responses'),
    path('filter-responses/', filter_responses, name='filter_responses'),

]