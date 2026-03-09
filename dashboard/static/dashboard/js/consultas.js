/* =====================================================
   TABS
===================================================== */
document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const target = btn.dataset.tab
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"))
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"))
    btn.classList.add("active")
    document.getElementById("tab-" + target).classList.add("active")
  })
})


/* =====================================================
   SIDEBAR: clic en tabla → SELECT con sus columnas
===================================================== */
const QUERIES_TABLA = {
  dashboard_persona:
`SELECT id, nombre, cedula, fecha_inicio, fecha_fin, honorarios
FROM dashboard_persona
ORDER BY nombre
LIMIT 20;`,
  dashboard_proyecto:
`SELECT *
FROM dashboard_proyecto
ORDER BY nombre
LIMIT 20;`,
  dashboard_modulo:
`SELECT *
FROM dashboard_modulo
ORDER BY nombre
LIMIT 20;`,
  dashboard_rol:
`SELECT *
FROM dashboard_rol
ORDER BY nombre;`,
  dashboard_asignacion:
`SELECT *
FROM dashboard_asignacion
LIMIT 20;`,
  dashboard_planaccion:
`SELECT *
FROM dashboard_planaccion
LIMIT 20;`
}

document.querySelectorAll(".tabla-ref").forEach(ref => {
  ref.addEventListener("click", () => {
    const tabla = ref.dataset.tabla
    cargarQuery(QUERIES_TABLA[tabla] || `SELECT *\nFROM ${tabla}\nLIMIT 20;`)
  })
})


/* =====================================================
   CONSULTAS SUGERIDAS
===================================================== */
document.querySelectorAll(".sugerida-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    cargarQuery(btn.dataset.query)
    // auto-ejecutar al hacer clic en sugerida
    setTimeout(ejecutarQuery, 50)
  })
})

function cargarQuery(sql) {
  document.getElementById("sqlInput").value = sql
  ocultarTodo()
  mostrar("sqlVacio")
}


/* =====================================================
   EJECUTAR CONSULTA
===================================================== */
// Guardamos el último resultado para exportar
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
  a.download = `consulta_srni_${new Date().toISOString().slice(0,10)}.csv`
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
