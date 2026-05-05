# Arquitectura de Software — Modulo Cronograma SRNI 2026

**Sistema:** Dashboard de Instrumentalizacion — Subdireccion Red Nacional de Informacion  
**Version:** 2.0  
**Fecha:** Abril 2026

---

## 1. Vista General

```
                    +-----------------------+
                    |    USUARIO FINAL      |
                    |  (Browser / HTTPS)    |
                    +-----------+-----------+
                                |
                    +-----------+-----------+
                    |       NGROK           |
                    |  (Tunel HTTPS:443)    |
                    +-----------+-----------+
                                |
                    +-----------+-----------+
                    |     GUNICORN          |
                    |  (WSGI :8085)         |
                    |  3 workers            |
                    +-----------+-----------+
                                |
              +-----------------+-----------------+
              |                                   |
   +----------+----------+            +-----------+-----------+
   |    DJANGO APP       |            |     WHITENOISE        |
   |  (config.wsgi)      |            |  (Archivos estaticos) |
   +----------+----------+            +-----------+-----------+
              |                                   |
   +----------+----------+            +-----------+-----------+
   |     SQLite3         |            |   /staticfiles/       |
   |   (db.sqlite3)      |            |   CSS, JS, IMG        |
   +---------------------+            +-----------------------+
              |
   +----------+----------+
   |   /media/evidencias/ |
   |   (Archivos subidos) |
   +-----------------------+
```

---

## 2. Arquitectura por Capas

### Capa de Presentacion (Frontend)

```
Templates Django (Jinja2)
    |
    ├── base.html              # Layout: header, nav, footer
    ├── actividades.html       # Gantt + filtros + modal
    ├── semana.html            # Vista semanal + tarjetas
    ├── resumen.html           # KPIs + tabla colaboradores
    └── mi_cronograma.html     # Autoservicio colaborador

JavaScript (vanilla, sin frameworks)
    |
    ├── actividades.js         # Gantt rendering, coloreo por proyecto, filtros
    ├── semana.js              # Tarjetas semanales, navegacion
    ├── resumen.js             # KPIs, barra distribucion, tabla
    └── mi_cronograma.js       # Autoservicio, evidencias, reportes

CSS
    |
    ├── dashboard.css          # Variables globales, layout base
    ├── actividades.css        # Gantt, barras, modal, leyenda
    ├── semana.css             # Navegador semanas, tarjetas
    ├── resumen.css            # KPIs, distribucion, tabla avance
    └── mi_cronograma.css      # Vista personal
```

### Capa de Logica de Negocio (Backend)

```
dashboard/views.py (~1600 lineas)
    |
    ├── Autenticacion          # login_view, logout_view
    ├── Actividades API        # actividades_data, actividad_crear, actividad_detalle
    ├── Semana API             # semana_data (agrupacion por colaborador)
    ├── Resumen API            # resumen_data (KPIs + tabla)
    ├── Mi Cronograma API      # mi_cronograma_data, mi_actividad_update
    ├── Evidencias API         # evidencias_lista, evidencia_subir, evidencia_eliminar
    ├── Reportes API           # reporte_semanal_data, reporte_semanal_guardar
    └── Helpers                # _semana_actual(), _calcular_resumen()

dashboard/permisos.py
    |
    ├── _es_admin(user)        # Verifica rol admin
    ├── @admin_required        # Decorador para vistas admin
    └── user_role(request)     # Context processor para templates
```

### Capa de Datos (Modelos)

```
dashboard/models.py (10 modelos)

    Procedimiento (1)──>(N) Colaborador (1)──>(N) Obligacion (1)──>(N) Actividad
                              |                                         |
                              |                                    (1)──>(N) EvidenciaActividad
                              |
                              ├──(1)──>(1) Perfil ──>(1) User
                              ├──(1)──>(N) Asignacion ──> Modulo ──> Proyecto
                              ├──(1)──>(N) CuentaCobro
                              └──(1)──>(N) ReporteSemanal
```

### Capa de Importacion

```
dashboard/management/commands/
    |
    ├── importar_cronogramas.py    # .md → Obligacion + Actividad
    |       |
    |       ├── detectar_formato()         # 4 formatos soportados
    |       ├── parse_formato_secciones()  # ### con tablas
    |       ├── parse_formato_wbs()        # Fechas explicitas
    |       ├── parse_formato_tabla_plana_dos_cols()
    |       └── parse_formato_tabla_sin_secciones()
    |
    └── calcular_progreso.py       # Tiempo transcurrido → progreso %
```

---

## 3. Flujo de Datos

### 3.1 Carga Inicial (Importacion)

```
data/Cronogramas_actividades/*.md
         |
    [importar_cronogramas --limpiar]
         |
    +---------+     +------------+     +-----------+
    | Parsear |---->| Colaborador|---->| Obligacion|
    | formato |     | (match)    |     | (get/cre) |
    +---------+     +------------+     +-----------+
                                            |
                                       +-----------+
                                       | Actividad |
                                       | (create)  |
                                       +-----------+
         |
    [calcular_progreso]
         |
    progreso % + estado coherente
```

