# Dashboard de Proyectos - SRNI

Dashboard web para visualizar y hacer seguimiento a los proyectos, módulos, personas y planes de acción del **Procedimiento de Instrumentalización** de la **Subdirección de la Red Nacional de Información (SRNI)** - Unidad para las Víctimas.

---

## Descripcion

Aplicacion Django que consume datos de una matriz de proyectos en Excel y los expone a traves de una interfaz visual interactiva con graficos y filtros dinamicos.

---

## Estructura del proyecto

```
dashboard_proyectos/
├── config/                  # Configuracion del proyecto Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── dashboard/               # Aplicacion principal
│   ├── models.py            # Modelos de datos
│   ├── views.py             # Vistas (pagina + API)
│   ├── urls.py              # Rutas
│   ├── admin.py             # Registro en el admin de Django
│   ├── migrations/          # Migraciones de base de datos
│   ├── templates/
│   │   └── dashboard/
│   │       └── dashboard.html
│   └── static/
│       └── dashboard/
│           ├── css/dashboard.css
│           ├── js/dashboard.js
│           └── img/escudo.png
├── data/
│   └── matriz_proyectos.xlsx  # Fuente de datos
├── db.sqlite3               # Base de datos SQLite
├── manage.py
└── requirements.txt
```

---

## Modelos de datos

| Modelo | Campos principales |
|---|---|
| `Proyecto` | `nombre` (unico) |
| `Modulo` | `proyecto` (FK), `nombre`, `referente` |
| `Persona` | `nombre` (unico) |
| `Rol` | `nombre` (unico) |
| `Asignacion` | `modulo` (FK), `persona` (FK), `rol` (FK) |
| `PlanAccion` | `modulo` (FK), `compromiso`, `mes` |

**Relaciones:**
- Un `Proyecto` tiene muchos `Modulos`.
- Un `Modulo` tiene muchas `Asignaciones` y muchos `PlanAccion`.
- Una `Asignacion` vincula una `Persona` y un `Rol` a un `Modulo` (restriccion unica por combinacion modulo-persona-rol).

---

## Endpoints

| Ruta | Nombre | Descripcion |
|---|---|---|
| `/` | `dashboard` | Pagina principal del dashboard |
| `/api/dashboard/` | `dashboard_data` | API JSON con KPIs y datos de graficos |

### API `/api/dashboard/`

**Metodo:** `GET`

**Parametros opcionales (query string):**

| Parametro | Descripcion |
|---|---|
| `persona` | ID de la persona para filtrar |
| `rol` | ID del rol para filtrar |
| `proyecto` | ID del proyecto para filtrar |

**Respuesta:**

```json
{
  "kpis": {
    "proyectos": 10,
    "modulos": 45,
    "personas": 27,
    "asignaciones": 120
  },
  "proyectos_persona": [
    {"persona__nombre": "Juan Perez", "total": 3}
  ],
  "roles_persona": [
    {"rol__nombre": "Lider", "total": 5}
  ],
  "modulos_proyecto": [
    {"proyecto__nombre": "Proyecto A", "total": 8}
  ],
  "compromisos_mes": [
    {"mes": "Enero", "total": 12}
  ]
}
```

---

## Funcionalidades del dashboard

- **KPIs:** tarjetas con conteo total de proyectos, módulos, personas y asignaciones.
- **Filtros dinamicos:** por persona, rol y proyecto. Al cambiar cualquier filtro se recarga la informacion via fetch.
- **Graficos (Chart.js):**
  - Proyectos por persona (barras horizontales, top 10, ordenado alfabeticamente)
  - Distribucion de roles (torta)
  - Modulos por proyecto (barras verticales)
  - Compromisos por mes (linea)
- **Modal de obligaciones:** al hacer clic en una barra del grafico de personas, se abre un modal con las obligaciones del colaborador (definidas en `dashboard.js`).

---

## Instalacion y ejecucion

### 1. Clonar el repositorio y crear el entorno virtual

```bash
git clone <url-del-repositorio>
cd dashboard_proyectos
python -m venv venv
source venv/bin/activate
```

### 2. Instalar dependencias del proyecto

El archivo `requirements.txt` contiene los paquetes del sistema. Para este proyecto Django solo se necesitan:

```bash
pip install django openpyxl
```

### 3. Aplicar migraciones

```bash
python manage.py migrate
```

### 4. Cargar datos

Importar los datos desde el archivo `data/matriz_proyectos.xlsx` usando el admin de Django o un script de importacion.

Para acceder al admin:

```bash
python manage.py createsuperuser
```

### 5. Ejecutar el servidor

```bash
python manage.py runserver
```

Abrir en el navegador: `http://127.0.0.1:8000/`

---

## Admin de Django

Todos los modelos estan registrados en el panel de administracion:

`http://127.0.0.1:8000/admin/`

Desde ahi se pueden gestionar: Proyectos, Modulos, Personas, Roles, Asignaciones y Planes de Accion.

---

## Notas de configuracion

- **Base de datos:** SQLite (`db.sqlite3`). Para produccion reemplazar por PostgreSQL.
- **DEBUG:** activo (`True`). Desactivar en produccion.
- **SECRET_KEY:** cambiar por una clave segura antes de desplegar en produccion.
- **ALLOWED_HOSTS:** configurar con el dominio o IP del servidor en produccion.

---

## Tecnologias

- Python 3.13
- Django 6.0.3
- SQLite
- Chart.js (via CDN)
- HTML / CSS / JavaScript (vanilla)
