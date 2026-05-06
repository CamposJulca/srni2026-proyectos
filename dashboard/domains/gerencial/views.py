from django.http import JsonResponse
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
from dashboard.domains.gerencial.services import dashboard_payload, gerencial_payload
from dashboard.domains.gerencial.utils import (
    clasificar_cruce_cobro as _clasificar_cruce_cobro,
    resolver_periodo as _resolver_periodo,
)
from dashboard.permisos import admin_required


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
