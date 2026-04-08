from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Count, Q, Sum
from datetime import date
from django.db import connection
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json
import re
import unicodedata

from .models import (
    Procedimiento,
    Proyecto,
    Modulo,
    Colaborador,
    Rol,
    Asignacion,
    Obligacion,
    Actividad,
)


# ============================================================
#  CONFIGURACIÓN CRUD
# ============================================================

PROCEDIMIENTOS = [
    "INSTRUMENTALIZACIÓN",
    "EQUIPO BASE",
    "ANÁLISIS",
    "CARACTERIZACIÓN",
    "DIFUSIÓN Y APRENDIZAJE",
    "AIDI",
    "MESA DE SERVICIOS",
    "GIS",
]

def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")
    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get("next", "/"))
        error = "Usuario o contraseña incorrectos."
    return render(request, "dashboard/login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("/login/")


@login_required
def home(request):
    return render(request, "dashboard/home.html")


@login_required
def consultas_view(request):
    return render(request, "dashboard/consultas_view.html", {
        "modulo_activo": "consultas",
    })


@login_required
def crud_main_view(request):
    return render(request, "dashboard/crud_view.html", {
        "modulo_activo": "crud",
        "procedimientos": PROCEDIMIENTOS,
    })


@login_required
def gerencial_view(request):
    return render(request, "dashboard/gerencial_view.html", {
        "modulo_activo": "gerencial",
    })


@login_required
def gerencial_data(request):
    hoy = date.today()

    total       = Colaborador.objects.count()
    masa        = Colaborador.objects.filter(honorarios__isnull=False).aggregate(t=Sum('honorarios'))['t'] or 0
    vigentes    = Colaborador.objects.filter(fecha_fin__isnull=False, fecha_fin__gte=hoy).count()
    vencidos    = Colaborador.objects.filter(fecha_fin__isnull=False, fecha_fin__lt=hoy).count()
    sin_fecha   = Colaborador.objects.filter(fecha_fin__isnull=True).count()

    por_proc_qs = list(
        Colaborador.objects
        .values('procedimiento__nombre')
        .annotate(personas=Count('id'), masa=Sum('honorarios'))
        .order_by('-personas')
    )
    por_proc = []
    for p in por_proc_qs:
        por_proc.append({
            'procedimiento': p['procedimiento__nombre'] or 'Sin clasificar',
            'personas': p['personas'],
            'masa': float(p['masa'] or 0),
        })

    return JsonResponse({
        'kpis': {
            'total':     total,
            'masa':      float(masa),
            'vigentes':  vigentes,
            'vencidos':  vencidos,
            'sin_fecha': sin_fecha,
        },
        'por_procedimiento': por_proc,
        'compromisos_mes':   [],
    })


@login_required
def dashboard(request):

    procedimiento = request.GET.get("procedimiento", "INSTRUMENTALIZACIÓN")

    if procedimiento:
        colaboradores = Colaborador.objects.filter(
            procedimiento__nombre=procedimiento
        ).order_by("nombre")
    else:
        colaboradores = Colaborador.objects.all().order_by("nombre")

    roles = Rol.objects.all()
    proyectos = Proyecto.objects.all()

    return render(
        request,
        "dashboard/dashboard_view.html",
        {
            "personas": colaboradores,
            "roles": roles,
            "proyectos": proyectos,
            "procedimientos": PROCEDIMIENTOS,
            "procedimiento_activo": procedimiento,
            "modulo_activo": "dashboard",
        }
    )


def dashboard_data(request):

    persona = request.GET.get("persona")
    rol = request.GET.get("rol")
    proyecto = request.GET.get("proyecto")
    procedimiento = request.GET.get("procedimiento")

    asignaciones = Asignacion.objects.select_related(
        "colaborador",
        "rol",
        "modulo",
        "modulo__proyecto"
    )

    if persona:
        asignaciones = asignaciones.filter(colaborador_id=persona)

    if rol:
        asignaciones = asignaciones.filter(rol_id=rol)

    if proyecto:
        asignaciones = asignaciones.filter(modulo__proyecto_id=proyecto)

    # ==============================
    # KPIs
    # ==============================

    colaboradores_qs = (
        Colaborador.objects.filter(procedimiento__nombre=procedimiento)
        if procedimiento else Colaborador.objects.all()
    )

    kpis = {
        "proyectos": Proyecto.objects.count(),
        "modulos": Modulo.objects.count(),
        "personas": colaboradores_qs.count(),
        "asignaciones": asignaciones.count(),
    }

    # ==============================
    # Proyectos por colaborador
    # ==============================

    proyectos_persona = (
        asignaciones
        .values("colaborador__nombre")
        .annotate(total=Count("modulo__proyecto", distinct=True))
    )

    # ==============================
    # Roles por colaborador
    # ==============================

    roles_persona = (
        asignaciones
        .values("rol__nombre")
        .annotate(total=Count("colaborador", distinct=True))
    )

    # ==============================
    # Módulos filtrados
    # ==============================

    modulos_ids = asignaciones.values_list("modulo_id", flat=True)

    modulos_proyecto = (
        Modulo.objects
        .filter(id__in=modulos_ids)
        .values("proyecto__nombre")
        .annotate(total=Count("id", distinct=True))
    )

    data = {
        "kpis": kpis,
        "proyectos_persona": list(proyectos_persona),
        "roles_persona": list(roles_persona),
        "modulos_proyecto": list(modulos_proyecto),
        "compromisos_mes": [],
    }

    return JsonResponse(data)


@require_POST
def sql_query(request):
    try:
        body = json.loads(request.body)
        query = body.get("query", "").strip()
    except Exception:
        return JsonResponse({"error": "JSON inválido."}, status=400)

    if not query:
        return JsonResponse({"error": "La consulta está vacía."}, status=400)

    # Solo permite SELECT
    primera_palabra = re.split(r'\s+', query)[0].upper()
    if primera_palabra != "SELECT":
        return JsonResponse(
            {"error": "Solo se permiten consultas SELECT."},
            status=403
        )

    # Bloquea palabras peligrosas por si cuelan en subconsultas
    peligrosas = r'\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|REPLACE|ATTACH|DETACH|PRAGMA)\b'
    if re.search(peligrosas, query, re.IGNORECASE):
        return JsonResponse(
            {"error": "La consulta contiene operaciones no permitidas."},
            status=403
        )

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchmany(500)  # máximo 500 filas
        return JsonResponse({
            "columnas": columnas,
            "filas": [list(f) for f in filas],
            "total": len(filas)
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# ============================================================
#  CRUD API
# ============================================================

def _opciones_fk(modelo, campo_display="nombre"):
    try:
        qs = modelo.objects.all().order_by(campo_display)
        return [{"id": o.pk, "label": str(getattr(o, campo_display, None) or o)} for o in qs]
    except Exception:
        return [{"id": o.pk, "label": str(o)} for o in modelo.objects.all()]


TABLA_META = {
    "colaborador": {
        "modelo": Colaborador,
        "label": "Colaboradores",
        "buscar_en": ["nombre", "cedula"],
        "filtro_colaborador": False,
        "campos": [
            {"name": "nombre",           "label": "Nombre completo", "type": "text",     "required": True},
            {"name": "cedula",           "label": "Cédula",          "type": "text"},
            {"name": "procedimiento_id", "label": "Procedimiento",   "type": "fk",       "fk_modelo": "Procedimiento"},
            {"name": "fecha_inicio",     "label": "Fecha inicio",    "type": "date"},
            {"name": "fecha_fin",        "label": "Fecha fin",       "type": "date"},
            {"name": "honorarios",       "label": "Honorarios",      "type": "number"},
            {"name": "objeto",           "label": "Objeto contrato", "type": "textarea"},
        ],
        "columnas_lista": ["nombre", "cedula", "procedimiento__nombre", "fecha_inicio", "fecha_fin", "honorarios"],
    },
    "obligacion": {
        "modelo": Obligacion,
        "label": "Obligaciones",
        "buscar_en": ["descripcion"],
        "filtro_colaborador": True,
        "campos": [
            {"name": "colaborador_id", "label": "Colaborador", "type": "fk",      "required": True, "fk_modelo": "Colaborador"},
            {"name": "descripcion",    "label": "Descripción", "type": "textarea","required": True},
        ],
        "columnas_lista": ["colaborador__nombre", "descripcion"],
    },
    "actividad": {
        "modelo": Actividad,
        "label": "Actividades",
        "buscar_en": ["descripcion", "actividad_id"],
        "filtro_colaborador": True,
        "campos": [
            {"name": "obligacion_id",  "label": "Obligación",   "type": "fk",      "required": True, "fk_modelo": "Obligacion"},
            {"name": "actividad_id",   "label": "ID actividad", "type": "text"},
            {"name": "descripcion",    "label": "Descripción",  "type": "textarea","required": True},
            {"name": "fecha_inicio",   "label": "Fecha inicio", "type": "date"},
            {"name": "fecha_fin",      "label": "Fecha fin",    "type": "date"},
            {"name": "progreso",       "label": "Progreso (%)", "type": "number"},
            {"name": "estado",         "label": "Estado",       "type": "choice",
             "opciones_fijas": [
                {"id": "pendiente",   "label": "Pendiente"},
                {"id": "en_curso",    "label": "En curso"},
                {"id": "completada",  "label": "Completada"},
             ]},
            {"name": "orden",          "label": "Orden",        "type": "number"},
        ],
        "columnas_lista": ["obligacion__colaborador__nombre", "actividad_id", "descripcion", "estado", "progreso"],
    },
    "asignacion": {
        "modelo": Asignacion,
        "label": "Asignaciones",
        "buscar_en": [],
        "filtro_colaborador": False,
        "campos": [
            {"name": "colaborador_id", "label": "Colaborador", "type": "fk", "required": True, "fk_modelo": "Colaborador"},
            {"name": "rol_id",         "label": "Rol",         "type": "fk", "required": True, "fk_modelo": "Rol"},
            {"name": "modulo_id",      "label": "Módulo",      "type": "fk", "required": True, "fk_modelo": "Modulo"},
        ],
        "columnas_lista": ["colaborador__nombre", "rol__nombre", "modulo__nombre", "modulo__proyecto__nombre"],
    },
    "modulo": {
        "modelo": Modulo,
        "label": "Módulos",
        "buscar_en": ["nombre", "referente"],
        "filtro_colaborador": False,
        "campos": [
            {"name": "proyecto_id", "label": "Proyecto",  "type": "fk",  "required": True, "fk_modelo": "Proyecto"},
            {"name": "nombre",      "label": "Nombre",    "type": "text", "required": True},
            {"name": "referente",   "label": "Referente", "type": "text"},
        ],
        "columnas_lista": ["nombre", "proyecto__nombre", "referente"],
    },
    "rol": {
        "modelo": Rol,
        "label": "Roles",
        "buscar_en": ["nombre"],
        "filtro_colaborador": False,
        "campos": [
            {"name": "nombre", "label": "Nombre", "type": "text", "required": True},
        ],
        "columnas_lista": ["nombre"],
    },
}

FK_MODELOS = {
    "Procedimiento": Procedimiento,
    "Colaborador":   Colaborador,
    "Proyecto":      Proyecto,
    "Modulo":        Modulo,
    "Rol":           Rol,
    "Obligacion":    Obligacion,
    "Actividad":     Actividad,
}


def _serializar_fila(obj, columnas):
    fila = {"id": obj.pk}
    for col in columnas:
        if "__" in col:
            partes = col.split("__")
            val = obj
            for p in partes:
                val = getattr(val, p, None)
                if val is None:
                    break
        else:
            val = getattr(obj, col, None)
        if hasattr(val, 'isoformat'):
            val = val.isoformat()
        fila[col] = str(val) if val is not None else None
    return fila


def crud_meta(request):
    """Devuelve metadatos de todas las tablas (campos, conteos, opciones FK)."""
    resultado = {}
    for key, cfg in TABLA_META.items():
        campos = []
        for c in cfg["campos"]:
            campo = dict(c)
            if campo["type"] == "fk":
                fk_m = FK_MODELOS.get(campo.get("fk_modelo"))
                campo["opciones"] = _opciones_fk(fk_m) if fk_m else []
            elif campo["type"] == "choice":
                campo["opciones"] = campo.get("opciones_fijas", [])
            campos.append(campo)
        resultado[key] = {
            "label":              cfg["label"],
            "campos":             campos,
            "columnas":           cfg["columnas_lista"],
            "filtro_colaborador": cfg.get("filtro_colaborador", False),
            "total":              cfg["modelo"].objects.count(),
        }
    return JsonResponse(resultado)


def crud_lista(request, tabla):
    cfg = TABLA_META.get(tabla)
    if not cfg:
        return JsonResponse({"error": "Tabla no válida."}, status=404)

    qs = cfg["modelo"].objects.all()

    # Filtro por procedimiento (colaborador)
    proc = request.GET.get("proc", "").strip()
    if proc and tabla == "colaborador":
        qs = qs.filter(procedimiento__nombre=proc)

    # Filtro por colaborador (obligacion / actividad)
    colab_id = request.GET.get("colaborador", "").strip()
    if colab_id:
        if tabla == "obligacion":
            qs = qs.filter(colaborador_id=colab_id)
        elif tabla == "actividad":
            qs = qs.filter(obligacion__colaborador_id=colab_id)

    # Búsqueda
    q = request.GET.get("q", "").strip()
    if q and cfg["buscar_en"]:
        filtro = Q()
        for campo in cfg["buscar_en"]:
            filtro |= Q(**{f"{campo}__icontains": q})
        qs = qs.filter(filtro)

    # Relacionados
    if tabla == "modulo":
        qs = qs.select_related("proyecto")
    elif tabla == "asignacion":
        qs = qs.select_related("colaborador", "rol", "modulo", "modulo__proyecto")
    elif tabla == "colaborador":
        qs = qs.select_related("procedimiento")
    elif tabla == "obligacion":
        qs = qs.select_related("colaborador")
    elif tabla == "actividad":
        qs = qs.select_related("obligacion", "obligacion__colaborador")

    total = qs.count()
    page  = int(request.GET.get("page", 1))
    size  = 25
    qs    = qs[(page-1)*size : page*size]

    filas = [_serializar_fila(obj, cfg["columnas_lista"]) for obj in qs]
    return JsonResponse({"filas": filas, "total": total, "page": page, "size": size})


def crud_detalle(request, tabla, pk):
    cfg = TABLA_META.get(tabla)
    if not cfg:
        return JsonResponse({"error": "Tabla no válida."}, status=404)

    try:
        obj = cfg["modelo"].objects.get(pk=pk)
    except cfg["modelo"].DoesNotExist:
        return JsonResponse({"error": "Registro no encontrado."}, status=404)

    if request.method == "GET":
        datos = {"id": obj.pk}
        for c in cfg["campos"]:
            val = getattr(obj, c["name"], None)
            if hasattr(val, 'isoformat'):
                val = val.isoformat()
            datos[c["name"]] = val
        return JsonResponse(datos)

    if request.method in ("PUT", "PATCH"):
        try:
            body = json.loads(request.body)
        except Exception:
            return JsonResponse({"error": "JSON inválido."}, status=400)
        for c in cfg["campos"]:
            nombre = c["name"]
            if nombre in body:
                val = body[nombre] or None
                setattr(obj, nombre, val)
        try:
            obj.save()
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        return JsonResponse({"ok": True, "id": obj.pk})

    if request.method == "DELETE":
        try:
            obj.delete()
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        return JsonResponse({"ok": True})

    return JsonResponse({"error": "Método no permitido."}, status=405)


def crud_crear(request, tabla):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)

    cfg = TABLA_META.get(tabla)
    if not cfg:
        return JsonResponse({"error": "Tabla no válida."}, status=404)

    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "JSON inválido."}, status=400)

    kwargs = {}
    for c in cfg["campos"]:
        nombre = c["name"]
        val = body.get(nombre) or None
        kwargs[nombre] = val

    try:
        obj = cfg["modelo"].objects.create(**kwargs)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"ok": True, "id": obj.pk}, status=201)


