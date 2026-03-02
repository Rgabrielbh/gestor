from rest_framework.permissions import BasePermission
from .models import RoleChoices

class IsDiretor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == RoleChoices.DIRETOR)

class IsGestorOrAbove(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role in (RoleChoices.DIRETOR, RoleChoices.GESTOR))

class IsGerenteOrAbove(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role in (RoleChoices.DIRETOR, RoleChoices.GESTOR, RoleChoices.GERENTE_PROJETO))

class IsOwnerOrGestor(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.role in (RoleChoices.DIRETOR, RoleChoices.GESTOR):
            return True
        return obj == request.user
