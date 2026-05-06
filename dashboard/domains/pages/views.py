from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from dashboard.constants import PROCEDIMIENTOS
from dashboard.permisos import admin_required


@login_required
def home(request):
    perfil = getattr(request.user, "perfil", None)
    if perfil and perfil.rol == "colaborador":
        return redirect("/mi-cronograma/")
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
