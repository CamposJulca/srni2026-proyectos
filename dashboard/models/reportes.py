from django.db import models

from .organizacion import Colaborador


class ReporteSemanal(models.Model):
    colaborador = models.ForeignKey(
        Colaborador,
        on_delete=models.CASCADE,
        related_name="reportes_semanales",
    )
    semana = models.CharField(max_length=10)
    que_hizo = models.TextField(verbose_name="Que hizo esta semana")
    impedimentos = models.TextField(blank=True, verbose_name="Impedimentos o bloqueos")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("colaborador", "semana")
        ordering = ("-creado_en",)
        verbose_name = "Reporte semanal"
        verbose_name_plural = "Reportes semanales"

    def __str__(self):
        return f"{self.colaborador.nombre} — {self.semana}"
