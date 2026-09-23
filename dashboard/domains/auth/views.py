from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from dashboard.rutas import con_prefijo


def login_view(request):
    if request.user.is_authenticated:
        return redirect(con_prefijo("/"))
    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get("next", "")
            if next_url and url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
            ):
                return redirect(next_url)
            perfil = getattr(user, "perfil", None)
            if perfil and perfil.rol == "colaborador":
                return redirect(con_prefijo("/mi-cronograma/"))
            return redirect(con_prefijo("/"))
        error = "Usuario o contraseña incorrectos."
    return render(request, "dashboard/login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect(con_prefijo("/login/"))
