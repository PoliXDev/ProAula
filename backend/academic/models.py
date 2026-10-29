"""
Modelos de dominio académico y administrativo de ProAula.

Centraliza la gestión de usuarios, aulas, matrículas, evaluaciones,
asistencia diaria, comunicados internos y control de mensualidades.
"""

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    """
    Usuario personalizado del sistema.

    Distingue mediante el rol entre el personal del centro (STAFF), con
    acceso al panel de gestión, y los representantes (PARENT), con acceso
    exclusivo a la consulta académica de sus representados.
    """

    class Role(models.TextChoices):
        STAFF = "STAFF", "Personal"
        PARENT = "PARENT", "Padre / representante"

    role = models.CharField(
        "rol",
        max_length=10,
        choices=Role.choices,
        default=Role.STAFF,
    )
    phone = models.CharField("teléfono", max_length=20, blank=True)

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        full_name = self.get_full_name().strip()
        return full_name or self.username


class Classroom(models.Model):
    """
    Aula o grupo académico asignado a un periodo escolar.

    Restringe la duplicidad combinando grado, sección y año escolar.
    """

    name = models.CharField("nombre", max_length=80)
    section = models.CharField("sección", max_length=10)
    school_year = models.CharField("año escolar", max_length=9)

    class Meta:
        verbose_name = "aula"
        verbose_name_plural = "aulas"
        ordering = ["school_year", "name", "section"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "section", "school_year"],
                name="unique_classroom_per_year",
            )
        ]

    def __str__(self):
        return f"{self.name} {self.section} ({self.school_year})"


class Student(models.Model):
    """
    Ficha del alumno matriculado.

    Vincula al estudiante con su aula actual y su representante legal.
    Se restringe el borrado en cascada (PROTECT) para preservar el
    historial académico ante bajas accidentales de aulas o usuarios.
    """

    first_name = models.CharField("nombre", max_length=80)
    last_name = models.CharField("apellidos", max_length=80)
    enrollment_code = models.CharField("código de matrícula", max_length=20, unique=True)
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.PROTECT,
        related_name="students",
        verbose_name="aula",
    )
    parent = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="children",
        limit_choices_to={"role": User.Role.PARENT},
        verbose_name="representante",
    )

    class Meta:
        verbose_name = "alumno"
        verbose_name_plural = "alumnos"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"


class Grade(models.Model):
    """
    Registro de calificación de un alumno por asignatura y evaluación.

    Valida a nivel de modelo la escala de evaluación del centro (1 a 20 puntos),
    admitiendo un decimal para promedios y cortes parciales.
    """

    class Subject(models.TextChoices):
        MATH = "MATH", "Matemáticas"
        LANGUAGE = "LANGUAGE", "Lengua"
        SCIENCE = "SCIENCE", "Ciencias"
        ENGLISH = "ENGLISH", "Inglés"
        HISTORY = "HISTORY", "Historia"

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="grades",
        verbose_name="alumno",
    )
    subject = models.CharField("asignatura", max_length=20, choices=Subject.choices)
    evaluation_name = models.CharField("evaluación", max_length=120)
    score = models.DecimalField(
        "nota",
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
    )
    date = models.DateField("fecha")
    comment = models.TextField("comentario", blank=True)

    class Meta:
        verbose_name = "calificación"
        verbose_name_plural = "calificaciones"
        ordering = ["-date", "subject"]

    def __str__(self):
        return f"{self.student} — {self.get_subject_display()}: {self.score}"


class Attendance(models.Model):
    """
    Control de asistencia diaria del alumno.

    Garantiza mediante restricción en base de datos que solo exista
    un parte de asistencia por estudiante en cada fecha.
    """

    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Presente"
        ABSENT = "ABSENT", "Ausente"
        LATE = "LATE", "Tarde"

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="attendances",
        verbose_name="alumno",
    )
    date = models.DateField("fecha")
    status = models.CharField("estado", max_length=10, choices=Status.choices)
    notes = models.TextField("notas", blank=True)

    class Meta:
        verbose_name = "asistencia"
        verbose_name_plural = "asistencias"
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "date"],
                name="unique_attendance_per_student_and_date",
            )
        ]

    def __str__(self):
        return f"{self.student} — {self.date} ({self.get_status_display()})"


class Announcement(models.Model):
    """
    Comunicado oficial emitido por el centro educativo.

    Si no se especifica un aula destinataria, el comunicado tiene alcance
    general para todas las familias del colegio.
    """

    title = models.CharField("título", max_length=150)
    message = models.TextField("mensaje")
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="announcements",
        verbose_name="aula",
    )
    created_at = models.DateTimeField("creado", auto_now_add=True)

    class Meta:
        verbose_name = "comunicado"
        verbose_name_plural = "comunicados"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class TuitionFee(models.Model):
    """
    Estado de cuenta y mensualidades asociadas a un alumno.

    Registra el concepto de cobro en divisas (USD), su fecha de vencimiento
    y el estado administrativo del pago.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendiente"
        PAID = "PAID", "Pagada"

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="tuition_fees",
        verbose_name="alumno",
    )
    concept = models.CharField("concepto", max_length=120)
    amount_usd = models.DecimalField(
        "importe (USD)",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    due_date = models.DateField("vencimiento")
    status = models.CharField(
        "estado",
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )

    class Meta:
        verbose_name = "mensualidad"
        verbose_name_plural = "mensualidades"
        ordering = ["due_date"]

    def __str__(self):
        return f"{self.concept} — {self.student}"