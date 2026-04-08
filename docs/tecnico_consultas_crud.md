# Documento Técnico — Módulos `/consultas/` y `/crud/`
**Sistema:** SRNI 2026 — Dashboard de Gestión de Contratos  
**URL base:** `https://srni-backend.ngrok.io`  
**Fecha:** Abril 2026  
**Versión:** 1.0  

---

## 1. Resumen

Este documento describe la implementación técnica de dos módulos del sistema SRNI 2026:

| Módulo | URL | Propósito |
|--------|-----|-----------|
| Consultas SQL | `/consultas/` | Exploración del modelo de datos mediante diagrama ERD interactivo y editor SQL |
| Gestión CRUD | `/crud/` | Creación, lectura, actualización y eliminación de registros en las entidades del sistema |

Ambos módulos son de uso interno, accesibles únicamente con sesión autenticada.

---

## 2. Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | Django 4.x + Python 3.12 |
| Base de datos | SQLite 3 (producción local) |
| Servidor | Gunicorn 3 workers — puerto 8085 |
| Frontend | HTML5 + CSS3 + Vanilla JavaScript (ES2020) |
| Archivos estáticos | WhiteNoise + `collectstatic` |
| Autenticación | Django sessions (`SessionMiddleware`) |

---

## 3. Módulo Consultas SQL (`/consultas/`)

### 3.1 Archivos involucrados

```
dashboard/
├── views.py                              → vistas: consultas_view, sql_query
├── urls.py                               → path("consultas/"), path("api/sql/")
├── templates/dashboard/
│   └── consultas_view.html              → layout principal (tabs ERD + SQL)
└── static/dashboard/
    ├── css/dashboard.css                 → estilos ERD, tabs, tabla de resultados
    └── js/consultas.js                   → lógica tabs, ERD SVG, editor, exportar CSV
```

### 3.2 Vista principal

```python
# dashboard/views.py
@login_required
def consultas_view(request):
    return render(request, "dashboard/consultas_view.html", {
        "modulo_activo": "consultas"
    })
```

### 3.3 API de ejecución SQL

**Endpoint:** `POST /api/sql/`  
**Vista:** `sql_query(request)`  
**Autenticación requerida:** No (protegida por whitelist de operaciones)

#### Flujo de ejecución

```
Cliente → POST /api/sql/ { query: "SELECT ..." }
         ↓
    Validar primera palabra == "SELECT"
         ↓
    Buscar palabras peligrosas (INSERT, UPDATE, DELETE, DROP, ALTER, ...)
         ↓
    connection.cursor().execute(query)
         ↓
    cursor.fetchmany(500)          ← máximo 500 filas
         ↓
    JSON { columnas, filas, total }
```

#### Request

```json
POST /api/sql/
Content-Type: application/json
X-CSRFToken: <token>

{ "query": "SELECT * FROM dashboard_colaborador LIMIT 10;" }
```

#### Response exitoso

```json
{
  "columnas": ["id", "nombre", "cedula", "procedimiento_id", "..."],
  "filas": [
    [1, "JUAN GARCIA", "12345678", 20, "..."],
    ...
  ],
  "total": 10
}
```

#### Response con error

```json
{ "error": "no such column: foo" }
```

#### Seguridad

```python
# Solo permite SELECT
primera_palabra = re.split(r'\s+', query)[0].upper()
if primera_palabra != "SELECT":
    return JsonResponse({"error": "Solo se permiten consultas SELECT."}, status=403)

# Bloquea palabras peligrosas en subconsultas
peligrosas = r'\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|REPLACE|ATTACH|DETACH|PRAGMA)\b'
if re.search(peligrosas, query, re.IGNORECASE):
    return JsonResponse({"error": "..."}, status=403)
```

### 3.4 Diagrama ERD — implementación

El ERD se dibuja en JavaScript mediante SVG sobre un contenedor con posicionamiento absoluto.

**Estructura DOM:**
```html
<div class="erd-wrap" id="erd-wrap">          <!-- posición: relative -->
  <svg id="erd-svg" class="erd-svg">          <!-- overlay, z-index: 0 -->
    <defs>...</defs>
    <path d="M... C..." />                    <!-- bezier por cada FK -->
  </svg>
  <div class="eT" id="eT-colaborador">...</div>   <!-- posición: absolute -->
  <div class="eT" id="eT-obligacion">...</div>
  <!-- ... 8 tablas en total ... -->
</div>
```

