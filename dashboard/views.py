from .view_modules.actividades import (
    actividad_crear,
    actividad_detalle,
    actividades_data,
    actividades_view,
    mi_actividad_update,
    mi_cronograma_data,
    mi_cronograma_view,
    resumen_data,
    resumen_view,
    semana_data,
    semana_view,
)
from .view_modules.auth import login_view, logout_view
from .view_modules.crud import crud_crear, crud_detalle, crud_lista, crud_meta, sql_query
from .view_modules.dashboard import dashboard, dashboard_data, gerencial_data, personas_por_rol
from .view_modules.evidencias import evidencia_eliminar, evidencia_subir, evidencias_lista
from .view_modules.importacion import carga
from .view_modules.pages import crud_main_view, consultas_view, gerencial_view, home
from .view_modules.reportes import reporte_semanal_data, reporte_semanal_guardar, reportes_admin
