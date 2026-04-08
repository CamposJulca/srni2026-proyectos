"""
Comando para importar cronogramas desde archivos .md en data/Cronogramas_actividades/

Soporta cuatro formatos:
  1. Secciones ### con tablas por sección (Daniel Avendaño, David Ladino, etc.)
  2. Tabla WBS plana con fechas explícitas (Fabio Mesa, Diego Veloza)
  3. Tabla única con Obligación + Actividad + semanas (Luis Silvestre)
  4. Tabla plana sin secciones: # | Obligación | [extra] | SEMANAS... (la mayoría)

Guarda semanas_activas: lista exacta de semanas con ✅ (sin gaps).
"""

import os
import re
from django.core.management.base import BaseCommand
from dashboard.models import CronogramaActividad


# Mapeo semana → (fecha_inicio, fecha_fin)
SEMANAS = {
    'ENE S1': ('2026-01-05', '2026-01-09'),
    'ENE S2': ('2026-01-12', '2026-01-16'),
    'ENE S3': ('2026-01-19', '2026-01-23'),
    'ENE S4': ('2026-01-26', '2026-01-30'),
    'FEB S1': ('2026-02-02', '2026-02-06'),
    'FEB S2': ('2026-02-09', '2026-02-13'),
    'FEB S3': ('2026-02-16', '2026-02-20'),
    'FEB S4': ('2026-02-23', '2026-02-27'),
    'MAR S1': ('2026-03-02', '2026-03-06'),
    'MAR S2': ('2026-03-09', '2026-03-13'),
    'MAR S3': ('2026-03-16', '2026-03-20'),
    'MAR S4': ('2026-03-23', '2026-03-27'),
    'ABR S1': ('2026-04-06', '2026-04-10'),
    'ABR S2': ('2026-04-13', '2026-04-17'),
    'ABR S3': ('2026-04-20', '2026-04-24'),
    'ABR S4': ('2026-04-27', '2026-04-30'),
    'MAY S1': ('2026-05-04', '2026-05-08'),
    'MAY S2': ('2026-05-11', '2026-05-15'),
    'MAY S3': ('2026-05-18', '2026-05-22'),
    'MAY S4': ('2026-05-25', '2026-05-29'),
    'JUN S1': ('2026-06-01', '2026-06-05'),
    'JUN S2': ('2026-06-08', '2026-06-12'),
    'JUN S3': ('2026-06-15', '2026-06-19'),
    'JUN S4': ('2026-06-22', '2026-06-26'),
    'JUL S1': ('2026-07-06', '2026-07-10'),
    'JUL S2': ('2026-07-13', '2026-07-17'),
    'JUL S3': ('2026-07-20', '2026-07-24'),
    'JUL S4': ('2026-07-27', '2026-07-31'),
    'AGO S1': ('2026-08-03', '2026-08-07'),
    'AGO S2': ('2026-08-10', '2026-08-14'),
    'AGO S3': ('2026-08-17', '2026-08-21'),
    'AGO S4': ('2026-08-24', '2026-08-28'),
    'SEP S1': ('2026-09-07', '2026-09-11'),
    'SEP S2': ('2026-09-14', '2026-09-18'),
    'SEP S3': ('2026-09-21', '2026-09-25'),
    'SEP S4': ('2026-09-28', '2026-10-02'),
    'OCT S1': ('2026-10-05', '2026-10-09'),
    'OCT S2': ('2026-10-12', '2026-10-16'),
    'OCT S3': ('2026-10-19', '2026-10-23'),
    'OCT S4': ('2026-10-26', '2026-10-30'),
    'NOV S1': ('2026-11-02', '2026-11-06'),
    'NOV S2': ('2026-11-09', '2026-11-13'),
    'NOV S3': ('2026-11-16', '2026-11-20'),
    'NOV S4': ('2026-11-23', '2026-11-27'),
    'DIC S1': ('2026-11-30', '2026-12-04'),
    'DIC S2': ('2026-12-07', '2026-12-11'),
    'DIC S3': ('2026-12-14', '2026-12-18'),
    'DIC S4': ('2026-12-21', '2026-12-25'),
}

