from django.views import View
from django.http import HttpResponse
from django.core.mail import send_mail
from django.template import loader
from django.views import View
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import User, AttendanceResponse
from django.utils import timezone

from django.shortcuts import render, redirect
from .forms import DateForm, FilterResponseForm, UserForm, AttendanceResponseForm, UserSelectForm
from .models import User
from django.contrib import messages

def index(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    html_message = loader.render_to_string(
        'email_sender_app/message.html',
        {
            'title': 'Office Attendance Confirmation',
            'body': f'Hello {user.name}, this email is to verify whether you will attend the office tomorrow. Please confirm your attendance.',
            'sign': 'Your Manager',
            'user_id': user.user_id,
        })

    send_mail(
        'Will You Attend the Office Tomorrow?',
        'Please confirm your attendance for tomorrow.',
        'photo2pruthvi@gmail.com',  # Replace with your email address
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )

    return HttpResponse("Mail Sent!")

def send_emails(request):
    users = User.objects.all()
    for user in users:
        html_message = loader.render_to_string(
            'email_sender_app/message.html',
            {
                'title': 'Office Attendance Confirmation',
                'body': f'Hello {user.name}, this email is to verify whether you will attend the office tomorrow. Please confirm your attendance.',
                'sign': 'Your Manager',
                'user_id': user.user_id,
            })

        send_mail(
            'Will You Attend the Office Tomorrow?',
            'Please confirm your attendance for tomorrow.',
            'photo2pruthvi@gmail.com',  # Replace with your actual sender email address
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
    messages.success(request, 'Emails have been successfully sent to all users.')
    return redirect('control_panel')

class AttendanceResponseView(View):
    def get(self, request, user_id, response_value):
        user = get_object_or_404(User, pk=user_id)
        
        if response_value in ['yes', 'no']:
            response, created = AttendanceResponse.objects.get_or_create(
                user=user,
                date=timezone.now().date(),
                defaults={'response': response_value}
            )
            if not created:
                response.response = response_value
                response.save()

            return HttpResponse(f"Thank you, {user.name}, for your response!")

        return HttpResponse("Invalid response.", status=400)

import schedule
import time
import threading
from django.core.mail import send_mail
from django.template import loader
from .models import User

scheduler_thread = None  # Global variable to track if the scheduler is running

def send_emails_to_all_users():
    users = User.objects.all()
    for user in users:
        html_message = loader.render_to_string(
            'email_sender_app/message.html',
            {
                'title': 'Office Attendance Confirmation',
                'body': f'Hello {user.name}, this email is to verify whether you will attend the office tomorrow. Please confirm your attendance.',
                'sign': 'Your Manager',
                'user_id': user.user_id,
            })

        send_mail(
            'Will You Attend the Office Tomorrow?',
            'Please confirm your attendance for tomorrow.',
            'photo2pruthvi@gmail.com',  # Replace with your email address
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )

def start_scheduler():
    schedule.every().day.at("19:28").do(send_emails_to_all_users)

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

def control_panel(request):
    return render(request, 'email_sender_app/control_panel.html')

def add_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_user')
    else:
        form = UserForm()
    return render(request, 'email_sender_app/add_user.html', {'form': form})

def add_response(request):
    if request.method == 'POST':
        form = AttendanceResponseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_response')
    else:
        form = AttendanceResponseForm()
    return render(request, 'email_sender_app/add_response.html', {'form': form})

def view_responses(request):
    if request.method == 'POST':
        form = DateForm(request.POST)
        if form.is_valid():
            selected_date = form.cleaned_data['date']
            responses = AttendanceResponse.objects.filter(date=selected_date)
            yes_count = responses.filter(response='yes').count()
            no_count = responses.filter(response='no').count()
            return render(request, 'email_sender_app/view_responses.html', {
                'form': form,
                'responses': responses,
                'yes_count': yes_count,
                'no_count': no_count,
                'selected_date': selected_date
            })
    else:
        form = DateForm()
    return render(request, 'email_sender_app/view_responses.html', {'form': form})

def view_user_responses(request):
    form = UserSelectForm(request.POST or None)
    responses = None
    if request.method == 'POST' and form.is_valid():
        user = form.cleaned_data['user']
        responses = AttendanceResponse.objects.filter(user=user).order_by('-date')
    return render(request, 'email_sender_app/view_user_responses.html', {
        'form': form,
        'responses': responses,
        'selected_user': form.cleaned_data['user'] if responses else None
    })

def filter_responses(request):
    form = FilterResponseForm(request.GET or None)
    responses = AttendanceResponse.objects.all()

    yes_count = no_count = 0

    if request.GET and form.is_valid():
        if form.cleaned_data['user']:
            responses = responses.filter(user=form.cleaned_data['user'])
        if form.cleaned_data['date']:
            responses = responses.filter(date=form.cleaned_data['date'])

        yes_count = responses.filter(response='yes').count()
        no_count = responses.filter(response='no').count()

    return render(request, 'email_sender_app/filter_responses.html', {
        'form': form,
        'responses': responses,
        'yes_count': yes_count,
        'no_count': no_count
    })
