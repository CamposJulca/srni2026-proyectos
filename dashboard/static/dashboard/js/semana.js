/* ============================================================
   VISTA SEMANAL — compromisos por persona
   ============================================================ */

const PALETA = [
  '#003087','#00875a','#CE1126','#7c3aed','#0891b2',
  '#d97706','#be185d','#065f46','#1e40af','#92400e',
  '#5b21b6','#047857','#b91c1c','#1d4ed8','#15803d',
  '#c2410c','#6d28d9','#0e7490','#9a3412','#166534',
];
const coloresMap = {};
let paletaIdx = 0;
function colorColab(nombre) {
  if (!coloresMap[nombre]) { coloresMap[nombre] = PALETA[paletaIdx++ % PALETA.length]; }
  return coloresMap[nombre];
}

function getCookie(name) {
  const v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
  return v ? v[2] : null;
}

function formatFecha(s) {
  if (!s) return '';
  const [y, m, d] = s.split('-');
  return `${d}/${m}/${y}`;
}

function estadoColor(estado) {
  const m = { pendiente:'#94a3b8', en_curso:'#0891b2', completada:'#00875a', bloqueada:'#CE1126' };
  return m[estado] || '#94a3b8';
}

// ---- Obtener semana actual del selector ----
function semanaActual() {
  return document.getElementById('sel-semana').value;
}

function colaboradorFiltro() {
  return document.getElementById('filtro-colaborador-sem').value;
}

// ---- Actualizar display de fechas ----
function actualizarFechas(semana) {
  const fechas = SEMANA_FECHAS[semana];
  const el = document.getElementById('sem-fechas');
  if (fechas) {
    el.textContent = `${formatFecha(fechas[0])} — ${formatFecha(fechas[1])}`;
  }
  // Marcar si es la semana actual
  const hoyEsSemana = esHoy(semana);
  document.getElementById('sem-fechas').style.color = hoyEsSemana ? '#00875a' : '';
  if (hoyEsSemana) {
    document.getElementById('sem-fechas').textContent += '  ← semana actual';
  }
}

function esHoy(semana) {
  const hoy = new Date();
  const fechas = SEMANA_FECHAS[semana];
  if (!fechas) return false;
  const ini = new Date(fechas[0] + 'T00:00:00');
  const fin = new Date(fechas[1] + 'T23:59:59');
  return hoy >= ini && hoy <= fin;
}

// ---- Renderizar tarjetas ----
function renderGrupos(grupos) {
  const grid = document.getElementById('sem-grid');
  const vacio = document.getElementById('sem-vacio');
  const loading = document.getElementById('sem-loading');

  loading.style.display = 'none';

  if (!grupos || Object.keys(grupos).length === 0) {
    vacio.style.display = 'flex';
    grid.innerHTML = '';
    return;
  }
  vacio.style.display = 'none';

  grid.innerHTML = Object.entries(grupos).map(([nombre, acts]) => {
    const color = colorColab(nombre);
    const completadas = acts.filter(a => a.estado === 'completada').length;
    const progTotal = acts.length > 0
      ? Math.round(acts.reduce((s, a) => s + a.progreso, 0) / acts.length)
      : 0;

    const items = acts.map(a => {
      const esCompletada = a.estado === 'completada';
      const checkClass = esCompletada ? 'completada' : '';
      const progColor = estadoColor(a.estado);

      const checkBtn = (typeof ES_ADMIN !== 'undefined' && ES_ADMIN)
        ? `<button class="sem-item-check ${checkClass}" data-id="${a.id}" title="${esCompletada ? 'Marcar pendiente' : 'Marcar completada'}">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </button>`
        : '';

      return `
        <div class="sem-item" data-id="${a.id}">
          <span class="sem-item-estado estado-dot-${a.estado}"></span>
          <div class="sem-item-info">
            <div class="sem-item-desc">${a.actividad_id ? `<strong>${a.actividad_id}</strong> · ` : ''}${a.descripcion}</div>
            <div class="sem-item-meta">
              <span class="sem-item-oblig" title="${a.obligacion}">${a.obligacion}</span>
              <span class="sem-item-semnum">Sem ${a.semana_num} / ${a.total_semanas}</span>
            </div>
            <div class="sem-item-prog">
              <div class="sem-item-prog-bg">
                <div class="sem-item-prog-fill" style="width:${a.progreso}%;background:${progColor}"></div>
              </div>
              <span class="sem-item-prog-pct">${a.progreso}%</span>
            </div>
          </div>
          ${checkBtn}
        </div>`;
    }).join('');

    return `
      <div class="sem-card">
        <div class="sem-card-header">
          <span class="sem-card-dot" style="background:${color}"></span>
          <span class="sem-card-nombre" title="${nombre}">${nombre}</span>
          <span class="sem-card-badge">${acts.length} compromiso${acts.length !== 1 ? 's' : ''}</span>
        </div>
        <div class="sem-card-body">${items}</div>
        <div class="sem-card-footer">
          <div class="sem-card-prog-total">
            <div class="sem-card-prog-bg">
              <div class="sem-card-prog-fill" style="width:${progTotal}%;background:${color}"></div>
            </div>
            <span class="sem-card-pct" style="color:${color}">${progTotal}%</span>
          </div>
          <span class="sem-card-completadas">${completadas}/${acts.length} listos</span>
        </div>
      </div>`;
  }).join('');

  // Eventos: click en item → modal editar (solo admin)
  if (typeof ES_ADMIN !== 'undefined' && ES_ADMIN) {
    grid.querySelectorAll('.sem-item').forEach(el => {
      el.addEventListener('click', (e) => {
        if (e.target.closest('.sem-item-check')) return;
        const id = parseInt(el.dataset.id);
        abrirModal(id, grupos);
      });
    });
  }

  // Click en check → toggle completada
  grid.querySelectorAll('.sem-item-check').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = parseInt(btn.dataset.id);
      const esCompletada = btn.classList.contains('completada');
      const nuevoEstado = esCompletada ? 'pendiente' : 'completada';
      const progreso = nuevoEstado === 'completada' ? 100 : null;

      const payload = { estado: nuevoEstado };
      if (progreso !== null) payload.progreso = progreso;

      const res = await fetch(`/api/actividades/${id}/`, {
        method: 'PUT',
        headers: { 'Content-Type':'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify(payload),
      });
      if (res.ok) cargarSemana();
    });
  });
}