MESES_ABREV = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN',
               'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']

MES_NOMBRE_A_NUM = {
    'ENE': 1, 'FEB': 2, 'MAR': 3, 'ABR': 4, 'MAY': 5, 'JUN': 6,
    'JUL': 7, 'AGO': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DIC': 12,
}

# Mapa inverso: fecha_inicio → etiqueta de semana (ej. '2026-03-23' → 'MAR S4')
FECHA_A_SEMANA = {v[0]: k for k, v in SEMANAS.items()}

NOMBRE_CANONICO = {
    'Daniel Avendaño': 'Daniel Felipe Avendaño Pulido',
}


def normalizar_nombre(nombre):
    return NOMBRE_CANONICO.get(nombre, nombre)


def fecha_col_a_semana(s):
    """'Mar 23' → 'MAR S4', retorna None si la fecha no está en SEMANAS."""
    m = re.match(r'^([A-Za-záéíóúüñ]{3})\s+(\d{1,2})$', s.strip())
    if not m:
        return None
    mes_str = m.group(1).upper().replace('É', 'E').replace('Á', 'A')
    dia = int(m.group(2))
    num = MES_NOMBRE_A_NUM.get(mes_str)
    if num is None:
        return None
    fecha = f"2026-{num:02d}-{dia:02d}"
    return FECHA_A_SEMANA.get(fecha)  # None si no está en SEMANAS (festivo, etc.)


def es_columna_semana(s):
    s_upper = s.upper().strip()
    for mes in MESES_ABREV:
        if re.search(rf'\b{mes}\b.*S\d', s_upper):
            return True
    # Formato de fecha: "Mar 23", "Abr 06", etc.
    if re.match(r'^[A-Za-záéíóúüñ]{3}\s+\d{1,2}$', s.strip()):
        return True
    return False


def normalizar_semana(s):
    """'Feb S1 (17-23)' → 'FEB S1', 'Mar 23' → 'MAR S4', fechas sin semana → None."""
    s_upper = s.upper().strip()
    m = re.search(r'(ENE|FEB|MAR|ABR|MAY|JUN|JUL|AGO|SEP|OCT|NOV|DIC)\s+(S\d)', s_upper)
    if m:
        return f"{m.group(1)} {m.group(2)}"
    # Formato de columna de fecha: "Mar 23" → puede ser None si no está en SEMANAS
    if re.match(r'^[A-Za-záéíóúüñ]{3}\s+\d{1,2}$', s.strip()):
        return fecha_col_a_semana(s)
    return s_upper


def parse_wbs_date(s):
    """'lu. 2/16/26' → '2026-02-16'"""
    if not s or s.strip() in ('-', ''):
        return None
    s = re.sub(r'^[a-záéíóúün]+\.\s*', '', s.strip(), flags=re.IGNORECASE)
    m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', s)
    if m:
        mes, dia, anio = m.groups()
        anio = int(anio)
        if anio < 100:
            anio += 2000
        return f"{anio:04d}-{int(mes):02d}-{int(dia):02d}"
    return None


def parse_tabla(lines):
    """Devuelve (headers, filas) desde líneas de tabla markdown."""
    if len(lines) < 2:
        return [], []
    headers = [c.strip() for c in lines[0].split('|')[1:-1]]
    filas = []
    for line in lines[1:]:
        celdas = [c.strip() for c in line.split('|')[1:-1]]
        if not celdas:
            continue
        if all(re.match(r'^[-:*\s]*$', c) for c in celdas if c):
            continue
        filas.append(celdas)
    return headers, filas


