from calendar import month_name
from django.http import HttpResponse
from django.core.mail import send_mail
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Employee, EmployeeResponse
from django.utils import timezone

from django.shortcuts import render, redirect
from .forms import DateForm, EmployeeForm, EmployeeResponseForm, EmployeeSelectForm, FilterResponseForm
from django.contrib import messages
from django.views.generic import View, TemplateView

class SendConfirmationEmail(View):
    def get(self, request, employee_id):
        employee = get_object_or_404(Employee, pk=employee_id)
        html_message = loader.render_to_string(
            'email_sender_app/message.html',
            {
                'title': 'Office Attendance Confirmation',
                'body': f'Hello {employee.name}, this email is to verify whether you will attend the office tomorrow. Please confirm your attendance.',
                'sign': 'Your Manager',
                'employee_id': employee.user_id,
            })

        send_mail(
            'Will You Attend the Office Tomorrow?',
            'Please confirm your attendance for tomorrow.',
            'photo2pruthvi@gmail.com',  # Replace with your email address
            [employee.email],
            html_message=html_message,
            fail_silently=False,
        )

        return HttpResponse("Mail Sent!")

class SendEmailsToAllEmployees(View):
    def get(self, request):
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        employees = Employee.objects.all()
        for employee in employees:
            html_message = loader.render_to_string(
                'email_sender_app/message.html',
                {
                    'title': 'Office Attendance Confirmation',
                    'body': f'Hello {employee.name}, this email is to verify whether you will attend the office tomorrow. Please confirm your attendance.',
                    'sign': 'Your Manager',
                    'employee_id': employee.user_id,
                    'date': tomorrow ,
                })

            send_mail(
                'Will You Attend the Office Tomorrow?',
                'Please confirm your attendance for tomorrow.',
                'photo2pruthvi@gmail.com',  # Replace with your actual sender email address
                [employee.email],
                html_message=html_message,
                fail_silently=False,
            )
        messages.success(request, 'Emails have been successfully sent to all employees.')
        return redirect('control_panel')

class EmployeeResponseView(View):
    def get(self, request, employee_id, response_value):
        employee = get_object_or_404(Employee, pk=employee_id)
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        
        if response_value in ['yes', 'no']:
            response, created = EmployeeResponse.objects.get_or_create(
                employee=employee,
                date=tomorrow,
                defaults={'response': response_value}
            )
            if not created:
                response.response = response_value
                response.save()

            return HttpResponse(f"Thank you, {employee.name}, for your response!")

        return HttpResponse("Invalid response.", status=400)

import schedule
import time
import threading
from django.core.mail import send_mail
from django.template import loader

scheduler_thread = None

def send_emails_to_all_users():
    tomorrow = timezone.now().date() + timezone.timedelta(days=1)
    employees = Employee.objects.all()
    for employee in employees:
        html_message = loader.render_to_string(
            'email_sender_app/message.html',
            {
                'title': 'Office Attendance Confirmation',
                'body': f'Hello {employee.name}, this email is to verify whether you will attend the office tomorrow. Please confirm your attendance.',
                'sign': 'Your Manager',
                'employee_id': employee.user_id,
                'date': tomorrow ,
            })

        send_mail(
            'Will You Attend the Office Tomorrow?',
            'Please confirm your attendance for tomorrow.',
            'photo2pruthvi@gmail.com',  # Replace with your email address
            [employee.email],
            html_message=html_message,
            fail_silently=False,
        )

def start_scheduler():
    schedule.every().day.at("14:25").do(send_emails_to_all_users)

    while True:
        schedule.run_pending()
        time.sleep(10)  # Sleep for 10 seconds to reduce CPU usage

def start_scheduler_thread():
    global scheduler_thread
    if scheduler_thread is None or not scheduler_thread.is_alive():
        scheduler_thread = threading.Thread(target=start_scheduler)
        scheduler_thread.daemon = True  # Ensure the thread exits when the main program does
        scheduler_thread.start()

