"""
Acceso y operación diaria del personal.

Solo un usuario autenticado con rol STAFF entra a estas pantallas.
Un representante recibe la página de acceso restringido.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from .forms import (
    AnnouncementForm,
    AttendanceForm,
    ClassroomForm,
    GradeForm,
    StudentForm,
    TuitionFeeForm,
)
from .models import (
    Announcement,
    Attendance,
    Classroom,
    Grade,
    Student,
    TuitionFee,
    User,
)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Deja pasar solo a personal autenticado. El padre cae en la plantilla 403."""

    def test_func(self):
        return self.request.user.role == User.Role.STAFF


class FormPageMixin:
    """Página de alta o edición con el mismo marcado de campos."""

    template_name = "academic/form_page.html"
    page_title = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.page_title
        return context

    def form_valid(self, form):
        messages.success(self.request, "Registro guardado.")
        return super().form_valid(form)


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


class ClassroomListView(StaffRequiredMixin, ListView):
    """Aulas del curso, ordenadas por año, nombre y sección."""

    model = Classroom
    template_name = "academic/classroom_list.html"
    context_object_name = "classrooms"


class ClassroomCreateView(StaffRequiredMixin, FormPageMixin, CreateView):
    """Alta de un aula."""

    model = Classroom
    form_class = ClassroomForm
    page_title = "Nueva aula"
    success_url = reverse_lazy("classroom_list")


class StudentListView(StaffRequiredMixin, ListView):
    """
    Alumnos matriculados.

    El aula y el representante viajan en la misma consulta para no
    repetir una búsqueda por cada fila.
    """

    template_name = "academic/student_list.html"
    context_object_name = "students"

    def get_queryset(self):
        return Student.objects.select_related("classroom", "parent")


class StudentCreateView(StaffRequiredMixin, FormPageMixin, CreateView):
    """Alta de un alumno y de su representante."""

    model = Student
    form_class = StudentForm
    page_title = "Nuevo alumno"
    success_url = reverse_lazy("student_list")


class StudentUpdateView(StaffRequiredMixin, FormPageMixin, UpdateView):
    """Corrección de la ficha de un alumno ya matriculado."""

    model = Student
    form_class = StudentForm
    page_title = "Editar alumno"
    success_url = reverse_lazy("student_list")


class GradeListView(StaffRequiredMixin, ListView):
    """Calificaciones recientes, con el alumno y su aula ya cargados."""

    template_name = "academic/grade_list.html"
    context_object_name = "grades"

    def get_queryset(self):
        return Grade.objects.select_related("student", "student__classroom")[:30]


class GradeCreateView(StaffRequiredMixin, FormPageMixin, CreateView):
    """Carga de una calificación."""

    model = Grade
    form_class = GradeForm
    page_title = "Nueva calificación"
    success_url = reverse_lazy("grade_list")


class AttendanceListView(StaffRequiredMixin, ListView):
    """Partes de asistencia recientes, con el alumno y su aula ya cargados."""

    template_name = "academic/attendance_list.html"
    context_object_name = "attendances"

    def get_queryset(self):
        return Attendance.objects.select_related("student", "student__classroom")[:30]


class AttendanceCreateView(StaffRequiredMixin, FormPageMixin, CreateView):
    """Registro del parte de un alumno en una fecha."""

    model = Attendance
    form_class = AttendanceForm
    page_title = "Nueva asistencia"
    success_url = reverse_lazy("attendance_list")


class AnnouncementListView(StaffRequiredMixin, ListView):
    """Avisos del centro y de cada aula."""

    template_name = "academic/announcement_list.html"
    context_object_name = "announcements"

    def get_queryset(self):
        return Announcement.objects.select_related("classroom")


class AnnouncementCreateView(StaffRequiredMixin, FormPageMixin, CreateView):
    """Publicación de un aviso."""

    model = Announcement
    form_class = AnnouncementForm
    page_title = "Nuevo comunicado"
    success_url = reverse_lazy("announcement_list")


class TuitionFeeListView(StaffRequiredMixin, ListView):
    """Mensualidades, con el alumno ya cargado para pintar la fila."""

    template_name = "academic/tuition_list.html"
    context_object_name = "fees"

    def get_queryset(self):
        return TuitionFee.objects.select_related("student", "student__classroom")


class TuitionFeeCreateView(StaffRequiredMixin, FormPageMixin, CreateView):
    """Emisión de una mensualidad."""

    model = TuitionFee
    form_class = TuitionFeeForm
    page_title = "Nueva mensualidad"
    success_url = reverse_lazy("tuition_list")


class TuitionFeeToggleView(StaffRequiredMixin, View):
    """
    Alterna una mensualidad entre pendiente y pagada.

    Solo acepta POST. El estado nuevo lo decide el servidor, no el formulario.
    """

    def post(self, request, pk):
        fee = get_object_or_404(TuitionFee, pk=pk)
        if fee.status == TuitionFee.Status.PENDING:
            fee.status = TuitionFee.Status.PAID
        else:
            fee.status = TuitionFee.Status.PENDING
        fee.save(update_fields=["status"])
        messages.success(request, "Estado de la mensualidad actualizado.")
        return redirect("tuition_list")
