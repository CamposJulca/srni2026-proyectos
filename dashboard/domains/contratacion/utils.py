"""Utilidades del dominio contratación."""


def clasificar_cruce_fisico_financiero(avance_fisico, avance_financiero):
    """
    Clasifica la relación entre avance físico (actividades) y financiero (% ejecución
    del contrato). Se alerta cuando lo financiero se adelanta a lo físico —es decir,
    cuando se paga más de lo que se ha ejecutado en obra—. Sigue el patrón de
    `gerencial/utils.py::clasificar_cruce_cobro`.

    Ambos valores en escala 0–100.
    """
    if avance_fisico is None:
        return "sin_datos"
    brecha = float(avance_financiero or 0) - float(avance_fisico or 0)
    if brecha <= 5:
        return "alineado"
    if brecha <= 20:
        return "alerta"
    return "desalineado"
