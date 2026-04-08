/* =====================================================
   TABS: ERD / SQL
===================================================== */
document.querySelectorAll(".sql-tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const panelId = "panel-" + btn.dataset.panel

    document.querySelectorAll(".sql-tab-btn").forEach(b => b.classList.remove("activo"))
    document.querySelectorAll(".sql-tab-panel").forEach(p => p.classList.remove("activo"))

    btn.classList.add("activo")
    document.getElementById(panelId).classList.add("activo")

    if (btn.dataset.panel === "erd") dibujarConexionesERD()
  })
})

// Dibujar ERD al cargar (tab activo por defecto)
window.addEventListener("load", dibujarConexionesERD)
window.addEventListener("resize", dibujarConexionesERD)


/* =====================================================
   DIAGRAMA ERD — SVG connections
===================================================== */
function dibujarConexionesERD() {
  const svg = document.getElementById("erd-svg")
  if (!svg) return

  // Solo dibujar si el panel está visible
  const panel = document.getElementById("panel-erd")
  if (!panel || !panel.classList.contains("activo")) return

  const wrap = document.getElementById("erd-wrap")
  const wrapRect = wrap.getBoundingClientRect()

  // Helper: punto de conexión en un lado del elemento
  function punto(id, lado) {
    const el = document.getElementById(id)
    if (!el) return [0, 0]
    const r = el.getBoundingClientRect()
    const x = r.left - wrapRect.left
    const y = r.top - wrapRect.top
    switch (lado) {
      case "L": return [x,             y + r.height / 2]
      case "R": return [x + r.width,   y + r.height / 2]
      case "T": return [x + r.width / 2, y]
      case "B": return [x + r.width / 2, y + r.height]
    }
  }

  // Definiciones SVG (arrowheads)
  const DEFS = `<defs>
    <marker id="arr-fk" markerWidth="8" markerHeight="8" refX="7" refY="3.5" orient="auto">
      <path d="M0,0 L0,7 L8,3.5 z" fill="#7c3aed"/>
    </marker>
    <marker id="arr-opt" markerWidth="8" markerHeight="8" refX="7" refY="3.5" orient="auto">
      <path d="M0,0 L0,7 L8,3.5 z" fill="#22c55e"/>
    </marker>
  </defs>`

  // Conexiones: [fromId, fromSide, toId, toSide, opcional]
  // Cada FK apunta hacia la tabla referenciada
  const conexiones = [
    ["eT-colaborador", "L",  "eT-procedimiento", "R", false],
    ["eT-obligacion",  "L",  "eT-colaborador",   "R", false],
    ["eT-actividad",   "L",  "eT-obligacion",    "R", false],
    ["eT-actividad",   "B",  "eT-proyecto",      "T", true ],
    ["eT-asignacion",  "T",  "eT-colaborador",   "B", false],
    ["eT-asignacion",  "R",  "eT-modulo",        "L", false],
    ["eT-asignacion",  "L",  "eT-rol",           "R", false],
    ["eT-modulo",      "R",  "eT-proyecto",      "L", false],
  ]

  let paths = DEFS

  conexiones.forEach(([fromId, fromSide, toId, toSide, opt]) => {
    const [x1, y1] = punto(fromId, fromSide)
    const [x2, y2] = punto(toId,   toSide)

    const color = opt ? "#22c55e" : "#7c3aed"
    const dash  = opt ? 'stroke-dasharray="6 4"' : ""
    const mark  = opt ? "arr-opt" : "arr-fk"
    const BEND  = 55

    // Control points para la curva cúbica según la dirección
    let cx1, cy1, cx2, cy2

    if (fromSide === "L" && toSide === "R") {
      // from goes left, to is on the right side → ambas hacia el centro
      cx1 = x1 - BEND; cy1 = y1
      cx2 = x2 + BEND; cy2 = y2
    } else if (fromSide === "R" && toSide === "L") {
      cx1 = x1 + BEND; cy1 = y1
      cx2 = x2 - BEND; cy2 = y2
    } else if (fromSide === "T" && toSide === "B") {
      cx1 = x1; cy1 = y1 - BEND
      cx2 = x2; cy2 = y2 + BEND
    } else if (fromSide === "B" && toSide === "T") {
      cx1 = x1; cy1 = y1 + BEND
      cx2 = x2; cy2 = y2 - BEND
    } else {
      cx1 = x1; cy1 = y1
      cx2 = x2; cy2 = y2
    }

    paths += `<path
      d="M${x1},${y1} C${cx1},${cy1} ${cx2},${cy2} ${x2},${y2}"
      fill="none" stroke="${color}" stroke-width="1.8"
      ${dash} marker-end="url(#${mark})"
      opacity="0.75"
    />`
  })

  svg.innerHTML = paths
}


