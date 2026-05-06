from dashboard.models import Actividad, Asignacion, Colaborador, Procedimiento, Proyecto


def listar_colaboradores_nombres():
    return sorted(Colaborador.objects.values_list("nombre", flat=True).distinct())


def listar_obligaciones_descripciones():
    return list(
        Actividad.objects
        .values_list("obligacion__descripcion", flat=True)
        .distinct()
        .order_by("obligacion__descripcion")
    )


def listar_proyectos_nombres():
    return list(Proyecto.objects.values_list("nombre", flat=True).order_by("nombre"))


def listar_procedimientos_nombres():
    return list(Procedimiento.objects.values_list("nombre", flat=True).order_by("nombre"))


def colaboradores_por_procedimiento():
    agrupados = {}
    for colaborador in Colaborador.objects.select_related("procedimiento").order_by("nombre"):
        procedimiento = (
            colaborador.procedimiento.nombre
            if colaborador.procedimiento
            else "Sin procedimiento"
        )
        agrupados.setdefault(procedimiento, []).append(colaborador.nombre)
    return agrupados


def proyectos_por_colaborador():
    resultado = {}
    for asignacion in Asignacion.objects.select_related("modulo__proyecto").all():
        resultado.setdefault(asignacion.colaborador_id, set()).add(
            asignacion.modulo.proyecto.nombre
        )
    return resultado


def actividades_gantt(colaborador="", estado="", obligacion="", proyecto=""):
    qs = Actividad.objects.select_related("obligacion__colaborador", "proyecto").all()

    if colaborador:
        qs = qs.filter(obligacion__colaborador__nombre=colaborador)
    if estado:
        qs = qs.filter(estado=estado)
    if obligacion:
        qs = qs.filter(obligacion__descripcion=obligacion)
    if proyecto:
        colab_ids = Asignacion.objects.filter(
            modulo__proyecto__nombre=proyecto
        ).values_list("colaborador_id", flat=True).distinct()
        qs = qs.filter(obligacion__colaborador_id__in=colab_ids)

    return qs


def actividad_detalle_qs():
    return Actividad.objects.select_related("obligacion__colaborador", "proyecto")


def actividades_semana_qs(colaborador="", procedimiento=""):
    qs = Actividad.objects.select_related(
        "obligacion__colaborador__procedimiento"
    ).order_by("obligacion__colaborador__nombre", "orden")

    if colaborador:
        qs = qs.filter(obligacion__colaborador__nombre=colaborador)
    if procedimiento:
        qs = qs.filter(obligacion__colaborador__procedimiento__nombre=procedimiento)
    return qs


def actividades_en_semana(qs, semana):
    return [actividad for actividad in qs if semana in (actividad.semanas_activas or [])]


def nombres_colaboradores_con_actividades():
    return sorted(set(
        Actividad.objects.values_list("obligacion__colaborador__nombre", flat=True)
    ))


def actividades_resumen_qs(procedimiento=""):
    qs = Actividad.objects.select_related("obligacion__colaborador__procedimiento").all()
    if procedimiento:
        qs = qs.filter(obligacion__colaborador__procedimiento__nombre=procedimiento)
    return qs


def actividades_mi_cronograma(colaborador):
    return (
        Actividad.objects
        .filter(obligacion__colaborador=colaborador)
        .select_related("obligacion", "proyecto")
        .order_by("orden", "fecha_inicio")
    )