def rango_semanas(week_cols, celdas, offset=0):
    """
    Retorna (fecha_inicio, fecha_fin, semanas_activas[]).
    fecha_inicio/fin: de la primera/última semana con ✅.
    semanas_activas: lista exacta de etiquetas de semana con ✅ (sin None).
    """
    week_cells = celdas[offset:]
    activas_idx = [i for i, c in enumerate(week_cells) if '✅' in c and i < len(week_cols)]
    if not activas_idx:
        return None, None, []
    # Filtrar None (fechas no mapeadas a semana, p.ej. festivos)
    etiquetas = [week_cols[i] for i in activas_idx if week_cols[i] is not None]
    if not etiquetas:
        return None, None, []
    inicio = SEMANAS.get(etiquetas[0])
    fin    = SEMANAS.get(etiquetas[-1])
    return (inicio[0] if inicio else None), (fin[1] if fin else None), etiquetas


def limpiar_texto(s):
    return re.sub(r'\*+', '', s).strip()


def act_dict(persona, titulo, act_id, descripcion, inicio, fin, semanas, progreso=0, orden=0):
    return {
        'colaborador': persona,
        'obligacion': titulo,
        'actividad_id': act_id,
        'descripcion': descripcion,
        'fecha_inicio': inicio,
        'fecha_fin': fin,
        'semanas_activas': semanas,
        'progreso': progreso,
        'orden': orden,
    }


# ============================================================
#  FORMATO 1: Secciones ### con tablas
# ============================================================

def parse_formato_secciones(persona, content):
    actividades = []
    orden = 0

    section_pattern = re.compile(r'^###\s+(.+?)$', re.MULTILINE)
    section_matches = list(section_pattern.finditer(content))
    if not section_matches:
        return actividades

    for idx, match in enumerate(section_matches):
        titulo = re.sub(r'^\d+\.\s+', '', match.group(1).strip())
        start_pos = match.end()
        end_pos = section_matches[idx + 1].start() if idx + 1 < len(section_matches) else len(content)
        bloque = content[start_pos:end_pos]

        tabla_lines = [l.strip() for l in bloque.split('\n') if l.strip().startswith('|')]
        if not tabla_lines:
            continue

        headers, filas = parse_tabla(tabla_lines)
        if not headers:
            continue

        h0 = limpiar_texto(headers[0])
        h1 = limpiar_texto(headers[1]).lower() if len(headers) > 1 else ''

        if h0 in ('#', 'N°', 'No', 'Nro', '№') and h1 in (
                'actividad', 'obligación', 'obligacion', 'descripción', 'descripcion'):
            week_cols = [normalizar_semana(h) for h in headers[2:]]
            for fila in filas:
                if len(fila) < 3:
                    continue
                act_id = limpiar_texto(fila[0])
                desc = limpiar_texto(fila[1])
                ini, fin, sems = rango_semanas(week_cols, fila, 2)
                if ini and fin:
                    actividades.append(act_dict(persona, titulo, act_id, desc, ini, fin, sems, orden=orden))
                    orden += 1
        else:
            week_cols = [normalizar_semana(h) for h in headers]
            for fila in filas:
                ini, fin, sems = rango_semanas(week_cols, fila, 0)
                if ini and fin:
                    actividades.append(act_dict(persona, titulo, '', titulo, ini, fin, sems, orden=orden))
                    orden += 1

    return actividades


# ============================================================
#  FORMATO 2: WBS con fechas explícitas (Fabio Mesa, Diego Veloza)
# ============================================================