/* =====================================================
   SIDEBAR: clic en tabla → SELECT con sus columnas
===================================================== */
const QUERIES_TABLA = {
  dashboard_procedimiento:
`SELECT *
FROM dashboard_procedimiento
ORDER BY nombre;`,

  dashboard_proyecto:
`SELECT *
FROM dashboard_proyecto
ORDER BY nombre;`,

  dashboard_modulo:
`SELECT m.id, m.nombre, m.referente, p.nombre AS proyecto
FROM dashboard_modulo m
JOIN dashboard_proyecto p ON p.id = m.proyecto_id
ORDER BY p.nombre, m.nombre
LIMIT 20;`,

  dashboard_colaborador:
`SELECT id, nombre, cedula, fecha_inicio, fecha_fin, honorarios
FROM dashboard_colaborador
ORDER BY nombre
LIMIT 20;`,

  dashboard_rol:
`SELECT *
FROM dashboard_rol
ORDER BY nombre;`,

  dashboard_asignacion:
`SELECT a.id, c.nombre AS colaborador, r.nombre AS rol, m.nombre AS modulo
FROM dashboard_asignacion a
JOIN dashboard_colaborador c ON c.id = a.colaborador_id
JOIN dashboard_rol r         ON r.id = a.rol_id
JOIN dashboard_modulo m      ON m.id = a.modulo_id
ORDER BY c.nombre
LIMIT 20;`,

  dashboard_obligacion:
`SELECT o.id, c.nombre AS colaborador, o.descripcion
FROM dashboard_obligacion o
JOIN dashboard_colaborador c ON c.id = o.colaborador_id
ORDER BY c.nombre
LIMIT 20;`,

  dashboard_actividad:
`SELECT a.id, a.actividad_id, a.descripcion, a.estado, a.progreso,
       a.fecha_inicio, a.fecha_fin
FROM dashboard_actividad a
JOIN dashboard_obligacion o  ON o.id = a.obligacion_id
JOIN dashboard_colaborador c ON c.id = o.colaborador_id
ORDER BY c.nombre, a.orden
LIMIT 20;`,
}

document.querySelectorAll(".tabla-ref").forEach(ref => {
  ref.addEventListener("click", () => {
    const tabla = ref.dataset.tabla
    const q = QUERIES_TABLA[tabla] || `SELECT *\nFROM ${tabla}\nLIMIT 20;`
    // Cambiar al tab SQL si no está activo
    activarTabSQL()
    cargarQuery(q)
  })
})


/* =====================================================
   CONSULTAS SUGERIDAS
===================================================== */
document.querySelectorAll(".sugerida-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    activarTabSQL()
    cargarQuery(btn.dataset.query)
    setTimeout(ejecutarQuery, 50)
  })
})

function activarTabSQL() {
  document.querySelectorAll(".sql-tab-btn").forEach(b => b.classList.remove("activo"))
  document.querySelectorAll(".sql-tab-panel").forEach(p => p.classList.remove("activo"))
  document.querySelector('[data-panel="sql"]').classList.add("activo")
  document.getElementById("panel-sql").classList.add("activo")
}

function cargarQuery(sql) {
  document.getElementById("sqlInput").value = sql
  ocultarTodo()
  mostrar("sqlVacio")
}


/* =====================================================
   EJECUTAR CONSULTA
===================================================== */
let ultimoResultado = null