def _normalizar(s):
    s = str(s).upper().strip()
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


def personas_por_rol(request):
    rol_nombre = request.GET.get("rol", "")
    proyecto_id = request.GET.get("proyecto", "")

    qs = Asignacion.objects.select_related(
        "colaborador", "rol", "modulo", "modulo__proyecto"
    )

    if rol_nombre:
        qs = qs.filter(rol__nombre=rol_nombre)
    if proyecto_id:
        qs = qs.filter(modulo__proyecto_id=proyecto_id)

    data = [
        {
            "persona":  a.colaborador.nombre,
            "modulo":   a.modulo.nombre,
            "proyecto": a.modulo.proyecto.nombre,
        }
        for a in qs.order_by("colaborador__nombre")
    ]

    return JsonResponse({"asignaciones": data})


def carga(request):
    if request.method == "GET":
        return render(request, "dashboard/carga.html")

    # POST — procesar archivo
    archivo = request.FILES.get("archivo")
    if not archivo:
        return JsonResponse({"error": "No se recibió ningún archivo."}, status=400)

    try:
        import openpyxl
        wb = openpyxl.load_workbook(archivo)
    except Exception:
        return JsonResponse({"error": "No se pudo leer el archivo. Asegúrate de subir un .xlsx válido."}, status=400)

    if "OPS 2026" not in wb.sheetnames:
        hoja = wb.active
    else:
        hoja = wb["OPS 2026"]

    # Construir mapa de cabeceras
    headers = {}
    for c in range(1, hoja.max_column + 1):
        val = hoja.cell(1, c).value
        if val:
            headers[val] = c

    campos_requeridos = ["NOMBRES CONTRATISTA", "APELLIDOS CONTRATISTA"]
    for campo in campos_requeridos:
        if campo not in headers:
            return JsonResponse({"error": f"No se encontró la columna '{campo}'."}, status=400)

    # Construir mapa de colaboradores existentes en BD (normalizado → objeto)
    colaboradores_bd = {_normalizar(c.nombre): c for c in Colaborador.objects.all()}

    creadas, actualizadas, omitidas = [], [], []

    for row in range(2, hoja.max_row + 1):
        dep = hoja.cell(row, headers.get("DEPENDENCIA ASOCIADA", 0)).value if "DEPENDENCIA ASOCIADA" in headers else None
        if dep and "RED NACIONAL" not in str(dep).upper():
            continue

        nombres = (hoja.cell(row, headers["NOMBRES CONTRATISTA"]).value or "").strip()
        apellidos = (hoja.cell(row, headers["APELLIDOS CONTRATISTA"]).value or "").strip()
        if not nombres and not apellidos:
            continue

        nombre_completo = f"{nombres} {apellidos}".strip()
        norm = _normalizar(nombre_completo)

        # Extraer campos extra
        cedula = hoja.cell(row, headers["NUMERO DE CEDULA"]).value if "NUMERO DE CEDULA" in headers else None
        fecha_inicio = hoja.cell(row, headers["FECHA ESTIMADA INICIO CONTRATO"]).value if "FECHA ESTIMADA INICIO CONTRATO" in headers else None
        fecha_fin = hoja.cell(row, headers["FECHA TERMINACION CONTRATO"]).value if "FECHA TERMINACION CONTRATO" in headers else None
        honorarios = hoja.cell(row, headers["VALOR HONORARIOS MENSUALES ESTIMADOS"]).value if "VALOR HONORARIOS MENSUALES ESTIMADOS" in headers else None
        objeto = hoja.cell(row, headers["OBJETO PAA"]).value if "OBJETO PAA" in headers else None
        proc_texto = hoja.cell(row, headers["PROCEDIMIENTO"]).value if "PROCEDIMIENTO" in headers else None

        # Normalizar fechas
        if hasattr(fecha_inicio, 'date'):
            fecha_inicio = fecha_inicio.date()
        if hasattr(fecha_fin, 'date'):
            fecha_fin = fecha_fin.date()

        # Resolver FK de procedimiento
        procedimiento_obj = None
        if proc_texto:
            proc_texto = str(proc_texto).strip().upper()
            procedimiento_obj, _ = Procedimiento.objects.get_or_create(nombre=proc_texto)

        campos = {
            "cedula":       str(cedula) if cedula else None,
            "fecha_inicio": fecha_inicio,
            "fecha_fin":    fecha_fin,
            "honorarios":   honorarios,
            "objeto":       str(objeto).strip() if objeto else None,
            "procedimiento": procedimiento_obj,
        }

        if norm in colaboradores_bd:
            colaborador = colaboradores_bd[norm]
            for k, v in campos.items():
                if v is not None:
                    setattr(colaborador, k, v)
            colaborador.save()
            actualizadas.append(colaborador.nombre)
        else:
            colaborador = Colaborador.objects.create(nombre=nombre_completo, **{k: v for k, v in campos.items()})
            colaboradores_bd[norm] = colaborador
            creadas.append(nombre_completo)

    return JsonResponse({
        "creadas": creadas,
        "actualizadas": actualizadas,
        "omitidas": omitidas,
        "total_creadas": len(creadas),
        "total_actualizadas": len(actualizadas),
    })

