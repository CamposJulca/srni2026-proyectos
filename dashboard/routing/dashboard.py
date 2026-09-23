from django.urls import path

from dashboard import views


urlpatterns = [
    path("api/dashboard/", views.dashboard_data, name="dashboard_data"),
    path("api/dashboard/personas-por-rol/", views.personas_por_rol, name="personas_por_rol"),
    path("api/gerencial/", views.gerencial_data, name="gerencial_data"),
    path("api/gerencial/contratos/", views.contratacion_data, name="contratacion_data"),
    path("api/gerencial/contratos/sincronizar/", views.contratacion_sincronizar, name="contratacion_sincronizar"),
    path("api/proyectos/<int:pk>/", views.proyecto_detalle_data, name="proyecto_detalle_data"),
    path("api/proyectos/<int:pk>/exportar.csv", views.proyecto_exportar_csv, name="proyecto_exportar_csv"),
]
