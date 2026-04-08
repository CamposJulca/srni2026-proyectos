# Arquitectura de Software — SRNI 2026 Dashboard
**Sistema:** Dashboard de Instrumentalización — Subdirección Red Nacional de Información
**Fecha:** Marzo 2026
**Versión:** 1.0

---

## 1. Visión General del Sistema

```mermaid
graph TB
    subgraph Cliente["Navegador Web"]
        HTML["HTML5 Templates"]
        CSS["CSS3 (Vanilla)"]
        JS["JavaScript ES6 (Vanilla)"]
    end

    subgraph Tunel["Túnel ngrok"]
        NGROK["srni-backend.ngrok.io\n:443 HTTPS"]
    end

    subgraph Servidor["Servidor de Aplicación (Linux)"]
        GUNICORN["Gunicorn WSGI\n:8000"]
        DJANGO["Django 6.0.3"]
        WHITENOISE["WhiteNoise\n(archivos estáticos)"]
    end

    subgraph App["Aplicación Django"]
        URLS["URL Router\nurls.py"]
        VIEWS["View Functions\nviews.py"]
        MODELS["Models ORM\nmodels.py"]
        ADMIN["Django Admin\n/admin/"]
        MGMT["Management Commands\nimportar_cronogramas.py"]
    end

    subgraph Datos["Capa de Datos"]
        SQLITE[("SQLite\ndb.sqlite3")]
        MARKDOWN["Archivos Markdown\ndata/Cronogramas_actividades/"]
    end

    Cliente -->|HTTPS / JSON| NGROK
    NGROK -->|HTTP| GUNICORN
    GUNICORN --> DJANGO
    DJANGO --> WHITENOISE
    DJANGO --> App
    URLS --> VIEWS
    VIEWS --> MODELS
    MODELS --> SQLITE
    MGMT -->|Lee .md| MARKDOWN
    MGMT -->|Escribe| SQLITE
```

---

## 2. Arquitectura de Capas

```mermaid
graph LR
    subgraph Frontend["Capa de Presentación"]
        direction TB
        V1["actividades.html\nGantt Chart"]
        V2["semana.html\nVista Semanal"]
        V3["resumen.html\nDashboard Gerencial"]
        V4["dashboard_view.html\nProyectos / Módulos"]
        V5["gerencial_view.html\nDashboard Subdirector"]
        V6["crud_view.html\nGestión de Datos"]
        V7["login.html / home.html"]
    end

    subgraph API["Capa de Negocio (Views)"]
        direction TB
        A1["actividades_data\nactividad_crear\nactividad_detalle"]
        A2["semana_data"]
        A3["resumen_data"]
        A4["dashboard_data\ngerencial_data"]
        A5["crud_meta\ncrud_lista\ncrud_detalle\ncrud_crear"]
        A6["sql_query"]
        A7["carga (Excel import)"]
    end

    subgraph ORM["Capa de Acceso a Datos (ORM)"]
        direction TB
        M1["CronogramaActividad"]
        M2["Proyecto\nModulo"]
        M3["Persona\nRol\nAsignacion"]
        M4["PlanAccion"]
    end

    DB[("SQLite\ndb.sqlite3")]

    V1 & V2 & V3 -->|fetch JSON| A1 & A2 & A3
    V4 & V5 -->|fetch JSON| A4
    V6 -->|fetch JSON| A5
    A6 -->|SQL directo| DB
    A1 & A2 & A3 --> M1
    A4 --> M2 & M3
    A5 --> M2 & M3 & M4
    A7 --> M3
    M1 & M2 & M3 & M4 --> DB
```

---

## 3. Modelo de Datos (ERD)

```mermaid
erDiagram
    Proyecto {
        int id PK
        string nombre
    }

    Modulo {
        int id PK
        int proyecto_id FK
        string nombre
        string referente
    }

    Persona {
        int id PK
        string nombre
        string cedula
        string procedimiento
        date fecha_inicio
        date fecha_fin
        decimal honorarios
        text objeto
        text obligaciones
    }

    Rol {
        int id PK
        string nombre
    }

    Asignacion {
        int id PK
        int modulo_id FK
        int persona_id FK
        int rol_id FK
    }

    PlanAccion {
        int id PK
        int modulo_id FK
        text compromiso
        string mes
    }

    CronogramaActividad {
        int id PK
        string colaborador
        string obligacion
        string actividad_id
        text descripcion
        date fecha_inicio
        date fecha_fin
        int progreso
        string estado
        int orden
        json semanas_activas
    }

    Proyecto ||--o{ Modulo : "tiene"
    Modulo ||--o{ Asignacion : "tiene"
    Modulo ||--o{ PlanAccion : "tiene"
    Persona ||--o{ Asignacion : "participa en"
    Rol ||--o{ Asignacion : "define"
```

