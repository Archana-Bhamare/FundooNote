from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile, UserDetails


@receiver(post_save, sender=UserDetails)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
