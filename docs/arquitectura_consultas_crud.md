# Arquitectura — Módulos Consultas SQL y Gestión CRUD
**Sistema:** SRNI 2026  
**Fecha:** Abril 2026  

---

## 1. Modelo de datos (ERD completo)

```mermaid
erDiagram
    PROCEDIMIENTO {
        int id PK
        string nombre
    }
    COLABORADOR {
        int id PK
        int procedimiento_id FK
        string nombre
        string cedula
        date fecha_inicio
        date fecha_fin
        decimal honorarios
        text objeto
    }
    OBLIGACION {
        int id PK
        int colaborador_id FK
        text descripcion
    }
    ACTIVIDAD {
        int id PK
        int obligacion_id FK
        int proyecto_id FK
        string actividad_id
        text descripcion
        date fecha_inicio
        date fecha_fin
        int progreso
        string estado
        int orden
        json semanas_activas
    }
    ROL {
        int id PK
        string nombre
    }
    PROYECTO {
        int id PK
        string nombre
    }
    MODULO {
        int id PK
        int proyecto_id FK
        string nombre
        string referente
    }
    ASIGNACION {
        int id PK
        int colaborador_id FK
        int rol_id FK
        int modulo_id FK
    }

    PROCEDIMIENTO ||--o{ COLABORADOR : "pertenece a"
    COLABORADOR   ||--o{ OBLIGACION  : "tiene"
    OBLIGACION    ||--o{ ACTIVIDAD   : "genera"
    PROYECTO      ||--o{ MODULO      : "contiene"
    PROYECTO      ||--o{ ACTIVIDAD   : "referencia (opcional)"
    COLABORADOR   ||--o{ ASIGNACION  : "participa en"
    ROL           ||--o{ ASIGNACION  : "define rol"
    MODULO        ||--o{ ASIGNACION  : "asignado a"
```

---

## 2. Arquitectura del módulo Consultas SQL

### 2.1 Flujo completo de la aplicación

```mermaid
flowchart TD
    U([Usuario]) -->|GET /consultas/| V[consultas_view]
    V -->|render| T[consultas_view.html]
    T -->|load| JS[consultas.js]

    JS -->|DOMContentLoaded| TAB{Tab activo}
    TAB -->|ERD tab| ERD[dibujarConexionesERD]
    TAB -->|SQL tab| SQL[Panel SQL]

    ERD -->|getBoundingClientRect| DOM[DOM: 8 divs .eT]
    ERD -->|genera paths SVG| SVG[svg#erd-svg]

    SQL -->|click tabla sidebar| Q1[cargarQuery + activarTabSQL]
    SQL -->|click consulta sugerida| Q2[cargarQuery + ejecutarQuery]
    SQL -->|Ctrl+Enter / btnEjecutar| EJ[ejecutarQuery]

    EJ -->|POST /api/sql/| API[sql_query view]
    API -->|validar SELECT| SEC{¿Es SELECT?}
    SEC -->|No| ERR1[403 Solo SELECT]
    SEC -->|Sí| SEC2{¿Palabras peligrosas?}
    SEC2 -->|Sí| ERR2[403 Operación no permitida]
    SEC2 -->|No| DB[(SQLite)]
    DB -->|fetchmany 500| RES[JSON columnas + filas]
    RES -->|renderTabla| TABLE[Tabla resultados]
    TABLE -->|btnExportar| CSV[Archivo .csv]
```

### 2.2 Estructura de componentes del tab ERD

