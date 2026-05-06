import re

from django.db import connection


class CrudValidationError(Exception):
    pass


def ejecutar_select_seguro(query):
    query = query.strip()
    if not query:
        raise CrudValidationError("La consulta está vacía.")

    primera_palabra = re.split(r"\s+", query)[0].upper()
    if primera_palabra != "SELECT":
        raise PermissionError("Solo se permiten consultas SELECT.")

    peligrosas = r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|REPLACE|ATTACH|DETACH|PRAGMA)\b"
    if re.search(peligrosas, query, re.IGNORECASE):
        raise PermissionError("La consulta contiene operaciones no permitidas.")

    with connection.cursor() as cursor:
        cursor.execute(query)
        columnas = [desc[0] for desc in cursor.description]
        filas = cursor.fetchmany(500)

    return {
        "columnas": columnas,
        "filas": [list(fila) for fila in filas],
        "total": len(filas),
    }


def actualizar_objeto(obj, campos, body):
    for campo in campos:
        nombre = campo["name"]
        if nombre in body:
            setattr(obj, nombre, body[nombre] or None)
    obj.save()
    return obj


def crear_objeto(cfg, body):
    kwargs = {}
    for campo in cfg["campos"]:
        nombre = campo["name"]
        kwargs[nombre] = body.get(nombre) or None
    return cfg["modelo"].objects.create(**kwargs)
