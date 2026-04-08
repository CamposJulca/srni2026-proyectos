# Documento Funcional — Módulos Consultas SQL y Gestión CRUD
**Sistema:** SRNI 2026 — Dashboard de Gestión de Contratos  
**Fecha:** Abril 2026  
**Versión:** 1.0  
**Usuarios objetivo:** Equipo SRNI, supervisores de procedimientos, analistas de datos  

---

## 1. Propósito

El sistema SRNI 2026 centraliza la gestión de contratos, obligaciones y actividades de los colaboradores de la Subdirección Red Nacional de Información. Dos módulos soportan la exploración y administración de esta información:

| Módulo | Para qué sirve |
|--------|---------------|
| **Consultas SQL** | Explorar el modelo de datos, validar información, generar reportes ad-hoc |
| **Gestión CRUD** | Crear, editar y eliminar registros de cualquier entidad del sistema |

---

## 2. Módulo: Consultas SQL (`/consultas/`)

### 2.1 Descripción general

Permite al usuario explorar la base de datos del sistema de dos formas:
1. **Diagrama ERD visual** — muestra las tablas y sus relaciones gráficamente
2. **Editor SQL** — ejecuta consultas SELECT y visualiza los resultados en tabla

### 2.2 Interfaz

La pantalla está dividida en dos zonas:

```
┌─────────────────────┬───────────────────────────────────────────────┐
│                     │  [ ERD ]  [ SQL ]                              │
│  SIDEBAR            │                                                │
│  ──────────         │  ┌─── Panel activo (ERD o SQL) ─────────────┐ │
│  📋 8 tablas        │  │                                           │ │
│     con consultas   │  │  Diagrama ERD  /  Editor SQL + resultados│ │
│     predefinidas    │  │                                           │ │
│                     │  └───────────────────────────────────────────┘ │
│  ──────────         │                                                │
│  💡 10 consultas    │                                                │
│     sugeridas       │                                                │
└─────────────────────┴───────────────────────────────────────────────┘
```

### 2.3 Tab ERD — Diagrama Entidad-Relación

Muestra las 8 tablas del sistema organizadas en dos filas con sus relaciones trazadas como flechas Bezier:

**Fila superior:** Procedimiento → Colaborador → Obligación → Actividad  
**Fila inferior:** Rol ← Asignación → Módulo → Proyecto

**Convención de colores:**
- **Flecha morada** (sólida) → relación obligatoria (FK NOT NULL)
- **Flecha verde** (punteada) → relación opcional (FK nullable)

Por cada tabla se muestran sus columnas con su tipo y badge identificador (PK / FK).

### 2.4 Tab SQL — Editor de consultas

#### Escribir y ejecutar una consulta

1. Hacer clic en el tab **SQL**
2. Escribir la consulta en el área de texto
3. Presionar **Ejecutar** o usar el atajo `Ctrl+Enter`
4. Los resultados aparecen en la tabla inferior con el conteo de filas

#### Atajos

| Acción | Método |
|--------|--------|
| Ejecutar consulta | Botón "Ejecutar" o `Ctrl+Enter` |
| Limpiar editor | Botón "Limpiar" |
| Exportar resultados | Botón "Exportar CSV" |

#### Restricciones

- Solo se permiten consultas **SELECT**
- Máximo **500 filas** por consulta
- No se pueden ejecutar: `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE` ni otras operaciones de escritura

#### Exportar a CSV

El botón **Exportar CSV** descarga el resultado actual en formato CSV con codificación UTF-8 (compatible con Excel en español). El nombre del archivo incluye la fecha de descarga: `consulta_srni_YYYY-MM-DD.csv`.

### 2.5 Sidebar — Accesos rápidos

**Tablas del sistema:** Al hacer clic en cualquiera de las 8 tarjetas de tabla, el editor cambia automáticamente al tab SQL y carga una consulta predefinida con los campos más relevantes de esa tabla.

**Consultas sugeridas:** 10 consultas frecuentes listas para ejecutar de un solo clic:
- Colaboradores activos por procedimiento
- Asignaciones por proyecto
- Obligaciones por colaborador
- Actividades en curso / completadas / pendientes
- Distribución de semanas activas
- Entre otras

### 2.6 Casos de uso típicos

| Caso de uso | Pasos |
|-------------|-------|
| Ver qué obligaciones tiene un colaborador | Sidebar → Obligaciones → editor mostrará query → agregar `WHERE colaborador_id = X` |
| Validar que un colaborador tiene actividades cargadas | Ejecutar query del resumen en consultas sugeridas |
| Exportar lista de colaboradores para revisión | Sidebar → Colaboradores → Exportar CSV |
| Confirmar relaciones entre módulos y proyectos | Tab ERD → visualizar diagrama |
| Contar registros por estado de actividad | Consulta sugerida "Estado de actividades" |

---

## 3. Módulo: Gestión CRUD (`/crud/`)

### 3.1 Descripción general

Permite gestionar los registros de las 6 entidades principales del sistema sin necesidad de acceder al panel de administración de Django. Cada operación (crear, editar, eliminar) tiene validación y confirmación de seguridad.

### 3.2 Entidades gestionables

| Entidad | Icono | Registros | Descripción |
|---------|-------|-----------|-------------|
| Colaboradores | 👤 | 93 | Contratistas del sistema SRNI |
| Obligaciones | 📋 | 232 | Compromisos contractuales por colaborador |
| Actividades | ⚡ | 208 | Tareas concretas ligadas a cada obligación |
| Asignaciones | 🔗 | 57 | Rol de un colaborador en un módulo de proyecto |
| Módulos | 📦 | 22 | Componentes de los proyectos |
| Roles | 🏷 | 13 | Roles funcionales (desarrollador, analista, etc.) |

