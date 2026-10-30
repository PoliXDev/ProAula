"""Rutas del panel del personal."""

from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import (
    AnnouncementCreateView,
    AnnouncementListView,
    AttendanceCreateView,
    AttendanceListView,
    ClassroomCreateView,
    ClassroomListView,
    DashboardView,
    GradeCreateView,
    GradeListView,
    StudentCreateView,
    StudentListView,
    StudentUpdateView,
    TuitionFeeCreateView,
    TuitionFeeListView,
    TuitionFeeToggleView,
)

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("acceso/", LoginView.as_view(template_name="academic/login.html"), name="login"),
    path("salir/", LogoutView.as_view(), name="logout"),
    path("aulas/", ClassroomListView.as_view(), name="classroom_list"),
    path("aulas/nueva/", ClassroomCreateView.as_view(), name="classroom_create"),
    path("alumnos/", StudentListView.as_view(), name="student_list"),
    path("alumnos/nuevo/", StudentCreateView.as_view(), name="student_create"),
    path("alumnos/<int:pk>/editar/", StudentUpdateView.as_view(), name="student_update"),
    path("calificaciones/", GradeListView.as_view(), name="grade_list"),
    path("calificaciones/nueva/", GradeCreateView.as_view(), name="grade_create"),
    path("asistencias/", AttendanceListView.as_view(), name="attendance_list"),
    path("asistencias/nueva/", AttendanceCreateView.as_view(), name="attendance_create"),
    path("comunicados/", AnnouncementListView.as_view(), name="announcement_list"),
    path("comunicados/nuevo/", AnnouncementCreateView.as_view(), name="announcement_create"),
    path("mensualidades/", TuitionFeeListView.as_view(), name="tuition_list"),
    path("mensualidades/nueva/", TuitionFeeCreateView.as_view(), name="tuition_create"),
    path(
        "mensualidades/<int:pk>/estado/",
        TuitionFeeToggleView.as_view(),
        name="tuition_toggle",
    ),
]
