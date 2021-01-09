from django.contrib import admin

# Register your models here.
from User.models import UserDetails, Profile

admin.site.register(UserDetails)
admin.site.register(Profile)
