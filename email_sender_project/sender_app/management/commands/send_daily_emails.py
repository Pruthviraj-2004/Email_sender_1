from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template import loader
from django.utils import timezone
from sender_app.models import Employee, EmployeeResponse, WorkingDays

class Command(BaseCommand):
    help = 'Send daily emails to all users'

    def handle(self, *args, **kwargs):
        self.send_daily_summary_email()
        self.send_emails_to_all_users()

    def send_emails_to_all_users(self):
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)  # Get tomorrow's date
        month = tomorrow.month
        year = tomorrow.year

        try:
            # Retrieve the working days entry for the month and year of tomorrow's date
            working_days = WorkingDays.objects.get(month=month, year=year)

            # Check if tomorrow is a working day
            if tomorrow.day in working_days.days:
                employees = Employee.objects.all()
                for employee in employees:
                    html_message = loader.render_to_string(
                        'email_sender_app/message.html',
                        {
                            'title': 'Office Attendance Confirmation',
                            'body': f'Hello {employee.name}, this email is to verify whether you will attend the office tomorrow. Please confirm your attendance.',
                            'sign': 'Your Manager',
                            'employee_id': employee.user_id,
                            'date': tomorrow,
                        }
                    )

                    send_mail(
                        'Will You Attend the Office Tomorrow?',
                        'Please confirm your attendance for tomorrow.',
                        'photo2pruthvi@gmail.com',  # Replace with your actual sender email address
                        [employee.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                print(f"Emails sent to employees for {tomorrow}.")

            else:
                print(f"Tomorrow ({tomorrow}) is not a working day. No emails sent.")

        except WorkingDays.DoesNotExist:
            print(f"No working days configuration found for {month}/{year}.")
 
    def send_daily_summary_email(self):
        today = timezone.now().date()  # Get today's date
        month = today.month
        year = today.year

        try:
            # Check if today is a working day
            working_days = WorkingDays.objects.get(month=month, year=year)

            if today.day in working_days.days:  # Check if today is a working day
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
                print(f"Summary email sent for {today}.")

            else:
                print(f"Today ({today}) is not a working day. No summary email sent.")

        except WorkingDays.DoesNotExist:
            print(f"No working days configuration found for {month}/{year}.")
