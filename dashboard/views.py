from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from django.db import connection
from django.views.decorators.http import require_POST
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


def dashboard(request):

    personas = Persona.objects.all()
    roles = Rol.objects.all()
    proyectos = Proyecto.objects.all()

    return render(
        request,
        "dashboard/dashboard.html",
        {
            "personas": personas,
            "roles": roles,
            "proyectos": proyectos
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