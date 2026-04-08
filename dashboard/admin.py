from django.contrib import admin
from .models import (
    Procedimiento,
    Proyecto,
    Modulo,
    Colaborador,
    Rol,
    Asignacion,
    Obligacion,
    Actividad,
)

admin.site.register(Procedimiento)
admin.site.register(Proyecto)
admin.site.register(Modulo)
admin.site.register(Colaborador)
admin.site.register(Rol)
admin.site.register(Asignacion)
admin.site.register(Obligacion)
admin.site.register(Actividad)
