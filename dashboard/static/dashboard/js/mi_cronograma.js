/* ============================================================
   MI CRONOGRAMA — vista self-service para colaboradores
   ============================================================ */

function getCookie(name) {
  const v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
  return v ? v[2] : null;
}

function formatFecha(s) {
  if (!s) return '';
  const [y, m, d] = s.split('-');
  return `${d}/${m}/${y}`;
}

function estadoLabel(estado) {
  const m = { pendiente:'Pendiente', en_curso:'En Curso', completada:'Completada', bloqueada:'Bloqueada', vencida:'Vencida' };
  return m[estado] || estado;
}

function estadoColor(estado) {
  const m = { pendiente:'#94a3b8', en_curso:'#0891b2', completada:'#00875a', bloqueada:'#CE1126', vencida:'#d97706' };
  return m[estado] || '#94a3b8';
}

let allTasks = [];
let currentActividadId = null;

// ============================================================
//  CARGAR ACTIVIDADES
// ============================================================

async function cargarActividades() {
  const loading = document.getElementById('mic-loading');
  const grid = document.getElementById('mic-grid');
  const vacio = document.getElementById('mic-vacio');

  loading.style.display = 'flex';
  grid.innerHTML = '';
  vacio.style.display = 'none';

  const soloSemana = document.getElementById('chk-solo-semana').checked;
  const params = new URLSearchParams();
  if (soloSemana) params.set('semana', SEMANA_ACTUAL);

  try {
    const res = await fetch('/api/mi-cronograma/?' + params.toString());
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();
    allTasks = data.tasks;
    loading.style.display = 'none';

    if (allTasks.length === 0) {
      vacio.style.display = 'flex';
      actualizarStats([]);
      return;
    }

    actualizarStats(allTasks);
    renderActividades(allTasks);
  } catch (err) {
    loading.style.display = 'none';
    vacio.style.display = 'flex';
    vacio.querySelector('p').textContent = 'Error: ' + err.message;
  }
}

function actualizarStats(tasks) {
  const total = tasks.length;
  const completadas = tasks.filter(t => t.estado === 'completada').length;
  const en_curso = tasks.filter(t => t.estado === 'en_curso').length;
  const pendientes = tasks.filter(t => t.estado === 'pendiente').length;
  const avance = total > 0 ? Math.round(tasks.reduce((s, t) => s + t.progreso, 0) / total) : 0;

  document.getElementById('mic-stat-total').textContent = total;
  document.getElementById('mic-stat-completadas').textContent = completadas;
  document.getElementById('mic-stat-en_curso').textContent = en_curso;
  document.getElementById('mic-stat-pendientes').textContent = pendientes;
  document.getElementById('mic-stat-avance').textContent = avance + '%';
}

function renderActividades(tasks) {
  const grid = document.getElementById('mic-grid');

  // Agrupar por obligacion
  const grupos = {};
  tasks.forEach(t => {
    const key = t.obligacion;
    if (!grupos[key]) grupos[key] = [];
    grupos[key].push(t);
  });

  grid.innerHTML = Object.entries(grupos).map(([oblig, acts]) => {
    const completadas = acts.filter(a => a.estado === 'completada').length;
    const progTotal = acts.length > 0
      ? Math.round(acts.reduce((s, a) => s + a.progreso, 0) / acts.length)
      : 0;

    const items = acts.map(a => {
      const ev = a.estado_visual || a.estado;
      const color = estadoColor(ev);

      return `
        <div class="mic-item" data-id="${a.id}">
          <div class="mic-item-header">
            <span class="mic-item-badge" style="background:${color}">${estadoLabel(ev)}</span>
            <span class="mic-item-id">${a.actividad_id || ''}</span>
            <span class="mic-item-fechas">${formatFecha(a.fecha_inicio)} — ${formatFecha(a.fecha_fin)}</span>
          </div>
          <div class="mic-item-desc">${a.descripcion}</div>
          <div class="mic-item-prog">
            <div class="mic-item-prog-bg">
              <div class="mic-item-prog-fill" style="width:${a.progreso}%;background:${color}"></div>
            </div>
            <span class="mic-item-prog-pct">${a.progreso}%</span>
          </div>
          ${a.evidencia ? `<div class="mic-item-evidencia"><strong>Notas:</strong> ${a.evidencia}</div>` : ''}
        </div>`;
    }).join('');

    return `
      <div class="mic-card">
        <div class="mic-card-header">
          <span class="mic-card-oblig" title="${oblig}">${oblig}</span>
          <span class="mic-card-badge">${completadas}/${acts.length} completadas</span>
        </div>
        <div class="mic-card-body">${items}</div>
        <div class="mic-card-footer">
          <div class="sem-card-prog-total">
            <div class="sem-card-prog-bg">
              <div class="sem-card-prog-fill" style="width:${progTotal}%;background:#003087"></div>
            </div>
            <span class="sem-card-pct" style="color:#003087">${progTotal}%</span>
          </div>
        </div>
      </div>`;
  }).join('');

  // Click en item → modal
  grid.querySelectorAll('.mic-item').forEach(el => {
    el.addEventListener('click', () => {
      const id = parseInt(el.dataset.id);
      abrirModal(id);
    });
  });
}

