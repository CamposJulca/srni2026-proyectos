/* =====================================================
   GERENCIAL — Dashboard Ejecutivo
===================================================== */

const COLORES_PROC = [
  "#1d4ed8", "#065f46", "#92400e", "#5b21b6",
  "#9d174d", "#9a3412", "#166534", "#0e7490",
]

let chartProc, chartEstado, chartMasa, chartMes

document.addEventListener("DOMContentLoaded", () => {
  // Fecha actual en encabezado
  const hoy = new Date()
  document.getElementById("gerFecha").textContent =
    hoy.toLocaleDateString("es-CO", { weekday: "long", year: "numeric", month: "long", day: "numeric" })

  cargarGerencial()
  bindSubtabs()
})

/* =====================================================
   Sub-pestañas Ejecutivo / Contratación
===================================================== */
let contratacionCargada = false

function bindSubtabs() {
  document.querySelectorAll(".ger-subtab").forEach(btn => {
    btn.addEventListener("click", () => activarTab(btn.dataset.tab))
  })
  const btnSync = document.getElementById("btnSincronizar")
  if (btnSync) btnSync.addEventListener("click", sincronizarContratos)
}

function activarTab(tab) {
  document.querySelectorAll(".ger-subtab").forEach(el =>
    el.classList.toggle("activo", el.dataset.tab === tab))
  document.getElementById("panelEjecutivo").classList.toggle("activo", tab === "ejecutivo")
  document.getElementById("panelContratacion").classList.toggle("activo", tab === "contratacion")

  if (tab === "contratacion" && !contratacionCargada) {
    cargarContratacion()
  }
}

async function cargarGerencial() {
  const res  = await fetch((window.APP_BASE || '') + "/api/gerencial/")
  const data = await res.json()

  renderKPIs(data.kpis)
  renderGraficoProc(data.por_procedimiento)
  renderGraficoEstado(data.kpis)
  renderGraficoMasa(data.por_procedimiento)
  renderGraficoMes(data.compromisos_mes)
  renderProyectos(data.proyectos || [])
}

/* =====================================================
   KPIs
===================================================== */
function renderKPIs(k) {
  document.getElementById("gerTotal").textContent = k.total
  document.getElementById("gerVigentes").textContent = k.vigentes
  document.getElementById("gerVencidos").textContent = k.vencidos
  document.getElementById("gerMasa").textContent =
    "$ " + Math.round(k.masa).toLocaleString("es-CO")
}

/* =====================================================
   Contratistas por procedimiento (barras horizontales)
===================================================== */
function renderGraficoProc(datos) {
  const labels  = datos.map(d => d.procedimiento)
  const valores = datos.map(d => d.personas)

  if (chartProc) chartProc.destroy()
  chartProc = new Chart(document.getElementById("gerGraficoProc"), {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Contratistas",
        data: valores,
        backgroundColor: COLORES_PROC,
        borderRadius: 6,
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { beginAtZero: true, ticks: { stepSize: 1 } }
      }
    }
  })
}

/* =====================================================
   Estado de contratos (donut)
===================================================== */
function renderGraficoEstado(k) {
  if (chartEstado) chartEstado.destroy()
  chartEstado = new Chart(document.getElementById("gerGraficoEstado"), {
    type: "doughnut",
    data: {
      labels: ["Vigentes", "Vencidos", "Sin fecha"],
      datasets: [{
        data: [k.vigentes, k.vencidos, k.sin_fecha],
        backgroundColor: ["#10b981", "#CE1126", "#94a3b8"],
        borderWidth: 2,
        borderColor: "#fff",
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom", labels: { font: { size: 12 } } }
      },
      cutout: "60%",
    }
  })
}

/* =====================================================
   Masa salarial por procedimiento (barras horizontales)
===================================================== */
function renderGraficoMasa(datos) {
  const labels  = datos.map(d => d.procedimiento)
  const valores = datos.map(d => Math.round(d.masa))

  if (chartMasa) chartMasa.destroy()
  chartMasa = new Chart(document.getElementById("gerGraficoMasa"), {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "$ / mes",
        data: valores,
        backgroundColor: "#FCD116",
        borderColor: "#b8960d",
        borderWidth: 1,
        borderRadius: 6,
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: {
          beginAtZero: true,
          ticks: {
            callback: v => "$ " + (v / 1_000_000).toFixed(1) + "M"
          }
        }
      }
    }
  })
}

