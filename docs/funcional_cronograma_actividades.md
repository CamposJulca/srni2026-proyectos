# Documento Funcional — Módulo Cronograma de Actividades
**Sistema:** SRNI 2026 — Dashboard de Instrumentalización
**Fecha:** Marzo 2026
**Versión:** 1.0

---

## 1. Propósito

El módulo de **Cronograma de Actividades** permite al equipo de Instrumentalización de la Subdirección Red Nacional de Información (SRNI) registrar, visualizar y hacer seguimiento semanal a los compromisos contractuales de cada colaborador durante el año 2026. La herramienta centraliza la información que antes existía en documentos Markdown dispersos y la convierte en una interfaz interactiva de seguimiento en tiempo real.

---

## 2. Alcance

- **Período cubierto:** Enero – Diciembre 2026 (48 semanas hábiles)
- **Colaboradores activos:** 13
- **Total compromisos cargados:** 200 actividades
- **Audiencia principal:** Subdirector(a) y equipo de Instrumentalización

---

## 3. Colaboradores incluidos

| Colaborador | Actividades |
|---|---|
| Cristhiam Daniel Campos Julca | 26 |
| Daniel Felipe Avendaño Pulido | 37 |
| David Alonso Ladino Medina | 29 |
| Diego Fernando Orjuela Vinchira | 11 |
| Diego Mauricio Veloza Martínez | 11 |
| Fabio Raúl Mesa Sanabria | 27 |
| Gabriel Darío Villa Acevedo | 13 |
| Iván Camilo Cristancho Pérez | 5 |
| Jhoan Manuel Ramírez Pirazán | 10 |
| Julián Alberto Siachoque Granados | 10 |
| Luis Miguel Ramírez | 4 |
| Luis Silvestre Supelano Beltrán | 6 |
| Olaf Vladimir Santanilla Saavedra | 11 |
| **Total** | **200** |

---

## 4. Modelo de datos

Cada actividad (`CronogramaActividad`) almacena:

| Campo | Tipo | Descripción |
|---|---|---|
| `colaborador` | texto | Nombre completo del contratista |
| `obligacion` | texto | Obligación contractual padre |
| `actividad_id` | texto | Código de la actividad (ej. `1.1`, `2.3`) |
| `descripcion` | texto largo | Descripción detallada del compromiso |
| `fecha_inicio` | fecha | Inicio de la actividad |
| `fecha_fin` | fecha | Cierre de la actividad |
| `progreso` | entero 0–100 | Porcentaje de avance |
| `estado` | selección | `pendiente` / `en_curso` / `completada` / `bloqueada` |
| `semanas_activas` | lista JSON | Etiquetas de semanas con ✅ (ej. `["MAR S4", "ABR S1"]`) |
| `orden` | entero | Orden de aparición dentro del cronograma |

El campo `semanas_activas` es la clave del sistema: permite consultar en O(n) qué actividades corresponden a una semana específica sin necesidad de calcular rangos de fechas en cada consulta.

---

## 5. Fuente de datos — Cronogramas Markdown

Los cronogramas se cargan desde archivos `.md` ubicados en `data/Cronogramas_actividades/`. El sistema soporta cuatro formatos de tabla distintos:

| Formato | Descripción | Ejemplo de colaborador |
|---|---|---|
| `secciones` | Secciones `###` con tablas por obligación | Daniel Avendaño, David Ladino |
| `wbs` | Tabla WBS con fechas explícitas de inicio/fin | Fabio Mesa, Diego Veloza |
| `tabla_plana_dos_cols` | Columna Obligación + Actividad + semanas | Luis Silvestre |
| `tabla_sin_secciones` | `#` \| Obligación \| semanas o fechas | Todos los demás |

### Formato especial de columnas de fecha

Cristhiam Daniel Campos Julca usa un formato con fechas absolutas en las columnas (`Mar 23`, `Abr 06`, `Jun 01`) en lugar de etiquetas estándar (`MAR S4`, `ABR S1`). El parser resuelve esto mediante:

1. Detecta columnas con patrón `Mes DD` (ej. `Mar 23`)
2. Convierte a fecha ISO: `2026-03-23`
3. Busca en el mapa inverso `FECHA_A_SEMANA` → `MAR S4`
4. Ignora fechas que no corresponden a semana hábil (festivos: `Mar 30`, `Jun 29`, `Ago 31`, `Dic 28`)

