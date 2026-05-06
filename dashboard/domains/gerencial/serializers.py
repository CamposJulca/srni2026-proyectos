def por_procedimiento_dict(row):
    return {
        "procedimiento": row["procedimiento__nombre"] or "Sin clasificar",
        "personas": row["personas"],
        "masa": float(row["masa"] or 0),
    }


def persona_por_rol_dict(asignacion):
    return {
        "persona": asignacion.colaborador.nombre,
        "modulo": asignacion.modulo.nombre,
        "proyecto": asignacion.modulo.proyecto.nombre,
    }
