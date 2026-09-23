# Documento Tecnico - Dashboard de Proyectos SRNI

**Sistema:** Dashboard de Proyectos SRNI 2026  
**Aplicacion:** `dashboard`  
**Framework:** Django 6.0.3  
**Fecha:** Mayo 2026

## 1. Proposito

Este documento describe la implementacion tecnica del sistema de seguimiento de proyectos, cronogramas, actividades, evidencias, reportes semanales y consultas administrativas de la SRNI. El objetivo es facilitar mantenimiento, soporte, despliegue y evolucion del codigo.

## 2. Stack Tecnologico

| Componente | Tecnologia |
|---|---|
| Backend | Python, Django 6.0.3 |
| Servidor WSGI | Gunicorn |
| Base de datos | SQLite (`db.sqlite3`) |
| Archivos estaticos | WhiteNoise, `staticfiles/` |
| Archivos subidos | `media/evidencias/` |
| Frontend | Templates Django, HTML, CSS, JavaScript vanilla |
| Graficos e interaccion | JavaScript del proyecto |
| Importacion | `openpyxl` para archivos `.xlsx`; parser Markdown propio para cronogramas |

Dependencias declaradas en `requirements.txt`:

```txt
Django==6.0.3
gunicorn==25.1.0
whitenoise==6.12.0
asgiref==3.11.1
sqlparse==0.5.5
packaging==26.0
```

Nota: la funcionalidad de importacion desde Excel requiere `openpyxl`, usado por `dashboard/domains/importacion/services.py`.

## 3. Estructura del Proyecto

```txt
.
├── config/                         # Configuracion Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── dashboard/                      # Aplicacion principal
│   ├── models/                     # Modelos por dominio
│   ├── domains/                    # Vistas, servicios, selectores y serializers
│   ├── routing/                    # URL patterns por modulo
│   ├── templates/dashboard/        # Pantallas HTML
│   ├── static/dashboard/           # CSS, JS e imagenes
│   ├── management/commands/        # Comandos batch/importacion
│   ├── crud_config.py              # Metadatos de CRUD generico
│   ├── permisos.py                 # Autorizacion y contexto de usuario
│   └── views.py                    # Fachada que reexporta vistas por dominio
├── data/Cronogramas_actividades/   # Cronogramas fuente en Markdown
├── docs/                           # Documentacion del proyecto
├── media/                          # Evidencias subidas en ejecucion
├── staticfiles/                    # Estaticos recolectados
├── manage.py
└── requirements.txt
```

## 4. Configuracion Principal

Archivo: `config/settings.py`.

| Configuracion | Valor actual |
|---|---|
| `INSTALLED_APPS` | Apps Django base + `dashboard` |
| `DATABASES.default` | SQLite en `BASE_DIR / "db.sqlite3"` |
| `STATIC_URL` | `/static/` |
| `STATIC_ROOT` | `BASE_DIR / "staticfiles"` |
| `STATICFILES_STORAGE` | `whitenoise.storage.CompressedManifestStaticFilesStorage` |
| `MEDIA_URL` | `/media/` |
| `MEDIA_ROOT` | `BASE_DIR / "media"` |
| `LOGIN_URL` | `/login/` |
| `LOGIN_REDIRECT_URL` | `/` |
| `LOGOUT_REDIRECT_URL` | `/login/` |
| `DEFAULT_AUTO_FIELD` | `django.db.models.AutoField` |

Consideraciones de produccion:

- `DEBUG` esta activo y debe desactivarse para despliegues productivos.
- `SECRET_KEY` esta versionada y debe moverse a variable de entorno.
- `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` deben ajustarse al dominio final.
- SQLite es suficiente para pruebas o bajo volumen; para produccion se recomienda PostgreSQL.

## 5. Modelo de Datos

### 5.1 Organizacion y Proyectos

| Modelo | Responsabilidad |
|---|---|
| `Procedimiento` | Agrupa colaboradores y proyectos por procedimiento institucional. |
| `Proyecto` | Representa iniciativas, estado, prioridad, responsable, fechas, presupuesto y observaciones. |
| `Modulo` | Subdivision funcional de un proyecto. |
| `Rol` | Rol asignable dentro de un modulo. |
| `Asignacion` | Vincula colaborador, rol y modulo. Tiene unicidad por `modulo`, `colaborador`, `rol`. |
| `RiesgoProyecto` | Gestiona riesgos por proyecto con impacto, probabilidad, responsable y plan de mitigacion. |
| `AlertaProyecto` | Registra alertas por proyecto con severidad, responsable y plan de accion. |
| `ProyectoHistorial` | Guarda cambios de campos relevantes de `Proyecto` en formato JSON. |
| `Colaborador` | Persona contratista o integrante, con cedula, fechas, honorarios, objeto contractual y procedimiento. |

Reglas relevantes:

- `Proyecto.clean()` valida que `fecha_fin >= fecha_inicio`.
- `Proyecto.save()` registra historial cuando cambian campos trazables.
- `Modulo` impone unicidad de nombre por proyecto.

### 5.2 Actividades y Evidencias

