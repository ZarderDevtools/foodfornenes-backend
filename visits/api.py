from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django.db import transaction

from core.api import HouseholdScopedViewSet
from core.validators import (
    validate_rating_1_to_10,
    validate_price_non_negative,
    validate_non_blank_trimmed,
)
from .models import Visit
from places.models import Place
from foods.models import Food, VisitFood


# ============================================================
# SERIALIZERS
# ============================================================

class VisitSerializer(serializers.ModelSerializer):
    rating = serializers.DecimalField(max_digits=3, decimal_places=1, validators=[validate_rating_1_to_10])
    price_per_person = serializers.DecimalField(
        max_digits=7, decimal_places=2, required=False, allow_null=True,
        validators=[validate_price_non_negative]
    )

    class Meta:
        model = Visit
        fields = ["id", "place", "author", "date", "rating", "price_per_person", "comment", "created_at"]
        read_only_fields = ["author", "created_at"]

    def validate(self, attrs):
        """
        Validación: el 'place' debe existir y pertenecer al mismo household del usuario.
        """
        request = self.context.get("request")
        if request and request.user and "place" in attrs:
            place = attrs["place"] if isinstance(attrs["place"], Place) else Place.objects.filter(id=attrs["place"]).first()
            if place is None:
                raise serializers.ValidationError({"place": "El lugar indicado no existe."})
            user_hh = request.user.profile.household
            if getattr(place, "household_id", None) != user_hh.id:
                raise serializers.ValidationError({"place": "No puedes crear visitas en lugares de otro household."})
        return attrs


class VisitCreateWithFoodsSerializer(serializers.Serializer):
    """
    Serializer de entrada para el endpoint compuesto.
    Permite crear una visita y múltiples VisitFood a la vez.
    """
    place = serializers.UUIDField()
    date = serializers.DateField(required=False)  # Si falta, el modelo pondrá hoy
    rating = serializers.DecimalField(max_digits=3, decimal_places=1, validators=[validate_rating_1_to_10])
    price_per_person = serializers.DecimalField(
        max_digits=7, decimal_places=2, required=False, allow_null=True,
        validators=[validate_price_non_negative]
    )
    comment = serializers.CharField(required=False, allow_blank=True)
    foods = serializers.ListField(child=serializers.DictField(), required=False)

    def validate(self, attrs):
        """
        Verifica que el lugar existe y pertenece al household del usuario.
        """
        request = self.context.get("request")
        if request:
            place_id = attrs.get("place")
            place = Place.objects.filter(id=place_id).first()
            if not place:
                raise serializers.ValidationError({"place": "El lugar indicado no existe."})
            if place.household_id != request.user.profile.household_id:
                raise serializers.ValidationError({"place": "No puedes crear visitas en lugares de otro household."})
        return attrs


# ============================================================
# FILTERS
# ============================================================

class VisitFilter(filters.FilterSet):
    date_from = filters.DateFilter(field_name="date", lookup_expr="gte")
    date_to = filters.DateFilter(field_name="date", lookup_expr="lte")
    min_rating = filters.NumberFilter(field_name="rating", lookup_expr="gte")

    class Meta:
        model = Visit
        fields = ["place", "date_from", "date_to", "min_rating"]


# ============================================================
# VIEWSET
# ============================================================

class VisitViewSet(HouseholdScopedViewSet):
    queryset = Visit.objects.select_related("place", "author").all().order_by("-date", "-created_at")
    serializer_class = VisitSerializer
    filterset_class = VisitFilter
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    @action(detail=False, methods=["post"], url_path="create-with-foods")
    @transaction.atomic
    def create_with_foods(self, request):
        """
        Crea una Visit + varios VisitFood en una sola llamada.
        Ejemplo body:
        {
          "place": "uuid-lugar",
          "rating": 8.5,
          "price_per_person": 25.00,
          "comment": "Muy buena experiencia",
          "foods": [
            {"name": "Tarta de queso", "rating": 9.5, "price_paid": 6.5},
            {"food": "uuid-food-existente", "rating": 8.0}
          ]
        }
        """
        s = VisitCreateWithFoodsSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        data = s.validated_data

        user = request.user
        hh = user.profile.household

        # 1) Crear la visita (el modelo pone date=hoy si no se pasa)
        visit = Visit.objects.create(
            place_id=str(data["place"]),
            author=user.profile,
            date=data.get("date") or None,
            rating=data["rating"],
            price_per_person=data.get("price_per_person"),
            comment=(data.get("comment") or "").strip(),
        )

        # 2) Crear los VisitFood (opcionales)
        items = data.get("foods", []) or []
        for item in items:
            food_obj = None

            # (a) Por ID existente
            if "food" in item and item["food"]:
                food_obj = Food.objects.filter(id=item["food"], household=hh).first()
                if not food_obj:
                    return Response(
                        {"detail": "El food indicado no existe o pertenece a otro household."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # (b) Por nombre nuevo
            elif "name" in item and item["name"]:
                name = validate_non_blank_trimmed(item["name"])
                food_obj, _ = Food.objects.get_or_create(household=hh, name=name)

            else:
                continue  # ignorar si no trae ni food ni name

            # Validaciones de rating y precio
            vf_rating = item.get("rating")
            if vf_rating is not None:
                validate_rating_1_to_10(vf_rating)
            else:
                vf_rating = data["rating"]

            price_paid = item.get("price_paid")
            validate_price_non_negative(price_paid)

            VisitFood.objects.create(
                visit=visit,
                food=food_obj,
                rating=vf_rating,
                price_paid=price_paid,
                comment=(item.get("comment") or "").strip(),
            )

        # Las señales de Visit recalculan métricas del Place
        return Response({"visit_id": str(visit.id)}, status=status.HTTP_201_CREATED)
