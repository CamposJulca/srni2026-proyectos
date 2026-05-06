from dashboard.models import ReporteSemanal


def reportes_por_colaborador(colaborador, semana=""):
    qs = ReporteSemanal.objects.filter(colaborador=colaborador)
    if semana:
        qs = qs.filter(semana=semana)
    return qs


def reportes_admin_qs(semana=""):
    qs = ReporteSemanal.objects.select_related("colaborador").all()
    if semana:
        qs = qs.filter(semana=semana)
    return qs
