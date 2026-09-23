from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Procedimiento(models.Model):
    nombre = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.nombre


class Proyecto(models.Model):
    ESTADO_CHOICES = [
        ("planeado", "Planeado"),
        ("activo", "Activo"),
        ("en_riesgo", "En riesgo"),
        ("bloqueado", "Bloqueado"),
        ("finalizado", "Finalizado"),
        ("cancelado", "Cancelado"),
    ]
    PRIORIDAD_CHOICES = [
        ("baja", "Baja"),
        ("media", "Media"),
        ("alta", "Alta"),
        ("critica", "Crítica"),
    ]

    nombre = models.CharField(max_length=200, unique=True)
    objetivo = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="activo")
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default="media")
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    responsable = models.ForeignKey(
        "Colaborador",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="proyectos_responsable",
    )
    procedimiento = models.ForeignKey(
        Procedimiento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="proyectos",
    )
    presupuesto = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    observaciones = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["nombre"]

    def clean(self):
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValidationError({"fecha_fin": "La fecha fin debe ser mayor o igual a la fecha inicio."})

    def _snapshot(self):
        campos = [
            "nombre",
            "objetivo",
            "estado",
            "prioridad",
            "fecha_inicio",
            "fecha_fin",
            "responsable_id",
            "procedimiento_id",
            "presupuesto",
            "observaciones",
        ]
        snapshot = {}
        for campo in campos:
            valor = getattr(self, campo)
            if hasattr(valor, "isoformat"):
                valor = valor.isoformat()
            elif valor is not None:
                valor = str(valor)
            snapshot[campo] = valor
        return snapshot

    def save(self, *args, **kwargs):
        anterior = None
        if self.pk:
            anterior = Proyecto.objects.filter(pk=self.pk).first()
            anterior = anterior._snapshot() if anterior else None
        self.full_clean()
        super().save(*args, **kwargs)
        if anterior is not None:
            nuevo = self._snapshot()
            cambios = {
                campo: {"antes": anterior[campo], "despues": nuevo[campo]}
                for campo in nuevo
                if anterior.get(campo) != nuevo.get(campo)
            }
            if cambios:
                ProyectoHistorial.objects.create(proyecto=self, cambios=cambios)

    def __str__(self):
        return self.nombre


class Modulo(models.Model):
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="modulos",
    )
    nombre = models.CharField(max_length=200)
    referente = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["proyecto", "nombre"],
                name="unique_modulo_nombre_por_proyecto",
            )
        ]

    def __str__(self):
        return f"{self.proyecto} - {self.nombre}"


class RiesgoProyecto(models.Model):
    NIVEL_CHOICES = [
        ("bajo", "Bajo"),
        ("medio", "Medio"),
        ("alto", "Alto"),
        ("critico", "Crítico"),
    ]
    ESTADO_CHOICES = [
        ("abierto", "Abierto"),
        ("en_mitigacion", "En mitigación"),
        ("cerrado", "Cerrado"),
    ]

    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="riesgos",
    )
    riesgo = models.CharField(max_length=250)
    impacto = models.CharField(max_length=20, choices=NIVEL_CHOICES, default="medio")
    probabilidad = models.CharField(max_length=20, choices=NIVEL_CHOICES, default="medio")
    responsable = models.ForeignKey(
        "Colaborador",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="riesgos_responsable",
    )
    fecha_limite = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="abierto")
    plan_mitigacion = models.TextField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["estado", "fecha_limite", "riesgo"]
        verbose_name = "Riesgo de proyecto"
        verbose_name_plural = "Riesgos de proyecto"

    def __str__(self):
        return f"{self.proyecto} - {self.riesgo}"


class AlertaProyecto(models.Model):
    ESTADO_CHOICES = [
        ("abierta", "Abierta"),
        ("atendida", "Atendida"),
        ("cerrada", "Cerrada"),
    ]
    SEVERIDAD_CHOICES = [
        ("informativa", "Informativa"),
        ("media", "Media"),
        ("alta", "Alta"),
        ("critica", "Crítica"),
    ]

    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="alertas",
    )
    alerta = models.CharField(max_length=250)
    severidad = models.CharField(max_length=20, choices=SEVERIDAD_CHOICES, default="media")
    responsable = models.ForeignKey(
        "Colaborador",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alertas_responsable",
    )
    fecha_limite = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="abierta")
    plan_accion = models.TextField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["estado", "fecha_limite", "alerta"]
        verbose_name = "Alerta de proyecto"
        verbose_name_plural = "Alertas de proyecto"

    def __str__(self):
        return f"{self.proyecto} - {self.alerta}"


class ProyectoHistorial(models.Model):
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="historial",
    )
    cambios = models.JSONField(default=dict)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]
        verbose_name = "Historial de proyecto"
        verbose_name_plural = "Historial de proyectos"

    def __str__(self):
        return f"{self.proyecto} - {self.creado_en:%Y-%m-%d %H:%M}"


class Colaborador(models.Model):
    procedimiento = models.ForeignKey(
        Procedimiento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="colaboradores",
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
        related_name="asignaciones",
    )
    colaborador = models.ForeignKey(
        Colaborador,
        on_delete=models.CASCADE,
        related_name="asignaciones",
    )
    rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ("modulo", "colaborador", "rol")

    def __str__(self):
        return f"{self.colaborador} - {self.rol} - {self.modulo}"
