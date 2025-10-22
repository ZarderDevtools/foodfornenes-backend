# config/v1_urls_jwt.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("create/", TokenObtainPairView.as_view(), name="jwt-create"),
    path("refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
]
