from django.db import models


class Procedimiento(models.Model):

    nombre = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.nombre


class Proyecto(models.Model):

    nombre = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.nombre


class Modulo(models.Model):

    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="modulos"
    )
    nombre = models.CharField(max_length=200)
    referente = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.proyecto} - {self.nombre}"


class Colaborador(models.Model):

    procedimiento = models.ForeignKey(
        Procedimiento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="colaboradores"
    )
    nombre = models.CharField(max_length=200, unique=True)
    cedula = models.CharField(max_length=20, null=True, blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    honorarios = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    objeto = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre


class Rol(models.Model):

    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Asignacion(models.Model):

    modulo = models.ForeignKey(
        Modulo,
        on_delete=models.CASCADE,
        related_name="asignaciones"
    )
    colaborador = models.ForeignKey(
        Colaborador,
        on_delete=models.CASCADE,
        related_name="asignaciones"
    )
    rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("modulo", "colaborador", "rol")

    def __str__(self):
        return f"{self.colaborador} - {self.rol} - {self.modulo}"


class Obligacion(models.Model):

    colaborador = models.ForeignKey(
        Colaborador,
        on_delete=models.CASCADE,
        related_name="obligaciones"
    )
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.colaborador} - {self.descripcion[:60]}"


class Actividad(models.Model):

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_curso', 'En Curso'),
        ('completada', 'Completada'),
        ('bloqueada', 'Bloqueada'),
    ]

    obligacion = models.ForeignKey(
        Obligacion,
        on_delete=models.CASCADE,
        related_name="actividades"
    )
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actividades"
    )
    actividad_id = models.CharField(max_length=20, blank=True)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    progreso = models.IntegerField(default=0)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    orden = models.IntegerField(default=0)
    semanas_activas = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['obligacion__colaborador', 'orden', 'fecha_inicio']
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'

    def __str__(self):
        return f"{self.obligacion.colaborador} — {self.actividad_id} {self.descripcion[:50]}"
