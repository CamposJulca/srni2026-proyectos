# Arquitectura de Software - Dashboard de Proyectos SRNI

**Sistema:** Dashboard de Proyectos SRNI 2026  
**Aplicacion:** `dashboard`  
**Estilo arquitectonico:** Monolito modular Django por dominios  
**Fecha:** Mayo 2026

## 1. Vision General

El sistema es una aplicacion web Django que integra seguimiento de proyectos, colaboradores, cronogramas, evidencias, reportes y administracion de datos. La arquitectura actual corresponde a un monolito modular: una sola aplicacion desplegable, con separacion interna por dominios funcionales.

```txt
Usuario web
   |
   | HTTPS / HTTP
   v
Navegador
   |
   | HTML + CSS + JS / JSON APIs
   v
Django App
   |
   +-- URL routing por modulo
   +-- Vistas HTML y APIs JSON
   +-- Servicios de negocio
   +-- Selectores ORM
   +-- Serializadores
   |
   +-- SQLite db.sqlite3
   +-- media/evidencias/
   +-- staticfiles/ servido por WhiteNoise
```

## 2. Principios Arquitectonicos

- Modularidad por dominio funcional.
- Uso del ORM de Django como capa principal de acceso a datos.
- Templates Django para renderizado inicial de pantallas.
- APIs JSON para interaccion dinamica del frontend.
- Servicios para reglas de negocio y operaciones de escritura.
- Selectores para consultas reutilizables.
- Configuracion declarativa para CRUD generico.
- Autenticacion basada en sesiones de Django.
- Autorizacion por rol y por propiedad del recurso.

## 3. Vista de Componentes

```txt
config/
  settings.py
  urls.py
  wsgi.py
  asgi.py

dashboard/
  routing/
    auth.py
    pages.py
    dashboard.py
    crud.py
    actividades.py
    evidencias.py
    reportes.py

  views.py
    Fachada de importacion para vistas por dominio

  domains/
    auth/
    pages/
    actividades/
    crud/
    evidencias/
    gerencial/
    importacion/
    reportes/

  models/
    organizacion.py
    actividades.py
    evidencias.py
    reportes.py
    cuentas.py
    usuarios.py

  templates/dashboard/
  static/dashboard/
  management/commands/
```

## 4. Capas

### 4.1 Presentacion

Responsable de la experiencia de usuario.

| Elemento | Responsabilidad |
|---|---|
| Templates en `dashboard/templates/dashboard/` | Estructura HTML de pantallas. |
| CSS en `dashboard/static/dashboard/css/` | Estilos por pantalla y layout. |
| JS en `dashboard/static/dashboard/js/` | Consumo de APIs, render dinamico, filtros y acciones. |

Pantallas principales:

- `home.html`
- `dashboard.html`
- `dashboard_view.html`
- `gerencial_view.html`
- `proyecto_detalle.html`
- `consultas_view.html`
- `crud_view.html`
- `carga.html`
- `actividades.html`
- `semana.html`
- `resumen.html`
- `mi_cronograma.html`
- `login.html`

### 4.2 Enrutamiento

`dashboard/urls.py` compone rutas desde archivos especializados en `dashboard/routing/`. Esta decision evita un unico archivo de URLs grande y mantiene agrupacion por modulo.

Ejemplo de grupos:

- Autenticacion: `/login/`, `/logout/`.
- Paginas: `/`, `/dashboard/`, `/gerencial/`, `/crud/`, `/carga/`.
- APIs gerenciales y dashboard: `/api/dashboard/`, `/api/gerencial/`, `/api/proyectos/<pk>/`.
- Actividades: `/actividades/`, `/api/actividades/`, `/mi-cronograma/`.
- Evidencias: `/api/evidencias/...`.
- Reportes: `/api/reporte-semanal/...`.
- CRUD y SQL: `/api/crud/...`, `/api/sql/`.

### 4.3 Controladores HTTP

Las vistas reciben solicitudes, aplican permisos, interpretan parametros, invocan servicios/selectores y retornan HTML o JSON.

`dashboard/views.py` funciona como fachada para conservar importaciones desde `dashboard.views`, mientras la implementacion esta separada en:

- `dashboard/view_modules/`
- `dashboard/domains/*/views.py`

### 4.4 Dominio y Aplicacion

La logica de negocio se organiza en servicios.

