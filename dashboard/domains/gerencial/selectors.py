from django.db.models import Count, Sum

from dashboard.models import Asignacion, Colaborador, Modulo, Proyecto, Rol


def colaboradores_dashboard(procedimiento=""):
    if procedimiento:
        return Colaborador.objects.filter(
            procedimiento__nombre=procedimiento
        ).order_by("nombre")
    return Colaborador.objects.all().order_by("nombre")


def roles_dashboard():
    return Rol.objects.all()


def proyectos_dashboard():
    return Proyecto.objects.all()


def asignaciones_filtradas(persona="", rol="", proyecto="", procedimiento=""):
    qs = Asignacion.objects.select_related(
        "colaborador",
        "rol",
        "modulo",
        "modulo__proyecto",
    )
    if procedimiento:
        qs = qs.filter(colaborador__procedimiento__nombre=procedimiento)
    if persona:
        qs = qs.filter(colaborador_id=persona)
    if rol:
        qs = qs.filter(rol_id=rol)
    if proyecto:
        qs = qs.filter(modulo__proyecto_id=proyecto)
    return qs


def colaboradores_filtrados(persona="", rol="", proyecto="", procedimiento=""):
    qs = Colaborador.objects.all()
    if procedimiento:
        qs = qs.filter(procedimiento__nombre=procedimiento)
    if persona:
        qs = qs.filter(pk=persona)
    if rol:
        qs = qs.filter(asignaciones__rol_id=rol)
    if proyecto:
        qs = qs.filter(asignaciones__modulo__proyecto_id=proyecto)
    return qs.distinct()


def gerencial_base_stats(hoy):
    masa = (
        Colaborador.objects
        .filter(honorarios__isnull=False)
        .aggregate(t=Sum("honorarios"))["t"]
        or 0
    )
    return {
        "total": Colaborador.objects.count(),
        "masa": float(masa),
        "vigentes": Colaborador.objects.filter(
            fecha_fin__isnull=False,
            fecha_fin__gte=hoy,
        ).count(),
        "vencidos": Colaborador.objects.filter(
            fecha_fin__isnull=False,
            fecha_fin__lt=hoy,
        ).count(),
        "sin_fecha": Colaborador.objects.filter(fecha_fin__isnull=True).count(),
    }


def colaboradores_por_procedimiento_stats():
    return list(
        Colaborador.objects
        .values("procedimiento__nombre")
        .annotate(personas=Count("id"), masa=Sum("honorarios"))
        .order_by("-personas")
    )


def total_proyectos():
    return Proyecto.objects.count()


def total_modulos():
    return Modulo.objects.count()


def modulos_por_proyecto(asignaciones):
    modulos_ids = asignaciones.values_list("modulo_id", flat=True)
    return (
        Modulo.objects
        .filter(id__in=modulos_ids)
        .values("proyecto__nombre")
        .annotate(total=Count("id", distinct=True))
    )
