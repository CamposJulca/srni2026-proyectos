# Documento Técnico — Módulo `/actividades/`
**Sistema:** SRNI 2026 — Dashboard de Instrumentalización
**URL base:** `https://srni-backend.ngrok.io/actividades/`
**Fecha:** Marzo 2026
**Versión:** 1.0

---

## 1. Visión General

El módulo de actividades expone tres vistas web y cuatro endpoints de API REST que permiten crear, consultar, actualizar y eliminar actividades del cronograma de los colaboradores del equipo SRNI. El modelo central es `CronogramaActividad`, introducido en la migración `0004` y extendido con el campo `semanas_activas` en `0005`.

---

## 2. Modelo de Datos

### 2.1 `CronogramaActividad` (`dashboard/models.py`)

| Campo | Tipo Django | Notas |
|---|---|---|
| `id` | AutoField (PK) | |
| `colaborador` | CharField(200) | `db_index=True` |
| `obligacion` | CharField(200) | |
| `actividad_id` | CharField(20) | Código WBS p.ej. `"1.1"` |
| `descripcion` | TextField | |
| `fecha_inicio` | DateField | |
| `fecha_fin` | DateField | |
| `progreso` | IntegerField | 0 – 100 |
| `estado` | CharField(20) | `pendiente` · `en_curso` · `completada` · `bloqueada` |
| `orden` | IntegerField | Orden de despliegue |
| `semanas_activas` | JSONField | Lista de códigos de semana: `["ENE S1", "MAR S2", …]` |

**Orden por defecto:** `['colaborador', 'orden', 'fecha_inicio']`

### 2.2 Lógica de `estado_visual`

El campo `estado` almacena el estado manual. Las vistas API calculan un `estado_visual` adicional en tiempo real:

```python
if fecha_fin < hoy:
    estado_visual = "vencida"
elif fecha_inicio <= hoy <= fecha_fin:
    estado_visual = "en_curso"
else:
    estado_visual = estado  # valor guardado en BD
```

### 2.3 Estructura de `semanas_activas`

Cada actividad almacena exactamente las semanas donde hay trabajo comprometido (sin inferir huecos). Ejemplo:

```json
["ENE S3", "ENE S4", "FEB S1", "FEB S2", "MAR S4"]
```

El mapa completo de 52 semanas (`SEMANA_FECHAS`) se define en `views.py` y mapea cada código a su rango `(lunes, viernes)`:

```python
SEMANA_FECHAS = {
    'ENE S1': ('2026-01-05', '2026-01-09'),
    'ENE S2': ('2026-01-12', '2026-01-16'),
    # … 50 semanas más …
    'DIC S4': ('2026-12-21', '2026-12-25'),
}
```

---

## 3. Endpoints

### 3.1 Resumen de rutas (`dashboard/urls.py`)

| Método | URL | Función | Requiere login |
|---|---|---|---|
| GET | `/actividades/` | `actividades_view` | ✅ |
| GET | `/actividades/semana/` | `semana_view` | ✅ |
| GET | `/actividades/resumen/` | `resumen_view` | ✅ |
| GET | `/api/actividades/` | `actividades_data` | ✅ |
| POST | `/api/actividades/crear/` | `actividad_crear` | ✅ |
| GET/PUT/PATCH/DELETE | `/api/actividades/<pk>/` | `actividad_detalle` | ✅ |
| GET | `/api/actividades/semana/` | `semana_data` | ✅ |
| GET | `/api/actividades/resumen/` | `resumen_data` | ✅ |

---

### 3.2 `GET /api/actividades/`

**Función:** `actividades_data(request)`

#### Query params opcionales

| Parámetro | Tipo | Descripción |
|---|---|---|
| `colaborador` | string | Filtro exacto por nombre |
| `estado` | string | `pendiente` · `en_curso` · `completada` · `bloqueada` |
| `obligacion` | string | Filtro exacto por obligación |

