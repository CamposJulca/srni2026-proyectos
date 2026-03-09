from django.urls import path
from . import views

urlpatterns = [

    # Autenticación
    path('login/',  views.login_view,  name="login"),
    path('logout/', views.logout_view, name="logout"),

    # Páginas
    path('',           views.home,           name="home"),
    path('dashboard/', views.dashboard,      name="dashboard"),
    path('consultas/', views.consultas_view, name="consultas"),
    path('crud/',      views.crud_main_view, name="crud_main"),

    # APIs
    path("api/dashboard/",                    views.dashboard_data, name="dashboard_data"),
    path("api/sql/",                          views.sql_query,      name="sql_query"),
    path("api/crud/meta/",                    views.crud_meta,      name="crud_meta"),
    path("api/crud/<str:tabla>/",             views.crud_lista,     name="crud_lista"),
    path("api/crud/<str:tabla>/crear/",       views.crud_crear,     name="crud_crear"),
    path("api/crud/<str:tabla>/<int:pk>/",    views.crud_detalle,   name="crud_detalle"),

    path("carga/", views.carga, name="carga"),

]
