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
   SIDEBAR: clic en tabla inserta query de ejemplo
===================================================== */
document.querySelectorAll(".tabla-ref").forEach(ref => {
  ref.addEventListener("click", () => {
    const tabla = ref.dataset.tabla
    document.getElementById("sqlInput").value =
      `SELECT *\nFROM ${tabla}\nLIMIT 20;`

    ocultarTodo()
    mostrar("sqlVacio")
  })
})


/* =====================================================
   EJECUTAR CONSULTA
===================================================== */
document.getElementById("btnEjecutar").addEventListener("click", ejecutarQuery)

document.getElementById("sqlInput").addEventListener("keydown", e => {
  // Ctrl+Enter o Cmd+Enter ejecuta
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

  fetch("/api/sql/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken")
    },
    body: JSON.stringify({ query })
  })
  .then(r => r.json())
  .then(data => {
    if (data.error) {
      document.getElementById("sqlErrorMsg").textContent = data.error
      mostrar("sqlError")
    } else {
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
  const thead = document.getElementById("sqlThead")
  const tbody = document.getElementById("sqlTbody")
  const conteo = document.getElementById("sqlConteo")

  conteo.textContent = `${total} fila${total !== 1 ? "s" : ""}`

  // Encabezado
  thead.innerHTML = "<tr>" + columnas.map(c =>
    `<th title="${c}">${c}</th>`
  ).join("") + "</tr>"

  // Filas
  tbody.innerHTML = filas.map(fila =>
    "<tr>" + fila.map(celda => {
      if (celda === null || celda === undefined) {
        return `<td class="null">NULL</td>`
      }
      const texto = String(celda)
      return `<td title="${texto.replace(/"/g, "&quot;")}">${texto}</td>`
    }).join("") + "</tr>"
  ).join("")
}


/* =====================================================
   LIMPIAR
===================================================== */
document.getElementById("btnLimpiar").addEventListener("click", () => {
  document.getElementById("sqlInput").value = ""
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

// Animación spin para el botón cargando
const style = document.createElement("style")
style.textContent = `@keyframes spin { to { transform: rotate(360deg); } }`
document.head.appendChild(style)