#### Respuesta `200 OK`

```json
{
  "tasks": [
    {
      "id": 42,
      "colaborador": "Ana Gómez",
      "obligacion": "Análisis de datos",
      "actividad_id": "2.3",
      "descripcion": "Consolidar matriz de indicadores",
      "fecha_inicio": "2026-03-23",
      "fecha_fin": "2026-06-30",
      "progreso": 15,
      "estado": "pendiente",
      "estado_visual": "en_curso"
    }
  ]
}
```

---

### 3.3 `POST /api/actividades/crear/`

**Función:** `actividad_crear(request)`

#### Headers requeridos

```
Content-Type: application/json
X-CSRFToken: <token>
```

#### Cuerpo de solicitud

```json
{
  "colaborador": "Ana Gómez",
  "obligacion": "Análisis de datos",
  "actividad_id": "2.3",
  "descripcion": "Consolidar matriz de indicadores",
  "fecha_inicio": "2026-03-23",
  "fecha_fin": "2026-06-30",
  "progreso": 0,
  "estado": "pendiente"
}
```

| Campo | Requerido | Notas |
|---|---|---|
| `colaborador` | ✅ | |
| `obligacion` | ✅ | |
| `descripcion` | ✅ | |
| `fecha_inicio` | ✅ | `YYYY-MM-DD` |
| `fecha_fin` | ✅ | `YYYY-MM-DD` |
| `actividad_id` | ❌ | Default `""` |
| `progreso` | ❌ | Default `0` |
| `estado` | ❌ | Default `"pendiente"` |

#### Respuestas

| Código | Cuerpo | Condición |
|---|---|---|
| `200` | `{"ok": true, "id": 42}` | Creación exitosa |
| `400` | `{"error": "mensaje"}` | Campo requerido faltante o fecha inválida |
| `405` | `{"error": "método no permitido"}` | Verbo HTTP distinto a POST |

---

### 3.4 `GET /api/actividades/<pk>/`

**Función:** `actividad_detalle(request, pk)`

#### Respuesta `200 OK`

```json
{
  "id": 42,
  "colaborador": "Ana Gómez",
  "obligacion": "Análisis de datos",
  "actividad_id": "2.3",
  "descripcion": "Consolidar matriz de indicadores",
  "fecha_inicio": "2026-03-23",
  "fecha_fin": "2026-06-30",
  "progreso": 15,
  "estado": "pendiente"
}
```

---

### 3.5 `PUT/PATCH /api/actividades/<pk>/`

Actualización parcial o total. El cuerpo es idéntico al de creación; solo se aplican los campos presentes en el JSON.

#### Respuestas

| Código | Cuerpo | Condición |
|---|---|---|
| `200` | `{"ok": true}` | Actualización exitosa |
| `404` | `{"error": "no encontrada"}` | `pk` no existe |

---

### 3.6 `DELETE /api/actividades/<pk>/`

#### Respuestas

| Código | Cuerpo | Condición |
|---|---|---|
| `200` | `{"ok": true}` | Eliminación exitosa |
| `404` | `{"error": "no encontrada"}` | `pk` no existe |

---

### 3.7 `GET /api/actividades/semana/`

**Función:** `semana_data(request)`

#### Query params

| Parámetro | Requerido | Ejemplo |
|---|---|---|
| `semana` | ✅ | `MAR S1` |
| `colaborador` | ❌ | `Ana Gómez` |

#### Lógica de filtrado

Selecciona actividades donde el código de semana aparece en el campo `semanas_activas` (JSONField):

```python
qs = CronogramaActividad.objects.filter(
    semanas_activas__contains=semana
)
```

#### Respuesta `200 OK`

