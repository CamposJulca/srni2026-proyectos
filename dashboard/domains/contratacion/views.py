from django.http import JsonResponse
from django.views.decorators.http import require_POST

from dashboard.domains.contratacion.importador import ejecutar_importacion
from dashboard.domains.contratacion.services import contratacion_payload
from dashboard.domains.importacion.services import ImportacionValidationError
from dashboard.permisos import admin_required


@admin_required
def contratacion_data(request):
    return JsonResponse(contratacion_payload())


@admin_required
@require_POST
def contratacion_sincronizar(request):
    """Botón "Sincronizar": re-importa desde el .xlsx subido o el de la ruta por defecto."""
    archivo = request.FILES.get("archivo")
    try:
        resumen = ejecutar_importacion(
            archivo=archivo or None,
            origen="manual",
            usuario=request.user,
        )
    except ImportacionValidationError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    return JsonResponse(resumen)
