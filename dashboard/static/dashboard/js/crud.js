/* =====================================================
   CRUD MULTI-ENTIDAD — SRNI
===================================================== */

const ICONOS = {
  colaborador: "👤",
  obligacion:  "📋",
  actividad:   "⚡",
  asignacion:  "🔗",
  modulo:      "📦",
  rol:         "🏷",
}

const COLORES_ESTADO = {
  completada: "#10b981",
  en_curso:   "#f59e0b",
  pendiente:  "#6b7280",
  bloqueada:  "#ef4444",
}

let META         = {}   // { colaborador: {...}, obligacion: {...}, ... }
let tablaActiva  = "colaborador"
let paginaActual = 1
let filtroColaborador = ""
let idEdicion    = null
let idBorrar     = null
let searchTimer  = null

const $ = id => document.getElementById(id)
const CSRF = () => {
  const v = document.cookie.split(";").find(c => c.trim().startsWith("csrftoken="))
  return v ? decodeURIComponent(v.trim().split("=")[1]) : ""
}


/* =====================================================
   INIT
===================================================== */
document.addEventListener("DOMContentLoaded", async () => {
  META = await fetch("/api/crud/meta/").then(r => r.json())
  renderSidebarCounts()
  rellenarFiltroColaborador()
  bindSidebar()
  bindToolbar()
  bindModales()

  // Entidad inicial desde hash o por defecto
  const hash = location.hash.replace("#", "")
  selectEntidad(META[hash] ? hash : "colaborador")
})


/* =====================================================
   SIDEBAR
===================================================== */
function renderSidebarCounts() {
  for (const [key, cfg] of Object.entries(META)) {
    const el = $(`cnt-${key}`)
    if (el) el.textContent = cfg.total
  }
}

function bindSidebar() {
  document.querySelectorAll(".crud-sidebar-item").forEach(item => {
    item.addEventListener("click", () => selectEntidad(item.dataset.tabla))
  })
}

function selectEntidad(tabla) {
  if (!META[tabla]) return
  tablaActiva       = tabla
  paginaActual      = 1
  filtroColaborador = ""
  location.hash     = tabla

  // Actualizar sidebar activo
  document.querySelectorAll(".crud-sidebar-item").forEach(el => {
    el.classList.toggle("activo", el.dataset.tabla === tabla)
  })

  // Actualizar toolbar
  const cfg = META[tabla]
  $("crudIconoMain").textContent = ICONOS[tabla] || "📄"
  $("crudTituloMain").textContent = cfg.label

  // Mostrar/ocultar filtro de colaborador
  const filtroEl = $("crudFiltroColaborador")
  if (cfg.filtro_colaborador) {
    filtroEl.classList.remove("oculto")
    filtroEl.value = ""
  } else {
    filtroEl.classList.add("oculto")
    filtroEl.value = ""
  }

  $("crudSearch").value = ""
  cargarLista()
}


/* =====================================================
   FILTRO COLABORADOR (select precargado)
===================================================== */
function rellenarFiltroColaborador() {
  const colabs = META.colaborador?.campos
    ? null
    : null  // lo obtenemos diferente
  // Usamos los colaboradores de la meta de obligacion (fk_modelo Colaborador)
  const opcColabs = META.obligacion?.campos?.find(c => c.name === "colaborador_id")?.opciones || []
  const sel = $("crudFiltroColaborador")
  opcColabs.forEach(({ id, label }) => {
    const opt = document.createElement("option")
    opt.value = id
    opt.textContent = label.length > 50 ? label.slice(0, 50) + "…" : label
    sel.appendChild(opt)
  })
}


