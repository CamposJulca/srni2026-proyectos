"""Orquestador del payload de la Vista Gerencial de Contratación."""
from datetime import date

from dashboard.domains.contratacion.selectors import (
    avance_fisico_por_colaborador,
    contratos_por_vencer,
    contratos_unidad,
    kpis_contratacion,
    pagos_pendientes_mes,
    por_equipo,
    por_estado,
    ss_atrasada,
    ultimo_mes_pagos,
)
from dashboard.domains.contratacion.serializers import (
    contrato_vencer_dict,
    equipo_dict,
    pago_pendiente_dict,
)
from dashboard.domains.contratacion.utils import clasificar_cruce_fisico_financiero

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


def _cruce_fisico_financiero():
    avance_map = avance_fisico_por_colaborador()
    cruce = []
    contratos = (
        contratos_unidad()
        .filter(estado="ejecucion")
        .select_related("colaborador")
    )
    for contrato in contratos:
        financiero = round(float(contrato.porcentaje_ejecucion or 0), 1)
        fisico = avance_map.get(contrato.colaborador_id)
        estado = clasificar_cruce_fisico_financiero(fisico, financiero)
        cruce.append({
            "numero_contrato": contrato.numero_contrato,
            "contratista": contrato.nombre_contratista,
            "equipo": contrato.equipo,
            "avance_fisico": round(fisico, 1) if fisico is not None else None,
            "avance_financiero": financiero,
            "brecha": round(financiero - fisico, 1) if fisico is not None else None,
            "estado_cruce": estado,
        })
    # Primero los más desalineados.
    orden = {"desalineado": 0, "alerta": 1, "alineado": 2, "sin_datos": 3}
    cruce.sort(key=lambda x: (orden.get(x["estado_cruce"], 9), -(x["brecha"] or -999)))
    return cruce


def contratacion_payload(hoy=None):
    hoy = hoy or date.today()

    # El slot de referencia de pagos es data-driven: el último mes con pagos cargados
    # (no el mes calendario, que puede ir por delante del Excel).
    mes_pagos = ultimo_mes_pagos() or hoy.month

    vencer = contratos_por_vencer(hoy)
    pendientes_pago = pagos_pendientes_mes(mes_pagos)

    return {
        "periodo": {
            "mes": hoy.month,
            "mes_nombre": MESES[hoy.month - 1],
            "anio": hoy.year,
            "mes_pagos": mes_pagos,
            "mes_pagos_nombre": MESES[mes_pagos - 1],
        },
        "kpis": kpis_contratacion(),
        "por_estado": por_estado(),
        "por_equipo": [equipo_dict(row) for row in por_equipo()],
        "por_vencer": [contrato_vencer_dict(c, hoy) for c in vencer],
        "semaforo_ss": ss_atrasada(),
        "semaforo_pagos": [pago_pendiente_dict(p) for p in pendientes_pago],
        "cruce_fisico_financiero": _cruce_fisico_financiero(),
    }
