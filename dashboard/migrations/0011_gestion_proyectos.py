# Generated manually for project management enhancements.

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0010_evidenciaactividad_reportesemanal"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="proyecto",
            options={"ordering": ["nombre"]},
        ),
        migrations.AddField(
            model_name="proyecto",
            name="estado",
            field=models.CharField(
                choices=[
                    ("planeado", "Planeado"),
                    ("activo", "Activo"),
                    ("en_riesgo", "En riesgo"),
                    ("bloqueado", "Bloqueado"),
                    ("finalizado", "Finalizado"),
                    ("cancelado", "Cancelado"),
                ],
                default="activo",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="proyecto",
            name="fecha_fin",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="proyecto",
            name="fecha_inicio",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="proyecto",
            name="objetivo",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="proyecto",
            name="observaciones",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="proyecto",
            name="presupuesto",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=14,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        ),
        migrations.AddField(
            model_name="proyecto",
            name="prioridad",
            field=models.CharField(
                choices=[
                    ("baja", "Baja"),
                    ("media", "Media"),
                    ("alta", "Alta"),
                    ("critica", "Crítica"),
                ],
                default="media",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="proyecto",
            name="procedimiento",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="proyectos",
                to="dashboard.procedimiento",
            ),
        ),
        migrations.AddField(
            model_name="proyecto",
            name="responsable",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="proyectos_responsable",
                to="dashboard.colaborador",
            ),
        ),
        migrations.AlterField(
            model_name="actividad",
            name="progreso",
            field=models.IntegerField(
                default=0,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(100),
                ],
            ),
        ),
        migrations.CreateModel(
            name="RiesgoProyecto",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("riesgo", models.CharField(max_length=250)),
                (
                    "impacto",
                    models.CharField(
                        choices=[("bajo", "Bajo"), ("medio", "Medio"), ("alto", "Alto"), ("critico", "Crítico")],
                        default="medio",
                        max_length=20,
                    ),
                ),
                (
                    "probabilidad",
                    models.CharField(
                        choices=[("bajo", "Bajo"), ("medio", "Medio"), ("alto", "Alto"), ("critico", "Crítico")],
                        default="medio",
                        max_length=20,
                    ),
                ),
                ("fecha_limite", models.DateField(blank=True, null=True)),
                (
                    "estado",
                    models.CharField(
                        choices=[("abierto", "Abierto"), ("en_mitigacion", "En mitigación"), ("cerrado", "Cerrado")],
                        default="abierto",
                        max_length=20,
                    ),
                ),
                ("plan_mitigacion", models.TextField(blank=True, null=True)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
                (
                    "proyecto",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="riesgos", to="dashboard.proyecto"),
                ),
                (
                    "responsable",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="riesgos_responsable",
                        to="dashboard.colaborador",
                    ),
                ),
            ],
            options={
                "verbose_name": "Riesgo de proyecto",
                "verbose_name_plural": "Riesgos de proyecto",
                "ordering": ["estado", "fecha_limite", "riesgo"],
            },
        ),
        migrations.CreateModel(
            name="AlertaProyecto",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("alerta", models.CharField(max_length=250)),
                (
                    "severidad",
                    models.CharField(
                        choices=[
                            ("informativa", "Informativa"),
                            ("media", "Media"),
                            ("alta", "Alta"),
                            ("critica", "Crítica"),
                        ],
                        default="media",
                        max_length=20,
                    ),
                ),
                ("fecha_limite", models.DateField(blank=True, null=True)),
                (
                    "estado",
                    models.CharField(
                        choices=[("abierta", "Abierta"), ("atendida", "Atendida"), ("cerrada", "Cerrada")],
                        default="abierta",
                        max_length=20,
                    ),
                ),
                ("plan_accion", models.TextField(blank=True, null=True)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
                (
                    "proyecto",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="alertas", to="dashboard.proyecto"),
                ),
                (
                    "responsable",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="alertas_responsable",
                        to="dashboard.colaborador",
                    ),
                ),
            ],
            options={
                "verbose_name": "Alerta de proyecto",
                "verbose_name_plural": "Alertas de proyecto",
                "ordering": ["estado", "fecha_limite", "alerta"],
            },
        ),
        migrations.CreateModel(
            name="ProyectoHistorial",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("cambios", models.JSONField(default=dict)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                (
                    "proyecto",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="historial", to="dashboard.proyecto"),
                ),
            ],
            options={
                "verbose_name": "Historial de proyecto",
                "verbose_name_plural": "Historial de proyectos",
                "ordering": ["-creado_en"],
            },
        ),
        migrations.AddConstraint(
            model_name="modulo",
            constraint=models.UniqueConstraint(fields=("proyecto", "nombre"), name="unique_modulo_nombre_por_proyecto"),
        ),
    ]
