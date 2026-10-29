"""
Acceso al panel del personal.

El login de Django comprueba usuario y contraseña. El mixin añade
la regla del colegio: solo entra quien tiene rol STAFF. Un padre
autenticado recibe 403, no el resumen del centro.
"""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView

from .models import Announcement, Classroom, Student, TuitionFee, User


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Deja pasar solo a personal autenticado. El padre cae en la plantilla 403."""

    def test_func(self):
        return self.request.user.role == User.Role.STAFF


class DashboardView(StaffRequiredMixin, TemplateView):
    """
    Resumen del colegio para el personal.

    Cuenta aulas, alumnos y mensualidades pendientes. No muestra el
    expediente de una familia: eso corresponde al portal del representante.
    """

    template_name = "academic/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["classroom_count"] = Classroom.objects.count()
        context["student_count"] = Student.objects.count()
        context["pending_fees_count"] = TuitionFee.objects.filter(
            status=TuitionFee.Status.PENDING
        ).count()
        context["announcements"] = Announcement.objects.select_related("classroom")[:5]
        return context
