from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *


class RegistrationFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = ['username', 'email', 'password', 'confirm_password']


class LoginFormFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = ['username', 'password']


class ForgotPasswordFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = ['email']


class ResetPasswordFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = ['password', 'confirm_password']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['image']
