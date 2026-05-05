from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from .models import (
    Actividad,
    Asignacion,
    Colaborador,
    CuentaCobro,
    Modulo,
    Obligacion,
    Perfil,
    Procedimiento,
    Proyecto,
    Rol,
)


class DashboardCruceCobroTests(TestCase):

    def setUp(self):
        # Crear usuario admin para autenticación
        self.user = User.objects.create_user(username='testadmin', password='test1234')
        Perfil.objects.create(user=self.user, rol='admin')
        self.client.login(username='testadmin', password='test1234')

        self.procedimiento = Procedimiento.objects.create(nombre="INSTRUMENTALIZACIÓN")
        self.proyecto = Proyecto.objects.create(nombre="Proyecto A")
        self.modulo = Modulo.objects.create(
            proyecto=self.proyecto,
            nombre="Módulo 1",
            referente="Referente 1",
        )
        self.rol = Rol.objects.create(nombre="Desarrollador")

        self.colaborador = Colaborador.objects.create(
            nombre="Ana Contratista",
            procedimiento=self.procedimiento,
            honorarios=1_000_000,
        )
        Asignacion.objects.create(
            modulo=self.modulo,
            colaborador=self.colaborador,
            rol=self.rol,
        )

        obligacion = Obligacion.objects.create(
            colaborador=self.colaborador,
            descripcion="Cumplir actividades de desarrollo",
        )
        Actividad.objects.create(
            obligacion=obligacion,
            proyecto=self.proyecto,
            actividad_id="A-1",
            descripcion="Actividad completada",
            fecha_inicio=date(2026, 4, 1),
            fecha_fin=date(2026, 4, 10),
            progreso=100,
            estado="completada",
        )
        Actividad.objects.create(
            obligacion=obligacion,
            proyecto=self.proyecto,
            actividad_id="A-2",
            descripcion="Actividad en curso",
            fecha_inicio=date(2026, 4, 11),
            fecha_fin=date(2026, 4, 25),
            progreso=50,
            estado="en_curso",
        )

        CuentaCobro.objects.create(
            colaborador=self.colaborador,
            periodo=date(2026, 4, 7),  # se normaliza al día 1
            numero_cuenta="CC-APR-01",
            valor_cobrado=1_200_000,
            estado="radicada",
        )

    def test_dashboard_data_incluye_cruce_cobro(self):
        res = self.client.get(
            "/api/dashboard/",
            {
                "procedimiento": "INSTRUMENTALIZACIÓN",
                "periodo": "2026-04",
            },
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertIn("cruce_cobro", data)
        self.assertEqual(len(data["cruce_cobro"]), 1)
        fila = data["cruce_cobro"][0]

        self.assertEqual(fila["colaborador"], "Ana Contratista")
        self.assertEqual(fila["actividades_periodo"], 2)
        self.assertEqual(fila["actividades_completadas"], 1)
        self.assertEqual(fila["avance_pct"], 75.0)
        self.assertEqual(fila["cumplimiento_pct"], 50.0)
        self.assertEqual(fila["cobro_pct"], 120.0)
        self.assertEqual(fila["brecha_cumplimiento_cobro"], -70.0)
        self.assertEqual(fila["estado_cruce"], "desalineado")

    def test_dashboard_data_rechaza_periodo_invalido(self):
        res = self.client.get("/api/dashboard/", {"periodo": "2026/04"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.json())
