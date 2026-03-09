/* =====================================================
   CRUD MODULE — Vista Excel de Contratistas
===================================================== */

const PROCEDIMIENTOS = [
  "INSTRUMENTALIZACIÓN",
  "EQUIPO BASE",
  "ANÁLISIS",
  "CARACTERIZACIÓN",
  "DIFUSIÓN Y APRENDIZAJE",
  "AIDI",
  "MESA DE SERVICIOS",
  "GIS",
]

const CAMPOS_PERSONA = [
  { name: "nombre",        label: "Nombre completo", type: "text",     required: true },
  { name: "cedula",        label: "Cédula",          type: "text" },
  { name: "procedimiento", label: "Procedimiento",   type: "select" },
  { name: "fecha_inicio",  label: "Fecha inicio",    type: "date" },
  { name: "fecha_fin",     label: "Fecha fin",       type: "date" },
  { name: "honorarios",    label: "Honorarios/mes",  type: "number" },
  { name: "objeto",        label: "Objeto contrato", type: "textarea" },
  { name: "obligaciones",  label: "Obligaciones",    type: "textarea" },
]

let paginaActual  = 1
let modoEdicion   = false
let idEdicion     = null
let idBorrar      = null
let searchTimer   = null

const $  = id => document.getElementById(id)
const CSRF = () => {
  const v = document.cookie.split(";").find(c => c.trim().startsWith("csrftoken="))
  return v ? decodeURIComponent(v.trim().split("=")[1]) : ""
}


/* =====================================================
   INICIALIZACIÓN al activar la pestaña CRUD
===================================================== */
document.querySelector('[data-tab="crud"]').addEventListener("click", () => {
  cargarLista()
})


/* =====================================================
   LISTA DE REGISTROS
===================================================== */
async function cargarLista() {
  const q    = $("crudSearch").value.trim()
  const proc = $("xlsFiltroProc").value
  let url = `/api/crud/persona/?page=${paginaActual}`
  if (q)    url += `&q=${encodeURIComponent(q)}`
  if (proc) url += `&proc=${encodeURIComponent(proc)}`

  const res  = await fetch(url)
  const data = await res.json()

  $("xlsConteo").textContent = `${data.total} contratista${data.total !== 1 ? "s" : ""}`
  renderFilas(data.filas, data.total)
  renderPaginacion(data.total, data.page, data.size)
}

function renderFilas(filas, total) {
  const $vacio = $("crudVacio")
  const $tbody = $("crudTbody")

  if (!filas.length) {
    $tbody.innerHTML = ""
    $vacio.classList.remove("oculto")
    return
  }
  $vacio.classList.add("oculto")

  const offset = (paginaActual - 1) * 25
  $tbody.innerHTML = filas.map((fila, i) => {
    const honorarios = fila.honorarios
      ? `$ ${parseFloat(fila.honorarios).toLocaleString("es-CO")}`
      : "—"
    const proc = fila.procedimiento || "—"
    const procClass = "proc-badge proc-" + (fila.procedimiento || "").toLowerCase()
      .normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/\s+/g, "-").replace(/[^a-z0-9-]/g, "")
    return `
    <tr>
      <td class="xls-td-num">${offset + i + 1}</td>
      <td class="xls-td-nombre" title="${(fila.nombre || "").replace(/"/g, "&quot;")}">${fila.nombre || "—"}</td>
      <td>${fila.cedula || "—"}</td>
      <td><span class="${procClass}">${proc}</span></td>
      <td>${fila.fecha_inicio || "—"}</td>
      <td>${fila.fecha_fin || "—"}</td>
      <td class="xls-td-honorarios">${honorarios}</td>
      <td class="td-acciones">
        <button class="btn-accion btn-editar" data-id="${fila.id}" title="Editar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
        </button>
        <button class="btn-accion btn-borrar" data-id="${fila.id}" data-desc="${(fila.nombre || fila.id).replace(/"/g, "&quot;")}" title="Eliminar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/>
            <path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/>
          </svg>
        </button>
      </td>
    </tr>`
  }).join("")

  document.querySelectorAll(".btn-editar").forEach(b =>
    b.addEventListener("click", () => abrirEditar(parseInt(b.dataset.id))))
  document.querySelectorAll(".btn-borrar").forEach(b =>
    b.addEventListener("click", () => confirmarBorrar(parseInt(b.dataset.id), b.dataset.desc)))
}

function renderPaginacion(total, page, size) {
  const totalPags = Math.ceil(total / size)
  const $pag = $("crudPaginacion")
  if (totalPags <= 1) { $pag.innerHTML = ""; return }

  let html = `<button class="pag-btn" ${page <= 1 ? "disabled" : ""} data-p="${page-1}">&#8592;</button>`
  for (let p = Math.max(1, page-2); p <= Math.min(totalPags, page+2); p++) {
    html += `<button class="pag-btn${p===page?" pag-activo":""}" data-p="${p}">${p}</button>`
  }
  html += `<button class="pag-btn" ${page >= totalPags ? "disabled" : ""} data-p="${page+1}">&#8594;</button>`
  $pag.innerHTML = html

  $pag.querySelectorAll(".pag-btn:not([disabled])").forEach(b =>
    b.addEventListener("click", () => { paginaActual = parseInt(b.dataset.p); cargarLista() }))
}


