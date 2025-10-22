from rest_framework import serializers
from rest_framework import viewsets
from .models import Area

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ["id", "name", "created_at"]

class AreaViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.all().order_by("name")
    serializer_class = AreaSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    # No household filter (global)
