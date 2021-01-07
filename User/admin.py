from django.contrib import admin

# Register your models here.
from User.models import UserDetails

admin.site.register(UserDetails)