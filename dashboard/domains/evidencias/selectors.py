from dashboard.models import Actividad, EvidenciaActividad


def actividad_por_pk(pk):
    return Actividad.objects.get(pk=pk)


def actividad_con_colaborador(pk):
    return Actividad.objects.select_related("obligacion__colaborador").get(pk=pk)


def evidencia_con_actividad(pk):
    return EvidenciaActividad.objects.select_related(
        "actividad__obligacion__colaborador"
    ).get(pk=pk)
