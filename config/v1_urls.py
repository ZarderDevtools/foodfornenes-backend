# config/v1_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from locations.api import AreaViewSet
from categorization.api import PlaceTypeViewSet, TagViewSet
from places.api import PlaceViewSet
from visits.api import VisitViewSet
from foods.api import FoodViewSet, VisitFoodViewSet

router = DefaultRouter()
router.register(r"areas", AreaViewSet, basename="area")
router.register(r"place-types", PlaceTypeViewSet, basename="placetype")
router.register(r"tags", TagViewSet, basename="tag")
router.register(r"places", PlaceViewSet, basename="place")
router.register(r"visits", VisitViewSet, basename="visit")
router.register(r"foods", FoodViewSet, basename="food")
router.register(r"visit-foods", VisitFoodViewSet, basename="visitfood")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("rest_framework.urls")),  # opcional (login de DRF)
    path("auth/jwt/", include("config.v1_urls_jwt")),  # JWT endpoints
]
