from django.urls import path

from dashboard import views


urlpatterns = [
    path("api/dashboard/", views.dashboard_data, name="dashboard_data"),
    path("api/dashboard/personas-por-rol/", views.personas_por_rol, name="personas_por_rol"),
    path("api/gerencial/", views.gerencial_data, name="gerencial_data"),
]

