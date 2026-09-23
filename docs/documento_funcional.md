# Documento Funcional - Dashboard de Proyectos SRNI

**Sistema:** Dashboard de Proyectos SRNI 2026  
**Entidad usuaria:** Subdireccion Red Nacional de Informacion  
**Fecha:** Mayo 2026

## 1. Objetivo del Sistema

El sistema permite hacer seguimiento operativo y gerencial a proyectos, modulos, colaboradores, obligaciones, actividades, evidencias, reportes semanales, riesgos, alertas y cuentas de cobro asociadas a la gestion de la SRNI.

Su proposito funcional es centralizar la informacion de ejecucion, facilitar la consulta por responsables y periodos, permitir actualizacion de avances por colaborador y entregar indicadores para seguimiento administrativo.

## 2. Usuarios y Roles

| Rol | Descripcion | Capacidades principales |
|---|---|---|
| Administrador | Usuario con control funcional del sistema. Puede ser superusuario o perfil con rol `admin`. | Gestionar datos maestros, consultar dashboards, cargar informacion, administrar actividades, revisar reportes, operar consultas y CRUD. |
| Colaborador | Usuario asociado a un `Colaborador`. | Consultar su cronograma, actualizar avance de sus actividades, subir evidencias y registrar reporte semanal. |

## 3. Alcance Funcional

El sistema cubre los siguientes modulos:

- Inicio y navegacion general.
- Autenticacion de usuarios.
- Dashboard operativo.
- Vista gerencial.
- Gestion de proyectos y detalle integral.
- Cronograma de actividades tipo Gantt.
- Vista semanal de actividades.
- Resumen de actividades por colaborador/procedimiento.
- Mi cronograma para colaboradores.
- Evidencias de actividades.
- Reporte semanal.
- CRUD administrativo de entidades principales.
- Consultas SQL controladas.
- Carga de datos desde Excel y Markdown.

## 4. Funcionalidades por Modulo

### 4.1 Autenticacion

Permite a los usuarios iniciar y cerrar sesion. Luego del ingreso:

- Administradores acceden al inicio y vistas administrativas.
- Colaboradores son orientados a su cronograma personal.

Si un usuario no autenticado intenta acceder a vistas protegidas, se redirige a `/login/`.

### 4.2 Inicio

La pantalla inicial funciona como punto de entrada a las secciones principales del sistema, de acuerdo con el rol del usuario autenticado.

### 4.3 Dashboard Operativo

Presenta indicadores y graficos de seguimiento:

- Total de proyectos.
- Total de modulos.
- Total de personas.
- Total de asignaciones.
- Proyectos por persona.
- Roles por persona.
- Modulos por proyecto.
- Compromisos por mes.
- Carga de trabajo de colaboradores.
- Cruce entre cumplimiento de actividades y cuentas de cobro.

Filtros funcionales:

- Persona o colaborador.
- Rol.
- Proyecto.
- Periodo de cobro.

### 4.4 Vista Gerencial

Consolida informacion ejecutiva:

- KPIs generales.
- Distribucion por procedimiento.
- Compromisos mensuales.
- Resumen de proyectos.
- Avance promedio.
- Actividades vencidas.
- Actividades bloqueadas.
- Personas asignadas.
- Cumplimiento del mes.
- Semaforo de proyecto.

El semaforo de proyecto permite identificar rapidamente proyectos en estado verde, amarillo o rojo segun estado, bloqueos, vencimientos y cumplimiento.

### 4.5 Detalle de Proyecto

Permite consultar la informacion integral de un proyecto:

- Datos generales: nombre, objetivo, estado, prioridad, fechas, responsable, procedimiento, presupuesto y observaciones.
- Resumen ejecutivo.
- Modulos.
- Equipo asignado.
- Cronograma de actividades.
- Actividades vencidas y bloqueadas.
- Riesgos.
- Alertas.
- Cuentas de cobro relacionadas.
- Evidencias asociadas.
- Compromisos por mes.
- Historial de cambios del proyecto.

Tambien existe exportacion CSV del proyecto.

### 4.6 Cronograma de Actividades

Permite visualizar y administrar actividades del plan de trabajo. Las actividades tienen:

- Colaborador.
- Obligacion.
- Proyecto asociado.
- Identificador de actividad.
- Descripcion.
- Fecha inicio.
- Fecha fin.
- Progreso.
- Estado.
- Semanas activas.
- Evidencia o entregable textual.

Estados disponibles:

- `pendiente`
- `en_curso`
- `completada`
- `bloqueada`

Filtros funcionales:

- Colaborador.
- Estado.
- Obligacion.
- Proyecto.

Reglas funcionales:

