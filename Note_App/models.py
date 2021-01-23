from django.contrib.auth.models import User
from django.db import models

class Label(models.Model):
    labelname = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.labelname


class Notes(models.Model):
    note_title = models.CharField(max_length=20)
    note_text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    label = models.ManyToManyField(Label, blank=True)
    collaborator = models.ManyToManyField(User, related_name="Collabrator_of_note", blank=True)
    is_archive = models.BooleanField(default=False)
    is_pin = models.BooleanField(default=False)
    is_trash = models.BooleanField(default=False)
    reminder = models.DateTimeField(default=None,blank=True, null=True)
