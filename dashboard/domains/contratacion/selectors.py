"""Consultas agregadas sobre la capa de contratación."""
from datetime import timedelta

from django.db.models import Avg, Count, Max, Q, Sum

from dashboard.models import Contrato, PagoContrato, SeguridadSocialContrato


def contratos_unidad():
    """Maestro de contratos vigentes (modalidad 'unidad' = estado actual)."""
    return Contrato.objects.filter(modalidad="unidad")


def kpis_contratacion():
    qs = contratos_unidad()
    agg = qs.aggregate(
        valor_total=Sum("valor_total_contrato"),
        valor_cancelado=Sum("valor_cancelado"),
        saldo=Sum("saldo_contrato"),
        ejec_promedio=Avg("porcentaje_ejecucion"),
    )
    total = agg["valor_total"] or 0
    cancelado = agg["valor_cancelado"] or 0
    return {
        "total_contratos": qs.count(),
        "en_ejecucion": qs.filter(estado="ejecucion").count(),
        "cesion": qs.filter(estado="cesion").count(),
        "terminados": qs.filter(estado="terminado").count(),
        "valor_total": float(total),
        "valor_cancelado": float(cancelado),
        "saldo": float(agg["saldo"] or 0),
        "ejec_promedio": round(float(agg["ejec_promedio"] or 0), 1),
        "ejec_financiera_global": round(float(cancelado) * 100 / float(total), 1) if total else 0.0,
    }


def por_estado():
    return list(
        contratos_unidad()
        .values("estado")
        .annotate(total=Count("id"))
        .order_by("-total")
    )


def por_equipo():
    return list(
        contratos_unidad()
        .values("equipo")
        .annotate(
            contratos=Count("id"),
            valor_total=Sum("valor_total_contrato"),
            valor_cancelado=Sum("valor_cancelado"),
            saldo=Sum("saldo_contrato"),
        )
        .order_by("-valor_total")
    )


def contratos_por_vencer(hoy, dias=45):
    limite = hoy + timedelta(days=dias)
    return (
        contratos_unidad()
        .filter(
            estado="ejecucion",
            fecha_terminacion__isnull=False,
            fecha_terminacion__gte=hoy,
            fecha_terminacion__lte=limite,
        )
        .order_by("fecha_terminacion")
    )


def ultimo_mes_pagos():
    """Último slot mensual con algún pago registrado (proxy del periodo vigente)."""
    return (
        PagoContrato.objects
        .filter(contrato__modalidad="unidad", valor__isnull=False)
        .aggregate(m=Max("mes"))["m"]
    )


def ultimo_mes_ss():
    """Último slot mensual con seguridad social registrada."""
    return (
        SeguridadSocialContrato.objects
        .filter(contrato__modalidad="unidad")
        .exclude(codigo__isnull=True)
        .exclude(codigo="")
        .aggregate(m=Max("mes"))["m"]
    )


def pagos_pendientes_mes(mes):
    """Contratos en ejecución cuyo pago del mes indicado está pendiente en SECOP II."""
    return (
        PagoContrato.objects
        .filter(mes=mes, estado_secop="pendiente", contrato__modalidad="unidad",
                contrato__estado="ejecucion")
        .select_related("contrato")
        .order_by("contrato__equipo", "contrato__nombre_contratista")
    )


def ss_atrasada(rezago_permitido=1):
    """
    Contratos en ejecución cuya seguridad social va atrasada: tienen menos planillas
    aprobadas que meses efectivamente pagados (se permite `rezago_permitido` meses de
    rezago natural, porque la planilla suele pagarse el mes siguiente).
    """
    ss_ok = Q(seguridad_social__codigo__isnull=False) & ~Q(seguridad_social__codigo="")
    qs = (
        contratos_unidad()
        .filter(estado="ejecucion")
        .annotate(
            n_ss=Count("seguridad_social", filter=ss_ok, distinct=True),
            n_pagados=Count("pagos", filter=Q(pagos__estado_secop="pagado"), distinct=True),
        )
    )
    atrasados = []
    for contrato in qs:
        faltantes = contrato.n_pagados - rezago_permitido - contrato.n_ss
        if faltantes > 0:
            atrasados.append({
                "numero_contrato": contrato.numero_contrato,
                "contratista": contrato.nombre_contratista,
                "equipo": contrato.equipo,
                "planillas": contrato.n_ss,
                "meses_pagados": contrato.n_pagados,
                "faltantes": faltantes,
            })
    atrasados.sort(key=lambda x: -x["faltantes"])
    return atrasados


def avance_fisico_por_colaborador():
    """{colaborador_id: avance_promedio} desde las actividades (avance físico)."""
    from dashboard.models import Actividad

    filas = (
        Actividad.objects
        .exclude(obligacion__colaborador_id__isnull=True)
        .values("obligacion__colaborador_id")
        .annotate(avance=Avg("progreso"))
    )
    return {
        fila["obligacion__colaborador_id"]: float(fila["avance"] or 0)
        for fila in filas
    }
