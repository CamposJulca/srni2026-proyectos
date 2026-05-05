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

// Colores fijos por proyecto
const COLORES_PROYECTO = {
  'VIVANTO':                        '#003087',
  'Caracterización':                '#00875a',
  'Modelo Integrado':               '#CE1126',
  'Nuevo Ruv':                      '#7c3aed',
  'Ruv Temporal-Sirav-Sipod':       '#0891b2',
  'Transformación Ficha Estratégica':'#d97706',
};
const PALETA_PROYECTOS = Object.values(COLORES_PROYECTO);
const COLOR_SIN_PROYECTO = '#94a3b8';

function colorProyecto(nombre) {
  return COLORES_PROYECTO[nombre] || COLOR_SIN_PROYECTO;
}

// Proyecto activo en el filtro (se actualiza en cargarDatos)
let filtroProyectoActivo = '';

// Asignar colores a obligaciones de forma consistente
let coloresObligacion = {};
let obligIdx = 0;

function resetColoresObligacion() {
  coloresObligacion = {};
  obligIdx = 0;
}

function colorObligacion(obligacion) {
  if (!coloresObligacion[obligacion]) {
    coloresObligacion[obligacion] = PALETA_PROYECTOS[obligIdx % PALETA_PROYECTOS.length];
    obligIdx++;
  }
  return coloresObligacion[obligacion];
}