# ============================================================
#  MÓDULO ACTIVIDADES — CRONOGRAMA GANTT
# ============================================================

# Colaboradores sin archivo .md propio (no están en el DB aún)
COLABORADORES_SIN_CRONOGRAMA = [
    "Cristian Alejandro Neira López",
    "Edwin Alonso Villalobos Muñoz",
    "Jorge Andrés González Cetina",
    "Jorge Tomás Barreiro",
    "Martha Carolina Flórez Pérez",
    "Paola Andrea Arango Ferro",
    "Yovan Alirio Solano Flórez",
    "Cristhiam Daniel Campos Julca",
]


@login_required
def actividades_view(request):
    colaboradores = list(
        Actividad.objects
        .values_list('obligacion__colaborador__nombre', flat=True)
        .distinct()
        .order_by('obligacion__colaborador__nombre')
    )
    # Añadir colaboradores sin cronograma cargado aún
    for c in COLABORADORES_SIN_CRONOGRAMA:
        if c not in colaboradores:
            colaboradores.append(c)
    colaboradores.sort()

    obligaciones = list(
        Actividad.objects
        .values_list('obligacion__descripcion', flat=True)
        .distinct()
        .order_by('obligacion__descripcion')
    )
    return render(request, 'dashboard/actividades.html', {
        'modulo_activo': 'actividades',
        'colaboradores': colaboradores,
        'obligaciones': obligaciones,
    })


