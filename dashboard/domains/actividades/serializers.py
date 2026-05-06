from dashboard.constants import SEMANA_FECHAS
from dashboard.domains.actividades.utils import estado_visual_actividad


def actividad_gantt_dict(actividad, proyectos_colab):
    proyecto = (
        actividad.proyecto.nombre
        if actividad.proyecto
        else (proyectos_colab[0] if len(proyectos_colab) == 1 else None)
    )
    return {
        "id": actividad.pk,
        "colaborador": actividad.obligacion.colaborador.nombre,
        "obligacion": actividad.obligacion.descripcion,
        "actividad_id": actividad.actividad_id,
        "descripcion": actividad.descripcion,
        "fecha_inicio": actividad.fecha_inicio.isoformat(),
        "fecha_fin": actividad.fecha_fin.isoformat(),
        "progreso": actividad.progreso,
        "estado": actividad.estado,
        "estado_visual": estado_visual_actividad(actividad),
        "orden": actividad.orden,
        "proyecto": proyecto,
        "proyectos": proyectos_colab,
    }


def actividad_detalle_dict(actividad):
    return {
        "id": actividad.pk,
        "colaborador": actividad.obligacion.colaborador.nombre,
        "obligacion": actividad.obligacion.descripcion,
        "actividad_id": actividad.actividad_id,
        "descripcion": actividad.descripcion,
        "fecha_inicio": actividad.fecha_inicio.isoformat(),
        "fecha_fin": actividad.fecha_fin.isoformat(),
        "progreso": actividad.progreso,
        "estado": actividad.estado,
        "evidencia": actividad.evidencia or "",
    }


def semana_response(semana, actividades):
    grupos = {}
    for actividad in actividades:
        colaborador = actividad.obligacion.colaborador.nombre
        grupos.setdefault(colaborador, []).append({
            "id": actividad.pk,
            "actividad_id": actividad.actividad_id,
            "descripcion": actividad.descripcion,
            "obligacion": actividad.obligacion.descripcion,
            "estado": actividad.estado,
            "progreso": actividad.progreso,
            "fecha_inicio": actividad.fecha_inicio.isoformat(),
            "fecha_fin": actividad.fecha_fin.isoformat(),
            "total_semanas": len(actividad.semanas_activas),
            "semana_num": (
                actividad.semanas_activas.index(semana) + 1
                if semana in actividad.semanas_activas
                else 0
            ),
        })

    fechas = SEMANA_FECHAS.get(semana, ("", ""))
    return {
        "semana": semana,
        "fecha_inicio": fechas[0],
        "fecha_fin": fechas[1],
        "total_colaboradores": len(grupos),
        "total_actividades": sum(len(v) for v in grupos.values()),
        "grupos": grupos,
    }


def resumen_response(actividades):
    total = len(actividades)
    completadas = sum(1 for a in actividades if a.estado == "completada")
    en_curso = sum(1 for a in actividades if a.estado == "en_curso")
    pendientes = sum(1 for a in actividades if a.estado == "pendiente")
    bloqueadas = sum(1 for a in actividades if a.estado == "bloqueada")
    avance = round(sum(a.progreso for a in actividades) / total, 1) if total else 0

    por_colab = {}
    for actividad in actividades:
        nombre = actividad.obligacion.colaborador.nombre
        if nombre not in por_colab:
            por_colab[nombre] = {
                "total": 0,
                "completadas": 0,
                "en_curso": 0,
                "pendientes": 0,
                "bloqueadas": 0,
                "progreso_sum": 0,
            }
        item = por_colab[nombre]
        item["total"] += 1
        item["progreso_sum"] += actividad.progreso
        if actividad.estado == "completada":
            item["completadas"] += 1
        elif actividad.estado == "en_curso":
            item["en_curso"] += 1
        elif actividad.estado == "pendiente":
            item["pendientes"] += 1
        elif actividad.estado == "bloqueada":
            item["bloqueadas"] += 1

    colaboradores = []
    for nombre, item in sorted(
        por_colab.items(),
        key=lambda x: x[1]["progreso_sum"] / max(x[1]["total"], 1),
        reverse=True,
    ):
        avg = round(item["progreso_sum"] / item["total"], 1) if item["total"] else 0
        colaboradores.append({
            "nombre": nombre,
            "total": item["total"],
            "completadas": item["completadas"],
            "en_curso": item["en_curso"],
            "pendientes": item["pendientes"],
            "bloqueadas": item["bloqueadas"],
            "avance": avg,
        })

    return {
        "total": total,
        "completadas": completadas,
        "en_curso": en_curso,
        "pendientes": pendientes,
        "bloqueadas": bloqueadas,
        "avance": avance,
        "colaboradores": colaboradores,
    }


def resumen_general_response(semana, actividades):
    data = resumen_response(actividades)
    fechas = SEMANA_FECHAS.get(semana, ("", ""))
    return {
        "semana": semana,
        "fecha_inicio": fechas[0],
        "fecha_fin": fechas[1],
        "total_compromisos": data["total"],
        "avance_general": round(data["avance"]),
        "completadas": data["completadas"],
        "en_curso": data["en_curso"],
        "pendientes": data["pendientes"],
        "bloqueadas": data["bloqueadas"],
        "por_colaborador": [
            {
                "colaborador": item["nombre"],
                "compromisos": item["total"],
                "completadas": item["completadas"],
                "en_curso": item["en_curso"],
                "pendientes": item["pendientes"],
                "bloqueadas": item["bloqueadas"],
                "avance": round(item["avance"]),
            }
            for item in sorted(data["colaboradores"], key=lambda item: item["nombre"])
        ],
    }


def mi_cronograma_task_dict(actividad):
    return {
        "id": actividad.pk,
        "obligacion": actividad.obligacion.descripcion,
        "actividad_id": actividad.actividad_id,
        "descripcion": actividad.descripcion,
        "fecha_inicio": actividad.fecha_inicio.isoformat(),
        "fecha_fin": actividad.fecha_fin.isoformat(),
        "progreso": actividad.progreso,
        "estado": actividad.estado,
        "estado_visual": estado_visual_actividad(actividad),
        "evidencia": actividad.evidencia or "",
        "semanas_activas": actividad.semanas_activas or [],
    }
