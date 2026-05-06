from datetime import date
import json
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings

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
    ReporteSemanal,
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


class ArquitecturaCompatibilidadTests(TestCase):

    def test_dashboard_models_reexporta_modelos_partidos(self):
        from dashboard import models
        from dashboard.models.actividades import Actividad as ActividadPartida
        from dashboard.models.organizacion import Colaborador as ColaboradorPartido

        self.assertIs(models.Actividad, ActividadPartida)
        self.assertIs(models.Colaborador, ColaboradorPartido)


class CrudSqlTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="adminsql", password="test1234")
        Perfil.objects.create(user=self.user, rol="admin")
        self.client.login(username="adminsql", password="test1234")

    def test_sql_query_rechaza_operaciones_no_select(self):
        res = self.client.post(
            "/api/sql/",
            data=json.dumps({"query": "DELETE FROM dashboard_colaborador"}),
            content_type="application/json",
        )

        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.json()["error"], "Solo se permiten consultas SELECT.")

    def test_crud_meta_responde_para_admin(self):
        res = self.client.get("/api/crud/meta/")

        self.assertEqual(res.status_code, 200)
        self.assertIn("colaborador", res.json())


class ReportesTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="reportero", password="test1234")
        self.colaborador = Colaborador.objects.create(nombre="Reporter Uno")
        Perfil.objects.create(
            user=self.user,
            rol="colaborador",
            colaborador=self.colaborador,
        )
        self.client.login(username="reportero", password="test1234")

    def test_reporte_semanal_guardar_y_listar(self):
        res = self.client.post(
            "/api/reporte-semanal/guardar/",
            data=json.dumps({
                "semana": "ABR S3",
                "que_hizo": "Avancé compromisos",
                "impedimentos": "Ninguno",
            }),
            content_type="application/json",
        )

        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["created"])
        self.assertEqual(ReporteSemanal.objects.count(), 1)

        res = self.client.get("/api/reporte-semanal/", {"semana": "ABR S3"})
        self.assertEqual(res.status_code, 200)
        reportes = res.json()["reportes"]
        self.assertEqual(len(reportes), 1)
        self.assertEqual(reportes[0]["que_hizo"], "Avancé compromisos")

    def test_reporte_semanal_valida_campos_obligatorios(self):
        res = self.client.post(
            "/api/reporte-semanal/guardar/",
            data=json.dumps({"semana": "ABR S3", "que_hizo": ""}),
            content_type="application/json",
        )

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["error"], "Semana y reporte son obligatorios")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class EvidenciasTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="dueno", password="test1234")
        self.otro = User.objects.create_user(username="otro", password="test1234")
        self.colaborador = Colaborador.objects.create(nombre="Dueño Evidencia")
        self.otro_colaborador = Colaborador.objects.create(nombre="Otro Evidencia")
        Perfil.objects.create(
            user=self.user,
            rol="colaborador",
            colaborador=self.colaborador,
        )
        Perfil.objects.create(
            user=self.otro,
            rol="colaborador",
            colaborador=self.otro_colaborador,
        )
        obligacion = Obligacion.objects.create(
            colaborador=self.colaborador,
            descripcion="Adjuntar evidencia",
        )
        self.actividad = Actividad.objects.create(
            obligacion=obligacion,
            actividad_id="EV-1",
            descripcion="Actividad con evidencia",
            fecha_inicio=date(2026, 4, 1),
            fecha_fin=date(2026, 4, 2),
        )

    def test_dueno_sube_y_lista_evidencia(self):
        self.client.login(username="dueno", password="test1234")
        archivo = SimpleUploadedFile("evidencia.txt", b"contenido", content_type="text/plain")

        res = self.client.post(
            f"/api/evidencias/{self.actividad.pk}/subir/",
            data={"archivo": archivo, "comentario": "Entregado"},
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["nombre"], "evidencia.txt")

        res = self.client.get(f"/api/evidencias/{self.actividad.pk}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["total"], 1)
        self.assertEqual(res.json()["evidencias"][0]["comentario"], "Entregado")

    def test_otro_usuario_no_puede_subir_evidencia(self):
        self.client.login(username="otro", password="test1234")
        archivo = SimpleUploadedFile("evidencia.txt", b"contenido", content_type="text/plain")

        res = self.client.post(
            f"/api/evidencias/{self.actividad.pk}/subir/",
            data={"archivo": archivo, "comentario": "No autorizado"},
        )

        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.json()["error"], "No autorizado")


class ImportacionTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="adminimport", password="test1234")
        Perfil.objects.create(user=self.user, rol="admin")
        self.client.login(username="adminimport", password="test1234")

    def test_carga_post_sin_archivo_retorna_400(self):
        res = self.client.post("/carga/")

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["error"], "No se recibió ningún archivo.")
