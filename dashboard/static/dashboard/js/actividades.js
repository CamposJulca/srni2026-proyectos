/* ============================================================
   ACTIVIDADES — CRONOGRAMA GANTT
   ============================================================ */

// --- Configuración del timeline ---
const TIMELINE = {
  inicio: new Date('2026-01-01'),
  fin:    new Date('2026-12-31'),
};
const TOTAL_DIAS = (TIMELINE.fin - TIMELINE.inicio) / 86400000;

const MESES = [
  { label: 'Enero',      semanas: ['S1','S2','S3','S4'], dias_inicio: 1  },
  { label: 'Febrero',    semanas: ['S1','S2','S3','S4'], dias_inicio: 32 },
  { label: 'Marzo',      semanas: ['S1','S2','S3','S4'], dias_inicio: 60 },
  { label: 'Abril',      semanas: ['S1','S2','S3','S4'], dias_inicio: 91 },
  { label: 'Mayo',       semanas: ['S1','S2','S3','S4'], dias_inicio: 121},
  { label: 'Junio',      semanas: ['S1','S2','S3','S4'], dias_inicio: 152},
  { label: 'Julio',      semanas: ['S1','S2','S3','S4'], dias_inicio: 182},
  { label: 'Agosto',     semanas: ['S1','S2','S3','S4'], dias_inicio: 213},
  { label: 'Septiembre', semanas: ['S1','S2','S3','S4'], dias_inicio: 244},
  { label: 'Octubre',    semanas: ['S1','S2','S3','S4'], dias_inicio: 274},
  { label: 'Noviembre',  semanas: ['S1','S2','S3','S4'], dias_inicio: 305},
  { label: 'Diciembre',  semanas: ['S1','S2','S3','S4'], dias_inicio: 335},
];

// Ancho en px de cada semana en el timeline
const SEM_W = 52;
const MES_W = SEM_W * 4;

// Colores por colaborador (orden del array)
const PALETA = [
  '#003087','#00875a','#CE1126','#7c3aed','#0891b2',
  '#d97706','#be185d','#065f46','#1e40af','#92400e',
  '#5b21b6','#047857','#b91c1c','#1d4ed8','#15803d',
  '#c2410c','#6d28d9','#0e7490','#9a3412','#166534',
];

let coloresColaborador = {};
let paletaIdx = 0;

function colorColaborador(nombre) {
  if (!coloresColaborador[nombre]) {
    coloresColaborador[nombre] = PALETA[paletaIdx % PALETA.length];
    paletaIdx++;
  }
  return coloresColaborador[nombre];
}

// ---- Conversión fecha → posición ----
function diaDesdeInicio(fechaStr) {
  const d = new Date(fechaStr + 'T00:00:00');
  return (d - TIMELINE.inicio) / 86400000;
}

function fechaALeft(fechaStr) {
  const dias = diaDesdeInicio(fechaStr);
  return Math.max(0, (dias / TOTAL_DIAS) * (MESES.length * MES_W));
}

function fechaAWidth(inicioStr, finStr) {
  const d0 = diaDesdeInicio(inicioStr);
  const d1 = diaDesdeInicio(finStr);
  const anchoPx = ((d1 - d0 + 5) / TOTAL_DIAS) * (MESES.length * MES_W);
  return Math.max(8, anchoPx);
}

// ---- Estado visual ----
function badgeEstado(estado) {
  const labels = {
    pendiente: 'Pendiente', en_curso: 'En Curso',
    completada: 'Completada', bloqueada: 'Bloqueada',
  };
  return `<span class="badge-estado badge-${estado}">${labels[estado] || estado}</span>`;
}

