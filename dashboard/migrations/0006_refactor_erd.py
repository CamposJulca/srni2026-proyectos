"""
Migración: refactor completo del ERD
- Persona         → Colaborador (con FK a Procedimiento)
- CronogramaActividad → Actividad (con FK a Obligacion y Proyecto)
- Agrega: Procedimiento, Obligacion
- Elimina: PlanAccion
"""
from django.db import migrations, models
import django.db.models.deletion


def copiar_persona_a_colaborador(apps, schema_editor):
    Persona = apps.get_model('dashboard', 'Persona')
    Colaborador = apps.get_model('dashboard', 'Colaborador')
    Procedimiento = apps.get_model('dashboard', 'Procedimiento')

    proc_cache = {}

    for p in Persona.objects.all():
        proc_obj = None
        if p.procedimiento:
            nombre_proc = p.procedimiento.strip().upper()
            if nombre_proc not in proc_cache:
                proc_obj, _ = Procedimiento.objects.get_or_create(nombre=nombre_proc)
                proc_cache[nombre_proc] = proc_obj
            else:
                proc_obj = proc_cache[nombre_proc]

        Colaborador.objects.create(
            id=p.id,
            nombre=p.nombre,
            cedula=p.cedula,
            procedimiento=proc_obj,
            fecha_inicio=p.fecha_inicio,
            fecha_fin=p.fecha_fin,
            honorarios=p.honorarios,
            objeto=p.objeto,
        )


def migrar_asignaciones(apps, schema_editor):
    Asignacion = apps.get_model('dashboard', 'Asignacion')
    for a in Asignacion.objects.all():
        a.colaborador_id = a.persona_id
        a.save(update_fields=['colaborador_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_cronogramaactividad_semanas_activas'),
    ]

    operations = [

        # ── 1. Nueva tabla Procedimiento ──────────────────────────────
        migrations.CreateModel(
            name='Procedimiento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=200, unique=True)),
            ],
        ),

        # ── 2. Nueva tabla Colaborador ────────────────────────────────
        migrations.CreateModel(
            name='Colaborador',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=200, unique=True)),
                ('cedula', models.CharField(blank=True, max_length=20, null=True)),
                ('fecha_inicio', models.DateField(blank=True, null=True)),
                ('fecha_fin', models.DateField(blank=True, null=True)),
                ('honorarios', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('objeto', models.TextField(blank=True, null=True)),
                ('procedimiento', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='colaboradores',
                    to='dashboard.procedimiento',
                )),
            ],
        ),

        # ── 3. Copiar Persona → Colaborador (con datos) ───────────────
        migrations.RunPython(copiar_persona_a_colaborador, migrations.RunPython.noop),

        # ── 4. Agregar colaborador_id nullable a Asignacion ───────────
        migrations.AddField(
            model_name='asignacion',
            name='colaborador',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='asignaciones',
                to='dashboard.colaborador',
            ),
        ),

        # ── 5. Poblar colaborador_id desde persona_id ─────────────────
        migrations.RunPython(migrar_asignaciones, migrations.RunPython.noop),

        # ── 6. Eliminar unique_together viejo ─────────────────────────
        migrations.AlterUniqueTogether(
            name='asignacion',
            unique_together=set(),
        ),

        # ── 7. Quitar FK persona de Asignacion ────────────────────────
        migrations.RemoveField(
            model_name='asignacion',
            name='persona',
        ),

        # ── 8. Hacer colaborador_id NOT NULL ──────────────────────────
        migrations.AlterField(
            model_name='asignacion',
            name='colaborador',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='asignaciones',
                to='dashboard.colaborador',
            ),
        ),

        # ── 9. Restaurar unique_together nuevo ────────────────────────
        migrations.AlterUniqueTogether(
            name='asignacion',
            unique_together={('modulo', 'colaborador', 'rol')},
        ),

        # ── 10. Eliminar Persona ──────────────────────────────────────
        migrations.DeleteModel(name='Persona'),

        # ── 11. Eliminar PlanAccion ───────────────────────────────────
        migrations.DeleteModel(name='PlanAccion'),

        # ── 12. Eliminar CronogramaActividad ─────────────────────────
        migrations.DeleteModel(name='CronogramaActividad'),

        # ── 13. Nueva tabla Obligacion ────────────────────────────────
        migrations.CreateModel(
            name='Obligacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('descripcion', models.TextField()),
                ('colaborador', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='obligaciones',
                    to='dashboard.colaborador',
                )),
            ],
        ),

        # ── 14. Nueva tabla Actividad ─────────────────────────────────
        migrations.CreateModel(
            name='Actividad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('actividad_id', models.CharField(blank=True, max_length=20)),
                ('descripcion', models.TextField()),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
                ('progreso', models.IntegerField(default=0)),
                ('estado', models.CharField(
                    choices=[
                        ('pendiente', 'Pendiente'),
                        ('en_curso', 'En Curso'),
                        ('completada', 'Completada'),
                        ('bloqueada', 'Bloqueada'),
                    ],
                    default='pendiente',
                    max_length=20,
                )),
                ('orden', models.IntegerField(default=0)),
                ('semanas_activas', models.JSONField(blank=True, default=list)),
                ('obligacion', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='actividades',
                    to='dashboard.obligacion',
                )),
                ('proyecto', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='actividades',
                    to='dashboard.proyecto',
                )),
            ],
            options={
                'verbose_name': 'Actividad',
                'verbose_name_plural': 'Actividades',
                'ordering': ['obligacion__colaborador', 'orden', 'fecha_inicio'],
            },
        ),
    ]
