from dashboard.models import EvidenciaActividad
from dashboard.permisos import _es_admin


MAX_EVIDENCIA_BYTES = 10 * 1024 * 1024


class EvidenciaValidationError(Exception):
    pass


class EvidenciaPermissionError(Exception):
    pass


def puede_gestionar_evidencia(user, actividad):
    perfil = getattr(user, "perfil", None)
    es_dueno = perfil and perfil.colaborador_id == actividad.obligacion.colaborador_id
    return bool(es_dueno or _es_admin(user))


def subir_evidencia(user, actividad, archivo, comentario=""):
    if not puede_gestionar_evidencia(user, actividad):
        raise EvidenciaPermissionError("No autorizado")

    if not archivo:
        raise EvidenciaValidationError("No se recibio archivo")

    if archivo.size > MAX_EVIDENCIA_BYTES:
        raise EvidenciaValidationError("El archivo no puede superar 10MB")

    return EvidenciaActividad.objects.create(
        actividad=actividad,
        archivo=archivo,
        comentario=comentario.strip(),
        creado_por=user,
    )


def eliminar_evidencia(user, evidencia):
    if evidencia.creado_por_id != user.pk and not _es_admin(user):
        raise EvidenciaPermissionError("No autorizado")

    evidencia.archivo.delete(save=False)
    evidencia.delete()
