# Documento Tecnico — Modulo Cronograma `/actividades/`

**Sistema:** SRNI 2026 — Dashboard de Instrumentalizacion  
**URL base:** `https://srni-backend.ngrok.io/actividades/`  
**Version:** 2.0  
**Fecha:** Abril 2026

---

## 1. Stack Tecnologico

| Capa | Tecnologia |
|------|------------|
| Backend | Django 6.0.3 (Python 3.12) |
| Base de datos | SQLite3 |
| Frontend | HTML5 + CSS3 + JavaScript vanilla |
| Servidor | Gunicorn + WhiteNoise (staticos) |
| Graficos | Chart.js (CDN) |
| Importacion | openpyxl (Excel), Markdown parser propio |
| Proxy | ngrok (tunel HTTPS) |

---

## 2. Endpoints API

### Actividades (Gantt)

| Endpoint | Metodo | Auth | Descripcion |
|----------|--------|------|-------------|
| `/actividades/` | GET | Login | Pagina Gantt (HTML) |
| `/api/actividades/` | GET | Login | JSON: actividades con filtros |
| `/api/actividades/crear/` | POST | Admin | Crear actividad |
| `/api/actividades/<pk>/` | GET/PUT/PATCH/DELETE | Login/Admin | Detalle CRUD |

**Parametros GET `/api/actividades/`:**

| Param | Tipo | Descripcion |
|-------|------|-------------|
| `colaborador` | string | Nombre exacto del colaborador |
| `estado` | string | pendiente, en_curso, completada, bloqueada |
| `obligacion` | string | Descripcion exacta de la obligacion |
| `proyecto` | string | Nombre del proyecto (filtra por asignaciones) |

**Respuesta:**
```json
{
  "tasks": [{
    "id": 897,
    "colaborador": "CRISTHIAM DANIEL CAMPOS JULCA",
    "obligacion": "Monitorear la asignacion...",
    "actividad_id": "1.1",
    "descripcion": "Revision del tablero...",
    "fecha_inicio": "2026-03-23",
    "fecha_fin": "2026-12-25",
    "progreso": 12,
    "estado": "en_curso",
    "estado_visual": "en_curso",
    "orden": 0,
    "proyecto": null,
    "proyectos": ["Caracterizacion", "Modelo Integrado", ...]
  }]
}
```

### Vista Semanal

| Endpoint | Metodo | Auth | Descripcion |
|----------|--------|------|-------------|
| `/actividades/semana/` | GET | Login | Pagina semanal (HTML) |
| `/api/actividades/semana/` | GET | Login | JSON: actividades por semana |

**Parametros GET:**

| Param | Tipo | Descripcion |
|-------|------|-------------|
| `semana` | string | Etiqueta semana (ej: `ABR S3`) |
| `colaborador` | string | Nombre del colaborador |
| `procedimiento` | string | Nombre del procedimiento |

**Respuesta:**
```json
{
  "semana": "ABR S3",
  "fecha_inicio": "2026-04-20",
  "fecha_fin": "2026-04-24",
  "total_colaboradores": 13,
  "total_actividades": 117,
  "grupos": {
    "COLABORADOR A": [{
      "id": 901,
      "actividad_id": "1.1",
      "descripcion": "...",
      "obligacion": "...",
      "estado": "en_curso",
      "progreso": 45,
      "fecha_inicio": "2026-03-23",
      "fecha_fin": "2026-06-30",
      "total_semanas": 14,
      "semana_num": 5
    }]
  }
}
```

### Resumen General

| Endpoint | Metodo | Auth | Descripcion |
|----------|--------|------|-------------|
| `/actividades/resumen/` | GET | Login | Pagina resumen (HTML) |
| `/api/actividades/resumen/` | GET | Login | JSON: KPIs semanales |

**Parametros GET:**

| Param | Tipo | Descripcion |
|-------|------|-------------|
| `semana` | string | Etiqueta semana |
| `procedimiento` | string | Filtro por procedimiento |

