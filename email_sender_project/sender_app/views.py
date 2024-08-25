import json
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Employee, EmployeeResponse, WorkingDays
from django.utils import timezone

from django.shortcuts import render, redirect
from .forms import DateForm, EmployeeForm, EmployeeResponseForm, EmployeeSelectForm, FilterResponseForm, WorkingDaysForm
from django.contrib import messages
from django.views.generic import View, TemplateView

import schedule
import time
import threading
from django.core.mail import send_mail
from django.template import loader

from django.db.models import Count
from django.db.models.functions import TruncDay

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime


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

scheduler_thread = None

# def send_emails_to_all_users():
#     tomorrow = timezone.now().date() + timezone.timedelta(days=1)
#     employees = Employee.objects.all()
#     for employee in employees:
#         html_message = loader.render_to_string(
#             'email_sender_app/message.html',
#             {
#                 'title': 'Office Attendance Confirmation',
#                 'body': f'Hello {employee.name}, this email is to verify whether you will attend the office tomorrow. Please confirm your attendance.',
#                 'sign': 'Your Manager',
#                 'employee_id': employee.user_id,
#                 'date': tomorrow ,
#             })

#         send_mail(
#             'Will You Attend the Office Tomorrow?',
#             'Please confirm your attendance for tomorrow.',
#             'photo2pruthvi@gmail.com',  # Replace with your email address
#             [employee.email],
#             html_message=html_message,
#             fail_silently=False,
#         )

def send_emails_to_all_users():
    tomorrow = timezone.now() + timezone.timedelta(days=1)
    # .weekday() returns the day of the week as an integer, where Monday is 0 and Sunday is 6
    if tomorrow.weekday() in [0, 1, 2, 3, 6]:  # Monday to Thursday and Sunday
        employees = Employee.objects.all()
        for employee in employees:
            html_message = loader.render_to_string(
                'email_sender_app/message.html',
                {
                    'title': 'Office Attendance Confirmation',
                    'body': f'Hello {employee.name}, this email is to verify whether you will attend the office tomorrow. Please confirm your attendance.',
                    'sign': 'Your Manager',
                    'employee_id': employee.user_id,
                    'date': tomorrow.date(),
                })

            send_mail(
                'Will You Attend the Office Tomorrow?',
                'Please confirm your attendance for tomorrow.',
                'photo2pruthvi@gmail.com',  # Replace with your actual sender email address
                [employee.email],
                html_message=html_message,
                fail_silently=False,
            )

def start_scheduler():
    schedule.every().day.at("11:00").do(send_emails_to_all_users)

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

# def send_emails_to_all_usersss():
#     tomorrow = timezone.now().date() + timezone.timedelta(days=1)
#     month = tomorrow.month
#     year = tomorrow.year

#     try:
#         # Retrieve the working days entry for the month and year of tomorrow's date
#         working_days = WorkingDays.objects.get(month=month, year=year)
#         if tomorrow.day in working_days.days:  # Check if tomorrow is a working day
#             employees = Employee.objects.all()
#             for employee in employees:
#                 html_message = loader.render_to_string(
#                     'email_sender_app/message.html',
#                     {
#                         'title': 'Office Attendance Confirmation',
#                         'body': f'Hello {employee.name}, this email is to verify whether you will attend the office tomorrow. Please confirm your attendance.',
#                         'sign': 'Your Manager',
#                         'employee_id': employee.user_id,
#                         'date': tomorrow,
#                     })

#                 send_mail(
#                     'Will You Attend the Office Tomorrow?',
#                     'Please confirm your attendance for tomorrow.',
#                     'photo2pruthvi@gmail.com',  # Replace with your actual sender email address
#                     [employee.email],
#                     html_message=html_message,
#                     fail_silently=False,
#                 )
#     except WorkingDays.DoesNotExist:
#         print("No working days configuration found for the specified month and year.")

# def start_scheduler():
#     import schedule
#     import time

#     schedule.every().day.at("00:05").do(send_emails_to_all_usersss)

#     while True:
#         schedule.run_pending()
#         time.sleep(10) 

class ControlPanelView(TemplateView):
    template_name = 'email_sender_app/control_panel.html'

class EmployeeListView(View):
    def get(self, request):
        employees = Employee.objects.all()
        return render(request, 'email_sender_app/employees.html', {'employees': employees})

from django.views.generic import ListView
    
class EmployeeResponsesView(View):
    def get(self, request):
        responses = EmployeeResponse.objects.all().select_related('employee').order_by('-date')
        return render(request, 'email_sender_app/employees_responses.html', {'responses': responses})
    
class AddEmployeeView(View):
    def get(self, request):
        form = EmployeeForm()
        return render(request, 'email_sender_app/add_user.html', {'form': form})

    def post(self, request):
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee added successfully!')
            return redirect('add_employee')
        else:
            for field in form.errors:
                messages.error(request, f"{form.errors[field][0]}")

        return render(request, 'email_sender_app/add_user.html', {'form': form})