**Algoritmo de conexión:**
```javascript
function dibujarConexionesERD() {
  // 1. Lee BoundingRect de cada .eT relativo al #erd-wrap
  // 2. Calcula puntos de anclaje (L/R/T/B de cada caja)
  // 3. Genera curva cúbica Bezier: M x1,y1 C cx1,cy1 cx2,cy2 x2,y2
  // 4. Asigna color: morado (#7c3aed) = FK obligatoria, verde (#22c55e) = FK opcional
  // 5. Aplica marker-end con arrowhead SVG
}
```

**Conexiones definidas:**

| Desde | Lado | Hacia | Lado | Tipo |
|-------|------|-------|------|------|
| Colaborador | L | Procedimiento | R | FK obligatoria |
| Obligación | L | Colaborador | R | FK obligatoria |
| Actividad | L | Obligación | R | FK obligatoria |
| Actividad | B | Proyecto | T | FK opcional |
| Asignación | T | Colaborador | B | FK obligatoria |
| Asignación | R | Módulo | L | FK obligatoria |
| Asignación | L | Rol | R | FK obligatoria |
| Módulo | R | Proyecto | L | FK obligatoria |

### 3.5 Consultas sugeridas

Definidas en el template como atributo `data-query` en botones `.sugerida-btn`. Al hacer clic, el JS activa el tab SQL, carga la query en el textarea y la ejecuta automáticamente.

### 3.6 Exportación CSV

```javascript
// Genera CSV con BOM UTF-8 (compatible con Excel en español)
const blob = new Blob(["\uFEFF" + lineas.join("\n")], { type: "text/csv;charset=utf-8;" })
a.download = `consulta_srni_${new Date().toISOString().slice(0, 10)}.csv`
```

---

## 4. Módulo Gestión CRUD (`/crud/`)

### 4.1 Archivos involucrados

```
dashboard/
├── views.py                              → crud_main_view, crud_meta, crud_lista,
│                                           crud_detalle, crud_crear
├── urls.py                               → 4 rutas CRUD + meta
├── templates/dashboard/
│   └── crud_view.html                   → layout sidebar + main + modales
└── static/dashboard/
    ├── css/dashboard.css                 → estilos sidebar, tabla, badges, form
    └── js/crud.js                        → lógica completa multi-entidad
```

### 4.2 Registro de entidades — `TABLA_META`

Diccionario central en `views.py` que define para cada entidad:

```python
TABLA_META = {
    "colaborador": {
        "modelo": Colaborador,           # modelo Django
        "label": "Colaboradores",        # etiqueta UI
        "buscar_en": ["nombre", "cedula"], # campos de búsqueda
        "filtro_colaborador": False,     # muestra filtro adicional
        "campos": [...],                 # definición de campos del formulario
        "columnas_lista": [...],         # columnas visibles en la tabla
    },
    "obligacion": { ... },
    "actividad":  { ... },
    "asignacion": { ... },
    "modulo":     { ... },
    "rol":        { ... },
}
```

**Tipos de campo soportados:**

| `type` | Control HTML | Descripción |
|--------|-------------|-------------|
| `text` | `<input type="text">` | Texto libre |
| `number` | `<input type="number">` | Numérico |
| `date` | `<input type="date">` | Selector de fecha |
| `textarea` | `<textarea>` | Texto largo |
| `fk` | `<select>` | FK cargada desde `_opciones_fk()` |
| `choice` | `<select>` | Opciones fijas (`opciones_fijas`) |

### 4.3 API endpoints

#### `GET /api/crud/meta/`

Devuelve metadatos de todas las entidades: campos, opciones FK, columnas, totales.

```json
{
  "colaborador": {
    "label": "Colaboradores",
    "campos": [
      { "name": "nombre", "label": "Nombre completo", "type": "text", "required": true },
      { "name": "procedimiento_id", "label": "Procedimiento", "type": "fk",
        "opciones": [{ "id": 20, "label": "INSTRUMENTALIZACIÓN" }, ...] },
      ...
    ],
    "columnas": ["nombre", "cedula", "procedimiento__nombre", "fecha_inicio", "..."],
    "filtro_colaborador": false,
    "total": 93
  },
  ...
}
```

#### `GET /api/crud/<tabla>/`

Lista paginada de registros. Parámetros:

| Parámetro | Aplica a | Descripción |
|-----------|----------|-------------|
| `page` | todas | Página (25 registros/página) |
| `q` | todas | Búsqueda libre en `buscar_en` |
| `proc` | colaborador | Filtrar por nombre de procedimiento |
| `colaborador` | obligacion, actividad | Filtrar por `colaborador_id` |

