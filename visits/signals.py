# visits/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Visit
from .services import recompute_place_metrics


@receiver(post_save, sender=Visit)
def visit_saved(sender, instance: Visit, created, **kwargs):
    recompute_place_metrics(instance.place_id)


@receiver(post_delete, sender=Visit)
def visit_deleted(sender, instance: Visit, **kwargs):
    recompute_place_metrics(instance.place_id)
