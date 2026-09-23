"""Rutas con prefijo de despliegue (SCRIPT_NAME).

Permite servir la aplicación en la raíz del dominio o bajo un prefijo
(p. ej. /srni-dashboard) sin cambiar el código: el prefijo lo entrega
Gunicorn a partir de la variable de entorno SCRIPT_NAME.
"""
from django.urls import get_script_prefix


def base():
    """Prefijo sin barra final: '' en la raíz, '/srni-dashboard' bajo prefijo."""
    return get_script_prefix().rstrip("/")


def con_prefijo(ruta):
    """Antepone el prefijo a una ruta absoluta de la aplicación ('/login/')."""
    return base() + ruta


def app_base(request):
    """Context processor: expone APP_BASE a las plantillas."""
    return {"APP_BASE": base()}