@login_required
def actividades_data(request):
    qs = Actividad.objects.select_related('obligacion__colaborador', 'proyecto').all()
    colaborador = request.GET.get('colaborador', '').strip()
    estado = request.GET.get('estado', '').strip()
    obligacion = request.GET.get('obligacion', '').strip()

    if colaborador:
        qs = qs.filter(obligacion__colaborador__nombre=colaborador)
    if estado:
        qs = qs.filter(estado=estado)
    if obligacion:
        qs = qs.filter(obligacion__descripcion=obligacion)

    hoy = date.today()
    tasks = []
    for a in qs:
        # Auto-detectar estado visual si está pendiente y la fecha ya pasó o está en curso
        estado_visual = a.estado
        if a.estado == 'pendiente':
            if a.fecha_fin < hoy:
                estado_visual = 'vencida'
            elif a.fecha_inicio <= hoy <= a.fecha_fin:
                estado_visual = 'en_curso'

        tasks.append({
            'id':           a.pk,
            'colaborador':  a.obligacion.colaborador.nombre,
            'obligacion':   a.obligacion.descripcion,
            'actividad_id': a.actividad_id,
            'descripcion':  a.descripcion,
            'fecha_inicio': a.fecha_inicio.isoformat(),
            'fecha_fin':    a.fecha_fin.isoformat(),
            'progreso':     a.progreso,
            'estado':       a.estado,
            'estado_visual': estado_visual,
            'orden':        a.orden,
        })

    return JsonResponse({'tasks': tasks})