### 3.2 Consulta Gantt (Lectura)

```
Browser                    Django                      DB
   |                         |                          |
   |-- GET /actividades/ --->|                          |
   |<-- HTML + JS -----------|                          |
   |                         |                          |
   |-- GET /api/actividades/ |                          |
   |   ?colaborador=X        |                          |
   |   &proyecto=Y --------->|-- SELECT Actividad ----->|
   |                         |   JOIN Obligacion        |
   |                         |   JOIN Colaborador       |
   |                         |   JOIN Asignacion ------>|
   |                         |<-- QuerySet -------------|
   |                         |                          |
   |                         |-- Calcular estado_visual |
   |                         |-- Inferir proyecto       |
   |<-- JSON tasks[] --------|                          |
   |                         |                          |
   |-- Render Gantt -------->|                          |
   |   (color por proyecto)  |                          |
```

### 3.3 Actualizacion de Actividad (Colaborador)

```
Browser                    Django                      DB
   |                         |                          |
   |-- POST /api/mi-crono/  |                          |
   |   {progreso, estado} -->|                          |
   |                         |-- Verificar Perfil ----->|
   |                         |-- Verificar ownership -->|
   |                         |                          |
   |                         |-- Si completada:         |
   |                         |   evidencias.count() > 0 |
   |                         |                          |
   |                         |-- UPDATE Actividad ----->|
   |<-- {ok: true} ----------|                          |
```

### 3.4 Subida de Evidencia

```
Browser                    Django                      Filesystem
   |                         |                          |
   |-- POST multipart       |                          |
   |   archivo + comentario  |                          |
   |------------------------>|-- Validar tamano <=10MB  |
   |                         |-- Validar permisos       |
   |                         |-- FileField.save() ----->| /media/evidencias/2026/04/
   |                         |-- CREATE EvidenciaAct -->| DB
   |<-- {ok, url, id} ------|                          |
```

---

## 4. Modelo de Seguridad

### Autenticacion

```
POST /login/
    |
    ├── authenticate(username, password)
    ├── login(request, user)
    └── Redirect: admin → / , colaborador → /mi-cronograma/
```

### Autorizacion (3 niveles)

```
Nivel 1: @login_required
    Todo el modulo requiere sesion activa

Nivel 2: @admin_required
    CRUD, carga masiva, consultas SQL, reportes admin

Nivel 3: Ownership check (en la vista)
    - mi_actividad_update: Perfil.colaborador == actividad.obligacion.colaborador
    - evidencia_subir: dueno de la actividad o admin
    - evidencia_eliminar: creador del archivo o admin
```

### CSRF

Todas las peticiones POST incluyen `X-CSRFToken` desde cookie via JavaScript.

---

## 5. Configuracion

```python
# config/settings.py

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "srni-backend.ngrok.io"]
CSRF_TRUSTED_ORIGINS = ["https://srni-backend.ngrok.io"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_URL = '/login/'
```

---

## 6. Despliegue

```bash
# Servidor de produccion (actual)
gunicorn config.wsgi:application --workers 3 --bind 0.0.0.0:8085

# Recargar despues de cambios
kill -HUP <PID_MASTER>          # Recarga workers sin downtime

# Rebuild estaticos
rm -rf staticfiles/
python manage.py collectstatic --noinput

# Migraciones
python manage.py migrate

# Importar datos
python manage.py importar_cronogramas --limpiar
python manage.py calcular_progreso
python manage.py crear_usuarios
```

---

## 7. Decisiones de Arquitectura

| Decision | Justificacion |
|----------|---------------|
| SQLite en vez de PostgreSQL | Equipo pequeno (~100 usuarios), baja concurrencia, simplicidad de despliegue |
| JavaScript vanilla en vez de React/Vue | Modulo interno, sin necesidad de SPA, menor complejidad |
| JSON APIs propias en vez de DRF | Endpoints simples, sin necesidad de serializadores complejos |
| WhiteNoise en vez de Nginx | Despliegue simplificado, Django sirve todo |
| Semanas hardcodeadas en vez de calculadas | Calendario laboral colombiano con festivos, no sigue ISO weeks |
| `semanas_activas` JSONField | Permite semanas no contiguas (actividades intermitentes) |
| Importacion desde Markdown | Los colaboradores ya manejan ese formato para sus cronogramas |

---

## 8. Limitaciones Conocidas

| Limitacion | Impacto | Mitigacion |
|------------|---------|------------|
| SQLite: escrituras concurrentes | Locking en escrituras simultaneas | Bajo riesgo por baja concurrencia |
| Actividades sin proyecto directo | 200/200 actividades con proyecto=NULL | Se infiere desde asignaciones del colaborador |
| Calendario 2026 hardcodeado | Requiere actualizacion para 2027 | Actualizar SEMANA_FECHAS en views.py e importar_cronogramas.py |
| 16 colaboradores sin cronograma | Avance real del equipo incompleto | Pendiente recibir cronogramas estandar |
| Archivos estaticos con hash de cache | Requiere Ctrl+Shift+R despues de deploy | Comportamiento esperado de WhiteNoise |
