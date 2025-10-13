# locations/admin.py
from django.contrib import admin
from .models import Area

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "id")
    search_fields = ("name",)
