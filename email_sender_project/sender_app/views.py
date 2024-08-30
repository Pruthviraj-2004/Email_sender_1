import json
from urllib import response
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Employee, EmployeeEventResponse, EmployeeResponse, OrganizationEvent, WorkingDays
from django.utils import timezone

from django.shortcuts import render, redirect
from .forms import DateForm, EmailForm, EmployeeEventResponseForm, EmployeeForm, EmployeeResponseForm, EmployeeSelectForm, EventSelectForm, FilterResponseForm, OrganizationEventForm, WorkingDaysForm
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

from django.db.models import Count, Case, When, IntegerField

from tablib import Dataset
from .resources import EmployeeResource

import matplotlib
matplotlib.use('Agg') 
from io import BytesIO
import base64
import matplotlib.pyplot as plt

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

class SendSummaryEmail(View):
    def get(self, request):
        today = timezone.now().date()
        responses = EmployeeResponse.objects.filter(date=today)
        
        total_responses = responses.count()
        yes_count = responses.filter(response='yes').count()
        no_count = responses.filter(response='no').count()
        
        html_message = loader.render_to_string(
            'email_sender_app/summary_message.html',
            {
                'title': 'Daily Attendance Summary',
                'body': f'Attendance summary for {today.strftime("%Y-%m-%d")}:',
                'total_responses': total_responses,
                'yes_count': yes_count,
                'no_count': no_count,
                'sign': 'Your Manager',
            }
        )
        
        send_mail(
            'Daily Attendance Summary',
            'Here is the summary of today\'s attendance responses.',
            'photo2pruthvi@gmail.com',  # Replace with your email address
            ['photo2pruthvi@gmail.com'],  # Replace with the recipient's email address
            fail_silently=False,
            html_message=html_message  # Ensure this is correctly placed in the send_mail function
        )

        messages.success(request, 'Emails have been successfully sent to all employees.')
        return redirect('control_panel')

class SendEventSummaryEmail(View):
    def get(self, request):
        today = timezone.now().date()
        
        # Find the nearest upcoming event
        upcoming_event = OrganizationEvent.objects.filter(date__gte=today).order_by('date').first()
        
        if upcoming_event:
            responses = EmployeeEventResponse.objects.filter(event=upcoming_event)
            yes_count = responses.filter(response='yes').count()
            no_count = responses.filter(response='no').count()
            total_responses = responses.count()

            html_message = loader.render_to_string(
                'email_sender_app/summary_message.html',
                {
                    'title': 'Upcoming Event Summary',
                    'body': f'Event summary for {upcoming_event.name} on {upcoming_event.date.strftime("%Y-%m-%d")}:',
                    'total_responses': total_responses,
                    'yes_count': yes_count,
                    'no_count': no_count,
                    'sign': 'Your Manager',
                }
            )
            
            send_mail(
                'Upcoming Event Summary',
                f'Here is the summary of responses for the upcoming event: {upcoming_event.name}.',
                'photo2pruthvi@gmail.com',  # Replace with your email address
                ['photo2pruthvi@gmail.com'],  # Replace with the recipient's email address
                fail_silently=False,
                html_message=html_message  # Ensure this is correctly placed in the send_mail function
            )

            messages.success(request, f'Emails have been successfully sent for the upcoming event: {upcoming_event.name}')
        else:
            messages.warning(request, 'No upcoming events found to send summary emails.')

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

class EmployeeEventResponseView(View):
    def get(self, request, employee_id, event_id, response_value):
        employee = get_object_or_404(Employee, pk=employee_id)
        event = get_object_or_404(OrganizationEvent, pk=event_id)
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        
        if response_value in ['yes', 'no']:
            response, created = EmployeeEventResponse.objects.get_or_create(
                employee=employee,
                event=event,
                date=tomorrow,
                defaults={'response': response_value}
            )
            if not created:
                response.response = response_value
                response.save()

            return HttpResponse(f"Thank you, {employee.name}, for your response to the event {event.name}!")

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

