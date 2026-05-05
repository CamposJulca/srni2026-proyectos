# Documento Funcional — Modulo Cronograma de Actividades

**Sistema:** SRNI 2026 — Dashboard de Instrumentalizacion  
**URL:** `https://srni-backend.ngrok.io/actividades/`  
**Version:** 2.0  
**Fecha:** Abril 2026

---

## 1. Objetivo

Planificar, hacer seguimiento y controlar las actividades de los colaboradores de la Subdireccion de la Red Nacional de Informacion (SRNI), integrando obligaciones contractuales, cronogramas semanales, evidencias y reportes narrativos.

---

## 2. Roles y Permisos

| Rol | Acceso | Criterio |
|-----|--------|----------|
| **Administrador** | CRUD completo, Gantt, Semanal, Resumen, Carga masiva, Reportes admin | `Perfil.rol = 'admin'` o superusuario |
| **Colaborador** | Mi Cronograma: ver/actualizar sus actividades, subir evidencias, reportes semanales | `Perfil.rol = 'colaborador'` |

---

## 3. Vistas del Modulo

### 3.1 Cronograma Gantt (`/actividades/`)

Vista principal con diagrama de Gantt interactivo (enero-diciembre 2026).

**Filtros:** Procedimiento, Colaborador (busqueda por nombre con autocompletado), Proyecto, Estado, Obligacion.

**Comportamiento:**
- Agrupacion: Colaborador > Obligacion (sub-grupo con contador) > Actividades
- Barras coloreadas por proyecto (6 colores fijos + leyenda)
- Linea roja "Hoy" en la posicion actual del timeline
- Tabla detalle expandida debajo del Gantt
- Modal edicion (admin): crear, editar, eliminar actividad + gestion de evidencias

**Reglas:**
- No se puede marcar "Completada" sin al menos 1 evidencia adjunta
- Si la fecha fin paso y no esta completada, se muestra como "Vencida" (estado visual automatico)
- El filtro Procedimiento restringe el autocompletado de colaboradores

### 3.2 Vista Semanal (`/actividades/semana/`)

Compromisos de una semana especifica agrupados por colaborador en tarjetas.

**Filtros:** Procedimiento, Colaborador, Semana (navegacion con flechas).

**Comportamiento:**
- Tarjeta por colaborador con sus actividades de la semana
- Indicador semana N de M por actividad
- Stats: colaboradores activos, compromisos, completados, pendientes
- Modal de actualizacion rapida (admin)

### 3.3 Resumen General (`/actividades/resumen/`)

Dashboard ejecutivo para presentaciones a la Subdireccion.

**Filtros:** Procedimiento, Semana.

**Componentes:**
- 6 tarjetas KPI: Total, Avance %, Completadas, En curso, Pendientes, Bloqueadas
- Barra de distribucion por estado (verde/cyan/amarillo/rojo)
- Tabla de colaboradores con:
  - Barra de avance con porcentaje
  - Conteo por estado
  - Semaforo: "Al dia" (>=70%), "En riesgo" (40-70%), "Critico" (<40%)

### 3.4 Mi Cronograma (`/mi-cronograma/`)

Autoservicio para colaboradores.

**Funcionalidades:**
- Ve unicamente sus actividades propias
- Actualiza progreso (0-100%) y estado
- Sube evidencias (max 10MB)
- Redacta reportes semanales (que hizo + impedimentos)

**Restriccion:** Requiere `Perfil` con `colaborador` vinculado.

---

## 4. Calendario de Semanas

48 semanas laborales (lunes a viernes), 4 por mes:

| Mes | Semanas | Ejemplo |
|-----|---------|---------|
| Enero | ENE S1 – S4 | 05-ene a 30-ene |
| Febrero | FEB S1 – S4 | 02-feb a 27-feb |
| ... | ... | ... |
| Diciembre | DIC S1 – S4 | 30-nov a 25-dic |

Cada actividad almacena en `semanas_activas` la lista exacta de semanas donde tiene compromisos.

---

## 5. Flujos de Trabajo

### 5.1 Importacion de Cronogramas

```
Archivo .md  -->  importar_cronogramas --limpiar  -->  Obligaciones + Actividades
                                                  -->  calcular_progreso (estados)
```

Soporta 4 formatos de Markdown: secciones con `###`, tabla WBS con fechas, tabla plana con 2 columnas, tabla sin secciones.

### 5.2 Seguimiento Semanal (Admin)

```
Resumen General  -->  Filtrar procedimiento  -->  Identificar criticos/vencidos
Vista Semanal    -->  Revisar por colaborador -->  Actualizar estados
```

### 5.3 Ciclo del Colaborador

```
Login  -->  Mi Cronograma  -->  Ver actividades semana
                           -->  Actualizar progreso
                           -->  Subir evidencia  -->  Marcar completada
                           -->  Escribir reporte semanal
```

### 5.4 Regla de Completado

```
Actividad sin evidencia  -->  Intenta marcar "Completada"  -->  RECHAZADO
Actividad con evidencia  -->  Marca "Completada"           -->  OK
```

---

## 6. Gestion de Evidencias

| Aspecto | Valor |
|---------|-------|
| Tamano maximo | 10 MB |
| Formatos | PDF, DOC, DOCX, XLS, XLSX, PNG, JPG, ZIP, RAR, TXT, CSV, PPTX |
| Almacenamiento | `/media/evidencias/YYYY/MM/` |
| Subir | Dueno de la actividad o admin |
| Eliminar | Quien subio o admin |

---

## 7. Estados de Actividad

| Estado | Color | Transicion |
|--------|-------|------------|
| Pendiente | Gris | Estado inicial |
| En Curso | Cyan | Al iniciar trabajo |
| Completada | Verde | Requiere evidencia |
| Bloqueada | Rojo | Impedimento externo |
| Vencida (visual) | — | Automatico si fecha_fin < hoy y no completada |

---

## 8. Colores por Proyecto

| Proyecto | Color |
|----------|-------|
| VIVANTO | Azul oscuro (#003087) |
| Caracterizacion | Verde (#00875a) |
| Modelo Integrado | Rojo (#CE1126) |
| Nuevo Ruv | Morado (#7c3aed) |
| Ruv Temporal-Sirav-Sipod | Cyan (#0891b2) |
| Transformacion Ficha Estrategica | Naranja (#d97706) |
