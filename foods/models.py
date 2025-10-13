# foods/models.py
import uuid
from decimal import Decimal
from django.db import models
from django.db.models import Index
from django.db.models.functions import Lower
from django.core.exceptions import ValidationError

from accounts.models import Household
from visits.models import Visit


class Food(models.Model):
    """
    Catálogo de platos/productos por household.
    - Sin categorías.
    - Unicidad case-insensitive por (household, name).
    - is_active para ocultar sin borrar.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="foods")
    name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("name"), "household",
                name="uniq_food_household_lower_name",
            )
        ]
        indexes = [
            Index(Lower("name"), name="idx_food_lower_name"),
            Index(fields=["household"], name="idx_food_household"),
        ]

    def __str__(self):
        return self.name


class VisitFood(models.Model):
    """
    Plato (Food) probado durante una visita concreta.
    - rating: 1–10 (con un decimal).
    - price_paid: opcional, ≥ 0 si se informa.
    - El lugar se obtiene vía visit.place (no se duplica).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name="visit_foods")
    food = models.ForeignKey(Food, on_delete=models.PROTECT, related_name="visit_foods")

    rating = models.DecimalField(max_digits=3, decimal_places=1)  # 1–10
    price_paid = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            Index(fields=["food"], name="idx_visitfood_food"),
            Index(fields=["visit"], name="idx_visitfood_visit"),
            Index(fields=["created_at"], name="idx_visitfood_created"),
        ]

    def __str__(self):
        return f"{self.food.name} @ {self.visit.place.name} ({self.rating})"

    def clean(self):
        if self.rating is not None and not (Decimal("1.0") <= self.rating <= Decimal("10.0")):
            raise ValidationError("rating debe estar entre 1.0 y 10.0")
        if self.price_paid is not None and self.price_paid < 0:
            raise ValidationError("price_paid no puede ser negativo")
