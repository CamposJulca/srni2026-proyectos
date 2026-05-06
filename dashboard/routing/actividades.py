from django.urls import path

from dashboard import views


urlpatterns = [
    path("actividades/", views.actividades_view, name="actividades"),
    path("api/actividades/", views.actividades_data, name="actividades_data"),
    path("api/actividades/crear/", views.actividad_crear, name="actividad_crear"),
    path("api/actividades/<int:pk>/", views.actividad_detalle, name="actividad_detalle"),
    path("actividades/semana/", views.semana_view, name="semana"),
    path("api/actividades/semana/", views.semana_data, name="semana_data"),
    path("actividades/resumen/", views.resumen_view, name="resumen"),
    path("api/actividades/resumen/", views.resumen_data, name="resumen_data"),
    path("mi-cronograma/", views.mi_cronograma_view, name="mi_cronograma"),
    path("api/mi-cronograma/", views.mi_cronograma_data, name="mi_cronograma_data"),
    path("api/mi-cronograma/<int:pk>/", views.mi_actividad_update, name="mi_actividad_update"),
]