# Start the scheduler thread
start_scheduler_thread()

class ControlPanelView(TemplateView):
    template_name = 'email_sender_app/control_panel.html'

class AddEmployeeView(View):
    def get(self, request):
        form = EmployeeForm()
        return render(request, 'email_sender_app/add_user.html', {'form': form})

    def post(self, request):
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_employee')

class AddEmployeeResponseView(View):
    def get(self, request):
        form = EmployeeResponseForm()
        return render(request, 'email_sender_app/add_response.html', {'form': form})

    def post(self, request):
        form = EmployeeResponseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_employee_response')

class ViewEmployeeResponses(View):
    def get(self, request):
        form = DateForm()
        return render(request, 'email_sender_app/view_responses.html', {'form': form})

    def post(self, request):
        form = DateForm(request.POST)
        if form.is_valid():
            selected_date = form.cleaned_data['date']
            responses = EmployeeResponse.objects.filter(date=selected_date)
            yes_count = responses.filter(response='yes').count()
            no_count = responses.filter(response='no').count()
            return render(request, 'email_sender_app/view_responses.html', {
                'form': form,
                'responses': responses,
                'yes_count': yes_count,
                'no_count': no_count,
                'selected_date': selected_date
            })

class ViewEmployeeResponseByEmployee(View):
    def get(self, request):
        form = EmployeeSelectForm()
        return render(request, 'email_sender_app/view_user_responses.html', {'form': form})

    def post(self, request):
        form = EmployeeSelectForm(request.POST)
        responses = None
        if form.is_valid():
            employee = form.cleaned_data['employee']
            responses = EmployeeResponse.objects.filter(employee=employee).order_by('-date')
            return render(request, 'email_sender_app/view_user_responses.html', {
                'form': form,
                'responses': responses,
                'selected_user': employee
            })
    
class FilterEmployeeResponses(View):
    def get(self, request):
        form = FilterResponseForm(request.GET or None)
        responses = EmployeeResponse.objects.all()
        yes_count = no_count = 0

        if form.is_valid():
            employee = form.cleaned_data.get('employee')
            date = form.cleaned_data.get('date', timezone.localdate())
            if employee:
                responses = responses.filter(employee=employee)
            responses = responses.filter(date=date)
            yes_count = responses.filter(response='yes').count()
            no_count = responses.filter(response='no').count()

        else:
            # If form is not valid, show today's responses by default
            responses = responses.filter(date=timezone.localdate())
            yes_count = responses.filter(response='yes').count()
            no_count = responses.filter(response='no').count()

        return render(request, 'email_sender_app/filter_responses.html', {
            'form': form,
            'responses': responses,
            'yes_count': yes_count,
            'no_count': no_count
        })

from django.db.models import Count
from django.db.models.functions import TruncDay

class ViewResponsesByMonth(View):
    template_name = 'email_sender_app/view_responses_month.html'

    def get(self, request):
        # Get the current month if no month is explicitly selected
        current_month = timezone.now().strftime('%m')
        month = request.GET.get('month', current_month)
        responses_data = {}
        month_name_str = ""

        # Generate months range for the dropdown
        months = [{'number': i, 'name': month_name[i]} for i in range(1, 13)]

        if month:
            # Convert month to int and get the full month name for the selected month
            month_index = int(month)
            month_name_str = month_name[month_index]

            # Filter responses by the selected month and count per day
            responses_data = (EmployeeResponse.objects
                              .filter(date__month=month, date__year=timezone.now().year)  # Ensuring it filters by the current year
                              .annotate(day=TruncDay('date'))
                              .values('day')
                              .annotate(count=Count('id'))
                              .order_by('day'))

        return render(request, self.template_name, {
            'months': months,
            'responses': responses_data,
            'month_name': month_name_str,
            'selected_month': month
        })