// ============================================================
//  MODAL — actualizar actividad
// ============================================================

const overlay = document.getElementById('mic-modal-overlay');

function abrirModal(id) {
  const act = allTasks.find(t => t.id === id);
  if (!act) return;

  currentActividadId = id;
  document.getElementById('mic-modal-id').value = id;
  document.getElementById('mic-modal-oblig').textContent = act.obligacion;
  document.getElementById('mic-modal-desc').textContent = act.descripcion;
  document.getElementById('mic-modal-fechas').textContent =
    `${formatFecha(act.fecha_inicio)} — ${formatFecha(act.fecha_fin)}`;
  document.getElementById('mic-modal-estado').value = act.estado;
  document.getElementById('mic-modal-progreso').value = act.progreso;
  document.getElementById('mic-modal-progreso-val').textContent = act.progreso;
  document.getElementById('mic-modal-evidencia').value = act.evidencia || '';
  document.getElementById('mic-modal-titulo').textContent =
    (act.actividad_id ? `[${act.actividad_id}] ` : '') + 'Actualizar avance';
  document.getElementById('mic-modal-warning').style.display = 'none';

  overlay.classList.add('visible');
  cargarEvidencias(id);
}

document.getElementById('mic-modal-progreso').addEventListener('input', e => {
  document.getElementById('mic-modal-progreso-val').textContent = e.target.value;
});

document.getElementById('mic-modal-close').addEventListener('click', () => overlay.classList.remove('visible'));
document.getElementById('mic-modal-cancelar').addEventListener('click', () => overlay.classList.remove('visible'));
overlay.addEventListener('click', e => { if (e.target === overlay) overlay.classList.remove('visible'); });

