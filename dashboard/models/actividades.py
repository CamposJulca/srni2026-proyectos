from django.db import models

from .organizacion import Colaborador, Proyecto


class Obligacion(models.Model):
    colaborador = models.ForeignKey(
        Colaborador,
        on_delete=models.CASCADE,
        related_name="obligaciones",
    )
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.colaborador} - {self.descripcion[:60]}"


class Actividad(models.Model):
    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("en_curso", "En Curso"),
        ("completada", "Completada"),
        ("bloqueada", "Bloqueada"),
    ]

    obligacion = models.ForeignKey(
        Obligacion,
        on_delete=models.CASCADE,
        related_name="actividades",
    )
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actividades",
    )
    actividad_id = models.CharField(max_length=20, blank=True)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    progreso = models.IntegerField(default=0)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="pendiente")
    orden = models.IntegerField(default=0)
    semanas_activas = models.JSONField(default=list, blank=True)
    evidencia = models.TextField(null=True, blank=True, verbose_name="Evidencia / Entregables")

    class Meta:
        ordering = ["obligacion__colaborador", "orden", "fecha_inicio"]
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"

    def __str__(self):
        return f"{self.obligacion.colaborador} — {self.actividad_id} {self.descripcion[:50]}"
