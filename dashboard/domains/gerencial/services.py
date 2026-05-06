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
from dashboard.models import Actividad, CuentaCobro


def gerencial_payload():
    return {
        "kpis": gerencial_base_stats(date.today()),
        "por_procedimiento": [
            por_procedimiento_dict(row)
            for row in colaboradores_por_procedimiento_stats()
        ],
        "compromisos_mes": [],
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
        "compromisos_mes": [],
        "periodo_cobro": periodo.strftime("%Y-%m"),
        "cruce_cobro": cruce_cobro,
    }
