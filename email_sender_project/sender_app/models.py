from django.db import models
from .fields import EncryptedEmailField
 
# from encrypted_model_fields.fields import EncryptedCharField

# class MyModel(models.Model):
#     secure_data = EncryptedCharField(max_length=100)

class Employee(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = EncryptedEmailField(max_length=254, unique=True)

    def __str__(self):
        return self.name

class EmployeeResponse(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    response = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])

    def __str__(self):
        return f"{self.employee.name} - {self.date} - {self.response}"
    
    class Meta:
        unique_together = ('employee', 'date')

class WorkingDays(models.Model):
    MONTH_CHOICES = [
        (1, "January"), (2, "February"), (3, "March"),
        (4, "April"), (5, "May"), (6, "June"),
        (7, "July"), (8, "August"), (9, "September"),
        (10, "October"), (11, "November"), (12, "December")
    ]

    month = models.IntegerField(choices=MONTH_CHOICES)
    year = models.IntegerField()
    days = models.JSONField(default=list)

    def __str__(self):
        return f"{self.get_month_display()} {self.year}"

    class Meta:
        verbose_name_plural = "Working Days"
        unique_together = ('month', 'year')

# class EmployeeEventResponse(models.Model):
#     employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
#     date = models.DateField()
#     response = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])

#     def __str__(self):
#         return f"{self.employee.name} - {self.date} - {self.response}"
    
#     class Meta:
#         unique_together = ('employee', 'date')

# class EmailAccount(models.Model):
#     email = models.EmailField(unique=True)
#     password = models.CharField(max_length=255)
#     smtp_server = models.CharField(max_length=255)
#     smtp_port = models.IntegerField()
#     use_tls = models.BooleanField(default=True)
#     use_ssl = models.BooleanField(default=False)
    
#     def __str__(self):
#         return self.email
    
# class ManagerEmployee(models.Model):
#     name = models.CharField(max_length=255)
#     email = models.EmailField(unique=True)
#     password = models.CharField(max_length=255)
#     app_password = models.CharField(max_length=255)
#     login_count = models.IntegerField(default=0)

#     email_account = models.ForeignKey(EmailAccount, on_delete=models.CASCADE, related_name='manager_employees')
    
#     def __str__(self):
#         return f"{self.name} ({self.email})"    