| Dominio | Servicios principales |
|---|---|
| `actividades` | Crear actividades, actualizar actividades como admin o colaborador, validar evidencia antes de completar. |
| `crud` | Crear/actualizar objetos por configuracion, ejecutar consultas SELECT seguras. |
| `evidencias` | Validar permisos, tamano de archivo, crear y eliminar evidencias. |
| `gerencial` | Calcular KPIs, compromisos por mes, resumen de proyectos, carga de trabajo y cruce cobro-cumplimiento. |
| `importacion` | Procesar Excel de colaboradores OPS. |
| `reportes` | Guardar o actualizar reporte semanal. |

### 4.5 Acceso a Datos

El acceso a datos se realiza con modelos Django y QuerySets. Los selectores encapsulan consultas reutilizables y ayudan a separar lectura de escritura.

Modelos principales:

```txt
Procedimiento
  ├── Colaborador
  │     ├── Perfil -> User
  │     ├── Obligacion
  │     │     └── Actividad
  │     │           └── EvidenciaActividad
  │     ├── ReporteSemanal
  │     ├── CuentaCobro
  │     └── Asignacion -> Rol + Modulo
  │                         └── Proyecto
  │                               ├── RiesgoProyecto
  │                               ├── AlertaProyecto
  │                               └── ProyectoHistorial
  └── Proyecto
```

## 5. Vista de Datos

### 5.1 Relacion de Proyectos

```txt
Proyecto 1----N Modulo 1----N Asignacion N----1 Colaborador
                         |
                         N----1 Rol

Proyecto 1----N RiesgoProyecto
Proyecto 1----N AlertaProyecto
Proyecto 1----N ProyectoHistorial
Proyecto 1----N Actividad
```

### 5.2 Relacion de Actividades

```txt
Colaborador 1----N Obligacion 1----N Actividad 1----N EvidenciaActividad
Colaborador 1----N ReporteSemanal
Colaborador 1----N CuentaCobro
```

### 5.3 Usuarios y Permisos

```txt
User 1----1 Perfil 0..1----1 Colaborador

Perfil.rol:
  - admin
  - colaborador
```

## 6. Flujos Arquitectonicos

### 6.1 Render de Pantalla con API JSON

```txt
Navegador
  |
  | GET /dashboard/
  v
Django view
  |
  | render template
  v
HTML + JS
  |
  | fetch /api/dashboard/?filtros
  v
API view
  |
  | selectors + services
  v
ORM / SQLite
  |
  | JSON
  v
Frontend actualiza graficos/tablas
```

### 6.2 Actualizacion de Actividad por Colaborador

```txt
PATCH /api/mi-cronograma/<actividad_id>/
  |
  v
Vista valida sesion
  |
  v
Obtiene Perfil.colaborador
  |
  v
Verifica que la actividad pertenezca al colaborador
  |
  v
Servicio actualiza progreso/estado/evidencia textual
  |
  v
Si estado=completada, exige evidencia adjunta
  |
  v
Actividad.save()
  |
  v
Respuesta JSON
```

### 6.3 Subida de Evidencia

```txt
POST multipart /api/evidencias/<actividad_id>/subir/
  |
  v
Vista obtiene actividad
  |
  v
Servicio valida:
  - usuario dueno o admin
  - archivo presente
  - tamano <= 10 MB
  |
  v
EvidenciaActividad.objects.create()
  |
  +-- DB: metadatos
  +-- FS: media/evidencias/YYYY/MM/archivo
```

### 6.4 Dashboard Gerencial

```txt
GET /api/gerencial/
  |
  v
gerencial_payload()
  |
  +-- gerencial_base_stats()
  +-- colaboradores_por_procedimiento_stats()
  +-- compromisos_por_mes()
  +-- resumenes_proyecto()
        |
        +-- avance promedio
        +-- actividades vencidas
        +-- actividades bloqueadas
        +-- cumplimiento mensual
        +-- semaforo
  |
  v
JSON gerencial
```

### 6.5 CRUD Generico

```txt
Frontend CRUD
  |
  | GET /api/crud/meta/
  v
Metadatos desde crud_config.py
  |
  | GET /api/crud/<tabla>/
  | POST /api/crud/<tabla>/crear/
  | PATCH /api/crud/<tabla>/<pk>/
  v
Servicio CRUD
  |
  v
Modelo Django configurado
```

