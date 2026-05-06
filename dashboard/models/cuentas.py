from django.core.validators import MinValueValidator
from django.db import models

from .organizacion import Colaborador


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
