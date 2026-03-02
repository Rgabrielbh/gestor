from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Colaborador, RoleChoices
from .serializers import ColaboradorListSerializer, ColaboradorDetailSerializer, RegisterSerializer
from .permissions import IsGestorOrAbove, IsOwnerOrGestor
from .filters import ColaboradorFilter

class ColaboradorViewSet(viewsets.ModelViewSet):
    queryset = Colaborador.objects.select_related("gestor_direto").order_by("nome")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ColaboradorFilter
    search_fields = ["nome","email","matricula","cargo","funcao"]
    ordering_fields = ["nome","dt_admissao","role","status"]

    def get_serializer_class(self):
        if self.action == "create":
            return RegisterSerializer
        if self.action in ("retrieve","update","partial_update"):
            return ColaboradorDetailSerializer
        return ColaboradorListSerializer

    def get_permissions(self):
        if self.action in ("list","retrieve"):
            return [permissions.IsAuthenticated()]
        if self.action == "create":
            return [IsGestorOrAbove()]
        if self.action in ("update","partial_update"):
            return [IsOwnerOrGestor()]
        if self.action == "destroy":
            return [IsGestorOrAbove()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == RoleChoices.OPERADOR:
            return qs.filter(pk=user.pk)
        if user.role == RoleChoices.GERENTE_PROJETO:
            return qs.filter(gestor_direto=user) | qs.filter(pk=user.pk)
        return qs