// ---- Cargar datos de la semana ----
async function cargarSemana() {
  const semana = semanaActual();
  const colab = colaboradorFiltro();

  document.getElementById('sem-loading').style.display = 'flex';
  document.getElementById('sem-grid').innerHTML = '';
  document.getElementById('sem-vacio').style.display = 'none';

  actualizarFechas(semana);

  const params = new URLSearchParams({ semana });
  if (colab) params.set('colaborador', colab);
  const procEl = document.getElementById('filtro-procedimiento-sem');
  if (procEl && procEl.value) params.set('procedimiento', procEl.value);

  let data;
  try {
    const res = await fetch('/api/actividades/semana/?' + params.toString());
    if (!res.ok) throw new Error('HTTP ' + res.status);
    data = await res.json();
  } catch (err) {
    document.getElementById('sem-loading').style.display = 'none';
    document.getElementById('sem-vacio').style.display = 'flex';
    document.getElementById('sem-vacio').querySelector('p').textContent =
      'Error al cargar: ' + err.message;
    return;
  }

  // Stats
  document.getElementById('sem-stat-colaboradores').textContent = data.total_colaboradores;
  document.getElementById('sem-stat-actividades').textContent = data.total_actividades;

  let completadas = 0, pendientes = 0;
  Object.values(data.grupos).forEach(acts =>
    acts.forEach(a => {
      if (a.estado === 'completada') completadas++;
      else pendientes++;
    })
  );
  document.getElementById('sem-stat-completadas').textContent = completadas;
  document.getElementById('sem-stat-pendientes').textContent = pendientes;

  renderGrupos(data.grupos);
}

// ---- Navegación prev/next ----
document.getElementById('btn-sem-prev').addEventListener('click', () => {
  const sel = document.getElementById('sel-semana');
  const idx = SEMANAS_ORDENADAS.indexOf(sel.value);
  if (idx > 0) {
    sel.value = SEMANAS_ORDENADAS[idx - 1];
    cargarSemana();
  }
});

document.getElementById('btn-sem-next').addEventListener('click', () => {
  const sel = document.getElementById('sel-semana');
  const idx = SEMANAS_ORDENADAS.indexOf(sel.value);
  if (idx < SEMANAS_ORDENADAS.length - 1) {
    sel.value = SEMANAS_ORDENADAS[idx + 1];
    cargarSemana();
  }
});

document.getElementById('btn-hoy').addEventListener('click', () => {
  document.getElementById('sel-semana').value = SEMANA_ACTUAL_DEFAULT;
  cargarSemana();
});

document.getElementById('sel-semana').addEventListener('change', cargarSemana);
document.getElementById('filtro-colaborador-sem').addEventListener('change', cargarSemana);
var procSemEl = document.getElementById('filtro-procedimiento-sem');
if (procSemEl) procSemEl.addEventListener('change', cargarSemana);

