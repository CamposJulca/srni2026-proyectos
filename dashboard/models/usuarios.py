from django.contrib.auth.models import User
from django.db import models

from .organizacion import Colaborador


class Perfil(models.Model):
    ROL_CHOICES = [
        ("admin", "Administrador"),
        ("colaborador", "Colaborador"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    colaborador = models.OneToOneField(
        Colaborador,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="perfil",
    )
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default="colaborador")

    def __str__(self):
        return f"{self.user.username} ({self.get_rol_display()})"