```mermaid
graph LR
    subgraph HTML ["DOM: #erd-wrap (position: relative)"]
        SVG["svg#erd-svg\n(overlay, z-index:0)"]
        subgraph Row1 ["Fila 1 (top: 0)"]
            P["eT-procedimiento\nx=0"]
            C["eT-colaborador\nx=205px"]
            O["eT-obligacion\nx=410px"]
            A["eT-actividad\nx=615px"]
        end
        subgraph Row2 ["Fila 2 (top: 400px)"]
            R["eT-rol\nx=0"]
            AS["eT-asignacion\nx=205px"]
            M["eT-modulo\nx=410px"]
            PR["eT-proyecto\nx=615px"]
        end
    end

    C -->|"L→R morado"| P
    O -->|"L→R morado"| C
    A -->|"L→R morado"| O
    A -->|"B→T verde"| PR
    AS -->|"T→B morado"| C
    AS -->|"R→L morado"| M
    AS -->|"L→R morado"| R
    M -->|"R→L morado"| PR
```

---

## 3. Arquitectura del módulo Gestión CRUD

### 3.1 Flujo de inicio y carga inicial

```mermaid
sequenceDiagram
    actor U as Usuario
    participant B as Browser
    participant DJ as Django (Gunicorn)
    participant DB as SQLite

    U->>B: GET /crud/
    B->>DJ: HTTP GET /crud/
    DJ-->>B: crud_view.html (sidebar + layout vacío)

    B->>B: DOMContentLoaded → async init()
    B->>DJ: GET /api/crud/meta/
    DJ->>DB: COUNT(*) × 6 tablas + SELECT FK opciones
    DB-->>DJ: datos
    DJ-->>B: JSON { colaborador, obligacion, ... }

    B->>B: renderSidebarCounts()
    B->>B: rellenarFiltroColaborador()
    B->>B: selectEntidad("colaborador")
    B->>DJ: GET /api/crud/colaborador/?page=1
    DJ->>DB: SELECT ... FROM dashboard_colaborador LIMIT 25
    DB-->>DJ: 25 filas
    DJ-->>B: JSON { filas, total, page, size }
    B->>B: renderTabla() → puebla thead + tbody
```

### 3.2 Flujo de operaciones CRUD

```mermaid
stateDiagram-v2
    [*] --> Lista : selectEntidad(tabla)

    Lista --> ModalEditar : click ✏ btn-editar
    Lista --> ModalCrear  : click + Nuevo
    Lista --> ModalBorrar : click 🗑 btn-borrar

    ModalCrear --> Guardando : click Guardar (POST /crear/)
    ModalEditar --> Guardando : click Guardar (PUT /<pk>/)
    ModalBorrar --> Borrando  : click Sí eliminar (DELETE /<pk>/)

    Guardando --> Lista : OK → toast verde + reload
    Guardando --> ModalCrear : error → toast rojo
    Guardando --> ModalEditar : error → toast rojo

    Borrando --> Lista : OK → toast verde + reload
    Borrando --> Lista : error → toast rojo

    Lista --> Lista : búsqueda (debounce 350ms)
    Lista --> Lista : filtro colaborador
    Lista --> Lista : paginación
```

### 3.3 Registro de entidades (TABLA_META)

```mermaid
classDiagram
    class TABLA_META {
        +colaborador : EntidadMeta
        +obligacion  : EntidadMeta
        +actividad   : EntidadMeta
        +asignacion  : EntidadMeta
        +modulo      : EntidadMeta
        +rol         : EntidadMeta
    }

    class EntidadMeta {
        +modelo : Model
        +label  : str
        +buscar_en : list~str~
        +filtro_colaborador : bool
        +campos : list~CampoMeta~
        +columnas_lista : list~str~
    }

    class CampoMeta {
        +name : str
        +label : str
        +type : "text|number|date|textarea|fk|choice"
        +required : bool
        +fk_modelo : str
        +opciones_fijas : list
    }

    TABLA_META "1" --> "6" EntidadMeta
    EntidadMeta "1" --> "1..n" CampoMeta
```

### 3.4 API REST del módulo CRUD

