"""
Carga inicial de un colegio de ejemplo.

Se puede ejecutar varias veces: get_or_create reutiliza usuarios, aulas
y alumnos ya creados y no duplica notas ni asistencias.
"""

from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand

from academic.models import (
    Announcement,
    Attendance,
    Classroom,
    Grade,
    Student,
    TuitionFee,
    User,
)


class Command(BaseCommand):
    help = "Crea el personal, una familia con dos hijos y datos de ejemplo."

    def handle(self, *args, **options):
        staff = self._usuario(
            username="personal",
            password="aula_staff",
            first_name="Laura",
            last_name="Méndez",
            role=User.Role.STAFF,
            is_staff=True,
            phone="0414-5550101",
        )
        parent = self._usuario(
            username="familia",
            password="aula-familia",
            first_name="Carlos",
            last_name="Rivas",
            role=User.Role.PARENT,
            is_staff=False,
            phone="0412-5550199",
        )

        tercero = self._aula("3er Grado", "A")
        quinto = self._aula("5to Grado", "B")
        ana = self._alumno("Ana", "Rivas", "MAT-2026-014", tercero, parent)
        mateo = self._alumno("Mateo", "Rivas", "MAT-2026-031", quinto, parent)

        self._nota(ana, Grade.Subject.MATH, "Parcial 1", Decimal("18.5"), date(2026, 10, 8))
        self._nota(ana, Grade.Subject.LANGUAGE, "Parcial 1", Decimal("16.0"), date(2026, 10, 10))
        self._nota(mateo, Grade.Subject.SCIENCE, "Parcial 1", Decimal("14.5"), date(2026, 10, 9))
        self._nota(mateo, Grade.Subject.ENGLISH, "Oral", Decimal("19.0"), date(2026, 10, 14))

        self._asistencia(ana, date(2026, 10, 6), Attendance.Status.PRESENT, "")
        self._asistencia(ana, date(2026, 10, 7), Attendance.Status.LATE, "Llegó 10 minutos tarde")
        self._asistencia(mateo, date(2026, 10, 6), Attendance.Status.PRESENT, "")
        self._asistencia(mateo, date(2026, 10, 7), Attendance.Status.ABSENT, "Justificada por el padre")

        self._comunicado(
            "Reunión general de familias",
            "El viernes 30 de octubre, a las 8:00, en el salón principal.",
            None,
        )
        self._comunicado(
            "Salida al museo",
            "3er Grado A visita el museo el martes. Traer autorización firmada.",
            tercero,
        )
        self._comunicado(
            "Examen de ciencias",
            "5to Grado B presenta el examen de ciencias el jueves.",
            quinto,
        )

        self._mensualidad(
            ana,
            "Mensualidad octubre",
            Decimal("85.00"),
            date(2026, 10, 5),
            TuitionFee.Status.PENDING,
        )
        self._mensualidad(
            mateo,
            "Mensualidad octubre",
            Decimal("85.00"),
            date(2026, 10, 5),
            TuitionFee.Status.PAID,
        )

        self.stdout.write(self.style.SUCCESS("Datos de ejemplo listos."))
        self.stdout.write("Personal: personal / aula_staff")
        self.stdout.write("Familia: familia / aula-familia")
        self.stdout.write(
            f"Aulas: {Classroom.objects.count()} | "
            f"Alumnos: {Student.objects.count()} | "
            f"Recibos pendientes: "
            f"{TuitionFee.objects.filter(status=TuitionFee.Status.PENDING).count()}"
        )
        self.stdout.write(f"Personal de referencia: {staff.get_full_name()}")

    def _usuario(self, username, password, **defaults):
        user, created = User.objects.get_or_create(username=username, defaults=defaults)
        if created:
            user.set_password(password)
            user.save(update_fields=["password"])
        return user

    def _aula(self, name, section):
        classroom, _created = Classroom.objects.get_or_create(
            name=name,
            section=section,
            school_year="2026-2027",
        )
        return classroom

    def _alumno(self, first_name, last_name, enrollment_code, classroom, parent):
        student, _created = Student.objects.get_or_create(
            enrollment_code=enrollment_code,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "classroom": classroom,
                "parent": parent,
            },
        )
        return student

    def _nota(self, student, subject, evaluation_name, score, day):
        Grade.objects.get_or_create(
            student=student,
            subject=subject,
            evaluation_name=evaluation_name,
            defaults={"score": score, "date": day},
        )

    def _asistencia(self, student, day, status, notes):
        Attendance.objects.get_or_create(
            student=student,
            date=day,
            defaults={"status": status, "notes": notes},
        )

    def _comunicado(self, title, message, classroom):
        Announcement.objects.get_or_create(
            title=title,
            defaults={"message": message, "classroom": classroom},
        )

    def _mensualidad(self, student, concept, amount, due_date, status):
        TuitionFee.objects.get_or_create(
            student=student,
            concept=concept,
            defaults={"amount_usd": amount, "due_date": due_date, "status": status},
        )
