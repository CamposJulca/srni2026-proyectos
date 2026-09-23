import csv

from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from dashboard.constants import PROCEDIMIENTOS
from dashboard.domains.gerencial.selectors import (
    asignaciones_filtradas,
    colaboradores_dashboard,
    colaboradores_filtrados,
    proyectos_dashboard,
    roles_dashboard,
)
from dashboard.domains.gerencial.serializers import persona_por_rol_dict
from dashboard.domains.gerencial.services import dashboard_payload, gerencial_payload, proyecto_detalle_payload
from dashboard.domains.gerencial.utils import (
    clasificar_cruce_cobro as _clasificar_cruce_cobro,
    resolver_periodo as _resolver_periodo,
)
from dashboard.permisos import admin_required
from dashboard.models import Proyecto


@admin_required
def gerencial_data(request):
    return JsonResponse(gerencial_payload())


@admin_required
def dashboard(request):
    procedimiento = request.GET.get("procedimiento", "INSTRUMENTALIZACIÓN")

    return render(
        request,
        "dashboard/dashboard_view.html",
        {
            "personas": colaboradores_dashboard(procedimiento),
            "roles": roles_dashboard(),
            "proyectos": proyectos_dashboard(),
            "procedimientos": PROCEDIMIENTOS,
            "procedimiento_activo": procedimiento,
            "modulo_activo": "dashboard",
        },
    )


@admin_required
def dashboard_data(request):
    persona = request.GET.get("persona")
    rol = request.GET.get("rol")
    proyecto = request.GET.get("proyecto")
    procedimiento = request.GET.get("procedimiento")
    periodo = _resolver_periodo(request.GET.get("periodo", "").strip())

    if periodo is None:
        return JsonResponse(
            {"error": "Parámetro 'periodo' inválido. Use formato YYYY-MM."},
            status=400,
        )

    asignaciones = asignaciones_filtradas(
        persona=persona,
        rol=rol,
        proyecto=proyecto,
        procedimiento=procedimiento,
    )
    colaboradores_qs = colaboradores_filtrados(
        persona=persona,
        rol=rol,
        proyecto=proyecto,
        procedimiento=procedimiento,
    )

    return JsonResponse(dashboard_payload(
        asignaciones=asignaciones,
        colaboradores_qs=colaboradores_qs,
        periodo=periodo,
        proyecto=proyecto,
    ))


def personas_por_rol(request):
    qs = asignaciones_filtradas(
        rol=request.GET.get("rol", ""),
        proyecto=request.GET.get("proyecto", ""),
    )
    data = [
        persona_por_rol_dict(asignacion)
        for asignacion in qs.order_by("colaborador__nombre")
    ]
    return JsonResponse({"asignaciones": data})


@admin_required
def proyecto_detalle_data(request, pk):
    get_object_or_404(Proyecto, pk=pk)
    return JsonResponse(proyecto_detalle_payload(pk))


@admin_required
def proyecto_exportar_csv(request, pk):
    data = proyecto_detalle_payload(pk)
    proyecto = data["proyecto"]

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="proyecto-{pk}.csv"'
    writer = csv.writer(response)

    writer.writerow(["Ficha de proyecto", proyecto["nombre"]])
    writer.writerow(["Estado", proyecto["estado"]])
    writer.writerow(["Prioridad", proyecto["prioridad"]])
    writer.writerow(["Responsable", proyecto["responsable"] or ""])
    writer.writerow(["Procedimiento", proyecto["procedimiento"] or ""])
    writer.writerow(["Fecha inicio", proyecto["fecha_inicio"] or ""])
    writer.writerow(["Fecha fin", proyecto["fecha_fin"] or ""])
    writer.writerow(["Presupuesto", proyecto["presupuesto"]])
    writer.writerow([])

    resumen = data.get("resumen") or {}
    writer.writerow(["Resumen ejecutivo"])
    writer.writerow(["Avance promedio", resumen.get("avance_promedio", 0)])
    writer.writerow(["Cumplimiento mes", resumen.get("cumplimiento_mes", 0)])
    writer.writerow(["Actividades vencidas", resumen.get("actividades_vencidas", 0)])
    writer.writerow(["Actividades bloqueadas", resumen.get("actividades_bloqueadas", 0)])
    writer.writerow(["Personas asignadas", resumen.get("personas_asignadas", 0)])
    writer.writerow(["Semáforo", resumen.get("semaforo", "")])
    writer.writerow([])

    writer.writerow(["Cronograma"])
    writer.writerow(["ID", "Actividad", "Colaborador", "Inicio", "Fin", "Estado", "Progreso"])
    for actividad in data["cronograma"]:
        writer.writerow([
            actividad["actividad_id"],
            actividad["descripcion"],
            actividad["colaborador"],
            actividad["fecha_inicio"],
            actividad["fecha_fin"],
            actividad["estado"],
            actividad["progreso"],
        ])
    writer.writerow([])

    writer.writerow(["Riesgos"])
    writer.writerow(["Riesgo", "Impacto", "Probabilidad", "Responsable", "Fecha límite", "Estado", "Plan"])
    for riesgo in data["riesgos"]:
        writer.writerow([
            riesgo["riesgo"],
            riesgo["impacto"],
            riesgo["probabilidad"],
            riesgo["responsable"] or "",
            riesgo["fecha_limite"] or "",
            riesgo["estado"],
            riesgo["plan_mitigacion"] or "",
        ])

    return response
