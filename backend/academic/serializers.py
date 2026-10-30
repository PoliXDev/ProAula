"""
Salida de solo lectura para el portal familiar.

El representante ve su ficha y la de sus hijos: aula, notas,
asistencia, mensualidades y los comunicados que le corresponden.
"""

from rest_framework import serializers

from .models import Announcement, Attendance, Classroom, Grade, Student, TuitionFee, User


class ParentSerializer(serializers.ModelSerializer):
    """Datos del representante para la cabecera del portal."""

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["username", "full_name", "email", "phone"]

    def get_full_name(self, user):
        return user.get_full_name() or user.username


class ClassroomSerializer(serializers.ModelSerializer):
    """Aula en la que está matriculado el alumno."""

    class Meta:
        model = Classroom
        fields = ["name", "section", "school_year"]


class GradeSerializer(serializers.ModelSerializer):
    """Nota con la asignatura en el texto que ve la familia."""

    subject_label = serializers.CharField(source="get_subject_display", read_only=True)

    class Meta:
        model = Grade
        fields = [
            "subject",
            "subject_label",
            "evaluation_name",
            "score",
            "date",
            "comment",
        ]


class AttendanceSerializer(serializers.ModelSerializer):
    """Parte de asistencia con el estado en español."""

    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Attendance
        fields = ["date", "status", "status_label", "notes"]


class TuitionFeeSerializer(serializers.ModelSerializer):
    """Mensualidad del alumno con el estado del pago en español."""

    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = TuitionFee
        fields = ["concept", "amount_usd", "due_date", "status", "status_label"]


class AnnouncementSerializer(serializers.ModelSerializer):
    """Comunicado general del centro o dirigido al aula del alumno."""

    class Meta:
        model = Announcement
        fields = ["title", "message", "created_at"]


class StudentDashboardSerializer(serializers.ModelSerializer):
    """
    Ficha que el representante consulta de uno de sus hijos.

    Los comunicados llegan en el contexto: los generales del centro
    y los del aula de este alumno. No se incluyen los de otras aulas.
    """

    classroom = ClassroomSerializer(read_only=True)
    grades = GradeSerializer(many=True, read_only=True)
    attendances = AttendanceSerializer(many=True, read_only=True)
    tuition_fees = TuitionFeeSerializer(many=True, read_only=True)
    announcements = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            "first_name",
            "last_name",
            "enrollment_code",
            "classroom",
            "grades",
            "attendances",
            "tuition_fees",
            "announcements",
        ]

    def get_announcements(self, student):
        grouped = self.context["announcements_by_classroom"]
        notices = grouped.get(None, []) + grouped.get(student.classroom_id, [])
        return AnnouncementSerializer(notices, many=True).data
