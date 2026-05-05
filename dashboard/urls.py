from django.urls import path
from . import views

urlpatterns = [

    # Autenticación
    path('login/',  views.login_view,  name="login"),
    path('logout/', views.logout_view, name="logout"),

    # Páginas
    path('',            views.home,            name="home"),
    path('dashboard/',  views.dashboard,       name="dashboard"),
    path('gerencial/',  views.gerencial_view,  name="gerencial"),
    path('consultas/',  views.consultas_view,  name="consultas"),
    path('crud/',       views.crud_main_view,  name="crud_main"),

    # APIs
    path("api/dashboard/",                    views.dashboard_data,     name="dashboard_data"),
    path("api/dashboard/personas-por-rol/",   views.personas_por_rol,   name="personas_por_rol"),
    path("api/gerencial/",                    views.gerencial_data,  name="gerencial_data"),
    path("api/sql/",                          views.sql_query,      name="sql_query"),
    path("api/crud/meta/",                    views.crud_meta,      name="crud_meta"),
    path("api/crud/<str:tabla>/",             views.crud_lista,     name="crud_lista"),
    path("api/crud/<str:tabla>/crear/",       views.crud_crear,     name="crud_crear"),
    path("api/crud/<str:tabla>/<int:pk>/",    views.crud_detalle,   name="crud_detalle"),

    path("carga/", views.carga, name="carga"),

    # Actividades / Gantt
    path("actividades/",              views.actividades_view,    name="actividades"),
    path("api/actividades/",          views.actividades_data,    name="actividades_data"),
    path("api/actividades/crear/",    views.actividad_crear,     name="actividad_crear"),
    path("api/actividades/<int:pk>/", views.actividad_detalle,   name="actividad_detalle"),

    # Vista Semanal
    path("actividades/semana/",       views.semana_view,         name="semana"),
    path("api/actividades/semana/",   views.semana_data,         name="semana_data"),

    # Vista Resumen General (subdirector)
    path("actividades/resumen/",      views.resumen_view,        name="resumen"),
    path("api/actividades/resumen/",  views.resumen_data,        name="resumen_data"),

    # Mi Cronograma (self-service colaborador)
    path("mi-cronograma/",              views.mi_cronograma_view,   name="mi_cronograma"),
    path("api/mi-cronograma/",          views.mi_cronograma_data,   name="mi_cronograma_data"),
    path("api/mi-cronograma/<int:pk>/", views.mi_actividad_update,  name="mi_actividad_update"),

    # Evidencias (upload de archivos)
    path("api/evidencias/<int:actividad_pk>/",        views.evidencias_lista,     name="evidencias_lista"),
    path("api/evidencias/<int:actividad_pk>/subir/",  views.evidencia_subir,      name="evidencia_subir"),
    path("api/evidencias/eliminar/<int:pk>/",         views.evidencia_eliminar,   name="evidencia_eliminar"),

    # Reportes semanales
    path("api/reporte-semanal/",        views.reporte_semanal_data,     name="reporte_semanal_data"),
    path("api/reporte-semanal/guardar/", views.reporte_semanal_guardar, name="reporte_semanal_guardar"),
    path("api/reportes-admin/",         views.reportes_admin,           name="reportes_admin"),

]
