import re
from datetime import date


def resolver_periodo(periodo_texto):
    if not periodo_texto:
        hoy = date.today()
        return date(hoy.year, hoy.month, 1)

    match = re.match(r"^(\d{4})-(\d{2})$", periodo_texto)
    if not match:
        return None

    year = int(match.group(1))
    month = int(match.group(2))
    if not 1 <= month <= 12:
        return None

    return date(year, month, 1)


def clasificar_cruce_cobro(cuenta, cumplimiento_pct, cobro_pct):
    if not cuenta:
        return "sin_cuenta"
    if cuenta.estado == "rechazada":
        return "rechazada"
    if cobro_pct <= (cumplimiento_pct + 5):
        return "alineado"
    if cobro_pct <= (cumplimiento_pct + 20):
        return "alerta"
    return "desalineado"
