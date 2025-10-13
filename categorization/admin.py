# categorization/admin.py
from django.contrib import admin
from .models import PlaceType, Tag


@admin.register(PlaceType)
class PlaceTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "household", "is_active", "created_at", "id")
    list_filter = ("is_active", "household")
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "household", "created_at", "id")
    list_filter = ("household",)
    search_fields = ("name",)