// Determinar el color de una tarea
function colorTarea(task) {
  // 1. Si hay filtro de proyecto activo, usar ese color
  if (filtroProyectoActivo) return colorProyecto(filtroProyectoActivo);
  // 2. Si la actividad tiene proyecto directo
  if (task.proyecto) return colorProyecto(task.proyecto);
  // 3. Si el colaborador tiene un solo proyecto
  if (task.proyectos && task.proyectos.length === 1) return colorProyecto(task.proyectos[0]);
  // 4. Asignar color por obligación (cada obligación = un color distinto)
  return colorObligacion(task.obligacion);
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

  // Agrupar por colaborador → obligación
  const grupos = {};
  tasks.forEach(t => {
    if (!grupos[t.colaborador]) grupos[t.colaborador] = {};
    if (!grupos[t.colaborador][t.obligacion]) grupos[t.colaborador][t.obligacion] = [];
    grupos[t.colaborador][t.obligacion].push(t);
  });

  const timelineW = MESES.length * MES_W;
  const stripesCSS = `repeating-linear-gradient(90deg,transparent,transparent ${SEM_W - 1}px,#e2e8f0 ${SEM_W - 1}px,#e2e8f0 ${SEM_W}px)`;

  body.innerHTML = Object.entries(grupos).map(([colaborador, obligs]) => {
    const grupoHtml = `
      <div class="gantt-grupo">
        <div class="gantt-grupo-nombre">
          ${colaborador}
        </div>
        <div class="gantt-grupo-timeline" style="min-width:${timelineW}px;background:${stripesCSS}"></div>
      </div>`;

    const obligsHtml = Object.entries(obligs).map(([obligacion, acts]) => {
      const subgrupoHtml = `
        <div class="gantt-subgrupo">
          <div class="gantt-subgrupo-nombre" title="${obligacion}">
            <span class="gantt-subgrupo-num">${acts.length}</span>
            ${obligacion}
          </div>
          <div class="gantt-subgrupo-timeline" style="min-width:${timelineW}px"></div>
        </div>`;

      const filasHtml = acts.map(t => {
        const left  = fechaALeft(t.fecha_inicio);
        const width = fechaAWidth(t.fecha_inicio, t.fecha_fin);
        const barColor = colorTarea(t);
        const labelBar = t.actividad_id ? `${t.actividad_id} · ${t.descripcion}` : t.descripcion;
        const proyTag = t.proyecto ? `<span class="gantt-row-proy" style="background:${barColor}20;color:${barColor}">${t.proyecto}</span>` : '';

        return `
          <div class="gantt-row" data-id="${t.id}">
            <div class="gantt-row-izq">
              <div class="gantt-row-top">
                ${t.actividad_id ? `<span class="gantt-row-id">${t.actividad_id}</span>` : ''}
                ${proyTag}
              </div>
              <span class="gantt-row-desc" title="${t.descripcion}">${t.descripcion}</span>
            </div>
            <div class="gantt-row-der" style="min-width:${timelineW}px;background:${stripesCSS}"
                 data-task='${JSON.stringify(t).replace(/'/g,"&#39;")}'>
              <div class="gantt-bar" data-estado="${t.estado_visual}"
                   style="left:${left}px;width:${width}px;background:${barColor}"
                   title="${t.descripcion}">
                <div class="gantt-bar-progreso" style="width:${t.progreso}%"></div>
                <span class="gantt-bar-label">${labelBar}</span>
              </div>
            </div>
          </div>`;
      }).join('');

      return subgrupoHtml + filasHtml;
    }).join('');

    return grupoHtml + obligsHtml;
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

  tbody.innerHTML = tasks.map(t => {
    const pc = colorTarea(t);
    const pn = t.proyecto || (t.proyectos && t.proyectos.length === 1 ? t.proyectos[0] : '');
    const proyBadge = pn ? `<span class="td-proy-badge" style="background:${pc}20;color:${pc};border:1px solid ${pc}40">${pn}</span>` : '';
    return `
    <tr data-id="${t.id}">
      <td>${t.colaborador}</td>
      <td class="td-oblig" title="${t.obligacion}">${t.obligacion}</td>
      <td class="td-id">${t.actividad_id || '—'}</td>
      <td class="td-desc">${proyBadge}<span title="${t.descripcion}">${t.descripcion}</span></td>
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
    </tr>`;
  }).join('');

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
    <p>Selecciona un colaborador o proyecto para ver el cronograma</p>`;
  body.innerHTML = '';
  body.appendChild(empty);
  empty.style.display = 'flex';
  renderStats([]);
  renderTabla([]);
  const leyenda = document.getElementById('act-leyenda');
  if (leyenda) leyenda.innerHTML = '';
  document.getElementById('gantt-hoy-line').style.display = 'none';
}

// ---- Leyenda de proyectos ----
function renderLeyenda(tasks) {
  const leyenda = document.getElementById('act-leyenda');
  if (!leyenda || !tasks.length) { if (leyenda) leyenda.innerHTML = ''; return; }

  if (filtroProyectoActivo) {
    // Filtro por proyecto activo: mostrar solo ese proyecto
    const c = colorProyecto(filtroProyectoActivo);
    leyenda.innerHTML = `<span class="act-leyenda-titulo">Proyecto:</span>
      <span class="act-leyenda-item"><span class="act-leyenda-dot" style="background:${c}"></span>${filtroProyectoActivo}</span>`;
    return;
  }

  // Sin filtro de proyecto: mostrar leyenda completa
  const items = Object.entries(COLORES_PROYECTO).map(([nombre, color]) =>
    `<span class="act-leyenda-item"><span class="act-leyenda-dot" style="background:${color}"></span>${nombre}</span>`
  ).join('');
  leyenda.innerHTML = '<span class="act-leyenda-titulo">Proyectos:</span>' + items;
}

// ---- Cargar datos ----
async function cargarDatos() {
  const colaborador = document.getElementById('filtro-colaborador').value;
  const estado      = document.getElementById('filtro-estado').value;
  const obligacion  = document.getElementById('filtro-obligacion').value;
  const proyecto    = document.getElementById('filtro-proyecto').value;

  // Actualizar estado global para coloreo
  filtroProyectoActivo = proyecto;
  resetColoresObligacion();

  if (!colaborador && !proyecto) {
    mostrarPlaceholder();
    return;
  }

  const params = new URLSearchParams();
  if (colaborador) params.set('colaborador', colaborador);
  if (estado)      params.set('estado', estado);
  if (obligacion)  params.set('obligacion', obligacion);
  if (proyecto)    params.set('proyecto', proyecto);

  const res = await fetch('/api/actividades/?' + params.toString());
  const data = await res.json();

  renderStats(data.tasks);
  renderGantt(data.tasks);
  renderTabla(data.tasks);
  renderLeyenda(data.tasks);
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

let currentGanttActId = null;

function abrirModalEditar(task) {
  abrirModal('Editar actividad', task);
  currentGanttActId = task.id;
  document.getElementById('gantt-evidencias-wrap').style.display = 'block';
  const warn = document.getElementById('gantt-modal-warning');
  if (warn) warn.style.display = 'none';
  cargarEvidenciasGantt(task.id);
}

function abrirModalNuevo() {
  abrirModal('Nueva actividad', {});
  currentGanttActId = null;
  document.getElementById('gantt-evidencias-wrap').style.display = 'none';
}

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
    const data = await res.json();
    const warn = document.getElementById('gantt-modal-warning');
    if (warn) {
      warn.textContent = data.error || 'Error al guardar';
      warn.style.display = 'block';
    } else {
      alert('Error: ' + (data.error || 'No se pudo guardar'));
    }
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
const btnNueva = document.getElementById('btn-nueva-actividad');
if (btnNueva) btnNueva.addEventListener('click', abrirModalNuevo);

// Filtros
// ---- Filtro de procedimiento → actualiza datalist de colaboradores ----
const filtroProcEl = document.getElementById('filtro-procedimiento');
const filtroColabEl = document.getElementById('filtro-colaborador');
const datalistEl = document.getElementById('lista-colaboradores');

function actualizarDatalist() {
  const proc = filtroProcEl.value;
  let nombres;
  if (proc && COLABS_POR_PROC[proc]) {
    nombres = COLABS_POR_PROC[proc];
  } else {
    // Todos los colaboradores de todos los procedimientos
    nombres = Object.values(COLABS_POR_PROC).flat().sort();
  }
  datalistEl.innerHTML = nombres.map(n => `<option value="${n}">`).join('');
  // Si el colaborador actual no está en el nuevo listado, limpiar
  if (filtroColabEl.value && !nombres.includes(filtroColabEl.value)) {
    filtroColabEl.value = '';
  }
}

filtroProcEl.addEventListener('change', () => {
  actualizarDatalist();
  cargarDatos();
});

// Colaborador: cargar cuando se selecciona un valor válido del datalist
let colabTimer = null;
filtroColabEl.addEventListener('input', () => {
  clearTimeout(colabTimer);
  colabTimer = setTimeout(() => {
    // Verificar si el valor es un nombre completo válido
    const val = filtroColabEl.value.trim();
    const allNames = Object.values(COLABS_POR_PROC).flat();
    if (!val || allNames.includes(val)) {
      cargarDatos();
    }
  }, 300);
});

// Limpiar con Escape
filtroColabEl.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    filtroColabEl.value = '';
    cargarDatos();
  }
});

['filtro-estado', 'filtro-obligacion', 'filtro-proyecto'].forEach(id => {
  document.getElementById(id).addEventListener('change', cargarDatos);
});

// ============================================================
//  EVIDENCIAS en modal Gantt
// ============================================================

async function cargarEvidenciasGantt(actId) {
  const lista = document.getElementById('gantt-evidencias-list');
  if (!lista) return;
  lista.innerHTML = '<p class="mic-evidencias-vacio">Cargando...</p>';

  try {
    const res = await fetch(`/api/evidencias/${actId}/`);
    const data = await res.json();

    if (data.evidencias.length === 0) {
      lista.innerHTML = '<p class="mic-evidencias-vacio">Sin evidencias adjuntas</p>';
      return;
    }

    lista.innerHTML = data.evidencias.map(ev => `
      <div class="mic-ev-item">
        <a href="${ev.archivo_url}" target="_blank" class="mic-ev-link" title="${ev.nombre}">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;flex-shrink:0">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
          <span>${ev.nombre}</span>
        </a>
        <span class="mic-ev-meta">${ev.creado_por} · ${ev.creado_en}${ev.comentario ? ' — ' + ev.comentario : ''}</span>
        <button type="button" class="mic-ev-del" data-id="${ev.id}" title="Eliminar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:12px;height:12px">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
    `).join('');

    lista.querySelectorAll('.mic-ev-del').forEach(btn => {
      btn.addEventListener('click', async () => {
        if (!confirm('Eliminar esta evidencia?')) return;
        await fetch(`/api/evidencias/eliminar/${btn.dataset.id}/`, {
          method: 'POST', headers: { 'X-CSRFToken': getCookie('csrftoken') },
        });
        cargarEvidenciasGantt(actId);
      });
    });
  } catch {
    lista.innerHTML = '<p class="mic-evidencias-vacio">Error al cargar</p>';
  }
}

const ganttUploadBtn = document.getElementById('gantt-btn-upload');
const ganttUploadInput = document.getElementById('gantt-upload-input');

if (ganttUploadBtn && ganttUploadInput) {
  ganttUploadBtn.addEventListener('click', () => ganttUploadInput.click());

  ganttUploadInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
      alert('El archivo no puede superar 10MB');
      e.target.value = '';
      return;
    }

    const comentario = document.getElementById('gantt-upload-comentario').value.trim();
    const formData = new FormData();
    formData.append('archivo', file);
    formData.append('comentario', comentario);

    ganttUploadBtn.disabled = true;
    ganttUploadBtn.textContent = 'Subiendo...';

    try {
      const res = await fetch(`/api/evidencias/${currentGanttActId}/subir/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        body: formData,
      });
      if (res.ok) {
        document.getElementById('gantt-upload-comentario').value = '';
        cargarEvidenciasGantt(currentGanttActId);
      } else {
        const d = await res.json();
        alert(d.error || 'Error al subir');
      }
    } catch (err) {
      alert('Error: ' + err.message);
    } finally {
      ganttUploadBtn.disabled = false;
      ganttUploadBtn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:13px;height:13px"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg> Subir archivo`;
      e.target.value = '';
    }
  });
}

// ---- Init ----
renderTimelineHeader();
cargarDatos();
