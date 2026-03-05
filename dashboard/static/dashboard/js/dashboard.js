let chartPersonas
let chartRoles
let chartModulos
let chartMes

/* =====================================================
OBLIGACIONES POR COLABORADOR
Aquí puedes completar las obligaciones específicas
===================================================== */

const obligaciones = {

"Alexander Enrique Hernandez Maturana": [
"1. ",
"2. ",
"3. "
],

"Andres Camilo Rodriguez": [
"1. ",
"2. ",
"3. "
],

"Angela Lorena Rojas Contreras": [
"1. ",
"2. ",
"3. "
],

"Augusto Silva Velandia": [
"1. ",
"2. ",
"3. "
],

"Cristhiam Daniel Campos Julca": [
"1. ",
"2. ",
"3. "
],

"Cristian Alejandro Neira Lopez": [
"1. ",
"2. ",
"3. "
],

"Daniel Felipe Avendaño Puin": [
"1. ",
"2. ",
"3. "
],

"David Alonso Ladino Medina": [
"1. ",
"2. ",
"3. "
],

"Diego Fernando Orjuela Vinchira": [
"1. ",
"2. ",
"3. "
],

"Diego Mauricio Veloza Martinez": [
"1. ",
"2. ",
"3. "
],

"Diego Sáenz": [
"1. ",
"2. ",
"3. "
],

"Edwin Alonso Villalobos Munoz": [
"1. ",
"2. ",
"3. "
],

"Fabio Raul Mesa Sanabria": [
"1. ",
"2. ",
"3. "
],

"Fredy Andres Mora Guerrero": [
"1. ",
"2. ",
"3. "
],

"Gabriel Dario Villa Acevedo": [
"1. ",
"2. ",
"3. "
],

"Ivan Camilo Cristancho Perez": [
"1. ",
"2. ",
"3. "
],

"Ivan Gabriel Corredor Castillo": [
"1. ",
"2. ",
"3. "
],

"JESUS EDISSON MURCIA RODRIGUEZ": [
"1. ",
"2. ",
"3. "
],

"Jhoan Manuel Ramirez Pirazan": [
"1. ",
"2. ",
"3. "
],

"Jorge Andres Gonzalez Cetina": [
"1. ",
"2. ",
"3. "
],

"Jorge Tomas Barreiro": [
"1. ",
"2. ",
"3. "
],

"Julian Alberto Siachoque Granados": [
"1. ",
"2. ",
"3. "
],

"Luis Miguel Ramirez": [
"1. ",
"2. ",
"3. "
],

"Luis Silvestre Supelano Beltran": [
"1. ",
"2. ",
"3. "
],

"Martha Carolina Florez Perez": [
"1. ",
"2. ",
"3. "
],

"Olaf Vladimir Santanilla Saavedra": [
"1. ",
"2. ",
"3. "
],

"Yovan Alirio Solano Florez": [
"1. ",
"2. ",
"3. "
]

}


function cargarDashboard(){

let persona = document.getElementById("personaFiltro").value
let rol = document.getElementById("rolFiltro").value
let proyecto = document.getElementById("proyectoFiltro").value


fetch(`/api/dashboard/?persona=${persona}&rol=${rol}&proyecto=${proyecto}`)
.then(response => response.json())
.then(data => {

actualizarKPIs(data.kpis)

graficoPersonas(data.proyectos_persona)
graficoRoles(data.roles_persona)
graficoModulos(data.modulos_proyecto)
graficoMes(data.compromisos_mes)

})

}


function actualizarKPIs(kpis){

document.getElementById("kpiProyectos").innerText = kpis.proyectos
document.getElementById("kpiModulos").innerText = kpis.modulos
document.getElementById("kpiPersonas").innerText = kpis.personas
document.getElementById("kpiAsignaciones").innerText = kpis.asignaciones

}


/* =========================
GRAFICO PERSONAS
========================= */

function graficoPersonas(datos){

datos.sort((a,b)=>
a.persona__nombre.localeCompare(b.persona__nombre)
)

let visibles = datos.slice(0,10)

let labels = visibles.map(x => x.persona__nombre)
let valores = visibles.map(x => x.total)

let canvas = document.getElementById("graficoPersonas")

if(chartPersonas){ chartPersonas.destroy() }

chartPersonas = new Chart(canvas,{

type:"bar",

data:{
labels:labels,
datasets:[{
label:"Proyectos",
data:valores,
backgroundColor:"#4e79a7"
}]
},

options:{
indexAxis:"y",
responsive:true,
maintainAspectRatio:false,
plugins:{
legend:{display:false}
}
}

})

canvas.onclick = function(evt){

const points = chartPersonas.getElementsAtEventForMode(
evt,
'nearest',
{ intersect:true },
true
)

if(points.length){

let index = points[0].index
let persona = labels[index]

abrirModal(persona)

}

}

}


/* =========================
GRAFICO ROLES
========================= */

function graficoRoles(datos){

let labels = datos.map(x => x.rol__nombre)
let valores = datos.map(x => x.total)

if(chartRoles){ chartRoles.destroy() }

chartRoles = new Chart(

document.getElementById("graficoRoles"),

{
type:"pie",

data:{
labels:labels,
datasets:[{
data:valores
}]
},
options:{responsive:true}

})

}


/* =========================
GRAFICO MODULOS
========================= */

function graficoModulos(datos){

let labels = datos.map(x => x.proyecto__nombre)
let valores = datos.map(x => x.total)

if(chartModulos){ chartModulos.destroy() }

chartModulos = new Chart(

document.getElementById("graficoModulos"),

{
type:"bar",

data:{
labels:labels,
datasets:[{
label:"Módulos",
data:valores,
backgroundColor:"#59a14f"
}]
},
options:{responsive:true}

})

}


/* =========================
GRAFICO MESES
========================= */

function graficoMes(datos){

let labels = datos.map(x => x.mes)
let valores = datos.map(x => x.total)

if(chartMes){ chartMes.destroy() }

chartMes = new Chart(

document.getElementById("graficoMes"),

{
type:"line",

data:{
labels:labels,
datasets:[{
label:"Compromisos",
data:valores,
borderColor:"#f28e2b",
fill:false
}]
},
options:{responsive:true}

})

}


/* =========================
MODAL PERSONA
========================= */

function abrirModal(nombre){

let modal = document.getElementById("modalPersona")

document.getElementById("modalNombre").innerText = nombre

let contenido = ""

if(obligaciones[nombre]){

contenido = "<ol>"

obligaciones[nombre].forEach(function(item){

contenido += `<li>${item}</li>`

})

contenido += "</ol>"

}else{

contenido = "No hay obligaciones registradas para este colaborador."

}

document.getElementById("modalTexto").innerHTML = contenido

modal.style.display="flex"

}


document.querySelector(".close").onclick=function(){

document.getElementById("modalPersona").style.display="none"

}


window.onclick=function(event){

let modal = document.getElementById("modalPersona")

if(event.target==modal){

modal.style.display="none"

}

}


document.addEventListener("DOMContentLoaded", function(){

document.getElementById("personaFiltro").addEventListener("change", cargarDashboard)
document.getElementById("rolFiltro").addEventListener("change", cargarDashboard)
document.getElementById("proyectoFiltro").addEventListener("change", cargarDashboard)

cargarDashboard()

})