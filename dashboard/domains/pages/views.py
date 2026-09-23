from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from dashboard.constants import PROCEDIMIENTOS
from dashboard.models import Proyecto
from dashboard.permisos import admin_required
from dashboard.rutas import con_prefijo


@login_required
def home(request):
    perfil = getattr(request.user, "perfil", None)
    if perfil and perfil.rol == "colaborador":
        return redirect(con_prefijo("/mi-cronograma/"))
    return render(request, "dashboard/home.html")


@admin_required
def consultas_view(request):
    return render(request, "dashboard/consultas_view.html", {
        "modulo_activo": "consultas",
    })


@admin_required
def crud_main_view(request):
    return render(request, "dashboard/crud_view.html", {
        "modulo_activo": "crud",
        "procedimientos": PROCEDIMIENTOS,
    })


@admin_required
def gerencial_view(request):
    return render(request, "dashboard/gerencial_view.html", {
        "modulo_activo": "gerencial",
    })


@admin_required
def proyecto_detalle_view(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    return render(request, "dashboard/proyecto_detalle.html", {
        "modulo_activo": "gerencial",
        "proyecto": proyecto,
    })
