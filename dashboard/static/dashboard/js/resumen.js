/* Resumen General — dashboard ejecutivo por semana */

function semanaSeleccionada() {
  var sel = document.getElementById('sel-semana');
  return sel ? sel.value : '';
}

function actualizarFechas(semana) {
  var f = SEMANA_FECHAS[semana];
  if (!f) return;
  var meses = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'];
  function fmt(s) { var p = s.split('-'); return parseInt(p[2]) + ' ' + meses[parseInt(p[1])-1]; }
  var el = document.getElementById('sem-fechas');
  if (el) {
    el.textContent = fmt(f[0]) + ' \u2013 ' + fmt(f[1]) + ' \u00b7 ' + f[0].slice(0,4);
    el.style.color = semana === SEMANA_ACTUAL_DEFAULT ? 'var(--primario)' : '';
  }
}

function renderKPIs(d) {
  document.getElementById('kpi-total').textContent = d.total;
  document.getElementById('kpi-avance').textContent = d.avance;
  document.getElementById('kpi-completadas').textContent = d.completadas;
  document.getElementById('kpi-en-curso').textContent = d.en_curso;
  document.getElementById('kpi-pendientes').textContent = d.pendientes;
  document.getElementById('kpi-bloqueadas').textContent = d.bloqueadas;

  var fill = document.getElementById('kpi-avance-fill');
  if (fill) fill.style.width = d.avance + '%';
}

function renderDistribucion(d) {
  var bar = document.getElementById('res-dist-bar');
  if (!bar || !d.total) { if (bar) bar.innerHTML = ''; return; }

  var pcts = {
    completada: (d.completadas / d.total * 100).toFixed(1),
    encurso:    (d.en_curso / d.total * 100).toFixed(1),
    pendiente:  (d.pendientes / d.total * 100).toFixed(1),
    bloqueada:  (d.bloqueadas / d.total * 100).toFixed(1),
  };

  bar.innerHTML =
    '<div class="res-dist-seg res-dist-completada" style="width:' + pcts.completada + '%" title="Completadas: ' + d.completadas + ' (' + pcts.completada + '%)"></div>' +
    '<div class="res-dist-seg res-dist-encurso" style="width:' + pcts.encurso + '%" title="En curso: ' + d.en_curso + ' (' + pcts.encurso + '%)"></div>' +
    '<div class="res-dist-seg res-dist-pendiente" style="width:' + pcts.pendiente + '%" title="Pendientes: ' + d.pendientes + ' (' + pcts.pendiente + '%)"></div>' +
    '<div class="res-dist-seg res-dist-bloqueada" style="width:' + pcts.bloqueada + '%" title="Bloqueadas: ' + d.bloqueadas + ' (' + pcts.bloqueada + '%)"></div>';
}

function renderTabla(colaboradores) {
  var tbody = document.getElementById('res-tabla-body');
  if (!tbody) return;

  if (!colaboradores || !colaboradores.length) {
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:30px;color:var(--texto-s)">Sin actividades esta semana</td></tr>';
    return;
  }

  tbody.innerHTML = colaboradores.map(function(c) {
    var clase, label;
    if (c.avance >= 70) { clase = 'res-semaforo-verde'; label = 'Al d\u00eda'; }
    else if (c.avance >= 40) { clase = 'res-semaforo-amarillo'; label = 'En riesgo'; }
    else { clase = 'res-semaforo-rojo'; label = 'Cr\u00edtico'; }

    var fillClase;
    if (c.avance >= 70) fillClase = 'res-avance-alto';
    else if (c.avance >= 40) fillClase = 'res-avance-medio';
    else fillClase = 'res-avance-bajo';

    return '<tr>' +
      '<td><div class="res-td-nombre">' + c.nombre + '</div></td>' +
      '<td class="res-td-avance"><div class="res-avance-wrap">' +
        '<span class="res-avance-pct ' + fillClase + '">' + c.avance + '%</span>' +
        '<div class="res-avance-bar-bg"><div class="res-avance-bar-fill ' + fillClase + '" style="width:' + c.avance + '%"></div></div>' +
      '</div></td>' +
      '<td class="res-td-num">' + c.total + '</td>' +
      '<td class="res-td-num">' + c.completadas + '</td>' +
      '<td class="res-td-num">' + c.en_curso + '</td>' +
      '<td class="res-td-num">' + c.pendientes + '</td>' +
      '<td class="res-td-num">' + c.bloqueadas + '</td>' +
      '<td><span class="res-semaforo ' + clase + '">' + label + '</span></td>' +
    '</tr>';
  }).join('');
}

function cargarResumen() {
  var semana = semanaSeleccionada();
  if (!semana) return;
  actualizarFechas(semana);

  var params = 'semana=' + encodeURIComponent(semana);
  var procEl = document.getElementById('filtro-procedimiento-res');
  if (procEl && procEl.value) params += '&procedimiento=' + encodeURIComponent(procEl.value);

  fetch('/api/actividades/resumen/?' + params, { credentials: 'same-origin' })
    .then(function(r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    })
    .then(function(d) {
      renderKPIs(d);
      renderDistribucion(d);
      renderTabla(d.colaboradores);
    })
    .catch(function(err) {
      console.error('Error cargando resumen:', err);
    });
}

(function() {
  var sel     = document.getElementById('sel-semana');
  var btnPrev = document.getElementById('btn-sem-prev');
  var btnNext = document.getElementById('btn-sem-next');
  var btnHoy  = document.getElementById('btn-hoy');

  if (btnPrev) btnPrev.addEventListener('click', function() {
    if (sel && sel.selectedIndex > 0) { sel.selectedIndex--; cargarResumen(); }
  });
  if (btnNext) btnNext.addEventListener('click', function() {
    if (sel && sel.selectedIndex < sel.options.length - 1) { sel.selectedIndex++; cargarResumen(); }
  });
  if (sel)    sel.addEventListener('change', cargarResumen);
  if (btnHoy) btnHoy.addEventListener('click', function() {
    if (!sel) return;
    for (var i = 0; i < sel.options.length; i++) {
      if (sel.options[i].value === SEMANA_ACTUAL_DEFAULT) { sel.selectedIndex = i; break; }
    }
    cargarResumen();
  });

  var procEl = document.getElementById('filtro-procedimiento-res');
  if (procEl) procEl.addEventListener('change', cargarResumen);

  // Carga inicial con datos del servidor (sin fetch)
  actualizarFechas(SEMANA_DEFAULT);
  if (typeof DATOS_INICIALES !== 'undefined' && DATOS_INICIALES) {
    renderKPIs(DATOS_INICIALES);
    renderDistribucion(DATOS_INICIALES);
    renderTabla(DATOS_INICIALES.colaboradores);
  } else {
    cargarResumen();
  }
})();