/* =====================================================
   BÚSQUEDA Y FILTROS
===================================================== */
$("crudSearch").addEventListener("input", () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { paginaActual = 1; cargarLista() }, 350)
})

$("xlsFiltroProc").addEventListener("change", () => {
  paginaActual = 1
  cargarLista()
})


/* =====================================================
   MODAL CREAR / EDITAR
===================================================== */
$("btnNuevo").addEventListener("click", () => abrirCrear())
$("crudModalClose").addEventListener("click", cerrarModal)
$("btnCancelar").addEventListener("click", cerrarModal)
$("crudModal").addEventListener("click", e => { if (e.target === $("crudModal")) cerrarModal() })

function abrirCrear() {
  modoEdicion = false
  idEdicion   = null
  $("crudModalAvatar").textContent = "+"
  $("crudModalAvatar").style.background = "linear-gradient(135deg,#10b981,#00875a)"
  $("crudModalTitulo").textContent = "Nuevo contratista"
  renderForm({})
  $("crudModal").style.display = "flex"
}

async function abrirEditar(id) {
  modoEdicion = true
  idEdicion   = id
  const res   = await fetch(`/api/crud/persona/${id}/`)
  const datos = await res.json()
  $("crudModalAvatar").textContent = "✏"
  $("crudModalAvatar").style.background = "linear-gradient(135deg,#2563eb,#003087)"
  $("crudModalTitulo").textContent = "Editar contratista"
  renderForm(datos)
  $("crudModal").style.display = "flex"
}

function cerrarModal() {
  $("crudModal").style.display = "none"
}

function renderForm(datos) {
  $("crudForm").innerHTML = CAMPOS_PERSONA.map(c => {
    const val = datos[c.name] ?? ""
    const req = c.required ? "required" : ""

    if (c.type === "textarea") {
      return `<div class="form-grupo">
        <label>${c.label}${c.required ? " <span class='req'>*</span>" : ""}</label>
        <textarea name="${c.name}" rows="3" ${req}>${val}</textarea>
      </div>`
    }

    if (c.type === "select") {
      const options = PROCEDIMIENTOS.map(o =>
        `<option value="${o}" ${o===val?"selected":""}>${o}</option>`).join("")
      return `<div class="form-grupo">
        <label>${c.label}${c.required ? " <span class='req'>*</span>" : ""}</label>
        <select name="${c.name}" ${req}>
          <option value="">— Selecciona —</option>
          ${options}
        </select>
      </div>`
    }

    return `<div class="form-grupo">
      <label>${c.label}${c.required ? " <span class='req'>*</span>" : ""}</label>
      <input type="${c.type}" name="${c.name}" value="${val}" ${req}>
    </div>`
  }).join("")
}

$("btnGuardar").addEventListener("click", async () => {
  const body  = {}
  let valido  = true

  CAMPOS_PERSONA.forEach(c => {
    const el  = $("crudForm").elements[c.name]
    const val = el ? el.value.trim() : ""
    if (c.required && !val) {
      el && el.classList.add("input-error")
      valido = false
    } else {
      el && el.classList.remove("input-error")
      body[c.name] = val || null
    }
  })

  if (!valido) { crudToast("Completa los campos obligatorios", "error"); return }

  const url    = modoEdicion ? `/api/crud/persona/${idEdicion}/` : `/api/crud/persona/crear/`
  const method = modoEdicion ? "PUT" : "POST"

  const res  = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json", "X-CSRFToken": CSRF() },
    body: JSON.stringify(body)
  })
  const data = await res.json()

  if (data.error) { crudToast(data.error, "error"); return }

  cerrarModal()
  paginaActual = 1
  cargarLista()
  crudToast(modoEdicion ? "Registro actualizado" : "Registro creado", "ok")
})


/* =====================================================
   CONFIRMAR BORRADO
===================================================== */
$("btnBorrarCancelar").addEventListener("click", () => $("crudModalBorrar").style.display = "none")
$("crudModalBorrar").addEventListener("click", e => {
  if (e.target === $("crudModalBorrar")) $("crudModalBorrar").style.display = "none"
})

function confirmarBorrar(id, desc) {
  idBorrar = id
  $("borrarDescripcion").textContent = `¿Eliminar "${desc}"? Esta acción no se puede deshacer.`
  $("crudModalBorrar").style.display = "flex"
}

$("btnBorrarConfirmar").addEventListener("click", async () => {
  $("crudModalBorrar").style.display = "none"
  const res  = await fetch(`/api/crud/persona/${idBorrar}/`, {
    method: "DELETE",
    headers: { "X-CSRFToken": CSRF() }
  })
  const data = await res.json()
  if (data.error) { crudToast(data.error, "error"); return }
  paginaActual = 1
  cargarLista()
  crudToast("Registro eliminado", "ok")
})


/* =====================================================
   TOAST
===================================================== */
let toastTimer = null
function crudToast(msg, tipo = "ok") {
  const el = $("crudToast")
  el.textContent = msg
  el.className = `crud-toast crud-toast-${tipo}`
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => el.className = "crud-toast oculto", 3000)
}
