# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Household


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if not created:
        return
    # Si existe un único Household, úsalo; si no, crea uno por defecto
    household = Household.objects.first()
    if household is None:
        household = Household.objects.create(name="Default Household")
    UserProfile.objects.create(user=instance, household=household)