@login_required
@require_POST
def actividad_crear(request):
    try:
        data = json.loads(request.body)

        nombre_colab = data.get('colaborador', '').strip()
        desc_oblig   = data.get('obligacion', '').strip()

        if not nombre_colab:
            return JsonResponse({'ok': False, 'error': 'colaborador requerido'}, status=400)

        colaborador_obj = Colaborador.objects.filter(nombre=nombre_colab).first()
        if not colaborador_obj:
            return JsonResponse({'ok': False, 'error': f'Colaborador "{nombre_colab}" no encontrado'}, status=400)

        obligacion_obj, _ = Obligacion.objects.get_or_create(
            colaborador=colaborador_obj,
            descripcion=desc_oblig,
        )

        proyecto_id = data.get('proyecto_id')
        proyecto_obj = Proyecto.objects.filter(pk=proyecto_id).first() if proyecto_id else None

        a = Actividad.objects.create(
            obligacion=obligacion_obj,
            proyecto=proyecto_obj,
            actividad_id=data.get('actividad_id', ''),
            descripcion=data.get('descripcion', ''),
            fecha_inicio=data['fecha_inicio'],
            fecha_fin=data['fecha_fin'],
            progreso=int(data.get('progreso', 0)),
            estado=data.get('estado', 'pendiente'),
        )
        return JsonResponse({'ok': True, 'id': a.pk})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@login_required
