from django.urls import path
from . import views

urlpatterns = [

    path('', views.dashboard, name="dashboard"),

    path("api/dashboard/",          views.dashboard_data, name="dashboard_data"),
    path("api/sql/",                views.sql_query,      name="sql_query"),

    # CRUD
    path("api/crud/meta/",              views.crud_meta,    name="crud_meta"),
    path("api/crud/<str:tabla>/",       views.crud_lista,   name="crud_lista"),
    path("api/crud/<str:tabla>/crear/", views.crud_crear,   name="crud_crear"),
    path("api/crud/<str:tabla>/<int:pk>/", views.crud_detalle, name="crud_detalle"),

    path("carga/", views.carga, name="carga"),

]