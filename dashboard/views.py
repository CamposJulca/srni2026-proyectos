from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count

from .models import (
    Proyecto,
    Modulo,
    Persona,
    Rol,
    Asignacion,
    PlanAccion
)


def dashboard(request):

    personas = Persona.objects.all()
    roles = Rol.objects.all()
    proyectos = Proyecto.objects.all()

    return render(
        request,
        "dashboard/dashboard.html",
        {
            "personas": personas,
            "roles": roles,
            "proyectos": proyectos
        }
    )


def dashboard_data(request):

    persona = request.GET.get("persona")
    rol = request.GET.get("rol")
    proyecto = request.GET.get("proyecto")

    asignaciones = Asignacion.objects.select_related(
        "persona",
        "rol",
        "modulo",
        "modulo__proyecto"
    )

    if persona:
        asignaciones = asignaciones.filter(persona_id=persona)

    if rol:
        asignaciones = asignaciones.filter(rol_id=rol)

    if proyecto:
        asignaciones = asignaciones.filter(modulo__proyecto_id=proyecto)

    kpis = {

        "proyectos": Proyecto.objects.count(),
        "modulos": Modulo.objects.count(),
        "personas": Persona.objects.count(),
        "asignaciones": asignaciones.count(),
    }

    proyectos_persona = (
        asignaciones
        .values("persona__nombre")
        .annotate(total=Count("modulo__proyecto", distinct=True))
    )

    roles_persona = (
        asignaciones
        .values("rol__nombre")
        .annotate(total=Count("persona", distinct=True))
    )

    modulos_proyecto = (
        Modulo.objects
        .values("proyecto__nombre")
        .annotate(total=Count("id"))
    )

    compromisos_mes = (
        PlanAccion.objects
        .values("mes")
        .annotate(total=Count("id"))
    )

    data = {

        "kpis": kpis,

        "proyectos_persona": list(proyectos_persona),

        "roles_persona": list(roles_persona),

        "modulos_proyecto": list(modulos_proyecto),

        "compromisos_mes": list(compromisos_mes),
    }

    return JsonResponse(data)