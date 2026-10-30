"""Permisos de la API del portal familiar."""

from rest_framework.permissions import BasePermission

from .models import User


class IsParentUser(BasePermission):
    """
    Abre la consulta solo a un representante autenticado.

    El personal del centro trabaja en el panel. Un token de personal
    no da acceso a las fichas de las familias.
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.role == User.Role.PARENT
        )
