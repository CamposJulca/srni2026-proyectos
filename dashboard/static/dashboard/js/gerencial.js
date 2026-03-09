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
})

async function cargarGerencial() {
  const res  = await fetch("/api/gerencial/")
  const data = await res.json()

  renderKPIs(data.kpis)
  renderGraficoProc(data.por_procedimiento)
  renderGraficoEstado(data.kpis)
  renderGraficoMasa(data.por_procedimiento)
  renderGraficoMes(data.compromisos_mes)
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
