# Arquitectura de Software - Dashboard de Proyectos SRNI

---

## 1. Vista general del sistema

```mermaid
graph TD
    Usuario["Navegador / Usuario"]
    Django["Servidor Django"]
    SQLite["Base de datos SQLite"]
    Excel["data/matriz_proyectos.xlsx"]
    ChartJS["Chart.js (CDN)"]

    Usuario -->|"HTTP GET /"| Django
    Usuario -->|"HTTP GET /api/dashboard/"| Django
    Django -->|"Consultas ORM"| SQLite
    Excel -->|"Carga manual via admin"| SQLite
    Usuario -->|"Carga estatica"| ChartJS
```

---

## 2. Arquitectura de capas

```mermaid
graph TD
    subgraph Frontend
        HTML["dashboard.html"]
        CSS["dashboard.css"]
        JS["dashboard.js"]
        Charts["Chart.js"]
    end

    subgraph Backend["Backend (Django)"]
        URLs["urls.py (Router)"]
        Views["views.py"]
        Models["models.py (ORM)"]
        Admin["admin.py"]
    end

    subgraph Persistencia
        DB["db.sqlite3"]
    end

    HTML --> CSS
    HTML --> JS
    JS --> Charts
    JS -->|"fetch /api/dashboard/"| Views
    HTML -->|"GET /"| Views
    Views --> Models
    Models --> DB
    Admin --> Models
```

---

## 3. Modelo de datos (Entidad-Relacion)

```mermaid
erDiagram
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

    PERSONA {
        int id PK
        string nombre
    }

    ROL {
        int id PK
        string nombre
    }

    ASIGNACION {
        int id PK
        int modulo_id FK
        int persona_id FK
        int rol_id FK
    }

    PLANACCION {
        int id PK
        int modulo_id FK
        string compromiso
        string mes
    }

    PROYECTO ||--o{ MODULO : "tiene"
    MODULO ||--o{ ASIGNACION : "tiene"
    MODULO ||--o{ PLANACCION : "tiene"
    PERSONA ||--o{ ASIGNACION : "participa en"
    ROL ||--o{ ASIGNACION : "define"
```

---

## 4. Flujo de datos - Carga del dashboard

```mermaid
sequenceDiagram
    actor Usuario
    participant HTML as dashboard.html
    participant JS as dashboard.js
    participant Django as views.py
    participant ORM as models.py / ORM
    participant DB as SQLite

    Usuario->>HTML: Abre la pagina (GET /)
    HTML->>Django: Solicita vista dashboard()
    Django->>ORM: Persona.objects.all()
    Django->>ORM: Rol.objects.all()
    Django->>ORM: Proyecto.objects.all()
    ORM->>DB: SELECT
    DB-->>ORM: Resultados
    ORM-->>Django: QuerySets
    Django-->>HTML: Renderiza template con contexto

    HTML->>JS: DOMContentLoaded
    JS->>Django: fetch GET /api/dashboard/
    Django->>ORM: Asignacion, Modulo, PlanAccion queries
    ORM->>DB: SELECT + COUNT + GROUP BY
    DB-->>ORM: Resultados agregados
    ORM-->>Django: QuerySets
    Django-->>JS: JsonResponse

    JS->>JS: actualizarKPIs()
    JS->>JS: graficoPersonas()
    JS->>JS: graficoRoles()
    JS->>JS: graficoModulos()
    JS->>JS: graficoMes()
```

---

## 5. Flujo de datos - Filtros

```mermaid
sequenceDiagram
    actor Usuario
    participant HTML as Selectores (filtros)
    participant JS as dashboard.js
    participant API as GET /api/dashboard/
    participant Django as views.py / ORM

    Usuario->>HTML: Cambia filtro (persona / rol / proyecto)
    HTML->>JS: Evento change
    JS->>JS: cargarDashboard()
    JS->>API: fetch con ?persona=&rol=&proyecto=
    API->>Django: dashboard_data(request)
    Django->>Django: Filtra Asignacion.objects por parametros
    Django-->>JS: JSON actualizado
    JS->>JS: Destruye graficos anteriores
    JS->>JS: Renderiza nuevos graficos
```

---

## 6. Flujo - Modal de obligaciones

```mermaid
sequenceDiagram
    actor Usuario
    participant Canvas as graficoPersonas (Chart.js)
    participant JS as dashboard.js
    participant Modal as Modal HTML

    Usuario->>Canvas: Clic en barra de una persona
    Canvas->>JS: canvas.onclick event
    JS->>JS: getElementsAtEventForMode()
    JS->>JS: Obtiene nombre de la persona (labels[index])
    JS->>JS: abrirModal(nombre)
    JS->>JS: Busca en objeto "obligaciones"
    JS->>Modal: Inyecta nombre y lista de obligaciones
    Modal-->>Usuario: Muestra modal con obligaciones
```

---

## 7. Estructura de URLs

```mermaid
graph LR
    Root["/ (raiz)"]
    API["/api/dashboard/"]

    Root -->|"views.dashboard"| V1["Renderiza dashboard.html\nContexto: personas, roles, proyectos"]
    API -->|"views.dashboard_data"| V2["Retorna JSON\nKPIs + datos de graficos"]
```

---

## 8. Componentes del frontend

```mermaid
graph TD
    subgraph dashboard.html
        Filtros["Filtros (3 select)"]
        KPIs["KPI Cards (4 tarjetas)"]
        G1["Canvas: graficoPersonas"]
        G2["Canvas: graficoRoles"]
        G3["Canvas: graficoModulos"]
        G4["Canvas: graficoMes"]
        Modal["Modal: obligaciones por persona"]
    end

    subgraph dashboard.js
        cargarDashboard["cargarDashboard()"]
        actualizarKPIs["actualizarKPIs()"]
        fnPersonas["graficoPersonas()"]
        fnRoles["graficoRoles()"]
        fnModulos["graficoModulos()"]
        fnMes["graficoMes()"]
        abrirModal["abrirModal()"]
        obligaciones["const obligaciones{}"]
    end

    Filtros -->|"change event"| cargarDashboard
    cargarDashboard --> actualizarKPIs
    cargarDashboard --> fnPersonas
    cargarDashboard --> fnRoles
    cargarDashboard --> fnModulos
    cargarDashboard --> fnMes

    actualizarKPIs --> KPIs
    fnPersonas --> G1
    fnRoles --> G2
    fnModulos --> G3
    fnMes --> G4

    G1 -->|"click"| abrirModal
    abrirModal --> obligaciones
    abrirModal --> Modal
```

---

## 9. Despliegue (desarrollo)

```mermaid
graph LR
    Dev["Desarrollador"]
    Venv["venv (Python 3.13)"]
    Django["python manage.py runserver"]
    Browser["Navegador :8000"]

    Dev --> Venv
    Venv --> Django
    Django --> Browser
```
