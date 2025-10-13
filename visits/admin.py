# visits/admin.py
from django.contrib import admin
from .models import Visit

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("place", "author", "date", "rating", "price_per_person", "created_at", "id")
    list_filter = ("place", "author", "date")
    search_fields = ("place__name", "author__user__username", "comment")
    autocomplete_fields = ("place", "author")
    date_hierarchy = "date"
