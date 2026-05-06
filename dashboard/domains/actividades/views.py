import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from dashboard.constants import SEMANA_FECHAS, SEMANAS_ORDENADAS
from dashboard.domains.actividades.selectors import (
    actividad_detalle_qs,
    actividades_en_semana,
    actividades_gantt,
    actividades_mi_cronograma,
    actividades_resumen_qs,
    actividades_semana_qs,
    colaboradores_por_procedimiento,
    listar_colaboradores_nombres,
    listar_obligaciones_descripciones,
    listar_procedimientos_nombres,
    listar_proyectos_nombres,
    nombres_colaboradores_con_actividades,
    proyectos_por_colaborador,
)
from dashboard.domains.actividades.serializers import (
    actividad_detalle_dict,
    actividad_gantt_dict,
    mi_cronograma_task_dict,
    resumen_general_response,
    resumen_response,
    semana_response,
)
from dashboard.domains.actividades.services import (
    ActividadValidationError,
    actualizar_actividad_admin,
    actualizar_actividad_colaborador,
    crear_actividad,
)
from dashboard.domains.actividades.utils import semana_actual as _semana_actual
from dashboard.models import Actividad
from dashboard.permisos import _es_admin, admin_required


@login_required
def actividades_view(request):
    return render(request, "dashboard/actividades.html", {
        "modulo_activo": "actividades",
        "colaboradores": listar_colaboradores_nombres(),
        "obligaciones": listar_obligaciones_descripciones(),
        "proyectos": listar_proyectos_nombres(),
        "procedimientos": listar_procedimientos_nombres(),
        "colabs_por_proc_json": json.dumps(colaboradores_por_procedimiento()),
    })


@login_required
def actividades_data(request):
    qs = actividades_gantt(
        colaborador=request.GET.get("colaborador", "").strip(),
        estado=request.GET.get("estado", "").strip(),
        obligacion=request.GET.get("obligacion", "").strip(),
        proyecto=request.GET.get("proyecto", "").strip(),
    )
    colab_proyectos = proyectos_por_colaborador()
    tasks = []
    for actividad in qs:
        proyectos_colab = sorted(colab_proyectos.get(actividad.obligacion.colaborador_id, set()))
        tasks.append(actividad_gantt_dict(actividad, proyectos_colab))
    return JsonResponse({"tasks": tasks})


@admin_required
@require_POST
def actividad_crear(request):
    try:
        actividad = crear_actividad(json.loads(request.body))
        return JsonResponse({"ok": True, "id": actividad.pk})
    except ActividadValidationError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
    except Exception as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)


@login_required
def actividad_detalle(request, pk):
    try:
        actividad = actividad_detalle_qs().get(pk=pk)
    except Actividad.DoesNotExist:
        return JsonResponse({"error": "No encontrada"}, status=404)

    if request.method == "GET":
        return JsonResponse(actividad_detalle_dict(actividad))

    if not _es_admin(request.user):
        return JsonResponse({"error": "No autorizado"}, status=403)

    if request.method in ("PUT", "PATCH"):
        try:
            actualizar_actividad_admin(actividad, json.loads(request.body))
        except ActividadValidationError as exc:
            return JsonResponse({"ok": False, "error": str(exc)}, status=400)
        return JsonResponse({"ok": True})

    if request.method == "DELETE":
        actividad.delete()
        return JsonResponse({"ok": True})

    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required
def semana_view(request):
    semana_actual = _semana_actual()
    semana_param = request.GET.get("semana", "").strip()
    semana_inicial = semana_param if semana_param in SEMANAS_ORDENADAS else semana_actual

    return render(request, "dashboard/semana.html", {
        "modulo_activo": "actividades",
        "semanas": SEMANAS_ORDENADAS,
        "semana_actual": semana_actual,
        "semana_inicial": semana_inicial,
        "colaborador_inicial": request.GET.get("colaborador", "").strip(),
        "semana_fechas": SEMANA_FECHAS,
        "colaboradores": nombres_colaboradores_con_actividades(),
        "procedimientos": listar_procedimientos_nombres(),
    })


@login_required
def semana_data(request):
    semana = request.GET.get("semana", _semana_actual())
    qs = actividades_semana_qs(
        colaborador=request.GET.get("colaborador", "").strip(),
        procedimiento=request.GET.get("procedimiento", "").strip(),
    )
    return JsonResponse(semana_response(semana, actividades_en_semana(qs, semana)))


def _calcular_resumen(semana):
    actividades = actividades_en_semana(actividades_resumen_qs(), semana)
    return resumen_general_response(semana, actividades)


@login_required
def resumen_view(request):
    semana_actual = _semana_actual()
    idx = SEMANAS_ORDENADAS.index(semana_actual) if semana_actual in SEMANAS_ORDENADAS else 0
    semana_default = SEMANAS_ORDENADAS[max(0, idx - 1)]
    actividades = actividades_en_semana(actividades_resumen_qs(), semana_default)

    return render(request, "dashboard/resumen.html", {
        "modulo_activo": "actividades",
        "semanas": SEMANAS_ORDENADAS,
        "semana_actual": semana_actual,
        "semana_default": semana_default,
        "semana_fechas": SEMANA_FECHAS,
        "datos_iniciales": resumen_response(actividades),
        "procedimientos": listar_procedimientos_nombres(),
    })


@login_required
def resumen_data(request):
    semana = request.GET.get("semana", _semana_actual())
    qs = actividades_resumen_qs(
        procedimiento=request.GET.get("procedimiento", "").strip()
    )
    return JsonResponse(resumen_response(actividades_en_semana(qs, semana)))


@login_required
def mi_cronograma_view(request):
    perfil = getattr(request.user, "perfil", None)
    if not perfil or not perfil.colaborador:
        return redirect("/actividades/")

    return render(request, "dashboard/mi_cronograma.html", {
        "modulo_activo": "mi_cronograma",
        "colaborador": perfil.colaborador,
        "semana_actual": _semana_actual(),
        "semanas": SEMANAS_ORDENADAS,
        "semana_fechas": SEMANA_FECHAS,
    })


@login_required
def mi_cronograma_data(request):
    perfil = getattr(request.user, "perfil", None)
    if not perfil or not perfil.colaborador:
        return JsonResponse({"error": "Sin colaborador vinculado"}, status=403)

    semana = request.GET.get("semana", "").strip()
    qs = actividades_mi_cronograma(perfil.colaborador)
    actividades = actividades_en_semana(qs, semana) if semana else list(qs)
    tasks = [mi_cronograma_task_dict(actividad) for actividad in actividades]

    return JsonResponse({
        "colaborador": perfil.colaborador.nombre,
        "total": len(tasks),
        "tasks": tasks,
    })


@login_required
@require_POST
def mi_actividad_update(request, pk):
    perfil = getattr(request.user, "perfil", None)
    if not perfil or not perfil.colaborador:
        return JsonResponse({"error": "No autorizado"}, status=403)

    try:
        actividad = Actividad.objects.select_related("obligacion__colaborador").get(pk=pk)
    except Actividad.DoesNotExist:
        return JsonResponse({"error": "No encontrada"}, status=404)

    if actividad.obligacion.colaborador_id != perfil.colaborador_id:
        return JsonResponse({"error": "No autorizado"}, status=403)

    try:
        actualizar_actividad_colaborador(actividad, json.loads(request.body))
    except ActividadValidationError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)

    return JsonResponse({"ok": True})
