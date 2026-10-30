"""Rutas de la API del portal familiar."""

from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken

from .api_views import LogoutView, ParentDashboardView

urlpatterns = [
    path("login/", ObtainAuthToken.as_view(), name="api_login"),
    path("logout/", LogoutView.as_view(), name="api_logout"),
    path("parent/dashboard/", ParentDashboardView.as_view(), name="parent_dashboard"),
]
