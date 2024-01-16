from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Class(models.Model):
    github_access_token = models.CharField(max_length=200)
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,related_name="user")

    def __str__(self):
        return self.github_access_token

class Student(models.Model):
    user_1 = models.ForeignKey(User,on_delete=models.CASCADE,null=True,related_name="user_1")
    student = models.BooleanField

class GradingConfig(models.Model):
    standard = models.CharField(max_length=200, default='Standard')
    points = models.CharField(max_length=200, default='Points')
    row = models.CharField(max_length=200, default='Row')

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    json_file = models.FileField(upload_to='documents/%Y/%m/%d')
    github_access_token = models.CharField(max_length=200)