- Una actividad completada debe tener al menos una evidencia adjunta.
- El progreso esta entre 0% y 100%.
- Si una actividad llega a 100%, queda completada.
- Si se marca como completada, el progreso queda en 100%.

### 4.7 Vista Semanal

Permite consultar actividades activas en una semana especifica. La agrupacion se realiza por colaborador y puede filtrarse por:

- Colaborador.
- Procedimiento.
- Semana.

Esta vista ayuda a revisar compromisos inmediatos y seguimiento semanal.

### 4.8 Resumen de Actividades

Presenta una vision agregada del avance por colaborador o procedimiento:

- Total de actividades.
- Actividades pendientes.
- Actividades en curso.
- Actividades completadas.
- Actividades bloqueadas.
- Avance promedio.

### 4.9 Mi Cronograma

Es la vista de autoservicio del colaborador. Permite:

- Consultar las actividades asignadas al colaborador autenticado.
- Actualizar progreso.
- Cambiar estado.
- Registrar evidencia textual.
- Subir archivos de evidencia.
- Consultar evidencias asociadas.
- Registrar reporte semanal.

Reglas funcionales:

- El colaborador solo puede modificar actividades propias.
- No puede completar una actividad sin evidencia.
- La evidencia debe estar asociada a una actividad del colaborador o ser gestionada por un administrador.

### 4.10 Evidencias

Permite adjuntar soportes a actividades.

Datos de evidencia:

- Actividad.
- Archivo.
- Comentario.
- Usuario que carga.
- Fecha de carga.

Reglas:

- Tamano maximo de archivo: 10 MB.
- Los archivos se almacenan por anio y mes.
- Un administrador puede gestionar evidencias.
- Un colaborador puede gestionar evidencias de sus propias actividades.
- Solo el creador de la evidencia o un administrador puede eliminarla.

### 4.11 Reporte Semanal

Permite a cada colaborador registrar su avance semanal:

- Semana.
- Que hizo esta semana.
- Impedimentos o bloqueos.

Reglas:

- Semana y avance son obligatorios.
- Solo existe un reporte por colaborador y semana.
- Si se guarda de nuevo la misma semana, el reporte se actualiza.
- Los administradores pueden consultar reportes agregados.

### 4.12 CRUD Administrativo

Permite mantener entidades principales:

- Proyectos.
- Colaboradores.
- Obligaciones.
- Actividades.
- Cuentas de cobro.
- Asignaciones.
- Modulos.
- Roles.
- Riesgos de proyecto.
- Alertas de proyecto.

El CRUD usa formularios generados por metadatos, con busqueda, campos editables y relaciones foraneas configuradas por tabla.

### 4.13 Consultas SQL Controladas

Permite a administradores ejecutar consultas de lectura sobre la base de datos para analisis puntual.

Restricciones:

- Solo se permiten consultas `SELECT`.
- Se bloquean operaciones de modificacion o administracion de estructura.
- La respuesta se limita a 500 filas.

### 4.14 Carga de Informacion

El sistema permite cargar colaboradores desde archivos Excel de OPS y cronogramas desde archivos Markdown.

Carga de colaboradores:

- Identifica nombres y apellidos.
- Filtra registros de la Red Nacional.
- Actualiza datos contractuales.
- Crea procedimientos si no existen.

Carga de cronogramas:

- Lee archivos `.md` desde `data/Cronogramas_actividades/`.
- Interpreta tablas por semanas.
- Crea obligaciones y actividades.
- Calcula fechas a partir del calendario semanal 2026.

## 5. Entidades Funcionales

| Entidad | Descripcion |
|---|---|
| Procedimiento | Linea o procedimiento institucional asociado a proyectos y colaboradores. |
| Proyecto | Iniciativa que contiene modulos, responsables, estado, riesgos y alertas. |
| Modulo | Componente de un proyecto donde se asignan colaboradores y roles. |
| Colaborador | Persona vinculada al seguimiento de actividades y cuentas. |
| Rol | Papel de un colaborador dentro de un modulo. |
| Asignacion | Relacion entre colaborador, rol y modulo. |
| Obligacion | Compromiso contractual o funcional de un colaborador. |
| Actividad | Tarea planificada con fechas, avance, estado y evidencias. |
| Evidencia | Archivo soporte de cumplimiento de una actividad. |
| Reporte semanal | Registro narrativo de avances e impedimentos. |
| Cuenta de cobro | Registro mensual de cobro por colaborador. |
| Riesgo | Evento potencial que puede afectar un proyecto. |
| Alerta | Situacion que requiere atencion en un proyecto. |

## 6. Flujos Funcionales