**Respuesta:**
```json
{
  "total": 117,
  "completadas": 4,
  "en_curso": 98,
  "pendientes": 15,
  "bloqueadas": 0,
  "avance": 42.6,
  "colaboradores": [{
    "nombre": "LUIS MIGUEL RAMIREZ",
    "total": 2,
    "completadas": 1,
    "en_curso": 1,
    "pendientes": 0,
    "bloqueadas": 0,
    "avance": 78.5
  }]
}
```

### Mi Cronograma

| Endpoint | Metodo | Auth | Descripcion |
|----------|--------|------|-------------|
| `/mi-cronograma/` | GET | Login+Perfil | Pagina personal (HTML) |
| `/api/mi-cronograma/` | GET | Login+Perfil | JSON: actividades propias |
| `/api/mi-cronograma/<pk>/` | POST | Login+Dueno | Actualizar progreso/estado |

### Evidencias

| Endpoint | Metodo | Auth | Descripcion |
|----------|--------|------|-------------|
| `/api/evidencias/<act_pk>/` | GET | Login | Listar evidencias |
| `/api/evidencias/<act_pk>/subir/` | POST | Dueno/Admin | Subir archivo (multipart, max 10MB) |
| `/api/evidencias/eliminar/<pk>/` | POST | Creador/Admin | Eliminar evidencia |

### Reportes Semanales

| Endpoint | Metodo | Auth | Descripcion |
|----------|--------|------|-------------|
| `/api/reporte-semanal/` | GET | Login | Reportes del colaborador logueado |
| `/api/reporte-semanal/guardar/` | POST | Login+Perfil | Crear/actualizar reporte |
| `/api/reportes-admin/` | GET | Admin | Todos los reportes |

---

## 3. Modelos de Datos

### Actividad (modelo central)

```python
class Actividad(models.Model):
    obligacion     = ForeignKey(Obligacion, CASCADE)       # REQUERIDO
    proyecto       = ForeignKey(Proyecto, SET_NULL, null)   # Opcional
    actividad_id   = CharField(max_length=20, blank)       # "1.1", "2.3"
    descripcion    = TextField()                           # REQUERIDO
    fecha_inicio   = DateField()                           # REQUERIDO
    fecha_fin      = DateField()                           # REQUERIDO
    progreso       = IntegerField(default=0)               # 0-100
    estado         = CharField(choices=ESTADO_CHOICES)     # pendiente|en_curso|completada|bloqueada
    orden          = IntegerField(default=0)               # Orden de visualizacion
    semanas_activas = JSONField(default=list)              # ["MAR S4", "ABR S1", ...]
    evidencia      = TextField(null, blank)                # Texto libre entregables
```

### Obligacion

```python
class Obligacion(models.Model):
    colaborador = ForeignKey(Colaborador, CASCADE)
    descripcion = TextField()
```

### EvidenciaActividad

```python
class EvidenciaActividad(models.Model):
    actividad   = ForeignKey(Actividad, CASCADE, related_name='evidencias')
    archivo     = FileField(upload_to='evidencias/%Y/%m/')
    comentario  = TextField(blank)
    creado_por  = ForeignKey(User, SET_NULL, null)
    creado_en   = DateTimeField(auto_now_add)
```

### ReporteSemanal

```python
class ReporteSemanal(models.Model):
    colaborador  = ForeignKey(Colaborador, CASCADE)
    semana       = CharField(max_length=10)          # "ABR S3"
    que_hizo     = TextField()
    impedimentos = TextField(blank)
    # unique_together: (colaborador, semana)
```

### Diagrama de relaciones

```
Procedimiento
    |
Colaborador ──── Perfil ──── User
    |
    ├── Obligacion
    |       |
    |       └── Actividad ──── EvidenciaActividad
    |               |
    |               └── Proyecto (opcional)
    |
    ├── Asignacion ──── Modulo ──── Proyecto
    |                       |
    |                       └── Rol
    |
    ├── CuentaCobro
    └── ReporteSemanal
```