| Modelo | Responsabilidad |
|---|---|
| `Obligacion` | Obligacion contractual o funcional asociada a un colaborador. |
| `Actividad` | Actividad de cronograma ligada a una obligacion y opcionalmente a un proyecto. |
| `EvidenciaActividad` | Archivo soporte asociado a una actividad, con comentario, usuario creador y fecha. |

Reglas relevantes:

- `Actividad.progreso` esta validado entre 0 y 100.
- Si una actividad queda en estado `completada`, su progreso se fuerza a 100.
- Si el progreso se guarda en 100, el estado se fuerza a `completada`.
- No se permite marcar una actividad como completada desde servicios de actualizacion si no tiene evidencias.
- Cada evidencia se almacena en `media/evidencias/%Y/%m/`.
- El tamano maximo por evidencia es 10 MB.

### 5.3 Reportes y Cuentas

| Modelo | Responsabilidad |
|---|---|
| `ReporteSemanal` | Reporte por colaborador y semana con avances e impedimentos. Unico por `colaborador`, `semana`. |
| `CuentaCobro` | Registro mensual de cuenta de cobro por colaborador. Unico por `colaborador`, `periodo`. |

Reglas relevantes:

- `CuentaCobro.save()` normaliza `periodo` al primer dia del mes.
- `ReporteSemanal` exige semana y contenido de avance desde el servicio de guardado.

### 5.4 Usuarios

| Modelo | Responsabilidad |
|---|---|
| `Perfil` | Extension de `User` con rol `admin` o `colaborador` y enlace opcional a `Colaborador`. |

## 6. Capas de Aplicacion

### 6.1 Routing

`dashboard/urls.py` agrupa rutas desde:

- `dashboard/routing/auth.py`
- `dashboard/routing/pages.py`
- `dashboard/routing/dashboard.py`
- `dashboard/routing/crud.py`
- `dashboard/routing/actividades.py`
- `dashboard/routing/evidencias.py`
- `dashboard/routing/reportes.py`

### 6.2 Fachada de Vistas

`dashboard/views.py` reexporta las vistas implementadas en `dashboard/view_modules/` y `dashboard/domains/`. Esto mantiene compatibilidad con rutas que importan `dashboard.views`, mientras el codigo real queda separado por dominio.

### 6.3 Dominios

Cada dominio sigue una separacion similar:

| Carpeta | Responsabilidad |
|---|---|
| `views.py` | Entrada HTTP, validacion de metodo, permisos y respuesta JSON/HTML. |
| `services.py` | Reglas de negocio y operaciones de escritura. |
| `selectors.py` | Consultas ORM reutilizables. |
| `serializers.py` | Transformacion de modelos/querysets a diccionarios JSON. |
| `utils.py` | Funciones auxiliares del dominio. |

Dominios principales:

- `actividades`: Gantt, semana, resumen, mi cronograma y actualizacion de actividades.
- `crud`: consulta SQL restringida y CRUD generico por metadatos.
- `evidencias`: listar, subir y eliminar soportes.
- `gerencial`: KPIs, resumen de proyectos, compromisos por mes, carga de trabajo y cruce de cuentas de cobro.
- `importacion`: carga de colaboradores desde Excel.
- `reportes`: reporte semanal de colaboradores.
- `auth` y `pages`: autenticacion y renderizado de pantallas.

## 7. Endpoints Principales

### 7.1 Paginas

| Ruta | Vista |
|---|---|
| `/` | Inicio |
| `/dashboard/` | Dashboard operativo |
| `/gerencial/` | Vista gerencial |
| `/proyectos/<pk>/` | Detalle de proyecto |
| `/consultas/` | Consola de consultas |
| `/crud/` | Mantenimiento CRUD |
| `/carga/` | Carga/importacion |
| `/actividades/` | Cronograma Gantt |
| `/actividades/semana/` | Vista semanal |
| `/actividades/resumen/` | Resumen de actividades |
| `/mi-cronograma/` | Vista personal del colaborador |
| `/login/`, `/logout/` | Sesion |

### 7.2 APIs

| Ruta | Proposito |
|---|---|
| `GET /api/dashboard/` | KPIs, graficos, carga de trabajo y cruce de cuentas. |
| `GET /api/dashboard/personas-por-rol/` | Personas agrupadas por rol. |
| `GET /api/gerencial/` | Indicadores gerenciales. |
| `GET /api/proyectos/<pk>/` | Detalle integral de proyecto. |
| `GET /api/proyectos/<pk>/exportar.csv` | Exportacion CSV de proyecto. |
| `POST /api/sql/` | Ejecuta consultas `SELECT` controladas. |
| `GET /api/crud/meta/` | Metadatos del CRUD generico. |
| `GET /api/crud/<tabla>/` | Lista registros de una tabla configurada. |
| `POST /api/crud/<tabla>/crear/` | Crea registros en tabla configurada. |
| `GET/PATCH /api/crud/<tabla>/<pk>/` | Consulta o actualiza un registro. |
| `GET /api/actividades/` | Datos de cronograma. |
| `POST /api/actividades/crear/` | Crea actividad. |
| `GET/PATCH /api/actividades/<pk>/` | Detalle/actualizacion administrativa. |
| `GET /api/actividades/semana/` | Actividades filtradas por semana. |
| `GET /api/actividades/resumen/` | Resumen por colaborador/procedimiento. |
| `GET /api/mi-cronograma/` | Actividades del colaborador autenticado. |
| `PATCH /api/mi-cronograma/<pk>/` | Actualizacion por el colaborador propietario. |
| `GET /api/evidencias/<actividad_pk>/` | Lista evidencias. |
| `POST /api/evidencias/<actividad_pk>/subir/` | Sube evidencia. |
| `DELETE /api/evidencias/eliminar/<pk>/` | Elimina evidencia. |
| `GET /api/reporte-semanal/` | Obtiene reporte semanal del usuario. |
| `POST /api/reporte-semanal/guardar/` | Guarda o actualiza reporte semanal. |
| `GET /api/reportes-admin/` | Consulta administrativa de reportes. |