def send_daily_summary_email():
    today = timezone.now().date()
    responses = EmployeeResponse.objects.filter(date=today)
    
    total_responses = responses.count()
    yes_count = responses.filter(response='yes').count()
    no_count = responses.filter(response='no').count()
    
    html_message = loader.render_to_string(
        'email_sender_app/summary_message.html',
        {
            'title': 'Daily Attendance Summary',
            'body': f'Attendance summary for {today.strftime("%Y-%m-%d")}:',
            'total_responses': total_responses,
            'yes_count': yes_count,
            'no_count': no_count,
            'sign': 'Your Manager',
        }
    )
    
    send_mail(
        'Daily Attendance Summary',
        'Here is the summary of today\'s attendance responses.',
        'photo2pruthvi@gmail.com',  # Replace with your email address
        ['photo2pruthvi@gmail.com'],  # Replace with the recipient's email address
        fail_silently=False,
        html_message=html_message
    )

def start_scheduler():
    schedule.every().day.at("11:00").do(send_emails_to_all_users)
    schedule.every().day.at("11:05").do(send_daily_summary_email)

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
    
class EmployeeResponsesView(View):
    def get(self, request):
        responses = EmployeeResponse.objects.all().select_related('employee').order_by('-date')
        return render(request, 'email_sender_app/employees_responses.html', {'responses': responses})

class OrganizationEventListView(View):
    def get(self, request):
        events = OrganizationEvent.objects.all().order_by('-date')
        return render(request, 'email_sender_app/organization_events.html', {'events': events})
    
class EmployeeEventResponsesView(View):
    def get(self, request):
        responses = EmployeeEventResponse.objects.all().select_related('employee', 'event').order_by('-date')
        return render(request, 'email_sender_app/employee_event_responses.html', {'responses': responses})

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
    
class CreateOrganizationEventView(View):
    def get(self, request):
        form = OrganizationEventForm()
        return render(request, 'email_sender_app/create_event.html', {'form': form})

    def post(self, request):
        form = OrganizationEventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('organization_events')  # Redirect to a list of events or another relevant page
        return render(request, 'email_sender_app/create_event.html', {'form': form})

class CreateEmployeeEventResponseView(View):
    def get(self, request):
        form = EmployeeEventResponseForm()
        return render(request, 'email_sender_app/create_employee_response.html', {'form': form})

    def post(self, request):
        form = EmployeeEventResponseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employee_event_responses')  # Redirect to a list of responses or another relevant page
        return render(request, 'email_sender_app/create_employee_response.html', {'form': form})

# class ViewEmployeeResponses(View):
#     def get(self, request):
#         form = DateForm()
#         return render(request, 'email_sender_app/view_responses.html', {'form': form})

#     def post(self, request):
#         form = DateForm(request.POST)
#         if form.is_valid():
#             selected_date = form.cleaned_data['date']
#             responses = EmployeeResponse.objects.filter(date=selected_date)
#             yes_count = responses.filter(response='yes').count()
#             no_count = responses.filter(response='no').count()
#             if responses.exists():
#                 messages.success(request, f'Responses found for {selected_date}.')
#             else:
#                 messages.warning(request, f'No responses found for {selected_date}.')
#             return render(request, 'email_sender_app/view_responses.html', {
#                 'form': form,
#                 'responses': responses,
#                 'yes_count': yes_count,
#                 'no_count': no_count,
#                 'selected_date': selected_date
#             })
#         else:
#             messages.error(request, 'Error in form submission.')
#             return render(request, 'email_sender_app/view_responses.html', {'form': form})

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

            total_employees = Employee.objects.count()  # Get total number of employees
            not_responded_count = total_employees - (yes_count + no_count)  # Calculate not responded count

            # Generate the pie chart
            labels = ['Yes', 'No', 'Not Responded']
            sizes = [yes_count, no_count, not_responded_count]
            colors = ['#28a745', '#dc3545', '#ffc107']
            explode = (0.1, 0, 0)  # explode the 'yes' slice for emphasis

            plt.figure(figsize=(6, 4))
            plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
            plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            # Save the pie chart to a BytesIO object
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)

            # Encode the image to base64 string
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            if responses.exists():
                messages.success(request, f'Responses found for {selected_date}.')
            else:
                messages.warning(request, f'No responses found for {selected_date}.')

            return render(request, 'email_sender_app/view_responses.html', {
                'form': form,
                'responses': responses,
                'yes_count': yes_count,
                'no_count': no_count,
                'not_responded_count': not_responded_count,
                'selected_date': selected_date,
                'chart_image': image_base64  # Pass the image to the template
            })
        else:
            messages.error(request, 'Error in form submission.')
            return render(request, 'email_sender_app/view_responses.html', {'form': form})