def parse_formato_wbs(persona, content):
    actividades = []
    orden = 0

    tabla_lines = [l.strip() for l in content.split('\n') if l.strip().startswith('|')]
    if not tabla_lines:
        return actividades

    headers, filas = parse_tabla(tabla_lines)
    h_norm = [h.lower().strip().lstrip('*').rstrip('*') for h in headers]

    idx_desc = next((i for i, h in enumerate(h_norm) if 'obligación' in h or 'actividad' in h), 1)
    idx_ini = next((i for i, h in enumerate(h_norm) if 'inicio' in h), None)
    idx_fin = next((i for i, h in enumerate(h_norm) if 'finalización' in h or 'finalizacion' in h), None)
    idx_pct = next((i for i, h in enumerate(h_norm) if '%' in h or 'listo' in h), None)

    if idx_ini is None or idx_fin is None:
        return actividades

    obligacion_actual = ''
    for fila in filas:
        if len(fila) <= max(idx_desc, idx_ini, idx_fin):
            continue
        wbs = limpiar_texto(fila[0])
        desc = limpiar_texto(fila[idx_desc])

        if not re.match(r'\d+\.\d+', wbs):
            obligacion_actual = desc
            continue

        ini = parse_wbs_date(fila[idx_ini])
        fin = parse_wbs_date(fila[idx_fin])
        if not ini or not fin:
            continue

        progreso = 0
        if idx_pct is not None and idx_pct < len(fila):
            try:
                progreso = int(float(fila[idx_pct].replace('%', '').strip()))
            except (ValueError, TypeError):
                progreso = 0

        # Para WBS, semanas_activas se genera a partir del rango de fechas
        # (no hay columnas de semana en este formato — usamos semanas del rango)
        sems = semanas_en_rango(ini, fin)
        actividades.append(act_dict(persona, obligacion_actual, wbs, desc, ini, fin, sems, progreso, orden))
        orden += 1

    return actividades


def semanas_en_rango(fecha_ini_str, fecha_fin_str):
    """Genera lista de semanas del SEMANAS que caen en el rango de fechas dado."""
    from datetime import date
    try:
        ini = date.fromisoformat(fecha_ini_str)
        fin = date.fromisoformat(fecha_fin_str)
    except (ValueError, TypeError):
        return []
    resultado = []
    for sem, (s_ini, s_fin) in SEMANAS.items():
        s_ini_d = date.fromisoformat(s_ini)
        s_fin_d = date.fromisoformat(s_fin)
        if s_ini_d <= fin and s_fin_d >= ini:
            resultado.append(sem)
    return resultado


# ============================================================
#  FORMATO 3: Obligación + Actividad + semanas (Luis Silvestre)
# ============================================================

def parse_formato_tabla_plana_dos_cols(persona, content):
    actividades = []
    orden = 0

    tabla_lines = [l.strip() for l in content.split('\n') if l.strip().startswith('|')]
    if not tabla_lines:
        return actividades

    headers, filas = parse_tabla(tabla_lines)
    if len(headers) < 3:
        return actividades

    week_cols = [normalizar_semana(h) for h in headers[2:]]

    for fila in filas:
        if len(fila) < 3:
            continue
        obligacion = limpiar_texto(fila[0])
        desc = limpiar_texto(fila[1])
        ini, fin, sems = rango_semanas(week_cols, fila, 2)
        if ini and fin:
            actividades.append(act_dict(persona, obligacion, '', desc, ini, fin, sems, orden=orden))
            orden += 1

    return actividades


# ============================================================
#  FORMATO 4: Tabla plana sin secciones ###
#  (Diego Orjuela, Jhoan Ramírez, Olaf, Gabriel, Iván, Luis Miguel, Julián)
# ============================================================

def parse_formato_tabla_sin_secciones(persona, content):
    actividades = []
    orden = 0

    tabla_lines = [l.strip() for l in content.split('\n') if l.strip().startswith('|')]
    if not tabla_lines:
        return actividades

    headers, filas = parse_tabla(tabla_lines)
    if len(headers) < 3:
        return actividades

    # Encontrar primer índice de columna de semana
    week_start = None
    for i, h in enumerate(headers):
        if es_columna_semana(h):
            week_start = i
            break

    if week_start is None:
        return actividades

    week_cols = [normalizar_semana(h) for h in headers[week_start:]]

    obligacion_actual = ''
    for fila in filas:
        if len(fila) < week_start + 1:
            continue

        raw_id = fila[0].strip()
        act_id = limpiar_texto(raw_id)
        desc = limpiar_texto(fila[1]) if len(fila) > 1 else ''

        semanas_fila = fila[week_start:]
        tiene_activas = any('✅' in c for c in semanas_fila)

        # Fila de encabezado de obligación: negrita **N** o sin ✅
        es_header_oblig = (raw_id.startswith('**') and raw_id.endswith('**'))
        if not tiene_activas or es_header_oblig:
            if desc:
                obligacion_actual = re.sub(r'\s*_.*', '', desc).strip()
            continue

        ini, fin, sems = rango_semanas(week_cols, fila, week_start)
        if not ini or not fin:
            continue

        oblig = obligacion_actual if obligacion_actual else desc[:120]
        actividades.append(act_dict(persona, oblig, act_id, desc, ini, fin, sems, orden=orden))
        orden += 1

    return actividades


