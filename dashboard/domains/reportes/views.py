import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from dashboard.domains.reportes.selectors import reportes_admin_qs, reportes_por_colaborador
from dashboard.domains.reportes.serializers import reporte_admin_dict, reporte_colaborador_dict
from dashboard.domains.reportes.services import ReporteValidationError, guardar_reporte_semanal
from dashboard.permisos import admin_required


@login_required
def reporte_semanal_data(request):
    """GET: lista reportes del colaborador logueado. Filtrable por semana."""
    perfil = getattr(request.user, "perfil", None)
    if not perfil or not perfil.colaborador:
        return JsonResponse({"error": "Sin colaborador vinculado"}, status=403)

    semana = request.GET.get("semana", "").strip()
    reportes = [
        reporte_colaborador_dict(reporte)
        for reporte in reportes_por_colaborador(perfil.colaborador, semana)
    ]
    return JsonResponse({"reportes": reportes})


@login_required
@require_POST
def reporte_semanal_guardar(request):
    """Crea o actualiza el reporte de la semana para el colaborador logueado."""
    perfil = getattr(request.user, "perfil", None)
    if not perfil or not perfil.colaborador:
        return JsonResponse({"error": "No autorizado"}, status=403)

    try:
        reporte, created = guardar_reporte_semanal(
            perfil.colaborador,
            json.loads(request.body),
        )
    except ReporteValidationError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse({
        "ok": True,
        "id": reporte.pk,
        "created": created,
    })


@admin_required
def reportes_admin(request):
    """Vista admin: lista todos los reportes semanales, filtrable por semana."""
    semana = request.GET.get("semana", "").strip()
    reportes = [
        reporte_admin_dict(reporte)
        for reporte in reportes_admin_qs(semana)
    ]
    return JsonResponse({"reportes": reportes, "total": len(reportes)})