```json
{
  "semana": "MAR S1",
  "fecha_inicio": "2026-03-02",
  "fecha_fin": "2026-03-06",
  "total_colaboradores": 5,
  "total_actividades": 12,
  "grupos": {
    "Ana Gómez": [
      {
        "id": 42,
        "actividad_id": "2.3",
        "descripcion": "Consolidar matriz de indicadores",
        "obligacion": "Análisis de datos",
        "estado": "pendiente",
        "progreso": 15,
        "fecha_inicio": "2026-03-02",
        "fecha_fin": "2026-03-20",
        "total_semanas": 3,
        "semana_num": 1
      }
    ]
  }
}
```

---

### 3.8 `GET /api/actividades/resumen/`

**Función:** `resumen_data(request)`

#### Query params

| Parámetro | Requerido | Ejemplo |
|---|---|---|
| `semana` | ✅ | `MAR S1` |

#### Respuesta `200 OK`

```json
{ "total": 42 }
```

---

## 4. Vistas Web

### 4.1 `/actividades/` — Diagrama de Gantt

**Template:** `dashboard/templates/dashboard/actividades.html`
**CSS:** `dashboard/static/dashboard/css/actividades.css`
**JS:** `dashboard/static/dashboard/js/actividades.js`

#### Componentes de la interfaz

| Componente | Clase CSS | Descripción |
|---|---|---|
| Barra de filtros | `.gantt-toolbar` | Selector colaborador, estado, obligación |
| KPIs | `.stats-bar` | Totales por estado |
| Cabecera del Gantt | `.gantt-header` | Meses y semanas (sticky) |
| Filas del Gantt | `.gantt-row` / `.gantt-bar` | Una barra por actividad |
| Tabla de detalle | `#tabla-actividades` | Vista tabular paralela |
| Modal | `#modal-actividad` | Formulario crear / editar |

#### Cálculo de posición de barras

La línea de tiempo abarca el año 2026 completo (365 días). Cada semana ocupa `52 px`:

```javascript
const SEM_W = 52;                    // px por semana
const TOTAL_DIAS = 365;

function diaDesdeInicio(fechaStr) {
    const d = new Date(fechaStr);
    const ini = new Date('2026-01-01');
    return Math.round((d - ini) / 86400000);
}

function fechaALeft(fechaStr) {
    return (diaDesdeInicio(fechaStr) / 7) * SEM_W;
}

function fechaAWidth(inicioStr, finStr) {
    const dias = diaDesdeInicio(finStr) - diaDesdeInicio(inicioStr) + 1;
    return Math.max((dias / 7) * SEM_W, 8);
}
```

#### Asignación de colores

```javascript
const PALETA = [
    '#4e79a7','#f28e2b','#e15759','#76b7b2','#59a14f',
    '#edc948','#b07aa1','#ff9da7','#9c755f','#bab0ac',
    // … 10 más
];

function colorColaborador(nombre) {
    const idx = [...nombre].reduce((a, c) => a + c.charCodeAt(0), 0) % PALETA.length;
    return PALETA[idx];
}
```

---

### 4.2 `/actividades/semana/` — Vista Semanal

**Template:** `dashboard/templates/dashboard/semana.html`
**CSS:** `dashboard/static/dashboard/css/semana.css`
**JS:** `dashboard/static/dashboard/js/semana.js`

| Elemento | Descripción |
|---|---|
| Navegador de semanas | Botones `<` `>` + `select` + botón "Esta semana" |
| Tarjetas por colaborador | Grid auto-fill (`min-width: 340px`) |
| Ítem de tarea | Dot de color, descripción, badge `Sem X/Y`, barra de progreso, check rápido |
| Modal de edición | Dropdown de estado + slider de progreso |

#### Flujo de actualización rápida (check)

```
Click ✓ → PUT /api/actividades/<id>/ {estado: 'completada', progreso: 100}
         → cargarSemana() recarga la vista
```

---

### 4.3 `/actividades/resumen/` — Dashboard Gerencial

**Template:** `dashboard/templates/dashboard/resumen.html`
**JS:** `dashboard/static/dashboard/js/resumen.js`

