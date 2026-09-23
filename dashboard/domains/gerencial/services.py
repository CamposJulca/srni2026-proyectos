from calendar import monthrange
from datetime import date

from django.db.models import Avg, Count, Q

from dashboard.domains.gerencial.selectors import (
    colaboradores_por_procedimiento_stats,
    gerencial_base_stats,
    modulos_por_proyecto,
    total_modulos,
    total_proyectos,
)
from dashboard.domains.gerencial.serializers import por_procedimiento_dict
from dashboard.domains.gerencial.utils import clasificar_cruce_cobro
from dashboard.models import Actividad, AlertaProyecto, CuentaCobro, EvidenciaActividad, Proyecto, RiesgoProyecto


MESES = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]


def compromisos_por_mes(year=None, proyecto_id=None):
    year = year or date.today().year
    qs = Actividad.objects.filter(fecha_fin__year=year)
    if proyecto_id:
        qs = qs.filter(proyecto_id=proyecto_id)

    filas = qs.values("fecha_fin__month").annotate(
        total=Count("id"),
        completadas=Count("id", filter=Q(estado="completada")),
        bloqueadas=Count("id", filter=Q(estado="bloqueada")),
    )
    por_mes = {fila["fecha_fin__month"]: fila for fila in filas}
    return [
        {
            "mes": MESES[mes - 1],
            "total": int(por_mes.get(mes, {}).get("total") or 0),
            "completadas": int(por_mes.get(mes, {}).get("completadas") or 0),
            "bloqueadas": int(por_mes.get(mes, {}).get("bloqueadas") or 0),
        }
        for mes in range(1, 13)
    ]


def _semaforo_proyecto(proyecto, vencidas, bloqueadas, cumplimiento):
    if proyecto.estado in ("bloqueado", "cancelado") or bloqueadas or vencidas > 2:
        return "rojo"
    if proyecto.estado == "en_riesgo" or vencidas or cumplimiento < 70:
        return "amarillo"
    return "verde"


def resumenes_proyecto(periodo=None):
    hoy = date.today()
    periodo = periodo or hoy.replace(day=1)
    periodo_fin = date(periodo.year, periodo.month, monthrange(periodo.year, periodo.month)[1])

    resumenes = []
    proyectos = Proyecto.objects.select_related("responsable", "procedimiento").prefetch_related("modulos")
    for proyecto in proyectos:
        actividades = Actividad.objects.filter(proyecto=proyecto)
        actividades_mes = actividades.filter(fecha_inicio__lte=periodo_fin, fecha_fin__gte=periodo)
        total_mes = actividades_mes.count()
        completadas_mes = actividades_mes.filter(estado="completada").count()
        avance = actividades.aggregate(avance=Avg("progreso"))["avance"] or 0
        vencidas = actividades.filter(fecha_fin__lt=hoy).exclude(estado="completada").count()
        bloqueadas = actividades.filter(estado="bloqueada").count()
        personas = proyecto.modulos.values("asignaciones__colaborador_id").exclude(
            asignaciones__colaborador_id__isnull=True
        ).distinct().count()
        modulos_activos = proyecto.modulos.count()
        cumplimiento = round(completadas_mes * 100 / total_mes, 1) if total_mes else 0.0
        resumenes.append({
            "id": proyecto.id,
            "nombre": proyecto.nombre,
            "estado": proyecto.estado,
            "prioridad": proyecto.prioridad,
            "responsable": proyecto.responsable.nombre if proyecto.responsable else None,
            "procedimiento": proyecto.procedimiento.nombre if proyecto.procedimiento else None,
            "fecha_inicio": proyecto.fecha_inicio.isoformat() if proyecto.fecha_inicio else None,
            "fecha_fin": proyecto.fecha_fin.isoformat() if proyecto.fecha_fin else None,
            "presupuesto": float(proyecto.presupuesto or 0),
            "avance_promedio": round(float(avance), 1),
            "actividades_vencidas": vencidas,
            "actividades_bloqueadas": bloqueadas,
            "personas_asignadas": personas,
            "modulos_activos": modulos_activos,
            "cumplimiento_mes": cumplimiento,
            "semaforo": _semaforo_proyecto(proyecto, vencidas, bloqueadas, cumplimiento),
        })
    return resumenes


def carga_trabajo_colaboradores(colaboradores_ids):
    hoy = date.today()
    filas = (
        Actividad.objects
        .filter(obligacion__colaborador_id__in=colaboradores_ids)
        .values("obligacion__colaborador_id", "obligacion__colaborador__nombre")
        .annotate(
            actividades_activas=Count("id", filter=Q(estado__in=["pendiente", "en_curso"])),
            bloqueadas=Count("id", filter=Q(estado="bloqueada")),
            vencidas=Count("id", filter=Q(fecha_fin__lt=hoy) & ~Q(estado="completada")),
            avance_promedio=Avg("progreso"),
        )
    )
    data = []
    for fila in filas:
        avance = float(fila["avance_promedio"] or 0)
        data.append({
            "colaborador_id": fila["obligacion__colaborador_id"],
            "colaborador": fila["obligacion__colaborador__nombre"],
            "actividades_activas": int(fila["actividades_activas"] or 0),
            "bloqueadas": int(fila["bloqueadas"] or 0),
            "vencidas": int(fila["vencidas"] or 0),
            "avance_pendiente_pct": round(100 - avance, 1),
        })
    return data