/* =====================================================
   Compromisos por mes (línea)
===================================================== */
function renderGraficoMes(datos) {
  const ordenMeses = [
    "Enero","Febrero","Marzo","Abril","Mayo","Junio",
    "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
  ]
  datos.sort((a, b) => ordenMeses.indexOf(a.mes) - ordenMeses.indexOf(b.mes))

  if (chartMes) chartMes.destroy()
  chartMes = new Chart(document.getElementById("gerGraficoMes"), {
    type: "line",
    data: {
      labels: datos.map(d => d.mes),
      datasets: [{
        label: "Compromisos",
        data: datos.map(d => d.total),
        borderColor: "#CE1126",
        backgroundColor: "rgba(206,17,38,0.08)",
        fill: true,
        tension: 0.3,
        pointRadius: 4,
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
    }
  })
}

function renderProyectos(proyectos) {
  const tbody = document.getElementById("gerProyectos")
  if (!tbody) return
  tbody.innerHTML = proyectos.map(p => `
    <tr>
      <td><a href="${window.APP_BASE || ''}/proyectos/${p.id}/">${p.nombre}</a></td>
      <td>${p.estado}</td>
      <td>${p.prioridad}</td>
      <td>${p.responsable || "Sin responsable"}</td>
      <td>${p.avance_promedio}%</td>
      <td>${p.actividades_vencidas}</td>
      <td>${p.actividades_bloqueadas}</td>
      <td>${p.personas_asignadas}</td>
      <td><span class="proyecto-badge semaforo-mini-${p.semaforo}">${p.semaforo}</span></td>
    </tr>
  `).join("") || `<tr><td colspan="9">Sin proyectos registrados</td></tr>`
}

/* =====================================================
   CONTRATACIÓN
===================================================== */
let chartEquipo, chartEstadoContrato

const money = v => "$ " + Math.round(v || 0).toLocaleString("es-CO")
const moneyM = v => "$ " + ((v || 0) / 1_000_000).toFixed(1) + "M"

async function cargarContratacion() {
  const res = await fetch((window.APP_BASE || '') + "/api/gerencial/contratos/")
  if (!res.ok) return
  const data = await res.json()
  contratacionCargada = true

  const per = data.periodo || {}
  document.getElementById("ctrPeriodo").textContent =
    `Periodo actual: ${per.mes_nombre} ${per.anio} · último mes de pagos cargado: ${per.mes_pagos_nombre}`
  const mesPagosEl = document.getElementById("ctrMesPagos")
  if (mesPagosEl) mesPagosEl.textContent = per.mes_pagos_nombre || ""

  renderKPIsContrato(data.kpis)
  renderGraficoEquipo(data.por_equipo || [])
  renderGraficoEstadoContrato(data.kpis)
  renderCruce(data.cruce_fisico_financiero || [])
  renderPorVencer(data.por_vencer || [])
  renderPagosPendientes(data.semaforo_pagos || [])
  renderSSAtrasada(data.semaforo_ss || [])
}

function renderKPIsContrato(k) {
  k = k || {}
  document.getElementById("ctrContratos").textContent = k.total_contratos || 0
  document.getElementById("ctrValorTotal").textContent = moneyM(k.valor_total)
  document.getElementById("ctrCancelado").textContent = moneyM(k.valor_cancelado)
  document.getElementById("ctrSaldo").textContent = moneyM(k.saldo)
  document.getElementById("ctrEjec").textContent = (k.ejec_financiera_global || 0) + "%"
}

function renderGraficoEquipo(datos) {
  const labels = datos.map(d => d.equipo)
  if (chartEquipo) chartEquipo.destroy()
  chartEquipo = new Chart(document.getElementById("ctrGraficoEquipo"), {
    type: "bar",
    data: {
      labels,
      datasets: [
        { label: "Contratado", data: datos.map(d => d.valor_total), backgroundColor: "#1d4ed8", borderRadius: 5 },
        { label: "Pagado", data: datos.map(d => d.valor_cancelado), backgroundColor: "#10b981", borderRadius: 5 },
      ]
    },
    options: {
      indexAxis: "y",
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: "bottom" } },
      scales: { x: { beginAtZero: true, ticks: { callback: v => "$" + (v / 1_000_000).toFixed(0) + "M" } } }
    }
  })
}