## 8. CRUD Generico y Consultas SQL

El modulo CRUD esta controlado por `dashboard/crud_config.py`. Las tablas administrables son:

- `proyecto`
- `colaborador`
- `obligacion`
- `actividad`
- `cuenta_cobro`
- `asignacion`
- `modulo`
- `rol`
- `riesgo_proyecto`
- `alerta_proyecto`

Cada entrada define modelo, etiqueta, campos editables, columnas de lista, campos de busqueda y relaciones foraneas.

La consola SQL usa `ejecutar_select_seguro()`:

- Exige que la primera palabra sea `SELECT`.
- Bloquea palabras peligrosas: `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `TRUNCATE`, `REPLACE`, `ATTACH`, `DETACH`, `PRAGMA`.
- Limita la respuesta a 500 filas.

## 9. Seguridad

### 9.1 Autenticacion

El sistema usa autenticacion nativa de Django (`User`, sesiones y cookies). Las rutas de login/logout estan en `dashboard/routing/auth.py`.

### 9.2 Autorizacion

Archivo: `dashboard/permisos.py`.

| Mecanismo | Uso |
|---|---|
| `_es_admin(user)` | Considera admin a superusuarios o perfiles con `rol="admin"`. |
| `admin_required` | Restringe vistas administrativas; redirige o responde 403 para APIs. |
| `user_role` | Context processor para exponer rol y colaborador en templates. |

Controles de propiedad:

- Un colaborador solo actualiza actividades propias en `mi-cronograma`.
- Una evidencia puede gestionarse por el dueno de la actividad o por un admin.
- La eliminacion de evidencias esta limitada al creador del archivo o a un admin.

### 9.3 CSRF

Django mantiene proteccion CSRF. Las peticiones POST/PATCH/DELETE hechas desde JavaScript deben enviar el token correspondiente.

## 10. Importacion y Procesos Batch

### 10.1 Colaboradores OPS

`dashboard/domains/importacion/services.py` procesa Excel:

- Usa la hoja `OPS 2026` si existe; de lo contrario usa la hoja activa.
- Requiere columnas `NOMBRES CONTRATISTA` y `APELLIDOS CONTRATISTA`.
- Filtra por dependencia asociada que contenga `RED NACIONAL`.
- Crea o actualiza colaboradores por nombre normalizado.
- Crea procedimientos si vienen en la columna `PROCEDIMIENTO`.

### 10.2 Cronogramas Markdown

Comando: `python manage.py importar_cronogramas`.

Fuente: `data/Cronogramas_actividades/*.md`.

Soporta formatos:

- Secciones `###` con tablas por seccion.
- Tabla WBS con fechas explicitas.
- Tabla unica con obligacion, actividad y semanas.
- Tabla plana sin secciones con semanas como columnas.

El comando transforma cada fila en:

- `Colaborador`
- `Obligacion`
- `Actividad`
- `semanas_activas` como lista JSON.
- `fecha_inicio` y `fecha_fin` calculadas desde el calendario de semanas 2026.

### 10.3 Calculo de Progreso

Comando: `python manage.py calcular_progreso`.

Calcula avance segun fecha actual, fecha inicio y fecha fin. Sin `--forzar`, solo recalcula actividades con progreso 0. Con `--forzar`, recalcula todas.

## 11. Ejecucion Local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Comandos utiles:

```bash
python manage.py createsuperuser
python manage.py collectstatic
python manage.py importar_cronogramas
python manage.py calcular_progreso
python manage.py check
```

## 12. Riesgos Tecnicos y Recomendaciones

| Riesgo | Recomendacion |
|---|---|
| `DEBUG=True` y `SECRET_KEY` en codigo | Externalizar configuracion por variables de entorno. |
| SQLite en despliegue compartido | Migrar a PostgreSQL si crece concurrencia o volumen. |
| Dependencia `openpyxl` no declarada en `requirements.txt` | Agregarla si la carga Excel es parte del flujo soportado. |
| Consola SQL disponible para admins | Mantener solo `SELECT`, auditar accesos y evaluar bitacora de consultas. |
| Evidencias en filesystem local | Definir estrategia de backup y retencion de `media/`. |
| Documentos de cronograma con formatos variables | Mantener pruebas de importacion para cada formato soportado. |
