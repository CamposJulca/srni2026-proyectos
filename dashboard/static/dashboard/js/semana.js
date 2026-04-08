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
          <button class="sem-item-check ${checkClass}" data-id="${a.id}" title="${esCompletada ? 'Marcar pendiente' : 'Marcar completada'}">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </button>
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

  // Eventos: click en item → modal editar
  grid.querySelectorAll('.sem-item').forEach(el => {
    el.addEventListener('click', (e) => {
      if (e.target.closest('.sem-item-check')) return;
      const id = parseInt(el.dataset.id);
      abrirModal(id, grupos);
    });
  });

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

// ============================================================
//  MODAL EDITAR
// ============================================================
const overlay = document.getElementById('act-modal-overlay');

function abrirModal(id, grupos) {
  // Buscar la actividad en todos los grupos
  let act = null;
  for (const acts of Object.values(grupos)) {
    act = acts.find(a => a.id === id);
    if (act) break;
  }
  if (!act) return;

  document.getElementById('modal-id').value = id;
  document.getElementById('modal-desc-texto').textContent = act.descripcion;
  document.getElementById('modal-oblig-texto').textContent = act.obligacion;
  document.getElementById('modal-estado').value = act.estado;
  document.getElementById('modal-progreso').value = act.progreso;
  document.getElementById('modal-progreso-val').textContent = act.progreso;
  document.getElementById('act-modal-titulo').textContent =
    (act.actividad_id ? `[${act.actividad_id}] ` : '') + 'Actualizar actividad';

  overlay.classList.add('visible');
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
  }
});

cargarSemana();