```mermaid
graph LR
    subgraph URLs ["urls.py"]
        U1["GET  /api/crud/meta/"]
        U2["GET  /api/crud/tabla/"]
        U3["GET  /api/crud/tabla/pk/"]
        U4["PUT  /api/crud/tabla/pk/"]
        U5["DELETE /api/crud/tabla/pk/"]
        U6["POST /api/crud/tabla/crear/"]
    end

    subgraph Views ["views.py"]
        V1[crud_meta]
        V2[crud_lista]
        V3[crud_detalle GET]
        V4[crud_detalle PUT]
        V5[crud_detalle DELETE]
        V6[crud_crear]
    end

    U1 --> V1
    U2 --> V2
    U3 --> V3
    U4 --> V4
    U5 --> V5
    U6 --> V6

    V1 -->|"{ label, campos, columnas, total }"| R1[JSON meta]
    V2 -->|"{ filas[], total, page, size }"| R2[JSON lista paginada]
    V3 -->|"{ campo: valor, ... }"| R3[JSON un registro]
    V4 -->|"{ ok: true, id }"| R4[JSON confirmación]
    V5 -->|"{ ok: true }"| R5[JSON confirmación]
    V6 -->|"{ ok: true, id }"| R6[JSON nuevo id]
```

---

## 4. Arquitectura de archivos estáticos

```mermaid
graph TD
    subgraph SRC ["Fuentes (dashboard/static/)"]
        CSS["dashboard.css\n~2400 líneas\nEstilos globales + CRUD + ERD"]
        CJS["consultas.js\n~350 líneas\nERD + SQL editor"]
        CJSR["crud.js\n~300 líneas\nMulti-entidad CRUD"]
    end

    subgraph DIST ["Distribución (staticfiles/)"]
        SCSS["dashboard.css\n(copia hashed)"]
        SCJS["consultas.js"]
        SCJSR["crud.js"]
    end

    CSS -->|collectstatic| SCSS
    CJS -->|collectstatic| SCJS
    CJSR -->|collectstatic| SCJSR

    SCSS -->|WhiteNoise| Browser
    SCJS -->|WhiteNoise| Browser
    SCJSR -->|WhiteNoise| Browser
```

---

## 5. Despliegue y proceso de actualización

```mermaid
flowchart LR
    DEV[Desarrollador\nedita código] --> VIEWS[views.py\nmodificado]
    DEV --> STATIC[CSS / JS\nmodificado]

    VIEWS -->|"kill -HUP <pid>"| GUN[Gunicorn\nrecarga workers]
    STATIC -->|"python manage.py\ncollectstatic"| WN[WhiteNoise\narchivos nuevos]

    GUN --> PROD[Producción\nactualizada]
    WN --> PROD
```

---

## 6. Seguridad

```mermaid
flowchart TD
    REQ[Request del usuario] --> AUTH{¿Sesión válida?}
    AUTH -->|No| REDIR[Redirect /login/]
    AUTH -->|Sí| TIPO{Tipo de módulo}

    TIPO -->|Consultas SQL| SQL_SEC
    TIPO -->|CRUD| CRUD_SEC

    subgraph SQL_SEC ["Seguridad SQL"]
        S1{¿Primera palabra\nes SELECT?}
        S1 -->|No| E1[403 Bloqueado]
        S1 -->|Sí| S2{¿Contiene palabras\npeligrosas?}
        S2 -->|Sí| E2[403 Bloqueado]
        S2 -->|No| S3[Ejecutar en DB\nfetchmany 500]
    end

    subgraph CRUD_SEC ["Seguridad CRUD"]
        C1{¿Tabla válida\nen TABLA_META?}
        C1 -->|No| E3[404 No válida]
        C1 -->|Sí| C2{¿Método HTTP?}
        C2 -->|GET| C3[Lista / Detalle]
        C2 -->|POST/PUT| C4[CSRF Token\nvalidado por middleware]
        C2 -->|DELETE| C4
        C4 --> C5[Operación en DB]
        C5 -->|FK violation| E4[400 Error cascada]
        C5 -->|OK| C6[JSON ok: true]
    end
```