def actividad_detalle(request, pk):
    try:
        a = Actividad.objects.select_related('obligacion__colaborador', 'proyecto').get(pk=pk)
    except Actividad.DoesNotExist:
        return JsonResponse({'error': 'No encontrada'}, status=404)

    if request.method == 'GET':
        return JsonResponse({
            'id':           a.pk,
            'colaborador':  a.obligacion.colaborador.nombre,
            'obligacion':   a.obligacion.descripcion,
            'actividad_id': a.actividad_id,
            'descripcion':  a.descripcion,
            'fecha_inicio': a.fecha_inicio.isoformat(),
            'fecha_fin':    a.fecha_fin.isoformat(),
            'progreso':     a.progreso,
            'estado':       a.estado,
        })

    if request.method in ('PUT', 'PATCH'):
        data = json.loads(request.body)
        for field in ('actividad_id', 'descripcion', 'fecha_inicio', 'fecha_fin', 'estado'):
            if field in data:
                setattr(a, field, data[field])
        if 'progreso' in data:
            a.progreso = int(data['progreso'])
        a.save()
        return JsonResponse({'ok': True})

    if request.method == 'DELETE':
        a.delete()
        return JsonResponse({'ok': True})

    return JsonResponse({'error': 'Método no permitido'}, status=405)


# ============================================================
#  VISTA SEMANAL — compromisos por persona/semana
# ============================================================

# Orden cronológico de todas las semanas 2026
SEMANAS_ORDENADAS = [
    'ENE S1','ENE S2','ENE S3','ENE S4',
    'FEB S1','FEB S2','FEB S3','FEB S4',
    'MAR S1','MAR S2','MAR S3','MAR S4',
    'ABR S1','ABR S2','ABR S3','ABR S4',
    'MAY S1','MAY S2','MAY S3','MAY S4',
    'JUN S1','JUN S2','JUN S3','JUN S4',
    'JUL S1','JUL S2','JUL S3','JUL S4',
    'AGO S1','AGO S2','AGO S3','AGO S4',
    'SEP S1','SEP S2','SEP S3','SEP S4',
    'OCT S1','OCT S2','OCT S3','OCT S4',
    'NOV S1','NOV S2','NOV S3','NOV S4',
    'DIC S1','DIC S2','DIC S3','DIC S4',
]

