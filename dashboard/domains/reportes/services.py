from dashboard.models import ReporteSemanal


class ReporteValidationError(Exception):
    pass


def guardar_reporte_semanal(colaborador, data):
    semana = data.get("semana", "").strip()
    que_hizo = data.get("que_hizo", "").strip()

    if not semana or not que_hizo:
        raise ReporteValidationError("Semana y reporte son obligatorios")

    return ReporteSemanal.objects.update_or_create(
        colaborador=colaborador,
        semana=semana,
        defaults={
            "que_hizo": que_hizo,
            "impedimentos": data.get("impedimentos", "").strip(),
        },
    )
