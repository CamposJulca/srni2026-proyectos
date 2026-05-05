from functools import wraps

from django.http import JsonResponse
from django.shortcuts import redirect


def _es_admin(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    perfil = getattr(user, 'perfil', None)
    return perfil is not None and perfil.rol == 'admin'


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')
        if _es_admin(request.user):
            return view_func(request, *args, **kwargs)
        if request.path.startswith('/api/'):
            return JsonResponse({'error': 'No autorizado'}, status=403)
        return redirect('/mi-cronograma/')
    return wrapper


def user_role(request):
    if not request.user.is_authenticated:
        return {}
    if request.user.is_superuser:
        perfil = getattr(request.user, 'perfil', None)
        return {
            'es_admin': True,
            'perfil': perfil,
            'user_rol': 'admin',
            'mi_colaborador': perfil.colaborador if perfil else None,
        }
    perfil = getattr(request.user, 'perfil', None)
    if perfil:
        return {
            'es_admin': perfil.rol == 'admin',
            'perfil': perfil,
            'user_rol': perfil.rol,
            'mi_colaborador': perfil.colaborador,
        }
    return {'es_admin': False, 'perfil': None, 'user_rol': 'colaborador'}