### 6.6 Importacion de Datos

```txt
Excel OPS 2026
  |
  v
procesar_colaboradores_ops()
  |
  +-- normaliza nombres
  +-- filtra Red Nacional
  +-- crea/actualiza Colaborador
  +-- crea Procedimiento

Markdown cronogramas
  |
  v
python manage.py importar_cronogramas
  |
  +-- detecta formato
  +-- parsea tablas
  +-- calcula semanas activas
  +-- crea Obligacion
  +-- crea Actividad
```

## 7. Seguridad

### 7.1 Autenticacion

La autenticacion usa sesiones Django. El usuario inicia sesion con credenciales de `django.contrib.auth.models.User`.

### 7.2 Autorizacion

La autorizacion combina:

- Rol de `Perfil`.
- Estado `is_superuser`.
- Decorador `admin_required`.
- Verificacion de propiedad del colaborador para actividades y evidencias.

```txt
Usuario autenticado
  |
  +-- superuser -> admin
  +-- perfil.rol == admin -> admin
  +-- perfil.rol == colaborador -> acceso propio
```

### 7.3 Proteccion de Escritura

- CSRF activo en Django.
- CRUD administrativo protegido para admin.
- SQL limitado a `SELECT`.
- Evidencias limitadas por tamano y propiedad.
- Validaciones de modelos antes de guardar.

## 8. Despliegue Logico

```txt
Cliente
  |
  v
Servidor web / Tunel HTTPS
  |
  v
Gunicorn
  |
  v
Django WSGI config.wsgi
  |
  +-- SQLite db.sqlite3
  +-- staticfiles/ via WhiteNoise
  +-- media/ para evidencias
```

La configuracion actual incluye `ALLOWED_HOSTS` con `localhost`, `127.0.0.1` y un dominio ngrok. Para produccion debe reemplazarse por el dominio institucional definitivo.

## 9. Calidad y Mantenibilidad

Fortalezas actuales:

- Separacion por dominios.
- Metadatos centralizados para CRUD.
- Validaciones en servicios y modelos.
- Historial automatico de cambios de proyecto.
- Importadores especializados para fuentes existentes.
- Reuso de selectores y serializers por dominio.

Deuda tecnica o puntos de mejora:

- Externalizar secretos y banderas de entorno.
- Declarar `openpyxl` en dependencias si la carga Excel se mantiene.
- Agregar pruebas automatizadas para servicios criticos.
- Cubrir importadores Markdown con fixtures por formato.
- Evaluar PostgreSQL para despliegue productivo.
- Agregar auditoria para consultas SQL administrativas y cambios CRUD.
- Definir backups de `db.sqlite3` y `media/`.

## 10. Decisiones Arquitectonicas

| Decision | Justificacion |
|---|---|
| Monolito Django | El alcance funcional esta cohesionado y se beneficia de despliegue simple. |
| Modularizacion por dominio | Reduce acoplamiento interno y facilita mantenimiento por modulo. |
| Templates + JavaScript vanilla | Evita complejidad de SPA y mantiene integracion directa con Django. |
| APIs JSON para vistas dinamicas | Permite filtros y actualizaciones sin recargar toda la pagina. |
| SQLite actual | Sencillo para desarrollo y operacion inicial. |
| WhiteNoise | Sirve estaticos desde la app sin infraestructura adicional. |
| CRUD por metadatos | Reduce duplicacion para mantenimiento de entidades simples. |
| Servicios para escrituras | Centraliza reglas como evidencia obligatoria, permisos y validaciones. |

## 11. Recomendacion de Arquitectura Objetivo

Para una version productiva institucional, se recomienda evolucionar a:

```txt
Navegador
  |
  v
Reverse proxy HTTPS
  |
  v
Gunicorn + Django
  |
  +-- PostgreSQL
  +-- Almacenamiento persistente para media
  +-- Staticfiles versionados
  +-- Variables de entorno para secretos
  +-- Backups programados
  +-- Logs centralizados
```

Prioridades:

1. Configuracion por entorno: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, base de datos.
2. PostgreSQL si habra concurrencia real o despliegue multiusuario.
3. Backups de base de datos y evidencias.
4. Pruebas de servicios de actividades, evidencias, reportes, CRUD SQL e importadores.
5. Auditoria de operaciones administrativas.
