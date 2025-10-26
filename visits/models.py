# visits/models.py
import uuid
from decimal import Decimal
from django.db import models
from django.db.models import Index
from django.utils import timezone

from datetime import date

from accounts.models import UserProfile
from places.models import Place


class Visit(models.Model):
    """
    Visita a un Place en una fecha, con nota global y precio por persona opcional.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="visits")
    author = models.ForeignKey(UserProfile, on_delete=models.PROTECT, related_name="visits")

    date = models.DateField(default=timezone.now)
    rating = models.DecimalField(max_digits=3, decimal_places=1)  # rango 1–10
    price_per_person = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            Index(fields=["place", "date"], name="idx_visit_place_date"),
            Index(fields=["place", "created_at"], name="idx_visit_place_created"),
        ]

    def __str__(self):
        return f"{self.place.name} · {self.date} · {self.rating}"