/* =====================================================
   CARGAR LISTA
===================================================== */
async function cargarLista() {
  $("crudVacio").classList.add("oculto")
  $("crudCargando").classList.remove("oculto")
  $("crudTbody").innerHTML = ""
  $("crudThead").innerHTML = ""
  $("crudPaginacion").innerHTML = ""

  const q     = $("crudSearch").value.trim()
  const colab = $("crudFiltroColaborador").value

  let url = `/api/crud/${tablaActiva}/?page=${paginaActual}`
  if (q)     url += `&q=${encodeURIComponent(q)}`
  if (colab) url += `&colaborador=${encodeURIComponent(colab)}`

  try {
    const res  = await fetch(url)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()

    $("crudCargando").classList.add("oculto")

    if (data.error) {
      mostrarErrorTabla(data.error)
      return
    }

    $("crudConteo").textContent = `${data.total} registro${data.total !== 1 ? "s" : ""}`

    const cfg = META[tablaActiva]
    renderTabla(cfg, data.filas, data.total, data.page, data.size)
    renderPaginacion(data.total, data.page, data.size)

    const cnt = $(`cnt-${tablaActiva}`)
    if (cnt) cnt.textContent = data.total

  } catch (err) {
    $("crudCargando").classList.add("oculto")
    mostrarErrorTabla(`Error cargando datos: ${err.message}`)
    console.error("cargarLista error:", err)
  }
}

function mostrarErrorTabla(msg) {
  $("crudThead").innerHTML = ""
  $("crudTbody").innerHTML = `<tr><td colspan="20" style="text-align:center;color:#ef4444;padding:24px">${msg}</td></tr>`
  $("crudVacio").classList.add("oculto")
}


/* =====================================================
   RENDERIZAR TABLA
===================================================== */
const ETIQUETAS_COL = {
  "nombre":                       "Nombre",
  "cedula":                       "Cédula",
  "procedimiento__nombre":        "Procedimiento",
  "fecha_inicio":                 "Inicio",
  "fecha_fin":                    "Fin",
  "honorarios":                   "Honorarios",
  "proyecto__nombre":             "Proyecto",
  "referente":                    "Referente",
  "colaborador__nombre":          "Colaborador",
  "rol__nombre":                  "Rol",
  "modulo__nombre":               "Módulo",
  "modulo__proyecto__nombre":     "Proyecto",
  "descripcion":                  "Descripción",
  "obligacion__colaborador__nombre": "Colaborador",
  "actividad_id":                 "ID",
  "estado":                       "Estado",
  "progreso":                     "Progreso",
}

function etiqueta(col) {
  return ETIQUETAS_COL[col] || col.split("__").pop().replace(/_/g, " ")
}

