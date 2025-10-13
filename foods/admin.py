# foods/admin.py
from django.contrib import admin
from .models import Food, VisitFood


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ("name", "household", "is_active", "created_at", "id")
    list_filter = ("household", "is_active")
    search_fields = ("name",)
    autocomplete_fields = ("household",)


@admin.register(VisitFood)
class VisitFoodAdmin(admin.ModelAdmin):
    list_display = ("food", "visit", "rating", "price_paid", "created_at", "id")
    list_filter = ("food", "visit__place")
    search_fields = ("food__name", "visit__place__name", "comment")
    autocomplete_fields = ("food", "visit")
    date_hierarchy = "created_at"
