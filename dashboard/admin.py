from django.contrib import admin
from .models import (
    Proyecto,
    Modulo,
    Persona,
    Rol,
    Asignacion,
    PlanAccion
)

admin.site.register(Proyecto)
admin.site.register(Modulo)
admin.site.register(Persona)
admin.site.register(Rol)
admin.site.register(Asignacion)
admin.site.register(PlanAccion)