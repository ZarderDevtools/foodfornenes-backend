# places/models.py
import uuid
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower

from accounts.models import Household
from categorization.models import PlaceType, Tag
from locations.models import Area


class Place(models.Model):
    """
    Lugar gastronómico general (restaurante, bar, carnicería, pescadería, panadería, etc.).
    – Scope por household
    – Tipo vía PlaceType (global o local)
    – Área global
    – Métricas denormalizadas para filtros rápidos (avg_rating, avg_price_pp, visits_count, last_visit_at)
    """

    PRICE_RANGE_CHOICES = (
        ("€", "€"),
        ("€€", "€€"),
        ("€€€", "€€€"),
        ("€€€€", "€€€€"),
        ("€€€€€", "€€€€€"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    household = models.ForeignKey(Household, on_delete=models.PROTECT, related_name="places")
    name = models.CharField(max_length=200)
    place_type = models.ForeignKey(PlaceType, on_delete=models.PROTECT, related_name="places")
    area = models.ForeignKey(Area, null=True, blank=True, on_delete=models.SET_NULL, related_name="places")

    price_range = models.CharField(max_length=5, choices=PRICE_RANGE_CHOICES, default="€")
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)

    # Métricas (se actualizarán cuando creemos la app de visits)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    avg_price_pp = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    visits_count = models.PositiveIntegerField(default=0)
    last_visit_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tags = models.ManyToManyField(Tag, through="PlaceTag", related_name="places", blank=True)

    class Meta:
        # Evitar duplicados por nombre dentro del mismo household y área (case-insensitive)
        constraints = [
            models.UniqueConstraint(
                Lower("name"), "household", "area",
                name="uniq_place_household_area_lower_name",
            )
        ]
        indexes = [
            models.Index(fields=["household", "place_type"], name="idx_place_household_type"),
            models.Index(fields=["area", "price_range"], name="idx_place_area_pricerange"),
        ]

    def __str__(self):
        return self.name


class PlaceTag(models.Model):
    """
    Relación M:N entre Place y Tag.
    """
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("place", "tag"),)
        indexes = [
            models.Index(fields=["tag", "place"], name="idx_placetag_tag_place"),
        ]

    def __str__(self):
        return f"{self.place} · {self.tag}"
