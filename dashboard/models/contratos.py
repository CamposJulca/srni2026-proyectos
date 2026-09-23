"""
Modelos de la capa contractual/financiera importada desde
`data/Contratos SRNI 2026.xlsx` (libro maestro que la abogada actualiza a diario).

La data se importa a la base de datos (ver management/commands/importar_contratos.py);
las vistas NO leen el Excel en vivo.
"""
from django.conf import settings
from django.db import models


class Contrato(models.Model):
    ESTADO_CHOICES = [
        ("ejecucion", "Ejecución"),
        ("cesion", "Cesión"),
        ("terminado", "Terminado"),
        ("suspendido", "Suspendido"),
        ("otro", "Otro"),
    ]
    MODALIDAD_CHOICES = [
        ("unidad", "Unidad"),
        ("adicion", "Proyección/Adición"),
    ]

    # Enganche con la persona del sistema (match por cédula). Puede quedar nulo
    # si el contratista aún no existe como Colaborador.
    colaborador = models.ForeignKey(
        "Colaborador",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contratos",
    )

    numero_contrato = models.CharField(max_length=30, db_index=True)
    id_externo = models.CharField(max_length=30, null=True, blank=True)
    cedula = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    nombre_contratista = models.CharField(max_length=200)
    equipo = models.CharField(max_length=100, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="ejecucion")
    modalidad = models.CharField(max_length=20, choices=MODALIDAD_CHOICES, default="unidad")

    objeto = models.TextField(null=True, blank=True)
    perfil_academico = models.CharField(max_length=250, null=True, blank=True)
    cdp = models.CharField(max_length=30, null=True, blank=True)
    rp = models.CharField(max_length=30, null=True, blank=True)

    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_terminacion = models.DateField(null=True, blank=True)

    valor_honorarios = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    valor_total_contrato = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    valor_cancelado = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    saldo_contrato = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    # Porcentaje 0–100 (en el Excel viene como fracción 0–1).
    porcentaje_ejecucion = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    ibc = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    observaciones = models.TextField(null=True, blank=True)
    importado_en = models.DateTimeField(auto_now=True)

    class Meta:
        # Un mismo contrato aparece en la hoja "Unidad" (estado actual) y en
        # "Proye. adiciones" (proyección); se distinguen por modalidad.
        unique_together = ("numero_contrato", "modalidad")
        ordering = ["equipo", "nombre_contratista"]
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"

    def __str__(self):
        return f"{self.numero_contrato} - {self.nombre_contratista}"


class PagoContrato(models.Model):
    """Pago mensual del contrato (columnas PAGO 1–12 + estado en SECOP II)."""

    ESTADO_SECOP_CHOICES = [
        ("pagado", "Pagado"),
        ("pendiente", "Pendiente"),
    ]

    contrato = models.ForeignKey(
        Contrato,
        on_delete=models.CASCADE,
        related_name="pagos",
    )
    mes = models.PositiveSmallIntegerField()  # 1–12
    valor = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    estado_secop = models.CharField(
        max_length=20,
        choices=ESTADO_SECOP_CHOICES,
        default="pendiente",
    )

    class Meta:
        unique_together = ("contrato", "mes")
        ordering = ["contrato", "mes"]
        verbose_name = "Pago de contrato"
        verbose_name_plural = "Pagos de contrato"

    def __str__(self):
        return f"{self.contrato.numero_contrato} - mes {self.mes}"


class SeguridadSocialContrato(models.Model):
    """Aprobación de seguridad social por mes (hoja SISEG)."""

    contrato = models.ForeignKey(
        Contrato,
        on_delete=models.CASCADE,
        related_name="seguridad_social",
    )
    mes = models.PositiveSmallIntegerField()  # 1–12 (slot de pago de la planilla)
    codigo = models.CharField(max_length=50, null=True, blank=True)
    fecha_aprobado = models.DateField(null=True, blank=True)
    # Mes que cubre la planilla, tal cual en la hoja (ENERO, DICIEMBRE, ...).
    mes_cubierto = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        unique_together = ("contrato", "mes")
        ordering = ["contrato", "mes"]
        verbose_name = "Seguridad social de contrato"
        verbose_name_plural = "Seguridad social de contratos"

    @property
    def aprobado(self):
        return bool(self.codigo or self.fecha_aprobado)

    def __str__(self):
        return f"{self.contrato.numero_contrato} - SS mes {self.mes}"


class Convenio(models.Model):
    """Convenios interadministrativos y otras modalidades."""

    TIPO_CHOICES = [
        ("convenio", "Convenio"),
        ("otra_modalidad", "Otra modalidad"),
    ]

    entidad = models.CharField(max_length=250)
    articulador = models.CharField(max_length=200, null=True, blank=True)
    seyco = models.CharField(max_length=50, null=True, blank=True)
    numero_convenio = models.CharField(max_length=50, null=True, blank=True)
    fecha_suscripcion = models.DateField(null=True, blank=True)
    # Puede contener texto ("Renovacion automatica", "Vigencia ley 1448").
    fecha_terminacion = models.CharField(max_length=100, null=True, blank=True)
    num_modificatorios = models.CharField(max_length=30, null=True, blank=True)
    contratista = models.CharField(max_length=250, null=True, blank=True)
    clase_contrato = models.CharField(max_length=150, null=True, blank=True)
    valor_inicial = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    objeto = models.TextField(null=True, blank=True)
    link = models.TextField(null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default="convenio")

    class Meta:
        ordering = ["tipo", "entidad"]
        verbose_name = "Convenio"
        verbose_name_plural = "Convenios"

    def __str__(self):
        return f"{self.entidad} ({self.numero_convenio or 's/n'})"


class ContratoImportLog(models.Model):
    """Bitácora de cada corrida del importador de contratos."""

    ORIGEN_CHOICES = [
        ("cron", "Cron"),
        ("manual", "Manual"),
    ]

    archivo = models.CharField(max_length=500)
    filas_leidas = models.PositiveIntegerField(default=0)
    creados = models.PositiveIntegerField(default=0)
    actualizados = models.PositiveIntegerField(default=0)
    sin_match_colaborador = models.PositiveIntegerField(default=0)
    errores = models.JSONField(default=list, blank=True)
    origen = models.CharField(max_length=20, choices=ORIGEN_CHOICES, default="manual")
    ejecutado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="importaciones_contratos",
    )
    ejecutado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-ejecutado_en"]
        verbose_name = "Log de importación de contratos"
        verbose_name_plural = "Logs de importación de contratos"

    def __str__(self):
        return f"{self.ejecutado_en:%Y-%m-%d %H:%M} ({self.origen})"
