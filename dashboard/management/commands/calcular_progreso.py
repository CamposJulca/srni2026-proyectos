from datetime import date

from django.core.management.base import BaseCommand

from dashboard.models import Actividad


class Command(BaseCommand):
    help = 'Calcula progreso inicial basado en tiempo transcurrido'

    def add_arguments(self, parser):
        parser.add_argument('--forzar', action='store_true',
                            help='Recalcula incluso actividades con progreso > 0')

    def handle(self, *args, **options):
        hoy = date.today()
        forzar = options['forzar']

        qs = Actividad.objects.all()
        if not forzar:
            qs = qs.filter(progreso=0)

        actualizadas = 0
        for a in qs:
            total_dias = (a.fecha_fin - a.fecha_inicio).days
            if total_dias <= 0:
                progreso = 100 if hoy >= a.fecha_fin else 0
            elif hoy < a.fecha_inicio:
                progreso = 0
            elif hoy >= a.fecha_fin:
                progreso = 100
            else:
                elapsed = (hoy - a.fecha_inicio).days
                progreso = min(100, round((elapsed / total_dias) * 100))

            # Determinar estado coherente
            if progreso == 0:
                estado = 'pendiente'
            elif progreso >= 100:
                estado = 'completada'
                progreso = 100
            else:
                estado = 'en_curso'

            if a.progreso != progreso or a.estado != estado:
                a.progreso = progreso
                a.estado = estado
                a.save(update_fields=['progreso', 'estado'])
                actualizadas += 1

        self.stdout.write(f'Actividades actualizadas: {actualizadas} de {qs.count()}')
