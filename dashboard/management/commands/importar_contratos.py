"""
Importa el libro maestro de contratación (`data/Contratos SRNI 2026.xlsx`) a los
modelos Contrato / PagoContrato / SeguridadSocialContrato / Convenio.

Uso:
    python manage.py importar_contratos
    python manage.py importar_contratos --dry-run
    python manage.py importar_contratos --archivo data/otro.xlsx --origen cron
"""
from django.core.management.base import BaseCommand

from dashboard.domains.contratacion.importador import ejecutar_importacion
from dashboard.domains.importacion.services import ImportacionValidationError


class Command(BaseCommand):
    help = "Importa contratos, pagos, seguridad social y convenios desde el Excel maestro."

    def add_arguments(self, parser):
        parser.add_argument(
            "--archivo",
            default=None,
            help="Ruta al .xlsx (default: settings.CONTRATOS_XLSX_PATH).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simula la importación sin escribir en la base de datos.",
        )
        parser.add_argument(
            "--origen",
            default="cron",
            choices=["cron", "manual"],
            help="Origen registrado en la bitácora (default: cron).",
        )

    def handle(self, *args, **options):
        try:
            resumen = ejecutar_importacion(
                archivo=options["archivo"],
                dry_run=options["dry_run"],
                origen=options["origen"],
            )
        except ImportacionValidationError as exc:
            self.stderr.write(self.style.ERROR(str(exc)))
            return

        modo = " (DRY-RUN, sin cambios)" if resumen["dry_run"] else ""
        self.stdout.write(self.style.SUCCESS(
            f"Importación de contratos completada{modo}:"
            f"\n  Archivo                : {resumen['archivo']}"
            f"\n  Filas de contrato      : {resumen['filas_leidas']}"
            f"\n  Contratos creados      : {resumen['creados']}"
            f"\n  Contratos actualizados : {resumen['actualizados']}"
            f"\n  Sin match colaborador  : {resumen['sin_match_colaborador']}"
            f"\n  Convenios              : {resumen['convenios']}"
            f"\n  Errores                : {len(resumen['errores'])}"
        ))
        for error in resumen["errores"][:20]:
            self.stderr.write(f"  ! {error}")
