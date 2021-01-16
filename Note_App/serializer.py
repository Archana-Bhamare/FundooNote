from rest_framework import serializers
from .models import *


class CreateNoteSerializer(serializers.ModelSerializer):
    label = serializers.CharField(max_length=20,default=None)
    class Meta:
        model = Notes
        fields = ['note_title', 'note_text', 'label']


class DisplayNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = '__all__'


class RestoreNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['is_trash']


class SearchNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['note_title', 'note_text']

        def validate(self, data):
            note_title = data.get('note_title', '')
            content = data.get('note_text', '')
            return data


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['label']