// ---- Renderizar header del timeline ----
function renderTimelineHeader() {
  const hdr = document.getElementById('gantt-timeline-header');
  hdr.style.minWidth = (MESES.length * MES_W) + 'px';
  hdr.innerHTML = MESES.map(m => `
    <div class="gantt-mes" style="width:${MES_W}px;min-width:${MES_W}px">
      <div class="gantt-mes-label">${m.label}</div>
      <div class="gantt-mes-semanas">
        ${m.semanas.map(s =>
          `<div class="gantt-semana-label" style="width:${SEM_W}px">${s}</div>`
        ).join('')}
      </div>
    </div>
  `).join('');
}

// ---- Línea de hoy ----
function renderHoyLine() {
  const hoy = new Date();
  const line = document.getElementById('gantt-hoy-line');
  if (hoy < TIMELINE.inicio || hoy > TIMELINE.fin) { line.style.display = 'none'; return; }
  const left = fechaALeft(hoy.toISOString().slice(0, 10));
  // La línea se posiciona relativa al gantt-scroll-x, que incluye la col-izq (280px)
  line.style.left = (280 + left) + 'px';
  line.style.display = 'block';
}

// ---- Renderizar Gantt ----
function renderGantt(tasks) {
  const body = document.getElementById('gantt-body');
  let empty = document.getElementById('gantt-empty');

  // Restaurar el elemento empty si fue removido del DOM
  if (!empty) {
    empty = document.createElement('div');
    empty.id = 'gantt-empty';
    empty.className = 'gantt-empty';
  }

  if (!tasks.length) {
    empty.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/>
        <line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
      </svg>
      <p>No hay actividades para los filtros seleccionados</p>`;
    body.innerHTML = '';
    body.appendChild(empty);
    empty.style.display = 'flex';
    return;
  }
  empty.style.display = 'none';

  // Agrupar por colaborador
  const grupos = {};
  tasks.forEach(t => {
    if (!grupos[t.colaborador]) grupos[t.colaborador] = [];
    grupos[t.colaborador].push(t);
  });

  const timelineW = MESES.length * MES_W;
  const stripesCSS = `repeating-linear-gradient(90deg,transparent,transparent ${SEM_W - 1}px,#e2e8f0 ${SEM_W - 1}px,#e2e8f0 ${SEM_W}px)`;

  body.innerHTML = Object.entries(grupos).map(([colaborador, acts]) => {
    const color = colorColaborador(colaborador);
    const grupoHtml = `
      <div class="gantt-grupo">
        <div class="gantt-grupo-nombre">
          <span class="gantt-grupo-dot" style="background:${color}"></span>
          ${colaborador}
        </div>
        <div class="gantt-grupo-timeline" style="min-width:${timelineW}px;background:${stripesCSS},${color}11"></div>
      </div>`;

    const filasHtml = acts.map(t => {
      const left  = fechaALeft(t.fecha_inicio);
      const width = fechaAWidth(t.fecha_inicio, t.fecha_fin);
      const desc  = t.descripcion.length > 35 ? t.descripcion.slice(0, 35) + '…' : t.descripcion;
      const labelBar = t.actividad_id ? `${t.actividad_id} · ${desc}` : desc;

      return `
        <div class="gantt-row" data-id="${t.id}">
          <div class="gantt-row-izq">
            ${t.actividad_id ? `<span class="gantt-row-id">${t.actividad_id}</span>` : ''}
            <span class="gantt-row-desc" title="${t.descripcion}">${t.descripcion}</span>
            <span class="gantt-row-oblig" title="${t.obligacion}">${t.obligacion}</span>
          </div>
          <div class="gantt-row-der" style="min-width:${timelineW}px;background:${stripesCSS}"
               data-task='${JSON.stringify(t).replace(/'/g,"&#39;")}'>
            <div class="gantt-bar" data-estado="${t.estado_visual}"
                 style="left:${left}px;width:${width}px;background:${color}"
                 title="${t.descripcion}">
              <div class="gantt-bar-progreso" style="width:${t.progreso}%"></div>
              <span class="gantt-bar-label">${labelBar}</span>
            </div>
          </div>
        </div>`;
    }).join('');

    return grupoHtml + filasHtml;
  }).join('');

  // Click en barra → abrir modal edición
  body.querySelectorAll('.gantt-row-der').forEach(el => {
    el.addEventListener('click', () => {
      const t = JSON.parse(el.dataset.task);
      abrirModalEditar(t);
    });
  });
}

// ---- Renderizar tabla ----
function renderTabla(tasks) {
  const tbody = document.getElementById('act-tabla-body');
  document.getElementById('act-tabla-count').textContent = `${tasks.length} actividades`;

  if (!tasks.length) {
    tbody.innerHTML = `<tr><td colspan="9" style="text-align:center;padding:24px;color:var(--gris-3)">Sin resultados</td></tr>`;
    return;
  }

  tbody.innerHTML = tasks.map(t => `
    <tr data-id="${t.id}">
      <td>${t.colaborador}</td>
      <td class="td-oblig" title="${t.obligacion}">${t.obligacion}</td>
      <td class="td-id">${t.actividad_id || '—'}</td>
      <td class="td-desc" title="${t.descripcion}">${t.descripcion}</td>
      <td class="td-fecha">${formatFecha(t.fecha_inicio)}</td>
      <td class="td-fecha">${formatFecha(t.fecha_fin)}</td>
      <td>
        <div class="prog-wrap">
          <div class="prog-bar-bg"><div class="prog-bar-fill" style="width:${t.progreso}%"></div></div>
          <span class="prog-pct">${t.progreso}%</span>
        </div>
      </td>
      <td>${badgeEstado(t.estado)}</td>
      <td><button class="act-btn-edit" data-id="${t.id}">Editar</button></td>
    </tr>
  `).join('');

  tbody.querySelectorAll('.act-btn-edit').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = parseInt(btn.dataset.id);
      const t = tasks.find(x => x.id === id);
      if (t) abrirModalEditar(t);
    });
  });
}

