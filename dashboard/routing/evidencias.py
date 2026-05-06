from django.urls import path

from dashboard import views


urlpatterns = [
    path("api/evidencias/<int:actividad_pk>/", views.evidencias_lista, name="evidencias_lista"),
    path("api/evidencias/<int:actividad_pk>/subir/", views.evidencia_subir, name="evidencia_subir"),
    path("api/evidencias/eliminar/<int:pk>/", views.evidencia_eliminar, name="evidencia_eliminar"),
]