def gerencial_payload():
    return {
        "kpis": gerencial_base_stats(date.today()),
        "por_procedimiento": [
            por_procedimiento_dict(row)
            for row in colaboradores_por_procedimiento_stats()
        ],
        "compromisos_mes": compromisos_por_mes(),
        "proyectos": resumenes_proyecto(),
    }


def dashboard_payload(asignaciones, colaboradores_qs, periodo, proyecto=""):
    ultimo_dia = monthrange(periodo.year, periodo.month)[1]
    periodo_fin = date(periodo.year, periodo.month, ultimo_dia)

    kpis = {
        "proyectos": total_proyectos(),
        "modulos": total_modulos(),
        "personas": colaboradores_qs.count(),
        "asignaciones": asignaciones.count(),
    }

    proyectos_persona = (
        asignaciones
        .values("colaborador__nombre")
        .annotate(total=Count("modulo__proyecto", distinct=True))
    )
    roles_persona = (
        asignaciones
        .values("rol__nombre")
        .annotate(total=Count("colaborador", distinct=True))
    )
    modulos_proyecto = modulos_por_proyecto(asignaciones)

    colaboradores = list(colaboradores_qs.order_by("nombre"))
    colaboradores_ids = [colaborador.id for colaborador in colaboradores]

    cuentas_qs = CuentaCobro.objects.filter(
        colaborador_id__in=colaboradores_ids,
        periodo=periodo,
    )
    cuentas_map = {cuenta.colaborador_id: cuenta for cuenta in cuentas_qs}

    actividades_qs = Actividad.objects.filter(
        obligacion__colaborador_id__in=colaboradores_ids,
        fecha_inicio__lte=periodo_fin,
        fecha_fin__gte=periodo,
    )
    if proyecto:
        actividades_qs = actividades_qs.filter(proyecto_id=proyecto)

    actividad_por_colab = {
        row["obligacion__colaborador_id"]: row
        for row in actividades_qs.values("obligacion__colaborador_id").annotate(
            total=Count("id"),
            completadas=Count("id", filter=Q(estado="completada")),
            avance=Avg("progreso"),
        )
    }

    cruce_cobro = []
    total_actividades_periodo = 0
    total_completadas_periodo = 0
    suma_avance_ponderado = 0.0

    for colaborador in colaboradores:
        resumen = actividad_por_colab.get(colaborador.id, {})
        total = int(resumen.get("total") or 0)
        completadas = int(resumen.get("completadas") or 0)
        avance = round(float(resumen.get("avance") or 0.0), 1)

        cumplimiento = round((completadas * 100 / total), 1) if total else 0.0
        cuenta = cuentas_map.get(colaborador.id)
        valor_cobrado = float(cuenta.valor_cobrado) if cuenta else 0.0
        honorarios = float(colaborador.honorarios or 0.0)
        cobro_pct = round((valor_cobrado * 100 / honorarios), 1) if honorarios > 0 else 0.0

        total_actividades_periodo += total
        total_completadas_periodo += completadas
        suma_avance_ponderado += avance * total

        cruce_cobro.append({
            "colaborador_id": colaborador.id,
            "colaborador": colaborador.nombre,
            "periodo": periodo.isoformat(),
            "actividades_periodo": total,
            "actividades_completadas": completadas,
            "avance_pct": avance,
            "cumplimiento_pct": cumplimiento,
            "honorarios_mensuales": honorarios,
            "valor_cobrado": valor_cobrado,
            "cobro_pct": cobro_pct,
            "brecha_cumplimiento_cobro": round(cumplimiento - cobro_pct, 1),
            "estado_cuenta": cuenta.estado if cuenta else "sin_registro",
            "numero_cuenta": cuenta.numero_cuenta if cuenta else None,
            "estado_cruce": clasificar_cruce_cobro(cuenta, cumplimiento, cobro_pct),
        })

    kpis["cuentas_periodo"] = len(cuentas_map)
    kpis["avance_periodo"] = (
        round(suma_avance_ponderado / total_actividades_periodo, 1)
        if total_actividades_periodo else 0.0
    )
    kpis["cumplimiento_periodo"] = (
        round(total_completadas_periodo * 100 / total_actividades_periodo, 1)
        if total_actividades_periodo else 0.0
    )

    return {
        "kpis": kpis,
        "proyectos_persona": list(proyectos_persona),
        "roles_persona": list(roles_persona),
        "modulos_proyecto": list(modulos_proyecto),
        "compromisos_mes": compromisos_por_mes(periodo.year, proyecto or None),
        "proyectos": resumenes_proyecto(periodo),
        "carga_trabajo": carga_trabajo_colaboradores(colaboradores_ids),
        "periodo_cobro": periodo.strftime("%Y-%m"),
        "cruce_cobro": cruce_cobro,
    }


