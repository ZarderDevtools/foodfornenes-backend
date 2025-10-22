from rest_framework import serializers
from django_filters import rest_framework as filters
from core.api import HouseholdScopedViewSet
from core.validators import validate_non_blank_trimmed
from .models import PlaceType, Tag

# ---------- PlaceType ----------

class PlaceTypeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=60, validators=[validate_non_blank_trimmed])

    class Meta:
        model = PlaceType
        fields = ["id", "name", "household", "is_active", "created_at", "updated_at"]
        read_only_fields = ["household"]  # el household lo pone el servidor


class PlaceTypeFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    is_active = filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = PlaceType
        fields = ["name", "is_active"]


class PlaceTypeViewSet(HouseholdScopedViewSet):
    queryset = PlaceType.objects.all().order_by("name")
    serializer_class = PlaceTypeSerializer
    filterset_class = PlaceTypeFilter
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    include_global_readonly = True  # lista globales + locales; globales quedan solo lectura por el mixin

    # (opcional; el mixin ya autocompleta household)
    def perform_create(self, serializer):
        super().perform_create(serializer)

    # Quality of life:
    search_fields = ["name"]                      # ?search=rest
    ordering_fields = ["name", "created_at", "updated_at"]  # ?ordering=-updated_at


# ---------- Tag ----------

class TagSerializer(serializers.ModelSerializer):
    # Añadimos validación de nombre
    name = serializers.CharField(max_length=60, validators=[validate_non_blank_trimmed])

    class Meta:
        model = Tag
        fields = ["id", "name", "household", "created_at", "updated_at"]
        read_only_fields = ["household"]


class TagFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Tag
        fields = ["name"]


class TagViewSet(HouseholdScopedViewSet):
    queryset = Tag.objects.all().order_by("name")
    serializer_class = TagSerializer
    filterset_class = TagFilter
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    # Quality of life:
    search_fields = ["name"]
    ordering_fields = ["name", "created_at", "updated_at"]