---

## 4. Comandos de Gestion

### Importar cronogramas

```bash
python manage.py importar_cronogramas --limpiar
```

- Lee archivos `.md` de `data/Cronogramas_actividades/`
- Detecta 4 formatos automaticamente (secciones, WBS, tabla plana, tabla sin secciones)
- Matching de nombres: sin acentos, case-insensitive, busqueda parcial
- Crea Obligacion + Actividad con semanas_activas

### Calcular progreso

```bash
python manage.py calcular_progreso [--forzar]
```

- Calcula progreso basado en dias transcurridos vs dias totales
- Asigna estado coherente: 0% = pendiente, 1-99% = en_curso, 100% = completada
- `--forzar`: recalcula incluso actividades con progreso > 0

---

## 5. Logica de Semana Actual

```python
def _semana_actual():
    hoy = date.today()
    # Buscar semana que contiene la fecha actual
    for sem, (ini, fin) in SEMANA_FECHAS.items():
        if date.fromisoformat(ini) <= hoy <= date.fromisoformat(fin):
            return sem
    # Fallback: proxima semana mas cercana
    for sem in SEMANAS_ORDENADAS:
        if date.fromisoformat(SEMANA_FECHAS[sem][0]) >= hoy:
            return sem
    return SEMANAS_ORDENADAS[-1]
```

---

## 6. Coloreo por Proyecto (Frontend)

```javascript
const COLORES_PROYECTO = {
  'VIVANTO':                         '#003087',
  'Caracterizacion':                 '#00875a',
  'Modelo Integrado':                '#CE1126',
  'Nuevo Ruv':                       '#7c3aed',
  'Ruv Temporal-Sirav-Sipod':        '#0891b2',
  'Transformacion Ficha Estrategica':'#d97706',
};
```

**Logica de asignacion:**
1. Si hay filtro de proyecto activo: todas las barras con ese color
2. Si la actividad tiene proyecto directo (`Actividad.proyecto`): color del proyecto
3. Si el colaborador tiene un solo proyecto asignado: color de ese proyecto
4. Si tiene multiples: color por obligacion (ciclo de paleta)

---

## 7. Archivos del Modulo

| Archivo | Lineas | Funcion |
|---------|--------|---------|
| `views.py` | ~1600 | Vistas y APIs |
| `models.py` | 257 | Modelos de datos |
| `urls.py` | 59 | Rutas |
| `permisos.py` | 49 | Decoradores de acceso |
| `importar_cronogramas.py` | 560 | Importador Markdown |
| `calcular_progreso.py` | 52 | Calculo automatico de progreso |
| `actividades.js` | ~530 | Gantt + modal + evidencias |
| `semana.js` | ~400 | Vista semanal |
| `resumen.js` | ~140 | Dashboard KPIs |
| `mi_cronograma.js` | ~350 | Autoservicio |
| `actividades.css` | ~650 | Estilos Gantt |
| `semana.css` | ~300 | Estilos semanal |
| `resumen.css` | ~430 | Estilos resumen |
| `mi_cronograma.css` | ~250 | Estilos autoservicio |

---

## 8. Validaciones y Restricciones

| Regla | Nivel | Ubicacion |
|-------|-------|-----------|
| Actividad requiere obligacion FK | DB NOT NULL | `models.py` |
| Completar requiere evidencia | Vista | `actividad_detalle()`, `mi_actividad_update()` |
| Evidencia max 10MB | Vista | `evidencia_subir()` |
| Progreso 0-100 | Vista | `mi_actividad_update()` |
| (colaborador, semana) unico en ReporteSemanal | DB | `models.py` |
| (colaborador, periodo) unico en CuentaCobro | DB | `models.py` |
| Nombre de Colaborador unico | DB | `models.py` |
| SQL: solo SELECT, sin DROP/ALTER | Vista regex | `sql_query()` |
