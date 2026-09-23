const root = document.querySelector(".proyecto-detalle")
const proyectoId = root?.dataset.proyectoId

const text = value => value === null || value === undefined || value === "" ? "Sin registro" : value
const money = value => "$ " + Math.round(value || 0).toLocaleString("es-CO")
const pct = value => `${Number(value || 0).toFixed(1)}%`

function list(items, renderer, empty = "Sin registros") {
  if (!items.length) return `<p class="proyecto-vacio">${empty}</p>`
  return `<div class="proyecto-lista">${items.map(renderer).join("")}</div>`
}

function badge(value, cls = "") {
  return `<span class="proyecto-badge ${cls}">${text(value)}</span>`
}

document.addEventListener("DOMContentLoaded", async () => {
  const res = await fetch(`${window.APP_BASE || ''}/api/proyectos/${proyectoId}/`)
  const data = await res.json()
  renderProyecto(data)
})

function renderProyecto(data) {
  const proyecto = data.proyecto
  const resumen = data.resumen || {}

  document.getElementById("proyectoNombre").textContent = proyecto.nombre
  document.getElementById("proyectoObjetivo").textContent = text(proyecto.objetivo)

  document.getElementById("proyectoFicha").innerHTML = `
    <div><strong>Estado</strong>${badge(proyecto.estado)}</div>
    <div><strong>Prioridad</strong>${badge(proyecto.prioridad)}</div>
    <div><strong>Responsable</strong><span>${text(proyecto.responsable)}</span></div>
    <div><strong>Procedimiento</strong><span>${text(proyecto.procedimiento)}</span></div>
    <div><strong>Inicio</strong><span>${text(proyecto.fecha_inicio)}</span></div>
    <div><strong>Fin</strong><span>${text(proyecto.fecha_fin)}</span></div>
    <div><strong>Presupuesto</strong><span>${money(proyecto.presupuesto)}</span></div>
    <div><strong>Observaciones</strong><span>${text(proyecto.observaciones)}</span></div>
  `

  document.getElementById("proyectoSemaforo").innerHTML = `
    <div class="semaforo semaforo-${resumen.semaforo || "verde"}">${text(resumen.semaforo)}</div>
    <div class="proyecto-kpis">
      <span>Avance ${pct(resumen.avance_promedio)}</span>
      <span>Cumplimiento ${pct(resumen.cumplimiento_mes)}</span>
      <span>${resumen.actividades_vencidas || 0} vencidas</span>
      <span>${resumen.actividades_bloqueadas || 0} bloqueadas</span>
      <span>${resumen.personas_asignadas || 0} personas</span>
      <span>${resumen.modulos_activos || 0} módulos</span>
    </div>
  `

  document.getElementById("proyectoModulos").innerHTML = list(data.modulos, modulo => `
    <div class="proyecto-item">
      <strong>${modulo.nombre}</strong>
      <span>${text(modulo.referente)} · ${modulo.asignaciones} asignaciones</span>
    </div>
  `)

  document.getElementById("proyectoEquipo").innerHTML = list(data.equipo, persona => `
    <div class="proyecto-item">
      <strong>${persona.colaborador}</strong>
      <span>${persona.rol} · ${persona.modulo}</span>
    </div>
  `)

  const vencidas = new Set(data.actividades_vencidas)
  const bloqueadas = new Set(data.actividades_bloqueadas)
  document.getElementById("proyectoCronograma").innerHTML = data.cronograma.map(actividad => `
    <tr class="${vencidas.has(actividad.id) || bloqueadas.has(actividad.id) ? "proyecto-tr-alerta" : ""}">
      <td>${text(actividad.actividad_id)}</td>
      <td>${actividad.descripcion}</td>
      <td>${actividad.colaborador}</td>
      <td>${actividad.fecha_inicio} / ${actividad.fecha_fin}</td>
      <td>${badge(actividad.estado)}</td>
      <td>${actividad.progreso}%</td>
    </tr>
  `).join("") || `<tr><td colspan="6">Sin actividades</td></tr>`

  document.getElementById("proyectoRiesgos").innerHTML = list(data.riesgos, riesgo => `
    <div class="proyecto-item">
      <strong>${riesgo.riesgo}</strong>
      <span>${riesgo.impacto} · ${riesgo.probabilidad} · ${text(riesgo.responsable)} · ${text(riesgo.fecha_limite)}</span>
      <small>${text(riesgo.plan_mitigacion)}</small>
    </div>
  `)

  document.getElementById("proyectoAlertas").innerHTML = list(data.alertas, alerta => `
    <div class="proyecto-item">
      <strong>${alerta.alerta}</strong>
      <span>${alerta.severidad} · ${text(alerta.responsable)} · ${text(alerta.fecha_limite)}</span>
      <small>${text(alerta.plan_accion)}</small>
    </div>
  `)

  document.getElementById("proyectoCuentas").innerHTML = list(data.cuentas_cobro, cuenta => `
    <div class="proyecto-item">
      <strong>${cuenta.colaborador}</strong>
      <span>${cuenta.periodo} · ${money(cuenta.valor_cobrado)} · ${cuenta.estado}</span>
    </div>
  `)

  document.getElementById("proyectoEvidencias").innerHTML = list(data.evidencias, evidencia => `
    <div class="proyecto-item">
      <strong>${text(evidencia.nombre)}</strong>
      <span>${text(evidencia.actividad)} · ${text(evidencia.creado_por)} · ${text(evidencia.creado_en)}</span>
      <small>${text(evidencia.comentario)}</small>
    </div>
  `)

  document.getElementById("proyectoHistorial").innerHTML = list(data.historial, item => `
    <div class="proyecto-item">
      <strong>${item.creado_en}</strong>
      <span>${Object.keys(item.cambios).join(", ")}</span>
    </div>
  `)
}
