from django.contrib.auth.models import User
from django.db import models
from User.models import UserDetails


class Label(models.Model):
    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE)
    label = models.CharField(max_length=20)

    def __str__(self):
        return self.label


class Notes(models.Model):
    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE)
    note_title = models.CharField(max_length=20)
    note_text = models.TextField()
    label = models.ManyToManyField(to=Label, blank=True)
    collaborators = models.ManyToManyField(User, blank=True)
    is_archive = models.BooleanField(default=False)
    is_pin = models.BooleanField(default=False)
    is_trash = models.BooleanField(default=False)