---

## 4. Flujo de Petición HTTP

```mermaid
sequenceDiagram
    actor Usuario
    participant Browser as Navegador
    participant ngrok as ngrok (HTTPS)
    participant Gunicorn
    participant Django
    participant View as View Function
    participant ORM
    participant DB as SQLite

    Usuario->>Browser: Accede a /actividades/
    Browser->>ngrok: HTTPS GET
    ngrok->>Gunicorn: HTTP GET
    Gunicorn->>Django: WSGI request
    Django->>Django: Middleware (Auth, CSRF, Session)
    Django->>View: actividades_view(request)
    View->>View: @login_required check
    View->>ORM: CronogramaActividad.objects.values()
    ORM->>DB: SELECT DISTINCT colaborador, obligacion
    DB-->>ORM: rows
    ORM-->>View: QuerySet
    View-->>Django: render(template, context)
    Django-->>Gunicorn: HttpResponse (HTML)
    Gunicorn-->>ngrok: HTTP 200
    ngrok-->>Browser: HTTPS 200
    Browser->>ngrok: HTTPS GET /api/actividades/
    ngrok->>Gunicorn: HTTP GET
    Gunicorn->>Django: WSGI request
    Django->>View: actividades_data(request)
    View->>ORM: CronogramaActividad.objects.filter(...)
    ORM->>DB: SELECT * FROM cronograma WHERE ...
    DB-->>ORM: rows
    ORM-->>View: QuerySet
    View-->>Browser: JsonResponse {tasks: [...]}
    Browser->>Browser: renderGantt(tasks)
```

---

## 5. Flujo de Importación de Cronogramas

```mermaid
flowchart TD
    START([python manage.py importar_cronogramas]) --> LIMPIAR{--limpiar?}
    LIMPIAR -->|Sí| DELETE[DELETE FROM CronogramaActividad]
    LIMPIAR -->|No| SCAN
    DELETE --> SCAN

    SCAN[Escanear data/Cronogramas_actividades/*.md]
    SCAN --> FOREACH[Para cada archivo .md]

    FOREACH --> HEADER[Extraer nombre colaborador del encabezado]
    HEADER --> DETECT{Detectar formato}

    DETECT -->|WBS + fechas| FMT1[Parsear fechas explícitas\nStart/End/%]
    DETECT -->|Secciones + tabla| FMT2[Parsear secciones ### + tabla ✅]
    DETECT -->|Obligación+Actividad| FMT3[Parsear 2 cols fijas + semanas ✅]
    DETECT -->|Tabla plana| FMT4[Parsear # + Actividad + semanas ✅]

    FMT1 & FMT2 & FMT3 & FMT4 --> SEMANAS[Recopilar semanas_activas con ✅]
    SEMANAS --> FECHAS[fecha_inicio = primera semana\nfecha_fin = última semana]
    FECHAS --> SAVE[CronogramaActividad.objects.create]
    SAVE --> FOREACH

    FOREACH --> END([Fin: N actividades importadas])
```

---

## 6. Mapa de URLs

```mermaid
graph LR
    ROOT["/"] --> HOME["home\n(lanzador)"]

    subgraph Auth
        LOGIN["/login/"]
        LOGOUT["/logout/"]
    end

    subgraph Vistas["Vistas Web"]
        DASH["/dashboard/"]
        GER["/gerencial/"]
        CRUD["/crud/"]
        CONS["/consultas/"]
        CARGA["/carga/"]
        ACT["/actividades/"]
        SEM["/actividades/semana/"]
        RES["/actividades/resumen/"]
    end

    subgraph APIs["APIs JSON"]
        ADASH["/api/dashboard/"]
        AGER["/api/gerencial/"]
        ASQL["/api/sql/"]
        ACMETA["/api/crud/meta/"]
        ACLISTA["/api/crud/<tabla>/"]
        ACCREATE["/api/crud/<tabla>/crear/"]
        ACDETALLE["/api/crud/<tabla>/<pk>/"]
        AACT["/api/actividades/"]
        AACTCRE["/api/actividades/crear/"]
        AACTDET["/api/actividades/<pk>/"]
        ASEMANA["/api/actividades/semana/"]
        ARES["/api/actividades/resumen/"]
    end

    ACT -->|fetch| AACT
    ACT -->|POST| AACTCRE
    ACT -->|GET/PUT/DELETE| AACTDET
    SEM -->|fetch| ASEMANA
    RES -->|fetch| ARES
    DASH -->|fetch| ADASH
    GER -->|fetch| AGER
    CRUD -->|fetch| ACMETA & ACLISTA & ACCREATE & ACDETALLE
    CONS -->|POST| ASQL
```

