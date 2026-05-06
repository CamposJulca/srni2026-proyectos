from datetime import date

from dashboard.constants import SEMANA_FECHAS, SEMANAS_ORDENADAS


def semana_actual():
    """Devuelve la etiqueta de la semana del calendario que contiene hoy."""
    hoy = date.today()
    for sem, (ini, fin) in SEMANA_FECHAS.items():
        if date.fromisoformat(ini) <= hoy <= date.fromisoformat(fin):
            return sem

    for sem in SEMANAS_ORDENADAS:
        ini, _ = SEMANA_FECHAS[sem]
        if date.fromisoformat(ini) >= hoy:
            return sem
    return SEMANAS_ORDENADAS[-1]


def estado_visual_actividad(actividad, hoy=None):
    hoy = hoy or date.today()
    estado_visual = actividad.estado
    if actividad.estado == "pendiente":
        if actividad.fecha_fin < hoy:
            estado_visual = "vencida"
        elif actividad.fecha_inicio <= hoy <= actividad.fecha_fin:
            estado_visual = "en_curso"
    return estado_visual
