from django.db.models import Q


def aplicar_filtros(tabla, cfg, request_get):
    qs = cfg["modelo"].objects.all()

    proc = request_get.get("proc", "").strip()
    if proc and tabla == "colaborador":
        qs = qs.filter(procedimiento__nombre=proc)

    colab_id = request_get.get("colaborador", "").strip()
    if colab_id:
        if tabla == "obligacion":
            qs = qs.filter(colaborador_id=colab_id)
        elif tabla == "actividad":
            qs = qs.filter(obligacion__colaborador_id=colab_id)
        elif tabla == "cuenta_cobro":
            qs = qs.filter(colaborador_id=colab_id)

    q = request_get.get("q", "").strip()
    if q and cfg["buscar_en"]:
        filtro = Q()
        for campo in cfg["buscar_en"]:
            filtro |= Q(**{f"{campo}__icontains": q})
        qs = qs.filter(filtro)

    return aplicar_select_related(tabla, qs)


def aplicar_select_related(tabla, qs):
    if tabla == "modulo":
        return qs.select_related("proyecto")
    if tabla == "asignacion":
        return qs.select_related("colaborador", "rol", "modulo", "modulo__proyecto")
    if tabla == "colaborador":
        return qs.select_related("procedimiento")
    if tabla == "obligacion":
        return qs.select_related("colaborador")
    if tabla == "actividad":
        return qs.select_related("obligacion", "obligacion__colaborador")
    if tabla == "cuenta_cobro":
        return qs.select_related("colaborador")
    return qs


def obtener_objeto(cfg, pk):
    return cfg["modelo"].objects.get(pk=pk)