---

## 7. Módulo Actividades — Componentes Frontend

```mermaid
graph TB
    subgraph actividades_html["actividades.html"]
        TOOLBAR["Toolbar\n(filtros + botones)"]
        STATS["Stats Bar\n(KPI badges)"]
        GANTT["Gantt Chart\n(.gantt-scroll-x)"]
        TABLA["Detail Table\n(#tabla-actividades)"]
        MODAL["Modal\n(crear / editar)"]
    end

    subgraph actividades_js["actividades.js"]
        TIMELINE["TIMELINE config\n(2026-01-01 → 2026-12-31)"]
        RENDER_H["renderTimelineHeader()"]
        RENDER_G["renderGantt(tasks)"]
        RENDER_T["renderTabla(tasks)"]
        RENDER_S["renderStats(tasks)"]
        HOY["renderHoyLine()"]
        COLOR["colorColaborador(nombre)"]
        LOAD["cargarDatos()\nGET /api/actividades/"]
        MODAL_JS["abrirModal() / cerrarModal()\nPOST/PUT /api/actividades/"]
    end

    TOOLBAR -->|onChange| LOAD
    LOAD -->|tasks[]| RENDER_G & RENDER_T & RENDER_S
    RENDER_G --> GANTT
    RENDER_T --> TABLA
    RENDER_S --> STATS
    RENDER_H --> GANTT
    HOY --> GANTT
    COLOR --> RENDER_G
    MODAL_JS --> MODAL
    GANTT -->|click bar| MODAL_JS
    TABLA -->|click edit| MODAL_JS
```

---

## 8. Gestión de Autenticación y Sesiones

```mermaid
stateDiagram-v2
    [*] --> NoAutenticado

    NoAutenticado --> Login: GET /login/
    Login --> Autenticado: POST /login/ (credenciales válidas)
    Login --> Login: credenciales inválidas

    Autenticado --> Dashboard: GET /
    Autenticado --> Actividades: GET /actividades/
    Autenticado --> NoAutenticado: GET /logout/

    state Autenticado {
        [*] --> Sesion
        Sesion --> Sesion: Requests con session cookie
        Sesion --> CSRF: POST/PUT/DELETE requiere X-CSRFToken
    }

    NoAutenticado --> Login: @login_required\nredirect → /login/?next=...
```

---

## 9. Dependencias del Proyecto

```mermaid
graph LR
    subgraph Runtime["Dependencias Runtime"]
        DJ["Django 6.0.3\n(framework web)"]
        GU["Gunicorn 25.1.0\n(servidor WSGI)"]
        WN["WhiteNoise 6.12.0\n(archivos estáticos)"]
        AS["asgiref 3.11.1\n(ASGI support)"]
        SP["sqlparse 0.5.5\n(formato SQL)"]
    end

    subgraph Optional["Dependencia Opcional"]
        OP["openpyxl\n(importar Excel)"]
    end

    subgraph Python["Python 3.13+"]
        DJ & GU & WN & AS & SP & OP
    end

    subgraph Frontend["Sin dependencias externas"]
        VJS["Vanilla JS ES6"]
        VCSS["Vanilla CSS3"]
        VH["HTML5"]
    end
```

---

## 10. Despliegue

```mermaid
graph TB
    subgraph Internet
        CLIENTE["Usuario Final\n(Navegador)"]
        NGROK_SVC["Servicio ngrok\n(proxy inverso HTTPS)"]
    end

    subgraph LAN["Red Local / Servidor"]
        NGROK_CLI["ngrok client\n(túnel TCP)"]
        GUNICORN_SVC["Gunicorn\n0.0.0.0:8000"]

        subgraph Django_App["Aplicación Django"]
            SETTINGS["config/settings.py\nDEBUG=True\nSQLITE"]
            STATIC["staticfiles/\n(WhiteNoise)"]
            DB_FILE["db.sqlite3"]
        end
    end

    CLIENTE -->|HTTPS :443| NGROK_SVC
    NGROK_SVC <-->|túnel encriptado| NGROK_CLI
    NGROK_CLI -->|HTTP :8000| GUNICORN_SVC
    GUNICORN_SVC --> Django_App
    SETTINGS --> DB_FILE
    SETTINGS --> STATIC
```

> **Nota de producción:** Para un despliegue productivo se recomienda reemplazar SQLite por PostgreSQL, configurar `DEBUG=False`, usar una `SECRET_KEY` segura y considerar un servidor proxy como Nginx en lugar del túnel ngrok.
