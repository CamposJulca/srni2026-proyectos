/* =====================================================
   CRUD MODULE
===================================================== */

let META       = {}          // metadatos de todas las tablas
let tablaActiva = "persona"  // tabla seleccionada
let paginaActual = 1
let totalRegistros = 0
let modoEdicion  = false     // false=crear, true=editar
let idEdicion    = null
let idBorrar     = null
let searchTimer  = null

const CSRF = () => {
  const v = document.cookie.split(";").find(c => c.trim().startsWith("csrftoken="))
  return v ? decodeURIComponent(v.trim().split("=")[1]) : ""
}

const $ = id => document.getElementById(id)


/* =====================================================
   INICIALIZACIÓN al activar la pestaña CRUD
===================================================== */
document.querySelector('[data-tab="crud"]').addEventListener("click", () => {
  if (Object.keys(META).length === 0) iniciarCRUD()
})

async function iniciarCRUD() {
  const res  = await fetch("/api/crud/meta/")
  META       = await res.json()
  renderSidebar()
  activarTabla("persona")
}


/* =====================================================
   SIDEBAR
===================================================== */
function renderSidebar() {
  const iconos = {
    persona:     `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>`,
    proyecto:    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>`,
    modulo:      `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>`,
    rol:         `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M6 20v-2a6 6 0 0 1 12 0v2"/></svg>`,
    asignacion:  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><path d="m9 12 2 2 4-4"/></svg>`,
    planaccion:  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`,
  }

  $("crudTablasBtns").innerHTML = Object.entries(META).map(([key, cfg]) => `
    <button class="crud-tabla-btn${key === tablaActiva ? " active" : ""}" data-tabla="${key}">
      <span class="crud-tabla-icono">${iconos[key] || ""}</span>
      <span class="crud-tabla-info">
        <span class="crud-tabla-nombre">${cfg.label}</span>
        <span class="crud-tabla-count">${cfg.total}</span>
      </span>
    </button>
  `).join("")

  document.querySelectorAll(".crud-tabla-btn").forEach(btn => {
    btn.addEventListener("click", () => activarTabla(btn.dataset.tabla))
  })
}

function activarTabla(tabla) {
  tablaActiva  = tabla
  paginaActual = 1
  $("crudSearch").value = ""
  document.querySelectorAll(".crud-tabla-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.tabla === tabla)
  })
  $("crudTablaTitulo").textContent = META[tabla]?.label || tabla
  cargarLista()
}


/* =====================================================
   LISTA DE REGISTROS
===================================================== */
async function cargarLista() {
  const q    = $("crudSearch").value.trim()
  const url  = `/api/crud/${tablaActiva}/?page=${paginaActual}${q ? "&q=" + encodeURIComponent(q) : ""}`
  const res  = await fetch(url)
  const data = await res.json()

  totalRegistros = data.total
  renderCabecera()
  renderFilas(data.filas)
  renderPaginacion(data.total, data.page, data.size)
}

function renderCabecera() {
  const cols = META[tablaActiva]?.columnas || []
  const labels = cols.map(c => {
    const partes = c.split("__")
    return partes.map(p => p.charAt(0).toUpperCase() + p.slice(1)).join(" › ")
  })
  $("crudThead").innerHTML = `<tr>
    ${labels.map(l => `<th>${l}</th>`).join("")}
    <th class="th-acciones">Acciones</th>
  </tr>`
}

function renderFilas(filas) {
  const $vacio = $("crudVacio")
  const $tbody = $("crudTbody")

  if (!filas.length) {
    $tbody.innerHTML = ""
    $vacio.classList.remove("oculto")
    return
  }
  $vacio.classList.add("oculto")

  const cols = META[tablaActiva]?.columnas || []
  $tbody.innerHTML = filas.map(fila => `
    <tr>
      ${cols.map(c => {
        const val = fila[c]
        const corto = val && val.length > 60 ? val.slice(0, 60) + "…" : (val ?? "—")
        return `<td title="${(val || "").replace(/"/g, "&quot;")}">${corto}</td>`
      }).join("")}
      <td class="td-acciones">
        <button class="btn-accion btn-editar" data-id="${fila.id}" title="Editar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
        </button>
        <button class="btn-accion btn-borrar" data-id="${fila.id}" data-desc="${(fila[cols[0]] || fila.id).replace(/"/g, "&quot;")}" title="Eliminar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/>
            <path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/>
          </svg>
        </button>
      </td>
    </tr>
  `).join("")

  // Eventos
  document.querySelectorAll(".btn-editar").forEach(b =>
    b.addEventListener("click", () => abrirEditar(parseInt(b.dataset.id))))
  document.querySelectorAll(".btn-borrar").forEach(b =>
    b.addEventListener("click", () => confirmarBorrar(parseInt(b.dataset.id), b.dataset.desc)))
}

function renderPaginacion(total, page, size) {
  const totalPags = Math.ceil(total / size)
  const $pag = $("crudPaginacion")
  if (totalPags <= 1) { $pag.innerHTML = `<span class="pag-info">${total} registro${total !== 1 ? "s" : ""}</span>`; return }

  let html = `<span class="pag-info">${total} registros</span>`
  html += `<button class="pag-btn" ${page <= 1 ? "disabled" : ""} data-p="${page-1}">&#8592;</button>`
  for (let p = Math.max(1, page-2); p <= Math.min(totalPags, page+2); p++) {
    html += `<button class="pag-btn${p===page?" pag-activo":""}" data-p="${p}">${p}</button>`
  }
  html += `<button class="pag-btn" ${page >= totalPags ? "disabled" : ""} data-p="${page+1}">&#8594;</button>`
  $pag.innerHTML = html

  $pag.querySelectorAll(".pag-btn:not([disabled])").forEach(b =>
    b.addEventListener("click", () => { paginaActual = parseInt(b.dataset.p); cargarLista() }))
}


