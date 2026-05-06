import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from dashboard.crud_config import TABLA_META
from dashboard.domains.crud.selectors import aplicar_filtros, obtener_objeto
from dashboard.domains.crud.serializers import campo_meta_dict, detalle_dict, serializar_fila
from dashboard.domains.crud.services import (
    CrudValidationError,
    actualizar_objeto,
    crear_objeto,
    ejecutar_select_seguro,
)
from dashboard.permisos import admin_required


@admin_required
@require_POST
def sql_query(request):
    try:
        body = json.loads(request.body)
        data = ejecutar_select_seguro(body.get("query", ""))
        return JsonResponse(data)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido."}, status=400)
    except CrudValidationError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except PermissionError as exc:
        return JsonResponse({"error": str(exc)}, status=403)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)


@admin_required
def crud_meta(request):
    """Devuelve metadatos de todas las tablas (campos, conteos, opciones FK)."""
    resultado = {}
    for key, cfg in TABLA_META.items():
        resultado[key] = {
            "label": cfg["label"],
            "campos": [campo_meta_dict(campo) for campo in cfg["campos"]],
            "columnas": cfg["columnas_lista"],
            "filtro_colaborador": cfg.get("filtro_colaborador", False),
            "total": cfg["modelo"].objects.count(),
        }
    return JsonResponse(resultado)


@admin_required
def crud_lista(request, tabla):
    cfg = TABLA_META.get(tabla)
    if not cfg:
        return JsonResponse({"error": "Tabla no válida."}, status=404)

    qs = aplicar_filtros(tabla, cfg, request.GET)
    total = qs.count()
    page = int(request.GET.get("page", 1))
    size = 25
    qs = qs[(page - 1) * size: page * size]

    filas = [serializar_fila(obj, cfg["columnas_lista"]) for obj in qs]
    return JsonResponse({"filas": filas, "total": total, "page": page, "size": size})


@admin_required
def crud_detalle(request, tabla, pk):
    cfg = TABLA_META.get(tabla)
    if not cfg:
        return JsonResponse({"error": "Tabla no válida."}, status=404)

    try:
        obj = obtener_objeto(cfg, pk)
    except cfg["modelo"].DoesNotExist:
        return JsonResponse({"error": "Registro no encontrado."}, status=404)

    if request.method == "GET":
        return JsonResponse(detalle_dict(obj, cfg["campos"]))

    if request.method in ("PUT", "PATCH"):
        try:
            body = json.loads(request.body)
            actualizar_objeto(obj, cfg["campos"], body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido."}, status=400)
        except Exception as exc:
            return JsonResponse({"error": str(exc)}, status=400)
        return JsonResponse({"ok": True, "id": obj.pk})

    if request.method == "DELETE":
        try:
            obj.delete()
        except Exception as exc:
            return JsonResponse({"error": str(exc)}, status=400)
        return JsonResponse({"ok": True})

    return JsonResponse({"error": "Método no permitido."}, status=405)


@admin_required
def crud_crear(request, tabla):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)

    cfg = TABLA_META.get(tabla)
    if not cfg:
        return JsonResponse({"error": "Tabla no válida."}, status=404)

    try:
        body = json.loads(request.body)
        obj = crear_objeto(cfg, body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido."}, status=400)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse({"ok": True, "id": obj.pk}, status=201)
