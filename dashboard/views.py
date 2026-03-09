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
    Proyecto,
    Modulo,
    Persona,
    Rol,
    Asignacion,
    PlanAccion
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

    total       = Persona.objects.count()
    masa        = Persona.objects.filter(honorarios__isnull=False).aggregate(t=Sum('honorarios'))['t'] or 0
    vigentes    = Persona.objects.filter(fecha_fin__isnull=False, fecha_fin__gte=hoy).count()
    vencidos    = Persona.objects.filter(fecha_fin__isnull=False, fecha_fin__lt=hoy).count()
    sin_fecha   = Persona.objects.filter(fecha_fin__isnull=True).count()

    por_proc = list(
        Persona.objects.values('procedimiento')
        .annotate(personas=Count('id'), masa=Sum('honorarios'))
        .order_by('-personas')
    )
    # convertir Decimal a float para JSON
    for p in por_proc:
        p['masa'] = float(p['masa'] or 0)
        p['procedimiento'] = p['procedimiento'] or 'Sin clasificar'

    compromisos_mes = list(
        PlanAccion.objects.values('mes')
        .annotate(total=Count('id'))
    )

    return JsonResponse({
        'kpis': {
            'total':     total,
            'masa':      float(masa),
            'vigentes':  vigentes,
            'vencidos':  vencidos,
            'sin_fecha': sin_fecha,
        },
        'por_procedimiento': por_proc,
        'compromisos_mes':   compromisos_mes,
    })