SEMANA_FECHAS = {
    'ENE S1':('2026-01-05','2026-01-09'), 'ENE S2':('2026-01-12','2026-01-16'),
    'ENE S3':('2026-01-19','2026-01-23'), 'ENE S4':('2026-01-26','2026-01-30'),
    'FEB S1':('2026-02-02','2026-02-06'), 'FEB S2':('2026-02-09','2026-02-13'),
    'FEB S3':('2026-02-16','2026-02-20'), 'FEB S4':('2026-02-23','2026-02-27'),
    'MAR S1':('2026-03-02','2026-03-06'), 'MAR S2':('2026-03-09','2026-03-13'),
    'MAR S3':('2026-03-16','2026-03-20'), 'MAR S4':('2026-03-23','2026-03-27'),
    'ABR S1':('2026-04-06','2026-04-10'), 'ABR S2':('2026-04-13','2026-04-17'),
    'ABR S3':('2026-04-20','2026-04-24'), 'ABR S4':('2026-04-27','2026-04-30'),
    'MAY S1':('2026-05-04','2026-05-08'), 'MAY S2':('2026-05-11','2026-05-15'),
    'MAY S3':('2026-05-18','2026-05-22'), 'MAY S4':('2026-05-25','2026-05-29'),
    'JUN S1':('2026-06-01','2026-06-05'), 'JUN S2':('2026-06-08','2026-06-12'),
    'JUN S3':('2026-06-15','2026-06-19'), 'JUN S4':('2026-06-22','2026-06-26'),
    'JUL S1':('2026-07-06','2026-07-10'), 'JUL S2':('2026-07-13','2026-07-17'),
    'JUL S3':('2026-07-20','2026-07-24'), 'JUL S4':('2026-07-27','2026-07-31'),
    'AGO S1':('2026-08-03','2026-08-07'), 'AGO S2':('2026-08-10','2026-08-14'),
    'AGO S3':('2026-08-17','2026-08-21'), 'AGO S4':('2026-08-24','2026-08-28'),
    'SEP S1':('2026-09-07','2026-09-11'), 'SEP S2':('2026-09-14','2026-09-18'),
    'SEP S3':('2026-09-21','2026-09-25'), 'SEP S4':('2026-09-28','2026-10-02'),
    'OCT S1':('2026-10-05','2026-10-09'), 'OCT S2':('2026-10-12','2026-10-16'),
    'OCT S3':('2026-10-19','2026-10-23'), 'OCT S4':('2026-10-26','2026-10-30'),
    'NOV S1':('2026-11-02','2026-11-06'), 'NOV S2':('2026-11-09','2026-11-13'),
    'NOV S3':('2026-11-16','2026-11-20'), 'NOV S4':('2026-11-23','2026-11-27'),
    'DIC S1':('2026-11-30','2026-12-04'), 'DIC S2':('2026-12-07','2026-12-11'),
    'DIC S3':('2026-12-14','2026-12-18'), 'DIC S4':('2026-12-21','2026-12-25'),
}


def _semana_actual():
    """Devuelve la etiqueta de la semana del calendario que contiene hoy."""
    hoy = date.today()
    for sem, (ini, fin) in SEMANA_FECHAS.items():
        if date.fromisoformat(ini) <= hoy <= date.fromisoformat(fin):
            return sem
    # Si está fuera del rango, buscar la más próxima
    for sem in SEMANAS_ORDENADAS:
        ini, _ = SEMANA_FECHAS[sem]
        if date.fromisoformat(ini) >= hoy:
            return sem
    return SEMANAS_ORDENADAS[-1]


@login_required
def semana_view(request):
    semana_actual = _semana_actual()
    semana_param  = request.GET.get('semana', '').strip()
    colab_param   = request.GET.get('colaborador', '').strip()
    semana_inicial = semana_param if semana_param in SEMANAS_ORDENADAS else semana_actual
    return render(request, 'dashboard/semana.html', {
        'modulo_activo': 'actividades',
        'semanas': SEMANAS_ORDENADAS,
        'semana_actual': semana_actual,
        'semana_inicial': semana_inicial,
        'colaborador_inicial': colab_param,
        'semana_fechas': json.dumps(SEMANA_FECHAS),
        'colaboradores': sorted(set(
            Actividad.objects.values_list('obligacion__colaborador__nombre', flat=True)
        )),
    })


