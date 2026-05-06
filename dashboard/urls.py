from dashboard.routing import actividades, auth, crud, dashboard, evidencias, pages, reportes


urlpatterns = [
    *auth.urlpatterns,
    *pages.urlpatterns,
    *dashboard.urlpatterns,
    *crud.urlpatterns,
    *actividades.urlpatterns,
    *evidencias.urlpatterns,
    *reportes.urlpatterns,
]
