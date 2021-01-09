#from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
# Create your models here.
from User.models import UserDetails


class Label(models.Model):
    label = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Notes(models.Model):
    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE)
    note_title = models.CharField(max_length=20)
    note_text = models.TextField()
    is_archive = models.BooleanField(default=False)
    is_pin = models.BooleanField(default=False)
    is_trash = models.BooleanField(default=False)
    #date=models.DateTimeField(default=timezone.now, blank=True)
    label = models.ManyToManyField(Label, blank=True)