### 6.1 Seguimiento de Actividad por Colaborador

1. El colaborador inicia sesion.
2. Ingresa a `Mi cronograma`.
3. Revisa actividades asignadas.
4. Actualiza progreso o estado.
5. Adjunta evidencia si la actividad va a completarse.
6. Guarda el cambio.
7. El sistema valida propiedad, evidencia y rango de progreso.

### 6.2 Seguimiento Gerencial

1. El administrador ingresa al dashboard o vista gerencial.
2. Selecciona filtros de proyecto, periodo o colaborador.
3. El sistema calcula KPIs, avance, vencimientos, bloqueos y cumplimiento.
4. El administrador revisa proyectos con semaforo amarillo o rojo.
5. Ingresa al detalle para consultar equipo, cronograma, riesgos, alertas y evidencias.

### 6.3 Registro de Reporte Semanal

1. El colaborador abre su cronograma.
2. Selecciona o confirma la semana.
3. Diligencia avance e impedimentos.
4. Guarda el reporte.
5. El sistema crea o actualiza el registro unico de esa semana.

### 6.4 Carga Inicial de Cronogramas

1. Se ubican archivos Markdown en `data/Cronogramas_actividades/`.
2. Se ejecuta el comando de importacion.
3. El sistema detecta formato de tabla.
4. Se crean obligaciones y actividades por colaborador.
5. Se calculan fechas de inicio y fin desde semanas activas.
6. Opcionalmente se ejecuta calculo de progreso.

## 7. Reglas de Negocio

| Codigo | Regla |
|---|---|
| RN-01 | Una actividad no puede tener fecha fin menor a fecha inicio. |
| RN-02 | El progreso de una actividad debe estar entre 0 y 100. |
| RN-03 | Una actividad completada debe tener progreso 100. |
| RN-04 | Una actividad con progreso 100 queda en estado completada. |
| RN-05 | No se permite completar una actividad sin evidencia adjunta. |
| RN-06 | Un colaborador solo actualiza actividades propias. |
| RN-07 | Una evidencia no puede superar 10 MB. |
| RN-08 | Solo el creador de una evidencia o un admin puede eliminarla. |
| RN-09 | Solo existe un reporte semanal por colaborador y semana. |
| RN-10 | Solo existe una cuenta de cobro por colaborador y periodo. |
| RN-11 | El periodo de cuenta de cobro se normaliza al primer dia del mes. |
| RN-12 | Solo administradores pueden usar CRUD, carga masiva, consultas SQL y reportes administrativos. |
| RN-13 | Las consultas SQL administrativas deben ser solo de lectura. |
| RN-14 | Un modulo no puede repetir nombre dentro del mismo proyecto. |
| RN-15 | Una asignacion no puede repetirse para la misma combinacion modulo, colaborador y rol. |

## 8. Indicadores Funcionales

| Indicador | Descripcion |
|---|---|
| Proyectos | Total de proyectos registrados. |
| Modulos | Total de modulos registrados. |
| Personas | Total de colaboradores considerados en el filtro. |
| Asignaciones | Total de relaciones colaborador-rol-modulo. |
| Avance promedio | Promedio del progreso de actividades. |
| Cumplimiento del periodo | Porcentaje de actividades completadas sobre actividades del periodo. |
| Actividades vencidas | Actividades con fecha fin anterior a la fecha actual y no completadas. |
| Actividades bloqueadas | Actividades en estado bloqueada. |
| Cuentas periodo | Total de cuentas de cobro registradas para el periodo. |
| Brecha cumplimiento-cobro | Diferencia entre cumplimiento del colaborador y porcentaje cobrado. |
| Semaforo | Clasificacion visual de salud de proyecto. |

## 9. Supuestos y Restricciones

- El sistema requiere usuarios autenticados.
- El rol funcional se define en `Perfil`.
- Los colaboradores deben estar correctamente asociados a usuarios para usar `Mi cronograma`.
- Los cronogramas Markdown deben conservar una estructura soportada por el importador.
- Las evidencias se guardan en el servidor donde corre la aplicacion.
- La base de datos actual es SQLite.

## 10. Criterios de Aceptacion Globales

- Un administrador puede consultar indicadores operativos y gerenciales.
- Un administrador puede crear y actualizar entidades desde el CRUD configurado.
- Un colaborador puede ver y actualizar solo su propio cronograma.
- El sistema bloquea el cierre de actividades sin evidencia.
- Las evidencias quedan disponibles para consulta posterior.
- Los reportes semanales son unicos por colaborador y semana.
- Las consultas SQL no permiten modificar datos.
- La carga desde fuentes externas crea o actualiza informacion segun las reglas definidas.
