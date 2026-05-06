from django.contrib.auth.models import User
from django.db import models

from .actividades import Actividad


class EvidenciaActividad(models.Model):
    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.CASCADE,
        related_name="evidencias",
    )
    archivo = models.FileField(upload_to="evidencias/%Y/%m/")
    comentario = models.TextField(blank=True)
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="evidencias_creadas",
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-creado_en",)
        verbose_name = "Evidencia"
        verbose_name_plural = "Evidencias"

    def __str__(self):
        return f"Evidencia {self.actividad.actividad_id} — {self.creado_en:%Y-%m-%d %H:%M}"

    @property
    def nombre_archivo(self):
        if self.archivo:
            return self.archivo.name.split("/")[-1]
        return ""