Las filas en negrita (`**1**`) se interpretan como encabezados de obligación, no como actividades independientes.

---

## 6. Comando de importación

```bash
# Importar / reimportar todos los cronogramas
python manage.py importar_cronogramas --limpiar
```

- `--limpiar`: elimina todas las actividades existentes antes de importar (recomendado para reimportaciones completas).
- Sin `--limpiar`: agrega sin eliminar (útil si se agrega un colaborador nuevo sin afectar el resto).

El comando recorre todos los archivos `.md` en `data/Cronogramas_actividades/`, detecta el formato automáticamente, parsea las actividades y las guarda en base de datos.

---

## 7. Vistas del sistema

### 7.1 Diagrama de Gantt (`/actividades/`)

Vista principal del módulo. Muestra todas las actividades del año en una tabla tipo Gantt con:
- Filas por colaborador y actividad
- Columnas por semana (48 semanas)
- Celdas coloreadas según estado (`pendiente`, `en_curso`, `completada`, `bloqueada`)
- Filtro por colaborador
- Modal inline para actualizar estado y progreso de cada actividad

### 7.2 Vista Semanal (`/actividades/semana/`)

Vista de tarjetas por colaborador para una semana específica. Muestra:
- Tarjeta por colaborador con sus compromisos de la semana
- Barra de progreso total por colaborador
- Check rápido para marcar actividades como completadas
- Modal para actualizar estado y progreso detallado
- Navegación entre semanas (anterior / siguiente / semana actual)
- Filtro por colaborador individual

### 7.3 Resumen General (`/actividades/resumen/`)

Vista ejecutiva para el Subdirector. Muestra el contador total de compromisos activos para la semana seleccionada, con navegación entre semanas. El dato se renderiza desde el servidor en la carga inicial (sin dependencia de JavaScript para mostrar el número).

---

## 8. API interna

| Endpoint | Método | Descripción |
|---|---|---|
| `GET /api/actividades/` | GET | Lista de actividades con filtros (colaborador, semana) para el Gantt |
| `GET /api/actividades/semana/` | GET | Actividades agrupadas por colaborador para una semana |
| `PUT /api/actividades/<id>/` | PUT | Actualiza estado y/o progreso de una actividad |
| `GET /api/actividades/resumen/` | GET | Total de compromisos para una semana |

Todos los endpoints requieren sesión activa (`@login_required`).

---

## 9. Semanas del sistema

El sistema define 48 semanas hábiles para 2026 (enero a diciembre), excluyendo semanas de festivos extendidos:
- Semana Santa (30 Mar – 3 Abr): no existe `MAR S5`
- Festivos de mitad de año: `Jun 29`, `Ago 31` no corresponden a semana hábil
- Las semanas se identifican con etiquetas `MES S#` (ej. `MAR S4`, `ABR S1`)

La semana activa se determina comparando la fecha del servidor contra los rangos definidos en `SEMANA_FECHAS`.

---

## 10. Infraestructura de despliegue

| Componente | Detalle |
|---|---|
| Framework | Django 5.x + Gunicorn (puerto 8085) |
| Archivos estáticos | Whitenoise (`CompressedManifestStaticFilesStorage`) |
| Base de datos | SQLite (`db.sqlite3`) |
| Acceso externo | Túnel ngrok → Gunicorn (bypasa nginx) |
| Despliegue de cambios | `python manage.py collectstatic --noinput` + `sudo systemctl restart dashboard-srni.service` |

---

## 11. Flujo de trabajo recomendado

1. **Cargar o actualizar cronograma**: editar el `.md` del colaborador en `data/Cronogramas_actividades/` y ejecutar `python manage.py importar_cronogramas --limpiar`.
2. **Seguimiento semanal**: ingresar a `/actividades/semana/`, seleccionar la semana actual y actualizar estado/progreso de cada actividad mediante el modal.
3. **Revisión ejecutiva**: ingresar a `/actividades/resumen/` para ver el total de compromisos activos en la semana.
4. **Vista completa de año**: ingresar a `/actividades/` para revisar el Gantt completo de todos los colaboradores.