// ---- Stats ----
function renderStats(tasks) {
  const counts = { pendiente: 0, en_curso: 0, completada: 0, bloqueada: 0 };
  tasks.forEach(t => {
    if (counts[t.estado] !== undefined) counts[t.estado]++;
  });
  document.getElementById('stat-total').textContent = tasks.length;
  Object.entries(counts).forEach(([k, v]) => {
    const el = document.getElementById(`stat-${k}`);
    if (el) el.textContent = v;
  });
}

// ---- Helpers ----
function formatFecha(s) {
  if (!s) return '—';
  const [y, m, d] = s.split('-');
  return `${d}/${m}/${y}`;
}

function getCookie(name) {
  const v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
  return v ? v[2] : null;
}

// ---- Placeholder: seleccionar colaborador ----
function mostrarPlaceholder() {
  const body = document.getElementById('gantt-body');
  const empty = document.getElementById('gantt-empty');
  // Reemplazar contenido del empty sin destruir el elemento del DOM
  empty.innerHTML = `
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
    </svg>
    <p>Selecciona un colaborador para ver su cronograma</p>`;
  body.innerHTML = '';
  body.appendChild(empty);
  empty.style.display = 'flex';
  renderStats([]);
  renderTabla([]);
  document.getElementById('gantt-hoy-line').style.display = 'none';
}

// ---- Cargar datos ----
async function cargarDatos() {
  const colaborador = document.getElementById('filtro-colaborador').value;
  const estado      = document.getElementById('filtro-estado').value;
  const obligacion  = document.getElementById('filtro-obligacion').value;

  if (!colaborador) {
    mostrarPlaceholder();
    return;
  }

  const params = new URLSearchParams();
  params.set('colaborador', colaborador);
  if (estado)    params.set('estado', estado);
  if (obligacion) params.set('obligacion', obligacion);

  const res = await fetch('/api/actividades/?' + params.toString());
  const data = await res.json();

  renderStats(data.tasks);
  renderGantt(data.tasks);
  renderTabla(data.tasks);
  renderHoyLine();
}