@login_required
def dashboard(request):

    procedimiento = request.GET.get("procedimiento", "INSTRUMENTALIZACIÓN")

    if procedimiento:
        personas = Persona.objects.filter(procedimiento=procedimiento).order_by("nombre")
    else:
        personas = Persona.objects.all().order_by("nombre")

    roles = Rol.objects.all()
    proyectos = Proyecto.objects.all()

    return render(
        request,
        "dashboard/dashboard_view.html",
        {
            "personas": personas,
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

    asignaciones = Asignacion.objects.select_related(
        "persona",
        "rol",
        "modulo",
        "modulo__proyecto"
    )

    if persona:
        asignaciones = asignaciones.filter(persona_id=persona)

    if rol:
        asignaciones = asignaciones.filter(rol_id=rol)

    if proyecto:
        asignaciones = asignaciones.filter(modulo__proyecto_id=proyecto)

    # ==============================
    # KPIs
    # ==============================

    kpis = {
        "proyectos": Proyecto.objects.count(),
        "modulos": Modulo.objects.count(),
        "personas": Persona.objects.count(),
        "asignaciones": asignaciones.count(),
    }

    # ==============================
    # Proyectos por persona
    # ==============================

    proyectos_persona = (
        asignaciones
        .values("persona__nombre")
        .annotate(total=Count("modulo__proyecto", distinct=True))
    )

    # ==============================
    # Roles por persona
    # ==============================

    roles_persona = (
        asignaciones
        .values("rol__nombre")
        .annotate(total=Count("persona", distinct=True))
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

    # ==============================
    # Compromisos por mes
    # ==============================

    compromisos_query = PlanAccion.objects.select_related("modulo", "modulo__proyecto")

    if proyecto:
        compromisos_query = compromisos_query.filter(modulo__proyecto_id=proyecto)

    compromisos_mes = (
        compromisos_query
        .values("mes")
        .annotate(total=Count("id"))
    )

    data = {
        "kpis": kpis,
        "proyectos_persona": list(proyectos_persona),
        "roles_persona": list(roles_persona),
        "modulos_proyecto": list(modulos_proyecto),
        "compromisos_mes": list(compromisos_mes),
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
    return [{"id": o.pk, "label": str(getattr(o, campo_display, o.pk))}
            for o in modelo.objects.all().order_by(campo_display)]


TABLA_META = {
    "persona": {
        "modelo": Persona,
        "label": "Personas",
        "icono": "personas",
        "buscar_en": ["nombre", "cedula", "procedimiento"],
        "campos": [
            {"name": "nombre",        "label": "Nombre completo", "type": "text",     "required": True},
            {"name": "cedula",        "label": "Cédula",          "type": "text"},
            {"name": "procedimiento", "label": "Procedimiento",   "type": "select",   "opciones_fijas": None},
            {"name": "fecha_inicio",  "label": "Fecha inicio",    "type": "date"},
            {"name": "fecha_fin",     "label": "Fecha fin",       "type": "date"},
            {"name": "honorarios",    "label": "Honorarios",      "type": "number"},
            {"name": "objeto",        "label": "Objeto contrato", "type": "textarea"},
            {"name": "obligaciones",  "label": "Obligaciones",    "type": "textarea"},
        ],
        "columnas_lista": ["nombre", "cedula", "procedimiento", "fecha_inicio", "fecha_fin", "honorarios"],
    },
    "modulo": {
        "modelo": Modulo,
        "label": "Módulos",
        "icono": "modulos",
        "buscar_en": ["nombre", "referente"],
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
        "icono": "roles",
        "buscar_en": ["nombre"],
        "campos": [
            {"name": "nombre", "label": "Nombre", "type": "text", "required": True},
        ],
        "columnas_lista": ["nombre"],
    },
    "asignacion": {
        "modelo": Asignacion,
        "label": "Asignaciones",
        "icono": "asignaciones",
        "buscar_en": [],
        "campos": [
            {"name": "persona_id", "label": "Persona", "type": "fk", "required": True, "fk_modelo": "Persona"},
            {"name": "rol_id",     "label": "Rol",     "type": "fk", "required": True, "fk_modelo": "Rol"},
            {"name": "modulo_id",  "label": "Módulo",  "type": "fk", "required": True, "fk_modelo": "Modulo"},
        ],
        "columnas_lista": ["persona__nombre", "rol__nombre", "modulo__nombre", "modulo__proyecto__nombre"],
    },
    "planaccion": {
        "modelo": PlanAccion,
        "label": "Planes de acción",
        "icono": "planaccion",
        "buscar_en": ["compromiso", "mes"],
        "campos": [
            {"name": "modulo_id",   "label": "Módulo",      "type": "fk",      "required": True, "fk_modelo": "Modulo"},
            {"name": "mes",         "label": "Mes",         "type": "select",  "opciones_fijas": [
                "Enero","Febrero","Marzo","Abril","Mayo","Junio",
                "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
            ]},
            {"name": "compromiso",  "label": "Compromiso",  "type": "textarea","required": True},
        ],
        "columnas_lista": ["modulo__nombre", "modulo__proyecto__nombre", "mes", "compromiso"],
    },
}

FK_MODELOS = {
    "Persona": Persona,
    "Proyecto": Proyecto,
    "Modulo":   Modulo,
    "Rol":      Rol,
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
            elif campo["name"] == "procedimiento":
                campo["opciones_fijas"] = PROCEDIMIENTOS
            campos.append(campo)
        resultado[key] = {
            "label":    cfg["label"],
            "campos":   campos,
            "columnas": cfg["columnas_lista"],
            "total":    cfg["modelo"].objects.count(),
        }
    return JsonResponse(resultado)


def crud_lista(request, tabla):
    cfg = TABLA_META.get(tabla)
    if not cfg:
        return JsonResponse({"error": "Tabla no válida."}, status=404)

    qs = cfg["modelo"].objects.all()

    # Filtro por procedimiento (solo tabla persona)
    proc = request.GET.get("proc", "").strip()
    if proc and tabla == "persona":
        qs = qs.filter(procedimiento=proc)

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
        qs = qs.select_related("persona", "rol", "modulo", "modulo__proyecto")
    elif tabla == "planaccion":
        qs = qs.select_related("modulo", "modulo__proyecto")

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

    # Construir mapa de personas existentes en BD (normalizado → objeto)
    personas_bd = {_normalizar(p.nombre): p for p in Persona.objects.all()}

    creadas, actualizadas, omitidas = [], [], []

    for row in range(2, hoja.max_row + 1):
        dep = hoja.cell(row, headers.get("DEPENDENCIA ASOCIADA", 0)).value if "DEPENDENCIA ASOCIADA" in headers else None
        # Si hay columna de dependencia, filtrar solo SRNI; si no, importar todos
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
        obligaciones = hoja.cell(row, headers["OBLIGACIONES"]).value if "OBLIGACIONES" in headers else None

        # Normalizar fechas
        if hasattr(fecha_inicio, 'date'):
            fecha_inicio = fecha_inicio.date()
        if hasattr(fecha_fin, 'date'):
            fecha_fin = fecha_fin.date()

        campos = {
            "cedula": str(cedula) if cedula else None,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "honorarios": honorarios,
            "objeto": str(objeto).strip() if objeto else None,
            "obligaciones": str(obligaciones).strip() if obligaciones else None,
        }

        if norm in personas_bd:
            persona = personas_bd[norm]
            for k, v in campos.items():
                if v is not None:
                    setattr(persona, k, v)
            persona.save()
            actualizadas.append(persona.nombre)
        else:
            persona = Persona.objects.create(nombre=nombre_completo, **{k: v for k, v in campos.items()})
            personas_bd[norm] = persona
            creadas.append(nombre_completo)

    return JsonResponse({
        "creadas": creadas,
        "actualizadas": actualizadas,
        "omitidas": omitidas,
        "total_creadas": len(creadas),
        "total_actualizadas": len(actualizadas),
    })