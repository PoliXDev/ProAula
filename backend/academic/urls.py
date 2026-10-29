"""Rutas del panel del personal: acceso, salida y resumen."""

from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import DashboardView

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path(
        "acceso/",
        LoginView.as_view(template_name="academic/login.html"),
        name="login",
    ),
    path("salir/", LogoutView.as_view(), name="logout"),
]