# class ViewEventResponses(View):
#     def get(self, request):
#         form = EventSelectForm()
#         return render(request, 'email_sender_app/view_event_responses.html', {'form': form})

#     def post(self, request):
#         form = EventSelectForm(request.POST)
#         if form.is_valid():
#             selected_event = form.cleaned_data['event']
#             responses = EmployeeEventResponse.objects.filter(event=selected_event)
#             yes_count = responses.filter(response='yes').count()
#             no_count = responses.filter(response='no').count()
#             if responses.exists():
#                 messages.success(request, f'Responses found for {selected_event.name}.')
#             else:
#                 messages.warning(request, f'No responses found for {selected_event.name}.')
#             return render(request, 'email_sender_app/view_event_responses.html', {
#                 'form': form,
#                 'responses': responses,
#                 'yes_count': yes_count,
#                 'no_count': no_count,
#                 'selected_event': selected_event
#             })
#         else:
#             messages.error(request, 'Error in form submission.')
#             return render(request, 'email_sender_app/view_event_responses.html', {'form': form})

class ViewEventResponses(View):
    def get(self, request):
        form = EventSelectForm()
        return render(request, 'email_sender_app/view_event_responses.html', {'form': form})

    def post(self, request):
        form = EventSelectForm(request.POST)
        if form.is_valid():
            selected_event = form.cleaned_data['event']
            responses = EmployeeEventResponse.objects.filter(event=selected_event)
            yes_count = responses.filter(response='yes').count()
            no_count = responses.filter(response='no').count()

            total_employees = Employee.objects.count()  # Get total number of employees
            not_responded_count = total_employees - (yes_count + no_count)  # Calculate not responded count

            # Generate the pie chart
            labels = ['Yes', 'No', 'Not Responded']
            sizes = [yes_count, no_count, not_responded_count]
            colors = ['#28a745', '#dc3545', '#ffc107']
            explode = (0.1, 0, 0)  # explode the 'yes' slice for emphasis

            plt.figure(figsize=(6, 4))
            plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
            plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            # Save the pie chart to a BytesIO object
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)

            # Encode the image to base64 string
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            if responses.exists():
                messages.success(request, f'Responses found for {selected_event.name}.')
            else:
                messages.warning(request, f'No responses found for {selected_event.name}.')

            return render(request, 'email_sender_app/view_event_responses.html', {
                'form': form,
                'responses': responses,
                'yes_count': yes_count,
                'no_count': no_count,
                'not_responded_count': not_responded_count,
                'selected_event': selected_event,
                'chart_image': image_base64  # Pass the image to the template
            })
        else:
            messages.error(request, 'Error in form submission.')
            return render(request, 'email_sender_app/view_event_responses.html', {'form': form})

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

# class ViewResponsesByMonth(View):
#     template_name = 'email_sender_app/view_responses_month.html'

#     def get(self, request):
#         current_month = timezone.now().strftime('%m')
#         month = request.GET.get('month', current_month)
#         responses_data = {}
#         month_name_str = ""
#         month_name = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
#                       7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}

#         months = [{'number': i, 'name': month_name[i]} for i in range(1, 13)]

#         if month:
#             month_index = int(month)
#             month_name_str = month_name[month_index]

#             responses_data = (EmployeeResponse.objects
#                               .filter(date__month=month, date__year=timezone.now().year)
#                               .annotate(day=TruncDay('date'))
#                               .values('day')
#                               .annotate(
#                                   total=Count('id'),
#                                   yes_count=Count(Case(When(response='yes', then=1), output_field=IntegerField())),
#                                   no_count=Count(Case(When(response='no', then=1), output_field=IntegerField()))
#                               )
#                               .order_by('day'))

