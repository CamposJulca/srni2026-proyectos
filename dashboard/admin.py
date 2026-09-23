from django.contrib import admin, messages

from .domains.contratacion.importador import ejecutar_importacion
from .domains.importacion.services import ImportacionValidationError
from .models import (
    Procedimiento,
    Proyecto,
    Modulo,
    Colaborador,
    Rol,
    Asignacion,
    Obligacion,
    Actividad,
    Contrato,
    ContratoImportLog,
    Convenio,
    CuentaCobro,
    PagoContrato,
    Perfil,
    EvidenciaActividad,
    ReporteSemanal,
    RiesgoProyecto,
    AlertaProyecto,
    ProyectoHistorial,
    SeguridadSocialContrato,
)

admin.site.register(Procedimiento)
admin.site.register(Proyecto)
admin.site.register(Modulo)
admin.site.register(Colaborador)
admin.site.register(Rol)
admin.site.register(Asignacion)
admin.site.register(Obligacion)
admin.site.register(Actividad)
admin.site.register(CuentaCobro)
admin.site.register(Perfil)
admin.site.register(EvidenciaActividad)
admin.site.register(ReporteSemanal)
admin.site.register(RiesgoProyecto)
admin.site.register(AlertaProyecto)
admin.site.register(ProyectoHistorial)


@admin.action(description="Sincronizar contratos desde el Excel maestro")
def sincronizar_contratos(modeladmin, request, queryset):
    try:
        resumen = ejecutar_importacion(origen="manual", usuario=request.user)
    except ImportacionValidationError as exc:
        modeladmin.message_user(request, str(exc), level=messages.ERROR)
        return
    modeladmin.message_user(
        request,
        f"Importación: {resumen['creados']} nuevos, {resumen['actualizados']} actualizados, "
        f"{resumen['sin_match_colaborador']} sin colaborador, {len(resumen['errores'])} errores.",
        level=messages.SUCCESS if not resumen["errores"] else messages.WARNING,
    )


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ("numero_contrato", "nombre_contratista", "equipo", "estado",
                    "modalidad", "porcentaje_ejecucion")
    list_filter = ("modalidad", "estado", "equipo")
    search_fields = ("numero_contrato", "nombre_contratista", "cedula")
    actions = [sincronizar_contratos]


@admin.register(ContratoImportLog)
class ContratoImportLogAdmin(admin.ModelAdmin):
    list_display = ("ejecutado_en", "origen", "creados", "actualizados",
                    "sin_match_colaborador", "ejecutado_por")
    list_filter = ("origen",)
    actions = [sincronizar_contratos]


admin.site.register(PagoContrato)
admin.site.register(SeguridadSocialContrato)
admin.site.register(Convenio)
