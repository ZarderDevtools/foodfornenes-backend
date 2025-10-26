from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

def healthz(_request):  # 200 OK
    return HttpResponse("ok", content_type="text/plain")

def root(_request):     # opcional: redirige "/" a Swagger
    from django.shortcuts import redirect
    return redirect("swagger-ui")

urlpatterns = [
    path("", root),  # opcional, así el GET / no da 400/404
    path("healthz", healthz),

    path("admin/", admin.site.urls),

    # OpenAPI & Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

# Version 1
    path("api/v1/", include("config.v1_urls")),
]
