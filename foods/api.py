from rest_framework import serializers
from django_filters import rest_framework as filters
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db.models import OuterRef, Subquery
from core.api import HouseholdScopedViewSet
from core.validators import (
    validate_rating_1_to_10,
    validate_price_non_negative,
    validate_non_blank_trimmed,
)

from .models import Food, VisitFood
from places.models import Place


# ---------- Food ----------

class FoodSerializer(serializers.ModelSerializer):
    # Valida nombre no-vacío y lo deja trim()
    name = serializers.CharField(max_length=120, validators=[validate_non_blank_trimmed])

    class Meta:
        model = Food
        fields = ["id", "household", "name", "is_active", "created_at", "updated_at"]
        read_only_fields = ["household", "created_at", "updated_at"]

    def validate(self, attrs):
        # (opcional) podrías normalizar algo aquí si quisieras
        return attrs


class FoodFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Food
        fields = ["name", "is_active"]


class FoodViewSet(HouseholdScopedViewSet):
    queryset = Food.objects.all().order_by("name")
    serializer_class = FoodSerializer
    filterset_class = FoodFilter
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    # Bonus: búsqueda y ordenación
    search_fields = ["name"]
    ordering_fields = ["name", "created_at", "updated_at"]

    @action(detail=True, methods=["get"], url_path="latest-by-place")
    def latest_by_place(self, request, pk=None):
        """
        Para el Food {pk}, devuelve la última VisitFood por cada Place.
        Filtros opcionales: area, place_type, price_range, min_rating
        Orden: rating_desc (default), price_asc, date_desc
        """
        food = self.get_queryset().get(pk=pk)
        hh = request.user.profile.household

        # Subquery: última VisitFood para ese food en cada place
        vf = VisitFood.objects.filter(food=food, visit__place=OuterRef("pk")) \
                              .order_by("-visit__date", "-created_at")

        places_qs = Place.objects.filter(household=hh)

        # Filtros opcionales
        q = request.query_params
        if q.get("area"):
            places_qs = places_qs.filter(area=q["area"])
        if q.get("place_type"):
            places_qs = places_qs.filter(place_type=q["place_type"])
        if q.get("price_range"):
            places_qs = places_qs.filter(price_range=q["price_range"])

        # Anotar el ID del último VisitFood por place y quedarnos con los que tienen alguno
        places_qs = places_qs.annotate(
            latest_visitfood_id=Subquery(vf.values("id")[:1])
        ).filter(latest_visitfood_id__isnull=False)

        # Recuperar esos VisitFood
        latest_ids = list(places_qs.values_list("latest_visitfood_id", flat=True))
        latest_vf = VisitFood.objects.select_related("visit", "visit__place").filter(id__in=latest_ids)

        # (Nuevo) min_rating si viene
        if q.get("min_rating"):
            try:
                min_r = float(q["min_rating"])
                latest_vf = latest_vf.filter(rating__gte=min_r)
            except ValueError:
                pass  # si viene mal, lo ignoramos silenciosamente

        # Orden
        ordering = q.get("ordering", "rating_desc")
        if ordering == "price_asc":
            latest_vf = latest_vf.order_by("price_paid", "-visit__date", "-created_at")
        elif ordering == "date_desc":
            latest_vf = latest_vf.order_by("-visit__date", "-created_at")
        else:  # rating_desc
            latest_vf = latest_vf.order_by("-rating", "-visit__date", "-created_at")

        data = [
            {
                "visit_food_id": x.id,
                "food_id": x.food_id,
                "place_id": x.visit.place_id,
                "place_name": x.visit.place.name,
                "rating": float(x.rating),
                "price_paid": float(x.price_paid) if x.price_paid is not None else None,
                "visit_date": x.visit.date.isoformat(),
            }
            for x in latest_vf
        ]
        return Response(data)


# ---------- VisitFood ----------

class VisitFoodSerializer(serializers.ModelSerializer):
    rating = serializers.DecimalField(max_digits=3, decimal_places=1, validators=[validate_rating_1_to_10])
    price_paid = serializers.DecimalField(
        max_digits=7, decimal_places=2, required=False, allow_null=True,
        validators=[validate_price_non_negative]
    )

    class Meta:
        model = VisitFood
        fields = ["id", "visit", "food", "rating", "price_paid", "comment", "created_at"]
        read_only_fields = ["created_at"]

    def validate(self, attrs):
        """
        - El Visit debe pertenecer al household del usuario.
        - El Food debe pertenecer al mismo household.
        """
        request = self.context.get("request")
        if not request or not hasattr(request.user, "profile"):
            return attrs

        user_hh = request.user.profile.household_id

        visit = attrs.get("visit")
        food = attrs.get("food")

        # Asegurar households correctos
        if visit and getattr(visit.place, "household_id", None) != user_hh:
            raise serializers.ValidationError({"visit": "La visita corresponde a un lugar de otro household."})

        if food and getattr(food, "household_id", None) != user_hh:
            raise serializers.ValidationError({"food": "El food indicado pertenece a otro household."})

        # (Opcional) podrías comprobar coherencia extra si el visit.place y food difirieran de household
        return attrs


class VisitFoodFilter(filters.FilterSet):
    date_from = filters.DateFilter(field_name="visit__date", lookup_expr="gte")
    date_to = filters.DateFilter(field_name="visit__date", lookup_expr="lte")
    min_rating = filters.NumberFilter(field_name="rating", lookup_expr="gte")
    max_price_paid = filters.NumberFilter(field_name="price_paid", lookup_expr="lte")

    class Meta:
        model = VisitFood
        fields = ["food", "visit", "date_from", "date_to", "min_rating", "max_price_paid"]


class VisitFoodViewSet(HouseholdScopedViewSet):
    queryset = VisitFood.objects.select_related("visit", "food", "visit__place").all().order_by("-created_at")
    serializer_class = VisitFoodSerializer
    filterset_class = VisitFoodFilter
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    search_fields = ["food__name", "visit__place__name", "comment"]
    ordering_fields = ["created_at", "rating", "price_paid"]