#             messages.success(request, f"Displaying responses for {month_name_str}.")

#         return render(request, self.template_name, {
#             'months': months,
#             'responses': responses_data,
#             'month_name': month_name_str,
#             'selected_month': month
#         })

# class ViewResponsesByMonth(View):
#     template_name = 'email_sender_app/view_responses_month.html'

#     def get(self, request):
#         current_month = timezone.now().strftime('%m')
#         month = request.GET.get('month', current_month)
#         responses_data = {}
#         month_name_str = ""
#         month_name = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
#                       7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}

#         months = [{'number': i, 'name': month_name[i]} for i in range(1, 13)]

#         if month:
#             month_index = int(month)
#             month_name_str = month_name[month_index]

#             responses_data = (EmployeeResponse.objects
#                               .filter(date__month=month, date__year=timezone.now().year)
#                               .annotate(day=TruncDay('date'))
#                               .values('day')
#                               .annotate(
#                                   total=Count('id'),
#                                   yes_count=Count(Case(When(response='yes', then=1), output_field=IntegerField())),
#                                   no_count=Count(Case(When(response='no', then=1), output_field=IntegerField()))
#                               )
#                               .order_by('day'))

#             messages.success(request, f"Displaying responses for {month_name_str}.")

#             total_employees = Employee.objects.count()

#             days = [data['day'].strftime('%Y-%m-%d') for data in responses_data]
#             yes_counts = [data['yes_count'] for data in responses_data]
#             no_counts = [data['no_count'] for data in responses_data]
#             not_responded_counts = [total_employees - (yes + no) for yes, no in zip(yes_counts, no_counts)]

#             plt.figure(figsize=(10, 6))
#             bar_width = 0.2
#             index = range(len(days))
            
#             plt.bar(index, yes_counts, width=bar_width, color='#28a745', label='Yes')
#             plt.bar([i + bar_width for i in index], no_counts, width=bar_width, color='#dc3545', label='No')
#             plt.bar([i + 2 * bar_width for i in index], not_responded_counts, width=bar_width, color='#ffc107', label='Not Responded')
            
#             plt.xlabel('Day')
#             plt.ylabel('Number of Responses')
#             plt.title(f'Response Distribution for {month_name_str}')
#             plt.xticks([i + bar_width for i in index], days, rotation=45)
#             plt.legend()
#             plt.tight_layout()

#             # Save the chart to a BytesIO object
#             buffer = BytesIO()
#             plt.savefig(buffer, format='png')
#             plt.close()
#             buffer.seek(0)

#             # Encode the image to base64 string
#             image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

#         return render(request, self.template_name, {
#             'months': months,
#             'responses': responses_data,
#             'month_name': month_name_str,
#             'selected_month': month,
#             'chart_image': image_base64 if month else None
#         })

