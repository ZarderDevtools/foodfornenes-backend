# locations/models.py
import uuid
from django.db import models
from django.db.models.functions import Lower

class Area(models.Model):
    """
    Catálogo GLOBAL de zonas/barrios/ciudades.
    Se mantiene global para que no se duplique por household.
    Unicidad case-insensitive por nombre.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="uniq_area_lower_name_global",
            )
        ]
        indexes = [
            models.Index(Lower("name"), name="idx_area_lower_name"),
        ]

    def __str__(self):
        return self.name