Muestra un único número grande: total de actividades comprometidas en la semana seleccionada. Diseñado para revisión rápida por parte de la Subdirección.

---

## 5. Comando de Importación

**Ubicación:** `dashboard/management/commands/importar_cronogramas.py`

```bash
# Importar sin borrar datos existentes
python manage.py importar_cronogramas

# Reimportar desde cero
python manage.py importar_cronogramas --limpiar
```

### 5.1 Fuentes de datos

Archivos Markdown en `data/Cronogramas_actividades/<NombreColaborador>.md`.

### 5.2 Formatos soportados

| Formato | Cabeceras detectadas | Descripción |
|---|---|---|
| **Secciones + tabla** | `### N. Obligación` + tabla | Tabla por cada sección de obligación |
| **WBS con fechas** | `WBS`, `Inicio`, `Finalización`, `%` | Fechas explícitas, progreso en columna |
| **Obligación + Actividad + Semanas** | `Obligación`, `Actividad` + columnas de semana | Combinado con ✅ |
| **Tabla plana** | `#`, `Actividad` + columnas de semana | Formato más frecuente |

### 5.3 Proceso de parsing

```
Leer .md → Detectar formato → Iterar filas
→ Extraer actividad_id, descripcion, obligacion
→ Identificar columnas que son códigos de semana (ENE S1, FEB S3…)
→ Registrar semanas con ✅ → semanas_activas
→ fecha_inicio = SEMANA_FECHAS[primera semana activa][0]
→ fecha_fin   = SEMANA_FECHAS[última semana activa][1]
→ Crear CronogramaActividad(estado='pendiente', progreso=0)
```

---

## 6. Seguridad

| Mecanismo | Implementación |
|---|---|
| Autenticación | `@login_required` en todas las vistas y APIs |
| CSRF | Token en cookie; `X-CSRFToken` header requerido en POST/PUT/DELETE |
| Hosts permitidos | `ALLOWED_HOSTS` + `CSRF_TRUSTED_ORIGINS` incluyen `srni-backend.ngrok.io` |
| Autorización | Sin RBAC; todo usuario autenticado accede a todos los datos |

---

## 7. Stack Tecnológico

| Capa | Tecnología | Versión |
|---|---|---|
| Framework web | Django | 6.0.3 |
| Base de datos | SQLite | — |
| Servidor WSGI | Gunicorn | 25.1.0 |
| Archivos estáticos | WhiteNoise | 6.12.0 |
| Frontend | HTML5 + CSS3 + JavaScript ES6 | Vanilla (sin frameworks) |

---

## 8. Migraciones

| Migración | Fecha | Cambio |
|---|---|---|
| `0004_cronogramaactividad` | 2026-03-30 02:32 | Crea tabla `CronogramaActividad` con campos base |
| `0005_cronogramaactividad_semanas_activas` | 2026-03-30 02:41 | Agrega campo `semanas_activas` (JSONField) |

---

## 9. Estructura de Archivos del Módulo

```
dashboard/
├── models.py                          # Modelo CronogramaActividad
├── views.py                           # actividades_view, actividades_data,
│                                      # actividad_crear, actividad_detalle,
│                                      # semana_view, semana_data,
│                                      # resumen_view, resumen_data
├── urls.py                            # 8 rutas del módulo actividades
├── management/
│   └── commands/
│       └── importar_cronogramas.py    # Importador Markdown → BD
├── migrations/
│   ├── 0004_cronogramaactividad.py
│   └── 0005_cronogramaactividad_semanas_activas.py
├── templates/dashboard/
│   ├── actividades.html               # Vista Gantt
│   ├── semana.html                    # Vista semanal
│   └── resumen.html                   # Dashboard gerencial
└── static/dashboard/
    ├── css/
    │   ├── actividades.css
    │   ├── semana.css
    │   └── resumen.css
    └── js/
        ├── actividades.js
        ├── semana.js
        └── resumen.js
```