class AddEmployeeResponseView(View):
    def get(self, request):
        form = EmployeeResponseForm()
        return render(request, 'email_sender_app/add_response.html', {'form': form})

    def post(self, request):
        form = EmployeeResponseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee response added successfully!')
            return redirect('add_employee_response')
        else:
            for error in form.errors.values():
                messages.error(request, error)

        return render(request, 'email_sender_app/add_response.html', {'form': form})

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
            if responses.exists():
                messages.success(request, f'Responses found for {selected_date}.')
            else:
                messages.warning(request, f'No responses found for {selected_date}.')
            return render(request, 'email_sender_app/view_responses.html', {
                'form': form,
                'responses': responses,
                'yes_count': yes_count,
                'no_count': no_count,
                'selected_date': selected_date
            })
        else:
            messages.error(request, 'Error in form submission.')
            return render(request, 'email_sender_app/view_responses.html', {'form': form})

class ViewEmployeeResponseByEmployee(View):
    def get(self, request):
        form = EmployeeSelectForm()
        return render(request, 'email_sender_app/view_user_responses.html', {'form': form})

    def post(self, request):
        form = EmployeeSelectForm(request.POST)
        if form.is_valid():
            employee = form.cleaned_data['employee']
            responses = EmployeeResponse.objects.filter(employee=employee).order_by('-date')
            if responses.exists():
                messages.success(request, f'Responses found for {employee.name}.')
            else:
                messages.warning(request, f'No responses found for {employee.name}.')
            return render(request, 'email_sender_app/view_user_responses.html', {
                'form': form,
                'responses': responses,
                'selected_user': employee
            })
        else:
            messages.error(request, 'Error in form submission.')
            return render(request, 'email_sender_app/view_user_responses.html', {'form': form})
    
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
            messages.success(request, f"Filtered responses for {date}.")

        else:
            responses = responses.filter(date=timezone.localdate())
            yes_count = responses.filter(response='yes').count()
            no_count = responses.filter(response='no').count()
            messages.info(request, "Showing today's responses by default.")

        return render(request, 'email_sender_app/filter_responses.html', {
            'form': form,
            'responses': responses,
            'yes_count': yes_count,
            'no_count': no_count
        })
from django.db.models import Count, Case, When, IntegerField

class ViewResponsesByMonth(View):
    template_name = 'email_sender_app/view_responses_month.html'

    def get(self, request):
        current_month = timezone.now().strftime('%m')
        month = request.GET.get('month', current_month)
        responses_data = {}
        month_name_str = ""
        month_name = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
                      7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}

        months = [{'number': i, 'name': month_name[i]} for i in range(1, 13)]

        if month:
            month_index = int(month)
            month_name_str = month_name[month_index]

            responses_data = (EmployeeResponse.objects
                              .filter(date__month=month, date__year=timezone.now().year)
                              .annotate(day=TruncDay('date'))
                              .values('day')
                              .annotate(
                                  total=Count('id'),
                                  yes_count=Count(Case(When(response='yes', then=1), output_field=IntegerField())),
                                  no_count=Count(Case(When(response='no', then=1), output_field=IntegerField()))
                              )
                              .order_by('day'))

            messages.success(request, f"Displaying responses for {month_name_str}.")

        return render(request, self.template_name, {
            'months': months,
            'responses': responses_data,
            'month_name': month_name_str,
            'selected_month': month
        })
    
@method_decorator(csrf_exempt, name='dispatch')
class ManageWorkingDays(View):
    template_name = 'email_sender_app/manage_working_days.html'

    def get(self, request):
        form = WorkingDaysForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            month = data.get('month')
            year = data.get('year')

            existing_record = WorkingDays.objects.filter(month=month, year=year).first()
            if existing_record:
                form = WorkingDaysForm(data, instance=existing_record)
            else:
                form = WorkingDaysForm(data)

            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success'}, status=200)
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class ManageWorking(View):
    template_name = 'email_sender_app/mange_working.html'

    def get(self, request, year, month):
        try:
            working_days = WorkingDays.objects.get(month=month, year=year)
            days = working_days.days
        except WorkingDays.DoesNotExist:
            days = []

        form = WorkingDaysForm(initial={'month': month, 'year': year})
        context = {
            'form': form,
            'days': json.dumps(days),
            'month': month,
            'year': year
        }
        return render(request, self.template_name, context)

    def post(self, request, year, month):
        try:
            data = json.loads(request.body)
            month = data.get('month')
            year = data.get('year')

            existing_record = WorkingDays.objects.filter(month=month, year=year).first()
            if existing_record:
                form = WorkingDaysForm(data, instance=existing_record)
            else:
                form = WorkingDaysForm(data)

            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success'}, status=200)
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
       
class SelectMonthYearView(View):
    template_name = 'email_sender_app/month_year.html'

    def get(self, request):
        current_year = datetime.now().year
        current_month = datetime.now().month
        years = range(2023, 2031)
        months = range(1, 13)

        messages.info(request, 'Select a month and year to manage working days.')

        return render(request, self.template_name, {
            'years': years,
            'months': months,
            'current_year': current_year,
            'current_month': current_month
        })