function renderTabla(cfg, filas, total, page, size) {
  const columnas = cfg.columnas

  // Thead
  $("crudThead").innerHTML = "<tr>" +
    '<th class="xls-th-num">#</th>' +
    columnas.map(c => `<th>${etiqueta(c)}</th>`).join("") +
    '<th class="xls-th-acc">Acciones</th>' +
    "</tr>"

  if (!filas.length) {
    $("crudVacio").classList.remove("oculto")
    return
  }

  const offset = (page - 1) * size

  $("crudTbody").innerHTML = filas.map((fila, i) => {
    const celdas = columnas.map(col => {
      const val = fila[col]
      if (val === null || val === undefined) return `<td class="null">—</td>`

      if (col === "estado") {
        const color = COLORES_ESTADO[val] || "#6b7280"
        const etiq  = val.replace("_", " ")
        return `<td><span class="estado-badge" style="background:${color}20;color:${color};border:1px solid ${color}40">${etiq}</span></td>`
      }
      if (col === "honorarios" && val) {
        return `<td class="xls-td-honorarios">$ ${parseFloat(val).toLocaleString("es-CO")}</td>`
      }
      if (col === "progreso") {
        return `<td><span class="progreso-bar"><span style="width:${val}%"></span></span> ${val}%</td>`
      }
      if (col === "descripcion") {
        const corto = val.length > 90 ? val.slice(0, 90) + "…" : val
        return `<td title="${val.replace(/"/g, "&quot;")}">${corto}</td>`
      }
      const corto = String(val).length > 40 ? String(val).slice(0, 40) + "…" : String(val)
      return `<td title="${String(val).replace(/"/g, "&quot;")}">${corto}</td>`
    }).join("")

    const desc = fila[columnas[0]] || fila.id
    return `<tr>
      <td class="xls-td-num">${offset + i + 1}</td>
      ${celdas}
      <td class="td-acciones">
        <button class="btn-accion btn-editar" data-id="${fila.id}" title="Editar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
        </button>
        <button class="btn-accion btn-borrar" data-id="${fila.id}"
          data-desc="${String(desc).replace(/"/g, "&quot;").slice(0, 60)}" title="Eliminar">
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


/* =====================================================
   PAGINACIÓN
===================================================== */
function renderPaginacion(total, page, size) {
  const totalPags = Math.ceil(total / size)
  const $pag = $("crudPaginacion")
  if (totalPags <= 1) { $pag.innerHTML = ""; return }

  let html = `<button class="pag-btn" ${page <= 1 ? "disabled" : ""} data-p="${page - 1}">&#8592;</button>`
  for (let p = Math.max(1, page - 2); p <= Math.min(totalPags, page + 2); p++) {
    html += `<button class="pag-btn${p === page ? " pag-activo" : ""}" data-p="${p}">${p}</button>`
  }
  html += `<button class="pag-btn" ${page >= totalPags ? "disabled" : ""} data-p="${page + 1}">&#8594;</button>`
  $pag.innerHTML = html

  $pag.querySelectorAll(".pag-btn:not([disabled])").forEach(b =>
    b.addEventListener("click", () => { paginaActual = parseInt(b.dataset.p); cargarLista() }))
}


/* =====================================================
   TOOLBAR BINDINGS
===================================================== */
function bindToolbar() {
  $("crudSearch").addEventListener("input", () => {
    clearTimeout(searchTimer)
    searchTimer = setTimeout(() => { paginaActual = 1; cargarLista() }, 350)
  })

  $("crudFiltroColaborador").addEventListener("change", () => {
    paginaActual = 1
    cargarLista()
  })

  $("btnNuevo").addEventListener("click", () => abrirCrear())
}


/* =====================================================
   MODAL CREAR / EDITAR
===================================================== */
function abrirCrear() {
  idEdicion = null
  $("crudModalAvatar").textContent = "+"
  $("crudModalAvatar").style.background = "linear-gradient(135deg,#10b981,#00875a)"
  $("crudModalTitulo").textContent = `Nuevo — ${META[tablaActiva]?.label || ""}`

  // Pre-fill colaborador si hay filtro activo
  const preColaborador = $("crudFiltroColaborador").value || ""
  renderForm({}, preColaborador)
  $("crudModal").style.display = "flex"
}

async function abrirEditar(id) {
  idEdicion = id
  const res   = await fetch(`/api/crud/${tablaActiva}/${id}/`)
  const datos = await res.json()

  $("crudModalAvatar").textContent = "✏"
  $("crudModalAvatar").style.background = "linear-gradient(135deg,#2563eb,#003087)"
  $("crudModalTitulo").textContent = `Editar — ${META[tablaActiva]?.label || ""}`
  renderForm(datos)
  $("crudModal").style.display = "flex"
}

function renderForm(datos, preColaborador = "") {
  const cfg = META[tablaActiva]
  if (!cfg) return

  $("crudForm").innerHTML = cfg.campos.map(c => {
    let val = datos[c.name] ?? ""

    // Pre-fill FK de colaborador si viene de filtro
    if (c.name === "colaborador_id" && !val && preColaborador) {
      val = preColaborador
    }

    const req = c.required ? "required" : ""
    const star = c.required ? " <span class='req'>*</span>" : ""

    if (c.type === "textarea") {
      return `<div class="form-grupo form-grupo-full">
        <label>${c.label}${star}</label>
        <textarea name="${c.name}" rows="3" ${req}>${val}</textarea>
      </div>`
    }

    if (c.type === "fk" || c.type === "choice") {
      const opciones = c.opciones || []
      const opts = opciones.map(o =>
        `<option value="${o.id}" ${String(o.id) === String(val) ? "selected" : ""}>${o.label.length > 70 ? o.label.slice(0,70)+"…" : o.label}</option>`
      ).join("")
      return `<div class="form-grupo">
        <label>${c.label}${star}</label>
        <select name="${c.name}" ${req}>
          <option value="">— Selecciona —</option>
          ${opts}
        </select>
      </div>`
    }

    return `<div class="form-grupo">
      <label>${c.label}${star}</label>
      <input type="${c.type === 'number' ? 'number' : c.type === 'date' ? 'date' : 'text'}"
             name="${c.name}" value="${val}" ${req}>
    </div>`
  }).join("")
}

async function guardar() {
  const cfg  = META[tablaActiva]
  const body = {}
  let valido = true

  cfg.campos.forEach(c => {
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

  const url    = idEdicion ? `/api/crud/${tablaActiva}/${idEdicion}/` : `/api/crud/${tablaActiva}/crear/`
  const method = idEdicion ? "PUT" : "POST"

  const res  = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json", "X-CSRFToken": CSRF() },
    body: JSON.stringify(body),
  })
  const data = await res.json()

  if (data.error) { crudToast(data.error, "error"); return }

  cerrarModal()
  paginaActual = 1
  cargarLista()
  // Refrescar meta totals
  fetch("/api/crud/meta/").then(r => r.json()).then(m => {
    META = m
    renderSidebarCounts()
  })
  crudToast(idEdicion ? "Registro actualizado" : "Registro creado", "ok")
}


/* =====================================================
   MODAL BORRAR
===================================================== */
function confirmarBorrar(id, desc) {
  idBorrar = id
  $("borrarTitulo").textContent = `¿Eliminar ${ICONOS[tablaActiva] || ""} ${META[tablaActiva]?.label?.slice(0,-1) || "registro"}?`
  $("borrarDescripcion").textContent = `"${desc}" — Esta acción no se puede deshacer.`
  $("crudModalBorrar").style.display = "flex"
}

async function borrarConfirmado() {
  $("crudModalBorrar").style.display = "none"
  const res  = await fetch(`/api/crud/${tablaActiva}/${idBorrar}/`, {
    method: "DELETE",
    headers: { "X-CSRFToken": CSRF() },
  })
  const data = await res.json()
  if (data.error) { crudToast(data.error, "error"); return }
  paginaActual = 1
  cargarLista()
  fetch("/api/crud/meta/").then(r => r.json()).then(m => {
    META = m
    renderSidebarCounts()
  })
  crudToast("Registro eliminado", "ok")
}


/* =====================================================
   BIND MODALES
===================================================== */
function bindModales() {
  $("btnGuardar").addEventListener("click", guardar)
  $("crudModalClose").addEventListener("click", cerrarModal)
  $("btnCancelar").addEventListener("click", cerrarModal)
  $("crudModal").addEventListener("click", e => { if (e.target === $("crudModal")) cerrarModal() })

  $("btnBorrarConfirmar").addEventListener("click", borrarConfirmado)
  $("btnBorrarCancelar").addEventListener("click", () => $("crudModalBorrar").style.display = "none")
  $("crudModalBorrar").addEventListener("click", e => {
    if (e.target === $("crudModalBorrar")) $("crudModalBorrar").style.display = "none"
  })
}

function cerrarModal() {
  $("crudModal").style.display = "none"
}


/* =====================================================
   TOAST
===================================================== */
let toastTimer = null
function crudToast(msg, tipo = "ok") {
  const el = $("crudToast")
  el.textContent = msg
  el.className = `crud-toast crud-toast-${tipo}`
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => el.className = "crud-toast oculto", 3500)
}
