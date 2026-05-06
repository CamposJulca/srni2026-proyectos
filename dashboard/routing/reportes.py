from django.urls import path

from dashboard import views


urlpatterns = [
    path("api/reporte-semanal/", views.reporte_semanal_data, name="reporte_semanal_data"),
    path("api/reporte-semanal/guardar/", views.reporte_semanal_guardar, name="reporte_semanal_guardar"),
    path("api/reportes-admin/", views.reportes_admin, name="reportes_admin"),
]

