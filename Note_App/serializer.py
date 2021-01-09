from rest_framework import serializers
from .models import *


class CreateNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['note_title', 'note_text', 'is_archive', 'is_pin', 'is_trash', 'label']


class DisplayNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = '__all__'


class RestoreNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['is_trash']

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['label']
