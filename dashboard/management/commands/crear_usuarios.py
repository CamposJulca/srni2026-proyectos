import unicodedata

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from dashboard.models import Colaborador, Perfil


def _slug(nombre):
    """'Cristhiam Daniel Campos Julca' → 'cristhiam.campos'"""
    s = unicodedata.normalize('NFD', nombre)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    partes = s.strip().lower().split()
    if len(partes) >= 3:
        return f"{partes[0]}.{partes[-2]}"
    if len(partes) == 2:
        return f"{partes[0]}.{partes[1]}"
    return partes[0] if partes else 'user'


# Nombres parciales para identificar admins (se busca contenido en el nombre)
ADMINS_PARCIALES = [
    'CRISTHIAM DANIEL CAMPOS',
]


class Command(BaseCommand):
    help = 'Crea usuarios Django + Perfil para cada Colaborador'

    def add_arguments(self, parser):
        parser.add_argument('--admin', action='append', default=[],
                            help='Nombre parcial de colaborador a marcar como admin (puede repetirse)')

    def handle(self, *args, **options):
        admins_extra = [a.upper() for a in options['admin']]
        admins_parciales = ADMINS_PARCIALES + admins_extra

        password = 'srni2026'
        creados = []
        existentes = []
        usernames_usados = set(User.objects.values_list('username', flat=True))

        # Vincular superuser existente
        for su in User.objects.filter(is_superuser=True):
            perfil, created = Perfil.objects.get_or_create(user=su, defaults={'rol': 'admin'})
            if not created and perfil.rol != 'admin':
                perfil.rol = 'admin'
                perfil.save()

        for colab in Colaborador.objects.all().order_by('nombre'):
            username = _slug(colab.nombre)

            # Evitar colisiones
            base = username
            i = 1
            while username in usernames_usados:
                username = f"{base}{i}"
                i += 1

            # Determinar rol
            nombre_upper = colab.nombre.upper()
            es_admin = any(parcial in nombre_upper for parcial in admins_parciales)
            rol = 'admin' if es_admin else 'colaborador'

            # Verificar si ya tiene usuario
            perfil_existente = Perfil.objects.filter(colaborador=colab).first()
            if perfil_existente:
                existentes.append((perfil_existente.user.username, colab.nombre, perfil_existente.rol))
                continue

            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=colab.nombre.split()[0] if colab.nombre else '',
            )
            Perfil.objects.create(user=user, colaborador=colab, rol=rol)
            usernames_usados.add(username)
            creados.append((username, colab.nombre, rol))

        self.stdout.write('\n' + '=' * 80)
        self.stdout.write('USUARIOS CREADOS')
        self.stdout.write('=' * 80)
        self.stdout.write(f'{"USERNAME":<25} {"ROL":<15} {"COLABORADOR"}')
        self.stdout.write('-' * 80)
        for username, nombre, rol in creados:
            marca = ' ★' if rol == 'admin' else ''
            self.stdout.write(f'{username:<25} {rol:<15} {nombre}{marca}')

        if existentes:
            self.stdout.write(f'\n--- Ya existian {len(existentes)} perfiles (omitidos) ---')

        self.stdout.write(f'\nTotal creados: {len(creados)}')
        self.stdout.write(f'Password para todos: {password}')
        self.stdout.write('=' * 80)
