/* Resumen General — contador de compromisos por semana */

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

function cargarResumen() {
  var semana = semanaSeleccionada();
  if (!semana) return;
  actualizarFechas(semana);
  fetch('/api/actividades/resumen/?semana=' + encodeURIComponent(semana), { credentials: 'same-origin' })
    .then(function(r) { return r.json(); })
    .then(function(d) {
      var el = document.getElementById('res-total');
      if (el) el.textContent = d.total;
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

  actualizarFechas(SEMANA_DEFAULT);
})();