document.getElementById('mic-modal-form').addEventListener('submit', async e => {
  e.preventDefault();
  const id = document.getElementById('mic-modal-id').value;
  const payload = {
    estado:    document.getElementById('mic-modal-estado').value,
    progreso:  parseInt(document.getElementById('mic-modal-progreso').value),
    evidencia: document.getElementById('mic-modal-evidencia').value,
  };

  try {
    const res = await fetch(`/api/mi-cronograma/${id}/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (res.ok) {
      overlay.classList.remove('visible');
      cargarActividades();
    } else {
      document.getElementById('mic-modal-warning').style.display = 'block';
      document.getElementById('mic-modal-warning').textContent = data.error || 'Error al guardar';
    }
  } catch (err) {
    alert('Error de conexion: ' + err.message);
  }
});

// ============================================================
//  EVIDENCIAS — upload de archivos
// ============================================================

async function cargarEvidencias(actividadId) {
  const lista = document.getElementById('mic-evidencias-list');
  lista.innerHTML = '<p class="mic-evidencias-vacio">Cargando...</p>';

  try {
    const res = await fetch(`/api/evidencias/${actividadId}/`);
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
        <span class="mic-ev-meta">${ev.creado_en}${ev.comentario ? ' — ' + ev.comentario : ''}</span>
        <button type="button" class="mic-ev-del" data-id="${ev.id}" title="Eliminar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:12px;height:12px">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
    `).join('');

    // Eliminar evidencia
    lista.querySelectorAll('.mic-ev-del').forEach(btn => {
      btn.addEventListener('click', async () => {
        if (!confirm('Eliminar esta evidencia?')) return;
        const evId = btn.dataset.id;
        const r = await fetch(`/api/evidencias/eliminar/${evId}/`, {
          method: 'POST',
          headers: { 'X-CSRFToken': getCookie('csrftoken') },
        });
        if (r.ok) cargarEvidencias(actividadId);
      });
    });
  } catch {
    lista.innerHTML = '<p class="mic-evidencias-vacio">Error al cargar evidencias</p>';
  }
}

// Boton subir archivo
document.getElementById('mic-btn-upload').addEventListener('click', () => {
  document.getElementById('mic-upload-input').click();
});

document.getElementById('mic-upload-input').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  if (file.size > 10 * 1024 * 1024) {
    alert('El archivo no puede superar 10MB');
    e.target.value = '';
    return;
  }

  const comentario = document.getElementById('mic-upload-comentario').value.trim();
  const formData = new FormData();
  formData.append('archivo', file);
  formData.append('comentario', comentario);

  const btn = document.getElementById('mic-btn-upload');
  btn.disabled = true;
  btn.textContent = 'Subiendo...';

  try {
    const res = await fetch(`/api/evidencias/${currentActividadId}/subir/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken') },
      body: formData,
    });
    const data = await res.json();
    if (res.ok) {
      document.getElementById('mic-upload-comentario').value = '';
      cargarEvidencias(currentActividadId);
    } else {
      alert(data.error || 'Error al subir');
    }
  } catch (err) {
    alert('Error: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="17 8 12 3 7 8"/>
        <line x1="12" y1="3" x2="12" y2="15"/>
      </svg>
      Subir archivo (max 10MB)`;
    e.target.value = '';
  }
});

// ============================================================
//  REPORTE SEMANAL
// ============================================================

async function cargarReporte() {
  const semana = SEMANA_ACTUAL;
  document.getElementById('mic-reporte-semana').textContent = semana;

  try {
    const res = await fetch(`/api/reporte-semanal/?semana=${encodeURIComponent(semana)}`);
    const data = await res.json();

    if (data.reportes && data.reportes.length > 0) {
      const r = data.reportes[0];
      document.getElementById('mic-reporte-que-hizo').value = r.que_hizo;
      document.getElementById('mic-reporte-impedimentos').value = r.impedimentos || '';
      document.getElementById('mic-reporte-status').textContent = `Guardado: ${r.actualizado_en}`;
      document.getElementById('mic-reporte-status').className = 'mic-reporte-status mic-reporte-saved';
    } else {
      document.getElementById('mic-reporte-status').textContent = 'Sin reporte esta semana';
      document.getElementById('mic-reporte-status').className = 'mic-reporte-status mic-reporte-pending';
    }
  } catch {
    // silently fail
  }
}

document.getElementById('btn-guardar-reporte').addEventListener('click', async () => {
  const que_hizo = document.getElementById('mic-reporte-que-hizo').value.trim();
  if (!que_hizo) {
    alert('Escribe que hiciste esta semana');
    return;
  }

  const payload = {
    semana: SEMANA_ACTUAL,
    que_hizo,
    impedimentos: document.getElementById('mic-reporte-impedimentos').value.trim(),
  };

  const btn = document.getElementById('btn-guardar-reporte');
  btn.disabled = true;
  btn.textContent = 'Guardando...';

  try {
    const res = await fetch('/api/reporte-semanal/guardar/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (res.ok) {
      const statusEl = document.getElementById('mic-reporte-status');
      statusEl.textContent = data.created ? 'Reporte guardado' : 'Reporte actualizado';
      statusEl.className = 'mic-reporte-status mic-reporte-saved';
    } else {
      alert(data.error || 'Error al guardar');
    }
  } catch (err) {
    alert('Error: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Guardar reporte';
  }
});

// ---- Toggle semana actual ----
document.getElementById('chk-solo-semana').addEventListener('change', cargarActividades);

// ---- Init ----
cargarActividades();
cargarReporte();
