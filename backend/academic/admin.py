"""
Registro de los modelos del colegio en el admin de Django.

El usuario usa UserAdmin para que la contraseña se guarde hasheada.
El resto son listados simples para que el personal revise los datos
mientras no exista todavía el panel con plantillas propias.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import (
    Announcement,
    Attendance,
    Classroom,
    Grade,
    Student,
    TuitionFee,
    User,
)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Alta de personal y de representantes, con rol y teléfono visibles."""

    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Colegio", {"fields": ("role", "phone")}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Colegio", {"fields": ("role", "phone")}),
    )
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_staff",
    )
    list_filter = DjangoUserAdmin.list_filter + ("role",)
    search_fields = ("username", "email", "first_name", "last_name", "phone")


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ("name", "section", "school_year")
    list_filter = ("school_year",)
    search_fields = ("name", "section", "school_year")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("enrollment_code", "last_name", "first_name", "classroom", "parent")
    list_filter = ("classroom",)
    search_fields = ("enrollment_code", "first_name", "last_name")


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "evaluation_name", "score", "date")
    list_filter = ("subject", "date")
    search_fields = ("student__last_name", "student__enrollment_code", "evaluation_name")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "status")
    list_filter = ("status", "date")
    search_fields = ("student__last_name", "student__enrollment_code")


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "classroom", "created_at")
    list_filter = ("classroom",)
    search_fields = ("title", "message")


@admin.register(TuitionFee)
class TuitionFeeAdmin(admin.ModelAdmin):
    list_display = ("student", "concept", "amount_usd", "due_date", "status")
    list_filter = ("status", "due_date")
    search_fields = ("concept", "student__last_name", "student__enrollment_code")
