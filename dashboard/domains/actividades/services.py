from dashboard.models import Actividad, Colaborador, Obligacion, Proyecto


class ActividadValidationError(Exception):
    pass


def crear_actividad(data):
    nombre_colab = data.get("colaborador", "").strip()
    desc_oblig = data.get("obligacion", "").strip()

    if not nombre_colab:
        raise ActividadValidationError("colaborador requerido")

    colaborador = Colaborador.objects.filter(nombre=nombre_colab).first()
    if not colaborador:
        raise ActividadValidationError(f'Colaborador "{nombre_colab}" no encontrado')

    obligacion, _ = Obligacion.objects.get_or_create(
        colaborador=colaborador,
        descripcion=desc_oblig,
    )

    proyecto_id = data.get("proyecto_id")
    proyecto = Proyecto.objects.filter(pk=proyecto_id).first() if proyecto_id else None

    return Actividad.objects.create(
        obligacion=obligacion,
        proyecto=proyecto,
        actividad_id=data.get("actividad_id", ""),
        descripcion=data.get("descripcion", ""),
        fecha_inicio=data["fecha_inicio"],
        fecha_fin=data["fecha_fin"],
        progreso=int(data.get("progreso", 0)),
        estado=data.get("estado", "pendiente"),
    )


def actualizar_actividad_admin(actividad, data):
    if data.get("estado") == "completada" and actividad.evidencias.count() == 0:
        raise ActividadValidationError(
            "No se puede marcar como completada sin al menos una evidencia adjunta."
        )

    for field in ("actividad_id", "descripcion", "fecha_inicio", "fecha_fin", "estado"):
        if field in data:
            setattr(actividad, field, data[field])
    if "progreso" in data:
        actividad.progreso = int(data["progreso"])
    if "evidencia" in data:
        actividad.evidencia = data["evidencia"]
    actividad.save()
    return actividad


def actualizar_actividad_colaborador(actividad, data):
    if "progreso" in data:
        actividad.progreso = max(0, min(100, int(data["progreso"])))
    if "estado" in data and data["estado"] in ("pendiente", "en_curso", "completada", "bloqueada"):
        if data["estado"] == "completada" and actividad.evidencias.count() == 0:
            raise ActividadValidationError(
                "No puedes marcar como completada sin adjuntar al menos una evidencia."
            )
        actividad.estado = data["estado"]
    if "evidencia" in data:
        actividad.evidencia = str(data["evidencia"])[:2000]
    actividad.save()
    return actividad
