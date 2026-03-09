from django.urls import path
from . import views

urlpatterns = [

    path('', views.dashboard, name="dashboard"),

    path(
        "api/dashboard/",
        views.dashboard_data,
        name="dashboard_data"
    ),

    path(
        "api/sql/",
        views.sql_query,
        name="sql_query"
    ),

    path(
        "carga/",
        views.carga,
        name="carga"
    ),

]