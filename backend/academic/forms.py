"""
Formularios del panel del personal.

El estilo outlined se aplica una sola vez. Cada formulario añade solo
la regla de negocio que el modelo no puede expresar por sí solo.
"""

from django import forms

from .models import (
    Announcement,
    Attendance,
    Classroom,
    Grade,
    Student,
    TuitionFee,
    User,
)


class StyledModelForm(forms.ModelForm):
    """Borde claro, foco visible y altura cómoda en todos los controles."""

    control_class = (
        "mt-1 w-full rounded-xl border border-meadow-willow bg-white px-3 py-3 "
        "text-meadow-yale outline-none focus:border-meadow-teal"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            current = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{current} {self.control_class}".strip()


class ClassroomForm(StyledModelForm):
    """Alta de un aula. El año, el nombre y la sección no pueden repetirse juntos."""

    class Meta:
        model = Classroom
        fields = ("name", "section", "school_year")


class StudentForm(StyledModelForm):
    """
    Alta y edición de un alumno.

    El representante solo puede ser un usuario con rol PARENT. Un docente
    no aparece en la lista ni se acepta si llega en el envío.
    """

    class Meta:
        model = Student
        fields = ("first_name", "last_name", "enrollment_code", "classroom", "parent")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parent"].queryset = User.objects.filter(role=User.Role.PARENT)


class GradeForm(StyledModelForm):
    """
    Carga de una calificación.

    La nota se rechaza fuera de 1 a 20 porque el modelo ya declara ese rango.
    """

    class Meta:
        model = Grade
        fields = ("student", "subject", "evaluation_name", "score", "date", "comment")
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}


class AttendanceForm(StyledModelForm):
    """
    Parte de asistencia de un día.

    Si el alumno ya tiene registro en esa fecha, el formulario lo indica
    antes de llegar a la base de datos.
    """

    class Meta:
        model = Attendance
        fields = ("student", "date", "status", "notes")
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}

    def clean(self):
        cleaned = super().clean()
        student = cleaned.get("student")
        day = cleaned.get("date")
        if student and day:
            existing = Attendance.objects.filter(student=student, date=day)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                self.add_error(
                    "date",
                    "Este alumno ya tiene asistencia en esa fecha.",
                )
        return cleaned


class AnnouncementForm(StyledModelForm):
    """Publicación de un aviso. Sin aula, el aviso es de todo el centro."""

    class Meta:
        model = Announcement
        fields = ("title", "message", "classroom")


class TuitionFeeForm(StyledModelForm):
    """Emisión de una mensualidad, con su importe, vencimiento y estado inicial."""

    class Meta:
        model = TuitionFee
        fields = ("student", "concept", "amount_usd", "due_date", "status")
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}