// ============================================================
//  MODAL EDITAR
// ============================================================
const overlay = document.getElementById('act-modal-overlay');

let currentSemActId = null;

function abrirModal(id, grupos) {
  // Buscar la actividad en todos los grupos
  let act = null;
  for (const acts of Object.values(grupos)) {
    act = acts.find(a => a.id === id);
    if (act) break;
  }
  if (!act) return;

  currentSemActId = id;
  document.getElementById('modal-id').value = id;
  document.getElementById('modal-desc-texto').textContent = act.descripcion;
  document.getElementById('modal-oblig-texto').textContent = act.obligacion;
  document.getElementById('modal-estado').value = act.estado;
  document.getElementById('modal-progreso').value = act.progreso;
  document.getElementById('modal-progreso-val').textContent = act.progreso;
  document.getElementById('act-modal-titulo').textContent =
    (act.actividad_id ? `[${act.actividad_id}] ` : '') + 'Actualizar actividad';

  const warn = document.getElementById('sem-modal-warning');
  if (warn) warn.style.display = 'none';

  overlay.classList.add('visible');
  cargarEvidenciasSem(id);
}

document.getElementById('modal-progreso').addEventListener('input', e => {
  document.getElementById('modal-progreso-val').textContent = e.target.value;
});

document.getElementById('act-modal-close').addEventListener('click',  () => overlay.classList.remove('visible'));
document.getElementById('btn-modal-cancelar').addEventListener('click', () => overlay.classList.remove('visible'));
overlay.addEventListener('click', e => { if (e.target === overlay) overlay.classList.remove('visible'); });

document.getElementById('act-modal-form').addEventListener('submit', async e => {
  e.preventDefault();
  const id = document.getElementById('modal-id').value;
  const payload = {
    estado:   document.getElementById('modal-estado').value,
    progreso: parseInt(document.getElementById('modal-progreso').value),
  };
  const res = await fetch(`/api/actividades/${id}/`, {
    method: 'PUT',
    headers: { 'Content-Type':'application/json', 'X-CSRFToken': getCookie('csrftoken') },
    body: JSON.stringify(payload),
  });
  if (res.ok) {
    overlay.classList.remove('visible');
    cargarSemana();
  } else {
    const data = await res.json();
    const warn = document.getElementById('sem-modal-warning');
    if (warn) {
      warn.textContent = data.error || 'Error al guardar';
      warn.style.display = 'block';
    }
  }
});

// ============================================================
//  EVIDENCIAS en modal admin
// ============================================================

async function cargarEvidenciasSem(actId) {
  const lista = document.getElementById('sem-evidencias-list');
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
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px;flex-shrink:0">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
          <span>${ev.nombre}</span>
        </a>
        <span class="mic-ev-meta">${ev.creado_por} · ${ev.creado_en}${ev.comentario ? ' — ' + ev.comentario : ''}</span>
        <button type="button" class="mic-ev-del" data-id="${ev.id}" title="Eliminar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:12px;height:12px">
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
        cargarEvidenciasSem(actId);
      });
    });
  } catch {
    lista.innerHTML = '<p class="mic-evidencias-vacio">Error al cargar</p>';
  }
}

// Upload de archivos en modal admin
const semUploadBtn = document.getElementById('sem-btn-upload');
const semUploadInput = document.getElementById('sem-upload-input');

if (semUploadBtn && semUploadInput) {
  semUploadBtn.addEventListener('click', () => semUploadInput.click());

  semUploadInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
      alert('El archivo no puede superar 10MB');
      e.target.value = '';
      return;
    }

    const comentario = document.getElementById('sem-upload-comentario').value.trim();
    const formData = new FormData();
    formData.append('archivo', file);
    formData.append('comentario', comentario);

    semUploadBtn.disabled = true;
    semUploadBtn.textContent = 'Subiendo...';

    try {
      const res = await fetch(`/api/evidencias/${currentSemActId}/subir/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        body: formData,
      });
      if (res.ok) {
        document.getElementById('sem-upload-comentario').value = '';
        cargarEvidenciasSem(currentSemActId);
      } else {
        const d = await res.json();
        alert(d.error || 'Error al subir');
      }
    } catch (err) {
      alert('Error: ' + err.message);
    } finally {
      semUploadBtn.disabled = false;
      semUploadBtn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:13px;height:13px"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg> Subir archivo`;
      e.target.value = '';
    }
  });
}

cargarSemana();
