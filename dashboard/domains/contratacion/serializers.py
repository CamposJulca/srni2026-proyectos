"""Serialización de la capa de contratación hacia el front (sin exponer datos sensibles)."""


def equipo_dict(row):
    total = float(row["valor_total"] or 0)
    cancelado = float(row["valor_cancelado"] or 0)
    return {
        "equipo": row["equipo"] or "SIN EQUIPO",
        "contratos": row["contratos"],
        "valor_total": total,
        "valor_cancelado": cancelado,
        "saldo": float(row["saldo"] or 0),
        "ejec_pct": round(cancelado * 100 / total, 1) if total else 0.0,
    }


def contrato_vencer_dict(contrato, hoy):
    dias = (contrato.fecha_terminacion - hoy).days if contrato.fecha_terminacion else None
    return {
        "numero_contrato": contrato.numero_contrato,
        "contratista": contrato.nombre_contratista,
        "equipo": contrato.equipo,
        "fecha_terminacion": contrato.fecha_terminacion.isoformat() if contrato.fecha_terminacion else None,
        "dias_restantes": dias,
        "saldo": float(contrato.saldo_contrato or 0),
    }


def pago_pendiente_dict(pago):
    # Si el pago aún no tiene valor liquidado, se muestra el honorario mensual como referencia.
    valor = float(pago.valor) if pago.valor else float(pago.contrato.valor_honorarios or 0)
    return {
        "numero_contrato": pago.contrato.numero_contrato,
        "contratista": pago.contrato.nombre_contratista,
        "equipo": pago.contrato.equipo,
        "mes": pago.mes,
        "valor": valor,
    }
