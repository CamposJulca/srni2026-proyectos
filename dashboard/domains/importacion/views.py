from django.http import JsonResponse
from django.shortcuts import render

from dashboard.domains.importacion.services import (
    ImportacionValidationError,
    normalizar as _normalizar,
    procesar_colaboradores_ops,
)
from dashboard.permisos import admin_required


@admin_required
def carga(request):
    if request.method == "GET":
        return render(request, "dashboard/carga.html")

    archivo = request.FILES.get("archivo")
    if not archivo:
        return JsonResponse({"error": "No se recibió ningún archivo."}, status=400)

    try:
        return JsonResponse(procesar_colaboradores_ops(archivo))
    except ImportacionValidationError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