@login_required
def semana_data(request):
    semana = request.GET.get('semana', _semana_actual())
    colaborador = request.GET.get('colaborador', '').strip()

    base_qs = Actividad.objects.select_related(
        'obligacion__colaborador'
    ).order_by('obligacion__colaborador__nombre', 'orden')

    if colaborador:
        base_qs = base_qs.filter(obligacion__colaborador__nombre=colaborador)
    qs = [a for a in base_qs if semana in (a.semanas_activas or [])]

    # Agrupar por colaborador
    grupos = {}
    for a in qs:
        c = a.obligacion.colaborador.nombre
        if c not in grupos:
            grupos[c] = []
        grupos[c].append({
            'id':           a.pk,
            'actividad_id': a.actividad_id,
            'descripcion':  a.descripcion,
            'obligacion':   a.obligacion.descripcion,
            'estado':       a.estado,
            'progreso':     a.progreso,
            'fecha_inicio': a.fecha_inicio.isoformat(),
            'fecha_fin':    a.fecha_fin.isoformat(),
            'total_semanas': len(a.semanas_activas),
            'semana_num': (a.semanas_activas.index(semana) + 1) if semana in a.semanas_activas else 0,
        })

    fechas = SEMANA_FECHAS.get(semana, ('', ''))

    return JsonResponse({
        'semana':              semana,
        'fecha_inicio':        fechas[0],
        'fecha_fin':           fechas[1],
        'total_colaboradores': len(grupos),
        'total_actividades':   sum(len(v) for v in grupos.values()),
        'grupos':              grupos,
    })


# ============================================================
#  VISTA RESUMEN GENERAL — KPIs semanales para subdirector
# ============================================================

def _calcular_resumen(semana):
    """Calcula KPIs y tabla por colaborador para una semana dada."""
    base_qs = Actividad.objects.select_related(
        'obligacion__colaborador'
    ).order_by('obligacion__colaborador__nombre', 'orden')
    qs = [a for a in base_qs if semana in (a.semanas_activas or [])]

    total       = len(qs)
    completadas = sum(1 for a in qs if a.estado == 'completada')
    en_curso    = sum(1 for a in qs if a.estado == 'en_curso')
    pendientes  = sum(1 for a in qs if a.estado == 'pendiente')
    bloqueadas  = sum(1 for a in qs if a.estado == 'bloqueada')
    avance_general = round(sum(a.progreso for a in qs) / total) if total > 0 else 0

    grupos = {}
    for a in qs:
        c = a.obligacion.colaborador.nombre
        if c not in grupos:
            grupos[c] = {'compromisos': 0, 'completadas': 0, 'en_curso': 0,
                         'pendientes': 0, 'bloqueadas': 0, 'progreso_sum': 0}
        g = grupos[c]
        g['compromisos']  += 1
        g['progreso_sum'] += a.progreso
        if a.estado == 'completada':  g['completadas'] += 1
        elif a.estado == 'en_curso':  g['en_curso']    += 1
        elif a.estado == 'pendiente': g['pendientes']  += 1
        elif a.estado == 'bloqueada': g['bloqueadas']  += 1

    por_colaborador = []
    for nombre, g in sorted(grupos.items()):
        avance = round(g['progreso_sum'] / g['compromisos']) if g['compromisos'] > 0 else 0
        por_colaborador.append({
            'colaborador': nombre,
            'compromisos': g['compromisos'],
            'completadas': g['completadas'],
            'en_curso':    g['en_curso'],
            'pendientes':  g['pendientes'],
            'bloqueadas':  g['bloqueadas'],
            'avance':      avance,
        })

    fechas = SEMANA_FECHAS.get(semana, ('', ''))
    return {
        'semana':            semana,
        'fecha_inicio':      fechas[0],
        'fecha_fin':         fechas[1],
        'total_compromisos': total,
        'avance_general':    avance_general,
        'completadas':       completadas,
        'en_curso':          en_curso,
        'pendientes':        pendientes,
        'bloqueadas':        bloqueadas,
        'por_colaborador':   por_colaborador,
    }


@login_required
def resumen_view(request):
    semana_actual = _semana_actual()
    idx = SEMANAS_ORDENADAS.index(semana_actual) if semana_actual in SEMANAS_ORDENADAS else 0
    semana_default = SEMANAS_ORDENADAS[max(0, idx - 1)]
    total = len([a for a in Actividad.objects.all()
                 if semana_default in (a.semanas_activas or [])])
    return render(request, 'dashboard/resumen.html', {
        'modulo_activo':  'actividades',
        'semanas':        SEMANAS_ORDENADAS,
        'semana_actual':  semana_actual,
        'semana_default': semana_default,
        'semana_fechas':  json.dumps(SEMANA_FECHAS),
        'total_inicial':  total,
    })


@login_required
def resumen_data(request):
    semana = request.GET.get('semana', _semana_actual())
    total = len([a for a in Actividad.objects.all()
                 if semana in (a.semanas_activas or [])])
    return JsonResponse({'total': total})
