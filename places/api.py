from rest_framework import serializers
from django_filters import rest_framework as filters
from core.api import HouseholdScopedViewSet
from core.validators import validate_non_blank_trimmed
from .models import Place, PlaceTag
from categorization.models import PlaceType  # para validación


class PlaceSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=200, validators=[validate_non_blank_trimmed])
    tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Place
        fields = [
            "id", "household", "name", "place_type", "area", "price_range", "description", "url",
            "avg_rating", "avg_price_pp", "visits_count", "last_visit_at",
            "tags", "created_at", "updated_at",
        ]
        read_only_fields = [
            "household", "avg_rating", "avg_price_pp", "visits_count", "last_visit_at",
            "created_at", "updated_at"
        ]

    def validate(self, attrs):
        """
        place_type debe ser global (household=None) o del mismo household del usuario.
        (El household del Place lo establece el servidor en perform_create).
        """
        request = self.context.get("request")
        if not request or not hasattr(request.user, "profile"):
            return attrs

        pt = attrs.get("place_type")
        if pt:
            user_hh_id = request.user.profile.household_id
            # Si el PlaceType no es global, debe pertenecer a tu household
            if pt.household_id is not None and pt.household_id != user_hh_id:
                raise serializers.ValidationError({
                    "place_type": "El tipo de lugar no pertenece a tu household (ni es global)."
                })
        return attrs


class PlaceFilter(filters.FilterSet):
    min_avg_rating = filters.NumberFilter(field_name="avg_rating", lookup_expr="gte")
    max_avg_price_pp = filters.NumberFilter(field_name="avg_price_pp", lookup_expr="lte")

    class Meta:
        model = Place
        fields = ["place_type", "area", "price_range", "min_avg_rating", "max_avg_price_pp"]


class PlaceViewSet(HouseholdScopedViewSet):
    queryset = Place.objects.all().order_by("-last_visit_at", "name")
    serializer_class = PlaceSerializer
    filterset_class = PlaceFilter
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    # Quality of life para el cliente:
    search_fields = ["name"]  # ?search=pepe
    ordering_fields = ["avg_rating", "avg_price_pp", "last_visit_at", "name"]  # ?ordering=-avg_rating