def proyecto_detalle_payload(proyecto_id):
    proyecto = Proyecto.objects.select_related("responsable", "procedimiento").get(pk=proyecto_id)
    actividades = Actividad.objects.filter(proyecto=proyecto).select_related(
        "obligacion",
        "obligacion__colaborador",
    )
    modulos = proyecto.modulos.prefetch_related("asignaciones__colaborador", "asignaciones__rol")
    colaboradores_ids = list(
        modulos.values_list("asignaciones__colaborador_id", flat=True)
        .exclude(asignaciones__colaborador_id__isnull=True)
        .distinct()
    )
    resumen = next((item for item in resumenes_proyecto() if item["id"] == proyecto.id), None)

    equipo = []
    for modulo in modulos:
        for asignacion in modulo.asignaciones.all():
            equipo.append({
                "colaborador_id": asignacion.colaborador_id,
                "colaborador": asignacion.colaborador.nombre,
                "rol": asignacion.rol.nombre,
                "modulo": modulo.nombre,
            })

    cuentas = CuentaCobro.objects.filter(colaborador_id__in=colaboradores_ids).select_related("colaborador")[:50]
    evidencias = EvidenciaActividad.objects.filter(actividad__proyecto=proyecto).select_related(
        "actividad",
        "creado_por",
    )[:50]

    return {
        "proyecto": {
            "id": proyecto.id,
            "nombre": proyecto.nombre,
            "objetivo": proyecto.objetivo,
            "estado": proyecto.estado,
            "prioridad": proyecto.prioridad,
            "fecha_inicio": proyecto.fecha_inicio.isoformat() if proyecto.fecha_inicio else None,
            "fecha_fin": proyecto.fecha_fin.isoformat() if proyecto.fecha_fin else None,
            "responsable": proyecto.responsable.nombre if proyecto.responsable else None,
            "procedimiento": proyecto.procedimiento.nombre if proyecto.procedimiento else None,
            "presupuesto": float(proyecto.presupuesto or 0),
            "observaciones": proyecto.observaciones,
        },
        "resumen": resumen,
        "modulos": [
            {
                "id": modulo.id,
                "nombre": modulo.nombre,
                "referente": modulo.referente,
                "asignaciones": modulo.asignaciones.count(),
            }
            for modulo in modulos
        ],
        "equipo": equipo,
        "cronograma": [
            {
                "id": actividad.id,
                "actividad_id": actividad.actividad_id,
                "descripcion": actividad.descripcion,
                "colaborador": actividad.obligacion.colaborador.nombre,
                "fecha_inicio": actividad.fecha_inicio.isoformat(),
                "fecha_fin": actividad.fecha_fin.isoformat(),
                "estado": actividad.estado,
                "progreso": actividad.progreso,
            }
            for actividad in actividades.order_by("fecha_inicio", "orden")
        ],
        "actividades_vencidas": [
            actividad.id
            for actividad in actividades.filter(fecha_fin__lt=date.today()).exclude(estado="completada")
        ],
        "actividades_bloqueadas": [
            actividad.id
            for actividad in actividades.filter(estado="bloqueada")
        ],
        "riesgos": [
            {
                "id": riesgo.id,
                "riesgo": riesgo.riesgo,
                "impacto": riesgo.impacto,
                "probabilidad": riesgo.probabilidad,
                "responsable": riesgo.responsable.nombre if riesgo.responsable else None,
                "fecha_limite": riesgo.fecha_limite.isoformat() if riesgo.fecha_limite else None,
                "estado": riesgo.estado,
                "plan_mitigacion": riesgo.plan_mitigacion,
            }
            for riesgo in RiesgoProyecto.objects.filter(proyecto=proyecto)
        ],
        "alertas": [
            {
                "id": alerta.id,
                "alerta": alerta.alerta,
                "severidad": alerta.severidad,
                "responsable": alerta.responsable.nombre if alerta.responsable else None,
                "fecha_limite": alerta.fecha_limite.isoformat() if alerta.fecha_limite else None,
                "estado": alerta.estado,
                "plan_accion": alerta.plan_accion,
            }
            for alerta in AlertaProyecto.objects.filter(proyecto=proyecto)
        ],
        "cuentas_cobro": [
            {
                "colaborador": cuenta.colaborador.nombre,
                "periodo": cuenta.periodo.isoformat(),
                "numero_cuenta": cuenta.numero_cuenta,
                "valor_cobrado": float(cuenta.valor_cobrado),
                "estado": cuenta.estado,
            }
            for cuenta in cuentas
        ],
        "evidencias": [
            {
                "actividad_id": evidencia.actividad_id,
                "actividad": evidencia.actividad.actividad_id,
                "nombre": evidencia.nombre_archivo,
                "comentario": evidencia.comentario,
                "creado_en": evidencia.creado_en.isoformat(),
                "creado_por": evidencia.creado_por.username if evidencia.creado_por else None,
            }
            for evidencia in evidencias
        ],
        "compromisos_mes": compromisos_por_mes(proyecto_id=proyecto.id),
        "historial": [
            {
                "creado_en": item.creado_en.isoformat(),
                "cambios": item.cambios,
            }
            for item in proyecto.historial.all()[:30]
        ],
    }
