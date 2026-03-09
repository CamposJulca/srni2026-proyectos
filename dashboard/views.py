from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from django.db import connection
from django.views.decorators.http import require_POST
import json
import re

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

    # ==============================
    # KPIs
    # ==============================

    kpis = {
        "proyectos": Proyecto.objects.count(),
        "modulos": Modulo.objects.count(),
        "personas": Persona.objects.count(),
        "asignaciones": asignaciones.count(),
    }

    # ==============================
    # Proyectos por persona
    # ==============================

    proyectos_persona = (
        asignaciones
        .values("persona__nombre")
        .annotate(total=Count("modulo__proyecto", distinct=True))
    )

    # ==============================
    # Roles por persona
    # ==============================

    roles_persona = (
        asignaciones
        .values("rol__nombre")
        .annotate(total=Count("persona", distinct=True))
    )

    # ==============================
    # Módulos filtrados
    # ==============================

    modulos_ids = asignaciones.values_list("modulo_id", flat=True)

    modulos_proyecto = (
        Modulo.objects
        .filter(id__in=modulos_ids)
        .values("proyecto__nombre")
        .annotate(total=Count("id", distinct=True))
    )

    # ==============================
    # Compromisos por mes
    # ==============================

    compromisos_query = PlanAccion.objects.select_related("modulo", "modulo__proyecto")

    if proyecto:
        compromisos_query = compromisos_query.filter(modulo__proyecto_id=proyecto)

    compromisos_mes = (
        compromisos_query
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


@require_POST
def sql_query(request):
    try:
        body = json.loads(request.body)
        query = body.get("query", "").strip()
    except Exception:
        return JsonResponse({"error": "JSON inválido."}, status=400)

    if not query:
        return JsonResponse({"error": "La consulta está vacía."}, status=400)

    # Solo permite SELECT
    primera_palabra = re.split(r'\s+', query)[0].upper()
    if primera_palabra != "SELECT":
        return JsonResponse(
            {"error": "Solo se permiten consultas SELECT."},
            status=403
        )

    # Bloquea palabras peligrosas por si cuelan en subconsultas
    peligrosas = r'\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|REPLACE|ATTACH|DETACH|PRAGMA)\b'
    if re.search(peligrosas, query, re.IGNORECASE):
        return JsonResponse(
            {"error": "La consulta contiene operaciones no permitidas."},
            status=403
        )

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchmany(500)  # máximo 500 filas
        return JsonResponse({
            "columnas": columnas,
            "filas": [list(f) for f in filas],
            "total": len(filas)
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)