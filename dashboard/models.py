from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
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
    evidencia = models.TextField(null=True, blank=True, verbose_name='Evidencia / Entregables')

    class Meta:
        ordering = ['obligacion__colaborador', 'orden', 'fecha_inicio']
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'

    def __str__(self):
        return f"{self.obligacion.colaborador} — {self.actividad_id} {self.descripcion[:50]}"


class CuentaCobro(models.Model):

    ESTADO_CHOICES = [
        ("borrador", "Borrador"),
        ("radicada", "Radicada"),
        ("aprobada", "Aprobada"),
        ("pagada", "Pagada"),
        ("rechazada", "Rechazada"),
    ]

    colaborador = models.ForeignKey(
        Colaborador,
        on_delete=models.CASCADE,
        related_name="cuentas_cobro",
    )
    # Se normaliza al primer día del mes para representar periodos de prestación de servicios.
    periodo = models.DateField()
    numero_cuenta = models.CharField(max_length=50, null=True, blank=True)
    fecha_radicacion = models.DateField(null=True, blank=True)
    valor_cobrado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="radicada")
    observaciones = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ("colaborador", "periodo")
        ordering = ["-periodo", "colaborador__nombre"]
        verbose_name = "Cuenta de cobro"
        verbose_name_plural = "Cuentas de cobro"

    def save(self, *args, **kwargs):
        if self.periodo:
            self.periodo = self.periodo.replace(day=1)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.colaborador} - {self.periodo:%Y-%m}"


class Perfil(models.Model):

    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('colaborador', 'Colaborador'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    colaborador = models.OneToOneField(
        Colaborador,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perfil',
    )
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='colaborador')

    def __str__(self):
        return f"{self.user.username} ({self.get_rol_display()})"


class EvidenciaActividad(models.Model):

    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.CASCADE,
        related_name='evidencias',
    )
    archivo = models.FileField(upload_to='evidencias/%Y/%m/')
    comentario = models.TextField(blank=True)
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='evidencias_creadas',
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-creado_en',)
        verbose_name = 'Evidencia'
        verbose_name_plural = 'Evidencias'

    def __str__(self):
        return f"Evidencia {self.actividad.actividad_id} — {self.creado_en:%Y-%m-%d %H:%M}"

    @property
    def nombre_archivo(self):
        if self.archivo:
            return self.archivo.name.split('/')[-1]
        return ''


class ReporteSemanal(models.Model):

    colaborador = models.ForeignKey(
        Colaborador,
        on_delete=models.CASCADE,
        related_name='reportes_semanales',
    )
    semana = models.CharField(max_length=10)  # 'ABR S3'
    que_hizo = models.TextField(verbose_name='Que hizo esta semana')
    impedimentos = models.TextField(blank=True, verbose_name='Impedimentos o bloqueos')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('colaborador', 'semana')
        ordering = ('-creado_en',)
        verbose_name = 'Reporte semanal'
        verbose_name_plural = 'Reportes semanales'

    def __str__(self):
        return f"{self.colaborador.nombre} — {self.semana}"
