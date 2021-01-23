from rest_framework import serializers

from User.models import UserDetails
from .models import *
from datetime import datetime, timedelta


class CreateNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['note_title', 'note_text', 'label', 'collaborator']


class DisplayNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = '__all__'


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
        fields = ['labelname']


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['reminder']

        def validate(self, time):
            if time.replace(tzinfo=None) - datetime.now() < timedelta(seconds=10):
                raise serializers.ValidationError('SET THE REMINDER FOR VALID TIME')
            return time


class CollaboratorSerializer(serializers.ModelSerializer):
    collaborator = serializers.PrimaryKeyRelatedField(queryset=UserDetails.objects.all())

    class Meta:
        model = Notes
        fields = ['note_title', 'note_text', 'label', 'collaborator']
        extra_kwargs = {'note_title': {'read_only': True}, 'note_text': {'read_only': True},
                        'label': {'read_only': True}}