// ============================================================
//  MODAL
// ============================================================
const overlay    = document.getElementById('act-modal-overlay');
const modalTitulo = document.getElementById('act-modal-titulo');
const btnEliminar = document.getElementById('btn-modal-eliminar');

function abrirModal(titulo, task) {
  modalTitulo.textContent = titulo;
  document.getElementById('modal-id').value            = task.id || '';
  document.getElementById('modal-colaborador').value   = task.colaborador || '';
  document.getElementById('modal-actividad-id').value  = task.actividad_id || '';
  document.getElementById('modal-obligacion').value    = task.obligacion || '';
  document.getElementById('modal-descripcion').value   = task.descripcion || '';
  document.getElementById('modal-inicio').value        = task.fecha_inicio || '';
  document.getElementById('modal-fin').value           = task.fecha_fin || '';
  document.getElementById('modal-estado').value        = task.estado || 'pendiente';
  document.getElementById('modal-progreso').value      = task.progreso || 0;
  document.getElementById('modal-progreso-val').textContent = task.progreso || 0;

  btnEliminar.style.display = task.id ? 'block' : 'none';
  overlay.classList.add('visible');
}

function abrirModalEditar(task) { abrirModal('Editar actividad', task); }
function abrirModalNuevo()       { abrirModal('Nueva actividad', {}); }

function cerrarModal() { overlay.classList.remove('visible'); }

// Actualizar label del rango de progreso
document.getElementById('modal-progreso').addEventListener('input', e => {
  document.getElementById('modal-progreso-val').textContent = e.target.value;
});

// Cerrar modal
document.getElementById('act-modal-close').addEventListener('click', cerrarModal);
document.getElementById('btn-modal-cancelar').addEventListener('click', cerrarModal);
overlay.addEventListener('click', e => { if (e.target === overlay) cerrarModal(); });

// Guardar
document.getElementById('act-modal-form').addEventListener('submit', async e => {
  e.preventDefault();
  const id = document.getElementById('modal-id').value;
  const payload = {
    colaborador:  document.getElementById('modal-colaborador').value,
    actividad_id: document.getElementById('modal-actividad-id').value,
    obligacion:   document.getElementById('modal-obligacion').value,
    descripcion:  document.getElementById('modal-descripcion').value,
    fecha_inicio: document.getElementById('modal-inicio').value,
    fecha_fin:    document.getElementById('modal-fin').value,
    estado:       document.getElementById('modal-estado').value,
    progreso:     parseInt(document.getElementById('modal-progreso').value),
  };

  const headers = {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken'),
  };

  let res;
  if (id) {
    res = await fetch(`/api/actividades/${id}/`, { method: 'PUT', headers, body: JSON.stringify(payload) });
  } else {
    res = await fetch('/api/actividades/crear/', { method: 'POST', headers, body: JSON.stringify(payload) });
  }

  if (res.ok) {
    cerrarModal();
    cargarDatos();
  } else {
    const err = await res.json();
    alert('Error: ' + (err.error || 'No se pudo guardar'));
  }
});

// Eliminar
btnEliminar.addEventListener('click', async () => {
  const id = document.getElementById('modal-id').value;
  if (!id || !confirm('¿Eliminar esta actividad?')) return;
  const res = await fetch(`/api/actividades/${id}/`, {
    method: 'DELETE',
    headers: { 'X-CSRFToken': getCookie('csrftoken') },
  });
  if (res.ok) { cerrarModal(); cargarDatos(); }
});

// Nueva actividad
document.getElementById('btn-nueva-actividad').addEventListener('click', abrirModalNuevo);

// Filtros
['filtro-colaborador', 'filtro-estado', 'filtro-obligacion'].forEach(id => {
  document.getElementById(id).addEventListener('change', cargarDatos);
});

// ---- Init ----
renderTimelineHeader();
cargarDatos();