# ============================================================
#  DETECCIÓN DE FORMATO
# ============================================================

def detectar_formato(content):
    if re.search(r'^\s*\|\s*WBS\s*\|', content, re.MULTILINE | re.IGNORECASE):
        return 'wbs'
    if re.search(r'^###\s+\d+\.', content, re.MULTILINE):
        return 'secciones'
    primera_tabla = re.search(r'^\|(.+)\|$', content, re.MULTILINE)
    if primera_tabla:
        cols = [c.strip() for c in primera_tabla.group(1).split('|')]
        cols_lower = [c.lower() for c in cols]
        if len(cols_lower) >= 3 and 'obligaci' in cols_lower[0] and 'actividad' in cols_lower[1]:
            return 'tabla_plana_dos_cols'
        if cols_lower[0] in ('#', 'n°', 'no', 'nro') or re.match(r'^\d+$', cols[0]):
            return 'tabla_sin_secciones'
    return 'secciones'


def parsear_archivo(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    m = re.search(r'^#\s+Cronograma.*$', content, re.MULTILINE)
    if m:
        partes = re.split(r'[—–]', m.group(0))
        persona = normalizar_nombre(partes[-1].strip())
    else:
        persona = (
            os.path.basename(filepath)
            .replace('Cronograma_2026_', '')
            .replace('.md', '')
            .replace('_', ' ')
        )

    formato = detectar_formato(content)
    parsers = {
        'wbs':                    parse_formato_wbs,
        'secciones':              parse_formato_secciones,
        'tabla_plana_dos_cols':   parse_formato_tabla_plana_dos_cols,
        'tabla_sin_secciones':    parse_formato_tabla_sin_secciones,
    }
    return persona, parsers[formato](persona, content)


# ============================================================
#  COMMAND
# ============================================================

class Command(BaseCommand):
    help = 'Importa cronogramas desde archivos .md (guarda semanas exactas activas)'

    def add_arguments(self, parser):
        parser.add_argument('--limpiar', action='store_true',
                            help='Elimina actividades existentes antes de importar')

    def handle(self, *args, **options):
        data_dir = os.path.join(
            os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )),
            'data', 'Cronogramas_actividades'
        )

        if not os.path.isdir(data_dir):
            self.stderr.write(f"Directorio no encontrado: {data_dir}")
            return

        if options['limpiar']:
            deleted, _ = CronogramaActividad.objects.all().delete()
            self.stdout.write(f"  Eliminadas {deleted} actividades existentes.")

        archivos = sorted(f for f in os.listdir(data_dir) if f.endswith('.md'))
        total = 0

        for archivo in archivos:
            filepath = os.path.join(data_dir, archivo)
            try:
                persona, actividades = parsear_archivo(filepath)
                for a in actividades:
                    CronogramaActividad.objects.create(
                        colaborador=a['colaborador'],
                        obligacion=a['obligacion'],
                        actividad_id=a.get('actividad_id', ''),
                        descripcion=a['descripcion'],
                        fecha_inicio=a['fecha_inicio'],
                        fecha_fin=a['fecha_fin'],
                        semanas_activas=a.get('semanas_activas', []),
                        progreso=a.get('progreso', 0),
                        estado='pendiente',
                        orden=a.get('orden', 0),
                    )
                n = len(actividades)
                self.stdout.write(self.style.SUCCESS(f"  ✓ {persona}: {n} actividades"))
                total += n
            except Exception as e:
                import traceback
                self.stderr.write(f"  ✗ {archivo}: {e}\n{traceback.format_exc()}")

        self.stdout.write(self.style.SUCCESS(f"\nTotal importadas: {total} actividades"))
