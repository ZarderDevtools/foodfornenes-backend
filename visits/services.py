# visits/services.py
from decimal import Decimal
from django.db.models import Avg, Count, Max
from django.utils import timezone

from places.models import Place
from .models import Visit


def recompute_place_metrics(place_id: str) -> None:
    """
    Recalcula avg_rating, avg_price_pp, visits_count, last_visit_at para un Place.
    - avg_price_pp solo con visitas que tengan price_per_person válido (>= 0)
    """
    agg = Visit.objects.filter(place_id=place_id).aggregate(
        visits_count=Count("id"),
        avg_rating=Avg("rating"),
        avg_price_pp=Avg("price_per_person"),
        last_by_date=Max("date"),
        last_by_created=Max("created_at"),
    )

    place = Place.objects.get(id=place_id)

    place.visits_count = agg["visits_count"] or 0
    place.avg_rating = (agg["avg_rating"] or None)
    place.avg_price_pp = (agg["avg_price_pp"] or None)

    # Tomamos como referencia la última creación (más precisa en el tiempo);
    # si no hay, usamos la última fecha.
    place.last_visit_at = agg["last_by_created"] or (
        timezone.make_aware(
            timezone.datetime.combine(agg["last_by_date"], timezone.datetime.min.time())
        ) if agg["last_by_date"] else None
    )

    place.save(update_fields=["visits_count", "avg_rating", "avg_price_pp", "last_visit_at"])