document.getElementById("btnEjecutar").addEventListener("click", ejecutarQuery)

document.getElementById("sqlInput").addEventListener("keydown", e => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault()
    ejecutarQuery()
  }
})

function ejecutarQuery() {
  const query = document.getElementById("sqlInput").value.trim()
  if (!query) return

  const btn = document.getElementById("btnEjecutar")
  btn.classList.add("cargando")
  btn.disabled = true
  btn.innerHTML = `<svg viewBox="0 0 24 24" fill="currentColor" style="animation:spin 0.8s linear infinite;width:13px;height:13px"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg> Ejecutando...`

  ocultarTodo()
  ultimoResultado = null

  fetch("/api/sql/", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-CSRFToken": getCookie("csrftoken") },
    body: JSON.stringify({ query })
  })
  .then(r => r.json())
  .then(data => {
    if (data.error) {
      document.getElementById("sqlErrorMsg").textContent = data.error
      mostrar("sqlError")
    } else {
      ultimoResultado = data
      renderTabla(data.columnas, data.filas, data.total)
      mostrar("sqlResultados")
    }
  })
  .catch(() => {
    document.getElementById("sqlErrorMsg").textContent = "Error de conexión con el servidor."
    mostrar("sqlError")
  })
  .finally(() => {
    btn.classList.remove("cargando")
    btn.disabled = false
    btn.innerHTML = `<svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg> Ejecutar`
  })
}


/* =====================================================
   RENDERIZAR TABLA
===================================================== */
function renderTabla(columnas, filas, total) {
  document.getElementById("sqlConteo").textContent = `${total} fila${total !== 1 ? "s" : ""}`

  document.getElementById("sqlThead").innerHTML =
    "<tr>" + columnas.map(c => `<th title="${c}">${c}</th>`).join("") + "</tr>"

  document.getElementById("sqlTbody").innerHTML = filas.map(fila =>
    "<tr>" + fila.map(celda => {
      if (celda === null || celda === undefined) return `<td class="null">NULL</td>`
      const texto = String(celda)
      const corto = texto.length > 120 ? texto.slice(0, 120) + "…" : texto
      return `<td title="${texto.replace(/"/g, "&quot;")}">${corto}</td>`
    }).join("") + "</tr>"
  ).join("")
}


/* =====================================================
   EXPORTAR CSV
===================================================== */
document.getElementById("btnExportar").addEventListener("click", () => {
  if (!ultimoResultado) return

  const { columnas, filas } = ultimoResultado
  const escapar = v => {
    if (v === null || v === undefined) return ""
    const s = String(v).replace(/"/g, '""')
    return s.includes(",") || s.includes("\n") || s.includes('"') ? `"${s}"` : s
  }

  const lineas = [
    columnas.map(escapar).join(","),
    ...filas.map(f => f.map(escapar).join(","))
  ]

  const blob = new Blob(["\uFEFF" + lineas.join("\n")], { type: "text/csv;charset=utf-8;" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = `consulta_srni_${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
})


/* =====================================================
   LIMPIAR
===================================================== */
document.getElementById("btnLimpiar").addEventListener("click", () => {
  document.getElementById("sqlInput").value = ""
  ultimoResultado = null
  ocultarTodo()
  mostrar("sqlVacio")
  document.getElementById("sqlInput").focus()
})


/* =====================================================
   HELPERS
===================================================== */
function ocultarTodo() {
  document.getElementById("sqlResultados").classList.add("oculto")
  document.getElementById("sqlError").classList.add("oculto")
  document.getElementById("sqlVacio").classList.add("oculto")
}

function mostrar(id) {
  document.getElementById(id).classList.remove("oculto")
}

function getCookie(name) {
  const val = document.cookie.split(";").find(c => c.trim().startsWith(name + "="))
  return val ? decodeURIComponent(val.trim().split("=")[1]) : ""
}

const style = document.createElement("style")
style.textContent = `@keyframes spin { to { transform: rotate(360deg); } }`
document.head.appendChild(style)
