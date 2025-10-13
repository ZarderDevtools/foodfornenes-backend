# categorization/models.py
import uuid
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from accounts.models import Household


class PlaceType(models.Model):
    """
    Catálogo de tipos de lugar (restaurant, bar, carnicería, etc.).
    - Global (household = NULL) o local por household.
    - is_active para ocultar sin borrar.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=60)
    household = models.ForeignKey(
        Household, null=True, blank=True, on_delete=models.CASCADE, related_name="place_types"
    )  # NULL = global
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Reglas de unicidad:
        # 1) Para filas globales (household IS NULL): name en minúsculas único globalmente
        # 2) Para filas locales (household IS NOT NULL): (household, lower(name)) único
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                condition=Q(household__isnull=True),
                name="uniq_global_placetype_lower_name",
            ),
            models.UniqueConstraint(
                Lower("name"), "household",
                condition=Q(household__isnull=False),
                name="uniq_local_placetype_household_lower_name",
            ),
        ]
        indexes = [
            models.Index(Lower("name"), name="idx_placetype_lower_name"),
            models.Index(fields=["household", "is_active"], name="idx_placetype_household_active"),
        ]

    def __str__(self):
        scope = "(global)" if self.household_id is None else "(local)"
        return f"{self.name} · {scope}"


class Tag(models.Model):
    """
    Etiquetas normalizadas (italiano, tapas, veg-friendly, etc.) por household.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    household = models.ForeignKey(
        Household, on_delete=models.CASCADE, related_name="tags"
    )
    name = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("name"), "household",
                name="uniq_tag_household_lower_name",
            )
        ]
        indexes = [
            models.Index(Lower("name"), name="idx_tag_lower_name"),
            models.Index(fields=["household"], name="idx_tag_household"),
        ]

    def __str__(self):
        return f"{self.name}"
