def evidencia_dict(evidencia):
    return {
        "id": evidencia.pk,
        "archivo_url": evidencia.archivo.url if evidencia.archivo else "",
        "nombre": evidencia.nombre_archivo,
        "comentario": evidencia.comentario,
        "creado_por": evidencia.creado_por.username if evidencia.creado_por else "",
        "creado_en": evidencia.creado_en.strftime("%d/%m/%Y %H:%M") if evidencia.creado_en else "",
    }


def evidencia_creada_dict(evidencia):
    return {
        "ok": True,
        "id": evidencia.pk,
        "nombre": evidencia.nombre_archivo,
        "archivo_url": evidencia.archivo.url,
    }
