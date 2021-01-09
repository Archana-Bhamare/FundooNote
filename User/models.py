from django.db import models


class UserDetails(models.Model):
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=20)
    confirm_password = models.CharField(max_length=20)

    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(UserDetails, on_delete=models.CASCADE)
    image = models.ImageField(default='default.png', upload_to='profile_picture/')

