from django import forms
from django.utils import timezone
from .models import EmployeeResponse, Employee, WorkingDays

class EmployeeResponseForm(forms.ModelForm):
    class Meta:
        model = EmployeeResponse
        fields = ['employee', 'date', 'response']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'value': timezone.localdate()
                }
            ),
            'response': forms.Select(attrs={'class': 'form-control'}),
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }

class DateForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'value': timezone.localdate(),
                'class': 'form-control'
            }
        )
    )

class EmployeeSelectForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all().order_by('name'),
        label="Select Employee",
        empty_label="Choose...",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class FilterResponseForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all().order_by('name'),
        required=False,
        label="Select Employee",
        empty_label="All Employees",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        ),
        required=False,
        label="Select Date"
    )

class WorkingDaysForm(forms.ModelForm):
    class Meta:
        model = WorkingDays
        fields = ['month', 'year', 'days']
        widgets = {
            'month': forms.Select(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'days': forms.TextInput(attrs={'class': 'form-control'})
        }

class EmailForm(forms.Form):
    title = forms.CharField(
        max_length=128,
        label='Email Title',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the email title'})
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter the body of the email', 'rows': 5})
    )
    sign = forms.CharField(
        max_length=64,
        label='Signature',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your signature'})
    ) 