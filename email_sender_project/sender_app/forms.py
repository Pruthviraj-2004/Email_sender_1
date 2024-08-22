# forms.py
    
from django import forms
from django.utils import timezone
from .models import EmployeeResponse, Employee

class EmployeeResponseForm(forms.ModelForm):
    class Meta:
        model = EmployeeResponse
        fields = ['employee', 'date', 'response']
        widgets = {
            'date': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date', 'value': timezone.localdate()}),
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'email']

class DateForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'value': timezone.localdate()}))

class EmployeeSelectForm(forms.Form):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all().order_by('name'), label="Select Employee", empty_label="Choose...")

class FilterResponseForm(forms.Form):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all().order_by('name'), required=False, label="Select Employee", empty_label="All Employees")
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False, label="Select Date")
