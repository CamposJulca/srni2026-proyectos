from django.urls import path

from dashboard import views


urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("gerencial/", views.gerencial_view, name="gerencial"),
    path("proyectos/<int:pk>/", views.proyecto_detalle_view, name="proyecto_detalle"),
    path("consultas/", views.consultas_view, name="consultas"),
    path("crud/", views.crud_main_view, name="crud_main"),
    path("carga/", views.carga, name="carga"),
]