function renderGraficoEstadoContrato(k) {
  k = k || {}
  if (chartEstadoContrato) chartEstadoContrato.destroy()
  chartEstadoContrato = new Chart(document.getElementById("ctrGraficoEstado"), {
    type: "doughnut",
    data: {
      labels: ["En ejecución", "Cesión", "Terminados"],
      datasets: [{
        data: [k.en_ejecucion || 0, k.cesion || 0, k.terminados || 0],
        backgroundColor: ["#10b981", "#FCD116", "#94a3b8"],
        borderWidth: 2, borderColor: "#fff",
      }]
    },
    options: { responsive: true, plugins: { legend: { position: "bottom" } }, cutout: "60%" }
  })
}

function renderCruce(filas) {
  const tbody = document.getElementById("ctrCruce")
  const etiqueta = { alineado: "Alineado", alerta: "Alerta", desalineado: "Desalineado", sin_datos: "Sin datos" }
  tbody.innerHTML = filas.map(f => `
    <tr>
      <td>${f.numero_contrato}</td>
      <td>${f.contratista}</td>
      <td>${f.equipo || ""}</td>
      <td>${f.avance_fisico == null ? "—" : f.avance_fisico + "%"}</td>
      <td>${f.avance_financiero}%</td>
      <td>${f.brecha == null ? "—" : f.brecha + " pts"}</td>
      <td><span class="cruce-badge cruce-${f.estado_cruce}">${etiqueta[f.estado_cruce] || f.estado_cruce}</span></td>
    </tr>
  `).join("") || `<tr><td colspan="7">Sin datos</td></tr>`
}

function renderPorVencer(filas) {
  const tbody = document.getElementById("ctrPorVencer")
  tbody.innerHTML = filas.map(f => `
    <tr>
      <td>${f.numero_contrato}</td>
      <td>${f.contratista}</td>
      <td><span class="cruce-badge ${f.dias_restantes <= 7 ? "cruce-desalineado" : "cruce-alerta"}">${f.dias_restantes} d</span></td>
      <td>${money(f.saldo)}</td>
    </tr>
  `).join("") || `<tr><td colspan="4">Sin contratos próximos a vencer</td></tr>`
}

function renderPagosPendientes(filas) {
  const tbody = document.getElementById("ctrPagosPend")
  tbody.innerHTML = filas.map(f => `
    <tr>
      <td>${f.numero_contrato}</td>
      <td>${f.contratista}</td>
      <td>${f.equipo || ""}</td>
      <td>${money(f.valor)}</td>
    </tr>
  `).join("") || `<tr><td colspan="4">Sin pagos pendientes</td></tr>`
}

function renderSSAtrasada(filas) {
  const tbody = document.getElementById("ctrSSAtrasada")
  tbody.innerHTML = filas.map(f => `
    <tr>
      <td>${f.numero_contrato}</td>
      <td>${f.contratista}</td>
      <td>${f.planillas} / ${f.meses_pagados}</td>
      <td><span class="cruce-badge cruce-desalineado">${f.faltantes}</span></td>
    </tr>
  `).join("") || `<tr><td colspan="4">Seguridad social al día ✓</td></tr>`
}

async function sincronizarContratos() {
  const btn = document.getElementById("btnSincronizar")
  const estado = document.getElementById("ctrSyncEstado")
  btn.disabled = true
  estado.textContent = "Sincronizando…"
  estado.className = "ger-sync-estado sync-cargando"
  try {
    const res = await fetch((window.APP_BASE || '') + "/api/gerencial/contratos/sincronizar/", {
      method: "POST",
      headers: { "X-CSRFToken": getCookie("csrftoken") },
    })
    const d = await res.json()
    if (!res.ok) {
      estado.textContent = d.error || "Error al sincronizar"
      estado.className = "ger-sync-estado sync-error"
    } else {
      estado.textContent =
        `✓ ${d.creados} nuevos · ${d.actualizados} actualizados · ${d.errores.length} errores`
      estado.className = "ger-sync-estado sync-ok"
      contratacionCargada = false
      cargarContratacion()
    }
  } catch (e) {
    estado.textContent = "Error de red"
    estado.className = "ger-sync-estado sync-error"
  } finally {
    btn.disabled = false
  }
}

function getCookie(name) {
  const m = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)")
  return m ? m.pop() : ""
}