### 3.3 Interfaz

```
┌─────────────────┬────────────────────────────────────────────────────────┐
│  SIDEBAR        │  ÁREA PRINCIPAL                                        │
│  ─────────      │                                                        │
│  👤 Colabor. 93 │  [🔍 Buscar...] [Filtro colabs ▾] [+ Nuevo]           │
│  📋 Oblig.  232 │  ──────────────────────────────────────────────────    │
│  ⚡ Activ.  208 │  # │ Col1    │ Col2    │ Col3   │ Acciones             │
│  🔗 Asig.    57 │  1 │ ...     │ ...     │ ...    │ ✏ 🗑                │
│  📦 Módulos  22 │  2 │ ...     │ ...     │ ...    │ ✏ 🗑                │
│  🏷 Roles    13 │  ...                                                   │
│                 │  [← 1 2 3 →]                                           │
└─────────────────┴────────────────────────────────────────────────────────┘
```

### 3.4 Navegación entre entidades

Hacer clic en cualquier elemento del sidebar carga la tabla correspondiente con sus columnas específicas en el área principal. El número junto a cada entidad indica el total de registros.

### 3.5 Búsqueda y filtros

| Control | Disponible en | Función |
|---------|--------------|---------|
| Búsqueda de texto | Todas las entidades | Filtra por nombre, descripción, cédula según la entidad |
| Filtro por colaborador | Obligaciones, Actividades | Muestra solo registros de un colaborador seleccionado |

La búsqueda es en tiempo real con un retardo de 350ms para no saturar el servidor.

### 3.6 Crear nuevo registro

1. Seleccionar la entidad en el sidebar
2. Clic en **+ Nuevo**
3. Se abre un modal con el formulario de la entidad
4. Campos con `*` son obligatorios
5. Los campos FK muestran un selector con todos los registros disponibles
6. Clic en **Guardar** — aparece confirmación verde si es exitoso

**Atajo útil:** Si se tiene activo el filtro de colaborador en Obligaciones o Actividades, el campo "Colaborador" se pre-rellena automáticamente al abrir el formulario de creación.

### 3.7 Editar un registro

1. Clic en el ícono ✏ de la fila deseada
2. El modal se abre con los valores actuales precargados
3. Modificar los campos necesarios
4. Clic en **Guardar**

### 3.8 Eliminar un registro

1. Clic en el ícono 🗑 de la fila deseada
2. Aparece un modal de confirmación con el nombre del registro
3. Clic en **Sí, eliminar** para confirmar
4. El registro se elimina y la tabla se actualiza

> **Advertencia:** La eliminación es permanente. Si el registro tiene dependencias (ej. eliminar una Obligación que tiene Actividades), Django eliminará en cascada todos los registros relacionados.

### 3.9 Paginación

Los resultados se muestran de 25 en 25. Los botones de paginación aparecen automáticamente cuando hay más de 25 registros.

### 3.10 Casos de uso típicos

| Caso de uso | Pasos |
|-------------|-------|
| Eliminar obligaciones incorrectas de un colaborador | Sidebar → Obligaciones → Filtrar por colaborador → 🗑 en las filas incorrectas |
| Agregar un nuevo colaborador al sistema | Sidebar → Colaboradores → + Nuevo → llenar formulario |
| Corregir la descripción de una actividad | Sidebar → Actividades → buscar por texto → ✏ editar |
| Asignar un colaborador a un nuevo módulo | Sidebar → Asignaciones → + Nuevo → seleccionar colaborador, rol y módulo |
| Revisar qué módulos tiene un proyecto | Sidebar → Módulos → buscar por nombre del proyecto |
| Cambiar el nombre de un rol | Sidebar → Roles → ✏ editar |

### 3.11 Columnas por entidad

**Colaboradores:** Nombre · Cédula · Procedimiento · Fecha inicio · Fecha fin · Honorarios

**Obligaciones:** Colaborador · Descripción (truncada a 90 caracteres)

**Actividades:** Colaborador · ID Actividad · Descripción · Estado (badge con color) · Progreso (barra visual)

**Asignaciones:** Colaborador · Rol · Módulo · Proyecto

**Módulos:** Nombre · Proyecto · Referente

**Roles:** Nombre

### 3.12 Estados de actividad (badge de color)

| Estado | Color | Significado |
|--------|-------|-------------|
| Completada | 🟢 Verde | La actividad ya finalizó |
| En curso | 🟡 Amarillo | La actividad está en la semana activa actual |
| Pendiente | ⚫ Gris | La actividad aún no ha comenzado |

---

## 4. Comportamientos comunes

### Toast de notificaciones

Ambos módulos muestran mensajes de confirmación o error en una pequeña notificación (toast) en la esquina inferior de la pantalla:

- ✅ **Verde:** operación exitosa (creado, actualizado, eliminado)
- ❌ **Rojo:** error de validación o fallo del servidor

### Manejo de errores de API

Si el servidor responde con un error, el mensaje aparece directamente en la tabla en lugar de los datos, sin perder el contexto de navegación.

---

## 5. Limitaciones conocidas

| Limitación | Descripción |
|------------|-------------|
| Solo SELECT en SQL | No se pueden ejecutar consultas de escritura desde el editor |
| Máx. 500 filas en SQL | Consultas con más resultados son truncadas |
| Sin edición masiva | El CRUD opera sobre un registro a la vez |
| `semanas_activas` no editable | El campo JSON de semanas activas de las Actividades no tiene editor en CRUD |
| Sin confirmación de cascada | Al eliminar, no se advierte cuántos registros relacionados serán borrados |
