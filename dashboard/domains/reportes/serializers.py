def reporte_colaborador_dict(reporte):
    return {
        "id": reporte.pk,
        "semana": reporte.semana,
        "que_hizo": reporte.que_hizo,
        "impedimentos": reporte.impedimentos,
        "creado_en": reporte.creado_en.strftime("%d/%m/%Y %H:%M") if reporte.creado_en else "",
        "actualizado_en": reporte.actualizado_en.strftime("%d/%m/%Y %H:%M") if reporte.actualizado_en else "",
    }


def reporte_admin_dict(reporte):
    return {
        "id": reporte.pk,
        "colaborador": reporte.colaborador.nombre,
        "semana": reporte.semana,
        "que_hizo": reporte.que_hizo,
        "impedimentos": reporte.impedimentos,
        "creado_en": reporte.creado_en.strftime("%d/%m/%Y %H:%M") if reporte.creado_en else "",
    }
