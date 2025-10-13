# accounts/admin.py
from django.contrib import admin
from .models import Household, UserProfile


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "id")
    search_fields = ("name",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "household", "created_at", "id")
    list_filter = ("household",)
    search_fields = ("user__username", "household__name")