class ViewResponsesByMonth(View):
    template_name = 'email_sender_app/view_responses_month.html'

    def get(self, request):
        current_month = timezone.now().strftime('%m')
        month = request.GET.get('month', current_month)
        responses_data = []
        month_name = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
                      7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}

        months = [{'number': i, 'name': month_name[i]} for i in range(1, 13)]
        month_name_str = month_name.get(int(month), "")

        if month:
            month_index = int(month)
            month_name_str = month_name[month_index]

            # Get total number of employees once
            total_employees = Employee.objects.count()

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

            # Add not_responded_count to each response entry
            for data in responses_data:
                data['not_responded_count'] = total_employees - (data['yes_count'] + data['no_count'])

            messages.success(request, f"Displaying responses for {month_name_str}.")

            # Plotting code (if necessary) would go here...

            # # Example plotting code for a grouped bar chart:
            # days = [data['day'].strftime('%Y-%m-%d') for data in responses_data]
            # yes_counts = [data['yes_count'] for data in responses_data]
            # no_counts = [data['no_count'] for data in responses_data]
            # not_responded_counts = [data['not_responded_count'] for data in responses_data]

            # plt.figure(figsize=(10, 6))
            # bar_width = 0.2
            # index = range(len(days))

            # plt.bar(index, yes_counts, width=bar_width, color='#28a745', label='Yes')
            # plt.bar([i + bar_width for i in index], no_counts, width=bar_width, color='#dc3545', label='No')
            # plt.bar([i + 2 * bar_width for i in index], not_responded_counts, width=bar_width, color='#ffc107', label='Not Responded')

            # plt.xlabel('Day')
            # plt.ylabel('Number of Responses')
            # plt.title(f'Response Distribution for {month_name_str}')
            # plt.xticks([i + bar_width for i in index], days, rotation=45)
            # plt.legend()
            # plt.tight_layout()

            # # Save the chart to a BytesIO object
            # buffer = BytesIO()
            # plt.savefig(buffer, format='png')
            # plt.close()
            # buffer.seek(0)

            # # Encode the image to base64 string
            # image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            # Example plotting code for a stacked bar chart:
            days = [data['day'].strftime('%Y-%m-%d') for data in responses_data]
            yes_counts = [data['yes_count'] for data in responses_data]
            no_counts = [data['no_count'] for data in responses_data]
            not_responded_counts = [data['not_responded_count'] for data in responses_data]

            plt.figure(figsize=(10, 6))
            bar_width = 0.5
            index = range(len(days))

            # Plot 'Yes' counts
            bars_yes = plt.bar(index, yes_counts, width=bar_width, color='#28a745', label='Yes')

            # Plot 'No' counts on top of 'Yes' counts
            bars_no = plt.bar(index, no_counts, width=bar_width, bottom=yes_counts, color='#dc3545', label='No')

            # Plot 'Not Responded' counts on top of 'Yes' and 'No' counts
            bars_not_responded = plt.bar(index, not_responded_counts, width=bar_width,
                                        bottom=[yes + no for yes, no in zip(yes_counts, no_counts)],
                                        color='#ffc107', label='Not Responded')

            # Annotate 'Yes' counts
            for bar, count in zip(bars_yes, yes_counts):
                plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2, str(count), ha='center', va='center', color='white')

            # Annotate 'No' counts
            for bar, yes, count in zip(bars_no, yes_counts, no_counts):
                plt.text(bar.get_x() + bar.get_width() / 2, yes + bar.get_height() / 2, str(count), ha='center', va='center', color='white')

            # Annotate 'Not Responded' counts
            for bar, yes, no, count in zip(bars_not_responded, yes_counts, no_counts, not_responded_counts):
                plt.text(bar.get_x() + bar.get_width() / 2, yes + no + bar.get_height() / 2, str(count), ha='center', va='center', color='black')

            plt.xlabel('Day')
            plt.ylabel('Number of Responses')
            plt.title(f'Response Distribution for {month_name_str}')
            plt.xticks(index, days, rotation=45)
            plt.legend()
            plt.tight_layout()

            # Save the chart to a BytesIO object
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)

            # Encode the image to base64 string
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return render(request, self.template_name, {
            'months': months,
            'responses': responses_data,
            'month_name': month_name_str,
            'selected_month': month,
            'chart_image': image_base64 if month else None
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

class UploadFileView(View):
    def get(self, request):
        return render(request, 'email_sender_app/upload.html')

    def post(self, request):
        if 'file' in request.FILES:
            new_employees = request.FILES['file']
            file_extension = new_employees.name.split('.')[-1].lower()

            # Check if the file format is CSV or Excel
            if file_extension not in ['csv', 'xls', 'xlsx']:
                messages.error(request, 'Invalid file format. Please upload a .csv or .xls/.xlsx file.')
                return redirect('upload_file')

            try:
                dataset = Dataset()

                # Handle CSV files
                if file_extension == 'csv':
                    imported_data = dataset.load(new_employees.read().decode('utf-8'), format='csv')
                # Handle Excel files (xls and xlsx)
                elif file_extension == 'xls':
                    # Use openpyxl to read Excel files
                    imported_data = dataset.load(new_employees.read(), format='xls')
                elif file_extension == 'xlsx':
                    imported_data = dataset.load(new_employees.read(), format='xlsx')

                employee_resource = EmployeeResource()
                result = employee_resource.import_data(dataset, dry_run=True)  # Test the data import

                if not result.has_errors():
                    employee_resource.import_data(dataset, dry_run=False)  # Actually import now
                    messages.success(request, 'Employees imported successfully!')
                else:
                    messages.error(request, 'Import failed. Please check the data format.')

            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')

            return redirect('upload_file')

        messages.error(request, 'No file was provided.')
        return redirect('upload_file')

class EmployeeExportView(View):
    def get(self, request, *args, **kwargs):
        # Create an instance of EmployeeResource
        employee_resource = EmployeeResource()
        
        # Query all employees
        queryset = Employee.objects.all()
        
        # Use the export method to get the dataset
        dataset = employee_resource.export(queryset)
        
        # Choose the export format (e.g., CSV)
        export_format = request.GET.get('format', 'csv')
        
        if export_format == 'csv':
            content_type = 'text/csv'
            response = HttpResponse(dataset.csv, content_type=content_type)
            response['Content-Disposition'] = 'attachment; filename="employees.csv"'
        elif export_format == 'xls':
            content_type = 'application/vnd.ms-excel'
            response = HttpResponse(dataset.export('xls'), content_type=content_type)
            response['Content-Disposition'] = 'attachment; filename="employees.xls"'
        else:
            return HttpResponse("Unsupported format", status=400)
        
        return response

@method_decorator(csrf_exempt, name='dispatch')
class EmployeeDeleteView(View):
    def delete(self, request, user_id):
        try:
            employee = get_object_or_404(Employee, user_id=user_id)
            employee.delete()
            messages.success(request, 'Employee deleted successfully.')
            return JsonResponse({'message': 'Employee deleted successfully.'}, status=204)
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'Employee not found.'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class SendCustomEmailsYesNoToAllEmployees(View):
    def get(self, request):
        form = EmailForm()
        return render(request, 'email_sender_app/email_form.html', {'form': form})

    def post(self, request):
        form = EmailForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            body = form.cleaned_data['body']
            sign = form.cleaned_data['sign']
            tomorrow = timezone.now().date() + timezone.timedelta(days=1)
            employees = Employee.objects.all()

            for employee in employees:
                html_message = loader.render_to_string(
                    'email_sender_app/message.html',
                    {
                        'title': title,
                        'body': f'Hello {employee.name},<br><pre>{body}</pre>',
                        'sign': sign,
                        'employee_id': employee.user_id,
                        'date': tomorrow,
                    })

                send_mail(
                    title,
                    body,
                    'photo2pruthvi@gmail.com',  # Replace with your actual sender email address
                    [employee.email],
                    html_message=html_message,
                    fail_silently=False,
                )
            messages.success(request, 'Emails have been successfully sent to all employees.')
            return redirect('control_panel')
        else:
            return render(request, 'email_sender_app/email_form.html', {'form': form})

@method_decorator(csrf_exempt, name='dispatch')
class SendCustomEmailsToAllEmployees(View):
    def get(self, request):
        form = EmailForm()
        return render(request, 'email_sender_app/email_form.html', {'form': form})

    def post(self, request):
        form = EmailForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            body = form.cleaned_data['body']
            sign = form.cleaned_data['sign']
            employees = Employee.objects.all()

            for employee in employees:
                formatted_body = body.replace('\n', '<br>').replace(' ', '&nbsp;')
                html_message = loader.render_to_string(
                    'email_sender_app/custom_message.html',
                    {
                        'title': title,
                        'body': f'Hello {employee.name},<br>{formatted_body}',  # Preserving new lines and spaces
                        'sign': sign,
                        'employee_id': employee.user_id,
                    })
                
                send_mail(
                    title,
                    body,
                    'photo2pruthvi@gmail.com',  # Replace with your actual sender email address
                    [employee.email],
                    html_message=html_message,
                    fail_silently=False,
                )
            messages.success(request, 'Custom emails have been successfully sent to all employees.')
            return redirect('control_panel')
        else:
            return render(request, 'email_sender_app/email_form.html', {'form': form})



    
    