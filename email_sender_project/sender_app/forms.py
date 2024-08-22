# forms.py
from django import forms
from django.utils import timezone
from .models import AttendanceResponse, User

class AttendanceResponseForm(forms.ModelForm):
    class Meta:
        model = AttendanceResponse
        fields = ['user', 'date', 'response']
        widgets = {
            'date': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date', 'value': timezone.localdate()}),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email']

class DateForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'value': timezone.localdate()}))

class UserSelectForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all().order_by('name'), label="Select User", empty_label="Choose...")

class FilterResponseForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all().order_by('name'), required=False, label="Select User", empty_label="All Users")
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False, label="Select Date")
    