```json
{
  "filas": [{ "id": 1, "nombre": "JUAN GARCIA", "cedula": "...", ... }],
  "total": 93,
  "page": 1,
  "size": 25
}
```

#### `GET /api/crud/<tabla>/<pk>/`

Devuelve un registro para pre-llenar el formulario de edición.

#### `PUT /api/crud/<tabla>/<pk>/`

Actualiza un registro. Body: JSON con los campos del modelo.

#### `DELETE /api/crud/<tabla>/<pk>/`

Elimina un registro. Respeta las restricciones de FK en cascada de Django.

#### `POST /api/crud/<tabla>/crear/`

Crea un nuevo registro. Body: JSON con los campos del modelo.

### 4.4 Función `_opciones_fk`

```python
def _opciones_fk(modelo, campo_display="nombre"):
    try:
        qs = modelo.objects.all().order_by(campo_display)
        return [{"id": o.pk, "label": str(getattr(o, campo_display, None) or o)}
                for o in qs]
    except Exception:
        # Fallback para modelos sin campo 'nombre' (ej. Obligacion)
        return [{"id": o.pk, "label": str(o)} for o in modelo.objects.all()]
```

### 4.5 Serialización de filas — `_serializar_fila`

Soporta traversal de relaciones con `__`:

```python
# Ejemplo: columna "obligacion__colaborador__nombre"
val = obj
for parte in ["obligacion", "colaborador", "nombre"]:
    val = getattr(val, parte, None)
    if val is None: break
```

### 4.6 Frontend — flujo JavaScript

```
DOMContentLoaded
    │
    ├─ fetch /api/crud/meta/         → META = {}
    │
    ├─ renderSidebarCounts()         → actualiza badges del sidebar
    ├─ rellenarFiltroColaborador()   → puebla <select> de colaboradores
    ├─ bindSidebar()                 → eventos click en items del sidebar
    ├─ bindToolbar()                 → búsqueda, filtro, botón Nuevo
    ├─ bindModales()                 → modal crear/editar + modal borrar
    │
    └─ selectEntidad("colaborador")
            │
            └─ cargarLista()
                    │
                    ├─ fetch /api/crud/<tabla>/?page=N&q=...&colaborador=...
                    ├─ renderTabla(cfg, filas, total, page, size)
                    └─ renderPaginacion(total, page, size)
```

**Renderizado dinámico del formulario:**

```javascript
function renderForm(datos, preColaborador) {
  // Itera cfg.campos desde META
  // Para type="fk" o "choice": genera <select> con opciones de META
  // Para type="textarea": genera <textarea rows="3">
  // Para otros: genera <input type="text|number|date">
  // Si hay preColaborador activo, pre-rellena el campo colaborador_id
}
```

---

## 5. URLs registradas

```python
# dashboard/urls.py
path("consultas/",               views.consultas_view,  name="consultas"),
path("crud/",                    views.crud_main_view,  name="crud_main"),

path("api/sql/",                 views.sql_query,       name="sql_query"),
path("api/crud/meta/",           views.crud_meta,       name="crud_meta"),
path("api/crud/<str:tabla>/",    views.crud_lista,      name="crud_lista"),
path("api/crud/<str:tabla>/crear/",       views.crud_crear,   name="crud_crear"),
path("api/crud/<str:tabla>/<int:pk>/",    views.crud_detalle, name="crud_detalle"),
```

---

## 6. Modelos involucrados

```
Procedimiento  ←── Colaborador ←── Obligacion ←── Actividad
                        ↑               
                   Asignacion ──→ Rol
                        ↓
                      Modulo ──→ Proyecto
```

| Modelo | Tabla DB | Registros actuales |
|--------|----------|--------------------|
| Procedimiento | dashboard_procedimiento | 8 |
| Colaborador | dashboard_colaborador | 93 |
| Obligacion | dashboard_obligacion | 232 |
| Actividad | dashboard_actividad | 208 |
| Rol | dashboard_rol | 13 |
| Asignacion | dashboard_asignacion | 57 |
| Modulo | dashboard_modulo | 22 |
| Proyecto | dashboard_proyecto | 6 |

---

## 7. Consideraciones de despliegue

- **Cambios en `views.py`** requieren `kill -HUP <pid_master_gunicorn>` para que gunicorn recargue el código.
- **Cambios en CSS/JS** requieren `python manage.py collectstatic --noinput` para que WhiteNoise sirva los nuevos archivos.
- El PID del master de gunicorn para este proyecto es consultable con:  
  `ps aux | grep "srni2026-proyectos.*gunicorn" | grep -v worker`
