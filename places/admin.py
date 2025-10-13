# places/admin.py
from django.contrib import admin
from .models import Place, PlaceTag


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("name", "price_range", "household", "place_type", "area",
                    "avg_rating", "avg_price_pp", "visits_count", "last_visit_at", "id")
    list_filter = ("household", "place_type", "area", "price_range")
    search_fields = ("name",)
    autocomplete_fields = ("household", "place_type", "area")
    filter_horizontal = ("tags",)  # si prefieres widget M2M directo además de PlaceTag


@admin.register(PlaceTag)
class PlaceTagAdmin(admin.ModelAdmin):
    list_display = ("place", "tag")
    list_filter = ("tag",)
    search_fields = ("place__name", "tag__name")
    autocomplete_fields = ("place", "tag")
