"""
Consultas del portal familiar.

El panel del personal sigue con su sesión. Aquí cada petición
identifica al representante por token y solo devuelve a sus hijos.
"""

from django.db.models import Q
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Announcement, Student
from .permissions import IsParentUser
from .serializers import ParentSerializer, StudentDashboardSerializer


class LogoutView(APIView):
    """
    Cierra la sesión del portal borrando el token.

    La cookie del panel no interviene: sin este token la siguiente
    consulta del portal queda rechazada.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=204)


class ParentDashboardView(APIView):
    """
    Resumen de la familia que ha iniciado sesión.

    El filtro parent=request.user es el límite entre familias.
    Los comunicados se leen una sola vez: los de todo el centro
    y los de las aulas de estos hijos.
    """

    permission_classes = [IsParentUser]

    def get(self, request):
        children = list(
            Student.objects.filter(parent=request.user)
            .select_related("classroom")
            .prefetch_related("grades", "attendances", "tuition_fees")
        )
        classroom_ids = {child.classroom_id for child in children}
        announcements = Announcement.objects.filter(
            Q(classroom__isnull=True) | Q(classroom_id__in=classroom_ids)
        )
        grouped = {}
        for announcement in announcements:
            grouped.setdefault(announcement.classroom_id, []).append(announcement)
        return Response(
            {
                "parent": ParentSerializer(request.user).data,
                "children": StudentDashboardSerializer(
                    children,
                    many=True,
                    context={"announcements_by_classroom": grouped},
                ).data,
            }
        )
