# places/api.py
from django.db import transaction
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema_field, extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers

from core.api import HouseholdScopedViewSet
from core.validators import validate_non_blank_trimmed
from categorization.api import TagSerializer
from categorization.models import Tag
from .models import Place, PlaceTag


class BasePlaceSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=200, validators=[validate_non_blank_trimmed])

    class Meta:
        model = Place
        fields = [
            "id",
            "household",
            "name",
            "place_type",
            "area",
            "price_range",
            "description",
            "url",
            "avg_rating",
            "avg_price_pp",
            "visits_count",
            "last_visit_at",
            "tags",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "household",
            "avg_rating",
            "avg_price_pp",
            "visits_count",
            "last_visit_at",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not hasattr(request.user, "profile"):
            return attrs

        user_hh_id = request.user.profile.household_id

        place_type = attrs.get("place_type")
        if place_type:
            if hasattr(place_type, "household_id"):
                if place_type.household_id is not None and place_type.household_id != user_hh_id:
                    raise serializers.ValidationError({
                        "place_type": "El tipo de lugar no pertenece a tu household."
                    })

        tags = attrs.get("tags")
        if tags is not None:
            invalid_tags = []
            for tag in tags:
                if hasattr(tag, "household_id"):
                    if tag.household_id != user_hh_id:
                        invalid_tags.append(str(tag.pk))

            if invalid_tags:
                raise serializers.ValidationError({
                    "tags": (
                        "Uno o más tags no pertenecen a tu household. "
                        f"Tags inválidos: {', '.join(invalid_tags)}"
                    )
                })

        return attrs

    def _sync_tags(self, place: Place, tags) -> None:
        desired_tag_ids = {tag.pk for tag in tags}
        current_tag_ids = set(
            PlaceTag.objects.filter(place=place).values_list("tag_id", flat=True)
        )

        tag_ids_to_create = desired_tag_ids - current_tag_ids
        tag_ids_to_delete = current_tag_ids - desired_tag_ids

        if tag_ids_to_delete:
            PlaceTag.objects.filter(place=place, tag_id__in=tag_ids_to_delete).delete()

        if tag_ids_to_create:
            PlaceTag.objects.bulk_create(
                [PlaceTag(place=place, tag_id=tag_id) for tag_id in tag_ids_to_create]
            )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop("tags", None)
        place = super().create(validated_data)
        if tags is not None:
            self._sync_tags(place, tags)
        return place

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        place = super().update(instance, validated_data)
        if tags is not None:
            self._sync_tags(place, tags)
        return place


class PlaceWriteSerializer(BasePlaceSerializer):
    @extend_schema_field(serializers.UUIDField())
    class TagsField(serializers.PrimaryKeyRelatedField):
        pass

    tags = TagsField(
        many=True,
        queryset=Tag.objects.all(),
        required=False,
        help_text="Lista de IDs de tags",
    )


class PlaceReadSerializer(BasePlaceSerializer):
    tags = TagSerializer(many=True, read_only=True)


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class UUIDInFilter(filters.BaseInFilter, filters.UUIDFilter):
    pass


class PlaceFilter(filters.FilterSet):
    min_avg_rating = filters.NumberFilter(field_name="avg_rating", lookup_expr="gte")
    max_avg_price_pp = filters.NumberFilter(field_name="avg_price_pp", lookup_expr="lte")
    price_range_in = CharInFilter(field_name="price_range", lookup_expr="in")

    tags = UUIDInFilter(
        method="filter_tags",
        help_text="Filtrar por uno o varios tags (UUID separados por comas). Ej: tags=uuid1,uuid2"
    )

    def filter_tags(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(tags__id__in=value).distinct()

    class Meta:
        model = Place
        fields = [
            "place_type",
            "area",
            "price_range",
            "price_range_in",
            "min_avg_rating",
            "max_avg_price_pp",
            "tags",
        ]


class PlaceViewSet(HouseholdScopedViewSet):
    queryset = Place.objects.all().order_by("-last_visit_at", "name")
    filterset_class = PlaceFilter
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    search_fields = ["name"]
    ordering_fields = ["avg_rating", "avg_price_pp", "last_visit_at", "name"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return PlaceReadSerializer
        return PlaceWriteSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="tags",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                description="Filtrar por uno o varios tags (separados por comas). Ej: tags=uuid1,uuid2",
                required=False,
                many=True,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)