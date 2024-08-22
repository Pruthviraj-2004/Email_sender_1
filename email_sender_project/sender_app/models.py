from django.db import models
from .fields import EncryptedEmailField
 
# from encrypted_model_fields.fields import EncryptedCharField

# class MyModel(models.Model):
#     secure_data = EncryptedCharField(max_length=100)

class Employee(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = EncryptedEmailField(max_length=254)

    def __str__(self):
        return self.name

class EmployeeResponse(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    response = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])

    def __str__(self):
        return f"{self.employee.name} - {self.date} - {self.response}"