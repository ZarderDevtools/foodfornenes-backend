# core/api.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q

class HouseholdScopedViewSet(viewsets.ModelViewSet):
    """
    - Filtra por household del usuario.
    - (Opcional) Incluye filas globales (household=NULL) en lectura si include_global_readonly=True.
    - Auto-asigna household/author en creaciones.
    - Bloquea mutaciones sobre filas globales.
    """
    permission_classes = [IsAuthenticated]
    include_global_readonly = False  # <- los hijos lo activan si quieren incluir globales en lectura

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        model = self.queryset.model
        if hasattr(model, "household_id"):
            hh = user.profile.household
            if self.include_global_readonly:
                return qs.filter(Q(household=hh) | Q(household__isnull=True))
            else:
                return qs.filter(household=hh)
        return qs

    def _forbid_if_global(self, instance):
        """Evita editar/borrar filas globales (household=NULL)."""
        if hasattr(instance, "household_id") and instance.household_id is None:
            raise PermissionDenied("Este elemento global es de solo lectura.")

    def perform_create(self, serializer):
        data = {}
        user = self.request.user
        fields = [f.name for f in serializer.Meta.model._meta.fields]

        if "household" in fields:
            data["household"] = user.profile.household
        if "author" in fields:
            data["author"] = user.profile

        serializer.save(**data)

    def perform_update(self, serializer):
        instance = self.get_object()
        self._forbid_if_global(instance)
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        self._forbid_if_global(instance)
        super().perform_destroy(instance)
