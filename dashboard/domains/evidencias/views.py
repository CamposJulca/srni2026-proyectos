from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from dashboard.domains.evidencias.selectors import (
    actividad_con_colaborador,
    actividad_por_pk,
    evidencia_con_actividad,
)
from dashboard.domains.evidencias.serializers import evidencia_creada_dict, evidencia_dict
from dashboard.domains.evidencias.services import (
    EvidenciaPermissionError,
    EvidenciaValidationError,
    eliminar_evidencia,
    subir_evidencia,
)
from dashboard.models import Actividad, EvidenciaActividad


@login_required
def evidencias_lista(request, actividad_pk):
    """Lista evidencias de una actividad (GET)."""
    try:
        actividad = actividad_por_pk(actividad_pk)
    except Actividad.DoesNotExist:
        return JsonResponse({"error": "Actividad no encontrada"}, status=404)

    evidencias = [evidencia_dict(evidencia) for evidencia in actividad.evidencias.all()]
    return JsonResponse({"evidencias": evidencias, "total": len(evidencias)})


@login_required
@require_POST
def evidencia_subir(request, actividad_pk):
    """Sube una evidencia (archivo + comentario) a una actividad."""
    try:
        actividad = actividad_con_colaborador(actividad_pk)
    except Actividad.DoesNotExist:
        return JsonResponse({"error": "Actividad no encontrada"}, status=404)

    try:
        evidencia = subir_evidencia(
            request.user,
            actividad,
            request.FILES.get("archivo"),
            request.POST.get("comentario", ""),
        )
    except EvidenciaPermissionError as exc:
        return JsonResponse({"error": str(exc)}, status=403)
    except EvidenciaValidationError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse(evidencia_creada_dict(evidencia))


@login_required
@require_POST
def evidencia_eliminar(request, pk):
    """Elimina una evidencia (solo el creador o admin)."""
    try:
        evidencia = evidencia_con_actividad(pk)
    except EvidenciaActividad.DoesNotExist:
        return JsonResponse({"error": "No encontrada"}, status=404)

    try:
        eliminar_evidencia(request.user, evidencia)
    except EvidenciaPermissionError as exc:
        return JsonResponse({"error": str(exc)}, status=403)

    return JsonResponse({"ok": True})
