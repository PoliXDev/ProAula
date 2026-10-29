"""
Datos del colegio: usuarios, aulas, alumnos, notas, asistencia,
comunicados y mensualidades.

Viven en una sola app para poder explicar el esquema en la defensa
sin saltar entre paquetes. Las reglas que no pueden depender del
formulario (nota 1-20 y una sola asistencia por día) se validan aquí.
"""

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    """
    Usuario del sistema, personal o representante.

    Un solo modelo de login evita dos autenticaciones. El rol separa
    quién entra al panel (STAFF) y quién solo verá a sus hijos (PARENT).
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
    Aula de un curso escolar.

    Agrupa alumnos y comunicados de clase. La combinación de nombre,
    sección y año no puede repetirse: no hay dos "3er Grado A" en 2026-2027.
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
    Alumno matriculado en un aula y vinculado a un representante.

    El código de matrícula identifica al alumno dentro del colegio.
    El padre solo puede ser un usuario con rol PARENT: un docente
    no queda asignado como familia por error en el admin.
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
    # PROTECT: no se borra un aula o un padre si todavía tienen alumnos.
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
    Calificación de un alumno en una asignatura.

    Las asignaturas son una lista fija: no hace falta una tabla extra.
    La nota se rechaza fuera de 1 a 20 en el servidor, no solo en el formulario.
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
    # Un decimal admite 18.5 y los validadores cierran el rango de la guía.
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
    Asistencia de un alumno en un día.

    Solo puede existir un registro por alumno y fecha. Si el personal
    intenta cargar el mismo día dos veces, la base de datos lo impide.
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
    Comunicado del colegio o de un aula.

    Si el aula va vacía, el aviso es para todo el centro. Si tiene aula,
    solo corresponde a esa clase. No se borra el aula en cascada: el aviso
    no debe convertirse en general por un borrado accidental.
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
    Mensualidad de un alumno.

    Va aparte de las notas: el portal puede mostrar si el pago está
    pendiente sin mezclar el cobro con el expediente académico.
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
