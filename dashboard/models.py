from django.db import models


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

    referente = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.proyecto} - {self.nombre}"


class Persona(models.Model):

    nombre = models.CharField(max_length=200, unique=True)
    cedula = models.CharField(max_length=20, null=True, blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    honorarios = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    objeto = models.TextField(null=True, blank=True)
    obligaciones = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre


class Rol(models.Model):

    nombre = models.CharField(
        max_length=100,
        unique=True
    )

    def __str__(self):
        return self.nombre


class Asignacion(models.Model):

    modulo = models.ForeignKey(
        Modulo,
        on_delete=models.CASCADE,
        related_name="asignaciones"
    )

    persona = models.ForeignKey(
        Persona,
        on_delete=models.CASCADE
    )

    rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("modulo", "persona", "rol")

    def __str__(self):
        return f"{self.persona} - {self.rol} - {self.modulo}"


class PlanAccion(models.Model):

    modulo = models.ForeignKey(
        Modulo,
        on_delete=models.CASCADE,
        related_name="planes_accion"
    )

    compromiso = models.TextField()

    mes = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.modulo} - {self.mes}"