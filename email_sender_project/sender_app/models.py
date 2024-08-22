from django.db import models

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

class AttendanceResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    response = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])

    def __str__(self):
        return f"{self.user.name} - {self.date} - {self.response}"