/* =====================================================
   BÚSQUEDA
===================================================== */
$("crudSearch").addEventListener("input", () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { paginaActual = 1; cargarLista() }, 350)
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
  $("crudModalTitulo").textContent = `Nuevo — ${META[tablaActiva]?.label}`
  renderForm({})
  $("crudModal").style.display = "flex"
}

async function abrirEditar(id) {
  modoEdicion = true
  idEdicion   = id
  const res   = await fetch(`/api/crud/${tablaActiva}/${id}/`)
  const datos = await res.json()
  $("crudModalAvatar").textContent = "✏"
  $("crudModalAvatar").style.background = "linear-gradient(135deg,#2563eb,#003087)"
  $("crudModalTitulo").textContent = `Editar — ${META[tablaActiva]?.label}`
  renderForm(datos)
  $("crudModal").style.display = "flex"
}

function cerrarModal() {
  $("crudModal").style.display = "none"
}

function renderForm(datos) {
  const campos = META[tablaActiva]?.campos || []
  $("crudForm").innerHTML = campos.map(c => {
    const val = datos[c.name] ?? ""
    const req  = c.required ? "required" : ""

    if (c.type === "textarea") {
      return `<div class="form-grupo">
        <label>${c.label}${c.required ? " <span class='req'>*</span>" : ""}</label>
        <textarea name="${c.name}" rows="3" ${req}>${val}</textarea>
      </div>`
    }

    if (c.type === "select") {
      const opts = c.opciones_fijas || []
      const options = opts.map(o => `<option value="${o}" ${o===val?"selected":""}>${o}</option>`).join("")
      return `<div class="form-grupo">
        <label>${c.label}${c.required ? " <span class='req'>*</span>" : ""}</label>
        <select name="${c.name}" ${req}>
          <option value="">— Selecciona —</option>
          ${options}
        </select>
      </div>`
    }

    if (c.type === "fk") {
      const opts = c.opciones || []
      const options = opts.map(o => `<option value="${o.id}" ${o.id==val?"selected":""}>${o.label}</option>`).join("")
      return `<div class="form-grupo">
        <label>${c.label}${c.required ? " <span class='req'>*</span>" : ""}</label>
        <select name="${c.name}" ${req}>
          <option value="">— Selecciona —</option>
          ${options}
        </select>
      </div>`
    }

    // text / number / date
    return `<div class="form-grupo">
      <label>${c.label}${c.required ? " <span class='req'>*</span>" : ""}</label>
      <input type="${c.type}" name="${c.name}" value="${val}" ${req}>
    </div>`
  }).join("")
}

$("btnGuardar").addEventListener("click", async () => {
  const campos = META[tablaActiva]?.campos || []
  const body   = {}
  let valido   = true

  campos.forEach(c => {
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

  if (!valido) { toast("Completa los campos obligatorios", "error"); return }

  const url    = modoEdicion ? `/api/crud/${tablaActiva}/${idEdicion}/` : `/api/crud/${tablaActiva}/crear/`
  const method = modoEdicion ? "PUT" : "POST"

  const res  = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json", "X-CSRFToken": CSRF() },
    body: JSON.stringify(body)
  })
  const data = await res.json()

  if (data.error) { toast(data.error, "error"); return }

  cerrarModal()
  await iniciarCRUD()       // refresca conteos en sidebar
  activarTabla(tablaActiva) // recarga lista
  toast(modoEdicion ? "Registro actualizado" : "Registro creado", "ok")
})


/* =====================================================
   CONFIRMAR BORRADO
===================================================== */
$("btnBorrarCancelar").addEventListener("click", () => $("crudModalBorrar").style.display = "none")
$("crudModalBorrar").addEventListener("click", e => { if (e.target === $("crudModalBorrar")) $("crudModalBorrar").style.display = "none" })

function confirmarBorrar(id, desc) {
  idBorrar = id
  $("borrarDescripcion").textContent = `¿Eliminar "${desc}"? Esta acción no se puede deshacer.`
  $("crudModalBorrar").style.display = "flex"
}

$("btnBorrarConfirmar").addEventListener("click", async () => {
  $("crudModalBorrar").style.display = "none"
  const res  = await fetch(`/api/crud/${tablaActiva}/${idBorrar}/`, {
    method: "DELETE",
    headers: { "X-CSRFToken": CSRF() }
  })
  const data = await res.json()
  if (data.error) { toast(data.error, "error"); return }
  await iniciarCRUD()
  activarTabla(tablaActiva)
  toast("Registro eliminado", "ok")
})


/* =====================================================
   TOAST
===================================================== */
let toastTimer = null
function toast(msg, tipo = "ok") {
  const el = $("crudToast")
  el.textContent = msg
  el.className = `crud-toast crud-toast-${tipo}`
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => el.className = "crud-toast oculto", 3000)
}
