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
"1. Analizar y apoyar la orientación de nuevos módulos o herramientas que faciliten la generación, procesamiento y disposición de las soluciones de software y de los procedimientos informáticos existentes que soporten la automatización del Registro Único de Víctimas y de los aplicativos de la Red Nacional de Información",  
"2. Gestionar el ciclo de vida de software especialmente para la identificación, levantamiento, análisis, diseño y documentación de los requerimientos para la construcción y/ o modificación del portal de aplicaciones VIVANTO, el nuevo RUV o de algún sistema de información misional de la entidad",  
"3. Orientar técnica y conceptualmente a los equipos de la Subdirección Red Nacional de Información, en materia de desarrollo de software y automatización de los procesos de la UARIV", 
"4. Efectuar mantenimiento evolutivo y correctivo del aplicativo VIVANTO, sus aplicaciones, el nuevo RUV u otro sistema de información misional",  
"5. Actualizar o construir el documento de especificaciones, diagramas de arquitectura, manual técnico y código fuente de las herramientas tecnológicas diseñadas y/o administradas por la subdirección Red Nacional de Información", 
"6. Brindar soporte a nivel técnico para resolver incidentes de los sistemas de información", 
"7. Realizar el desarrollo y/o actualización de los nuevos módulos/o aplicaciones que requieran las herramientas tecnológicas administradas por la Subdirección Red Nacional de Información según metodologías definidas",  
"8. Asistir a las reuniones programadas para tratar temas relacionados con el desarrollo del objeto del contrato y las demás que sean requeridas por el supervisor",
"9. Utilizar e implementar las herramientas suministradas por la unidad para ciclo de vida del software y control del código fuente y documentación, de conformidad a las metodologías definidas por la Oficina de Tecnologías de la Información",  
"10. Entregar al supervisor del contrato todos los documentos, scripts, informes, manuales, procedimientos, instructivos y otros desarrollados en cumplimiento del objeto contractual de acuerdo con los lineamientos de gestión documental",  
"11. Cargar mensualmente en la ruta dispuesta por la Subdirección todos los documentos que den cuenta de la gestión realizada en el contrato", 
"12. Cumplir las demás actividades relacionadas con el objeto del contrato que sean acordadas con el supervisor."
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
"1. Realizar el desarrollo e implementación de las herramientas tecnológicas que se definan al interior de la Subdirección Red Nacional de Información así como el desarrollo de funcionalidades para Ruv temporal, Nuevo Ruv y SIRAV",
"2. Brindar el soporte técnico y mantenimiento de software de las diferentes aplicaciones tecnológicas (Ruv temporal, SIRAV, SIPOD, etc) de la Subdirección Red Nacional de Información", 
"3. Realizar la documentación técnica del funcionamiento y administración de las diferentes soluciones tecnológicas y procedimientos implementados en la Subdirección Red Nacional de Información (Ruv temporal, SIRAV, SIPOD, etc) ", 
"4. Implementar, documentar e integrar objetos de base de datos, según se requiera para la automatización de las herramientas tecnológicas del Registro Único de Víctimas y las soluciones tecnológicas administradas por la Subdirección Red Nacional de Información", 
"5. Realizar la planeación, elaboración y análisis de los nuevos reportes para las diferentes herramientas que requiera la Unidad para las Victimas",  
"6. Gestionar los requerimientos registrados en Aranda en términos de solución de incidencias o requerimientos a las soluciones tecnológicas administradas por la Subdirección Red Nacional de Información",  
"7. Asistir a las reuniones programadas para tratar temas relacionados con el desarrollo del objeto del contrato y las demás que sean requeridas por el supervisor", 
"8. Utilizar e implementar las herramientas suministradas por la unidad para ciclo de vida del software y control del código fuente y documentación, de conformidad a las metodologías definidas por la Oficina de Tecnologías de la Información",
"9. Entregar al supervisor del contrato todos los documentos, scripts, informes, manuales, procedimientos, instructivos y otros desarrollados en cumplimiento del objeto contractual de acuerdo con los lineamientos de gestión documental", 
"10. Cargar mensualmente en la ruta dispuesta por la Subdirección todos los documentos que den cuenta de la gestión realizada en el contrato", 
"11. Cumplir las demás actividades relacionadas con el objeto del contrato que sean acordadas con el supervisor"
],

"Daniel Felipe Avendaño Puin": [
"1. Desarrollar y poner en marcha los elementos de software web, móvil o de escritorio considerados de alta complejidad, siguiendo los requisitos especificados y la arquitectura de referencia establecida",  "2. Elaborar y ejecutar los planes, suite y casos de pruebas para los desarrollos realizados en los distintos ambientes de la Entidad, asegurando toda la documentación asociada en esta etapa del ciclo de vida del desarrollo", 
"3. Implementar, documentar y construir objetos de base de datos, según se requiera para la automatización de las herramientas tecnológicas del Registro Único de Víctimas y las soluciones tecnológicas administradas por la Subdirección Red Nacional de Información",  
"4. Gestionar los requerimientos registrados en Aranda en términos de solución de incidencias o requerimientos a las soluciones tecnológicas administradas por la Subdirección Red Nacional de Información",  
"5. Elaborar la documentación técnica de las soluciones tecnológicas desarrolladas para la subdirección Red Nacional de Información",  
"6. Realizar el desarrollo y/o actualización de los nuevos módulos/o aplicaciones que requieran las herramientas tecnológicas administradas por la Subdirección Red Nacional de Información según metodologías definidas",  
"7. Asistir a las reuniones programadas para tratar temas relacionados con el desarrollo del objeto del contrato y las demás que sean requeridas por el supervisor", 
"8. Utilizar e implementar las herramientas suministradas por la unidad para ciclo de vida del software y control del código fuente y documentación, de conformidad a las metodologías definidas por la Oficina de Tecnologías de la Información", 
"9. Entregar al supervisor del contrato todos los documentos, scripts, informes, manuales, procedimientos, instructivos y otros desarrollados en cumplimiento del objeto contractual de acuerdo con los lineamientos de gestión documental", 
"10. Cargar mensualmente en la ruta dispuesta por la Subdirección todos los documentos que den cuenta de la gestión realizada en el contrato",  
"11. Cumplir las demás actividades relacionadas con el objeto del contrato que sean acordadas con el supervisor"
],

"David Alonso Ladino Medina": [
"1. Desarrollar los objetos de base de datos para la implementación de nuevos módulos, aplicaciones o servicios web que se requieran para las herramientas tecnológicas administradas por la Subdirección Red Nacional de Información, específicamente en el proyecto Nuevo RUV", 
"2. Construir y optimizar las aplicaciones, módulos o servicios web para el adecuado funcionamiento del Modelo Integrado administrado por la Subdirección Red Nacional de información",  
"3. Diseñar, desarrollar y disponer esquemas de bases de datos estándares para almacenar y gestionar la información del aplicativo Vivanto, Nuevo RUV y las diferentes soluciones tecnológicas de la Subdirección Red Nacional de Información",  
"4. Proveer soporte continuo y mantenimiento a las aplicaciones que interactúan con las bases de datos, solucionando errores, asegurando la disponibilidad y actualizaciones de información", 
"5. Brindar asistencia técnica en la resolución de problemas y dudas relacionadas con el uso y la administración de las bases de datos y las aplicaciones asociadas",  
"6. Implementar y realizar mejoras continuas en los procesos de gestión de bases de datos, asegurando que se mantengan actualizados y optimizados a medida que crecen las necesidades", 
"7. Asistir a las reuniones programadas para tratar temas relacionados con el desarrollo del objeto del contrato y las demás que sean requeridas por el supervisor", 
"8. Utilizar las herramientas suministradas por la unidad para ciclo de vida del software y control del código fuente y Documentación, de conformidad a las metodologías definidas por la Oficina de Tecnologías de la Información",
"9. Entregar al supervisor del contrato todos los documentos, scripts, informes, manuales, procedimientos, instructivos y otros desarrollados en cumplimiento del objeto contractual de acuerdo con los lineamientos de gestión documental",  
"10. Cargar mensualmente en la ruta dispuesta por la Subdirección todos los documentos que den cuenta de la gestión realizada en el contrato",  
"11. Cumplir las demás actividades relacionadas con el objeto del contrato que sean acordadas con el supervisor"
],

"Diego Fernando Orjuela Vinchira": [
"1. Apoyar el desarrollo de soluciones tecnológicas que resuelvan las necesidades de información de las diferentes estrategias misionales de la Unidad", 
"2. Efectuar el soporte técnico y mantenimiento de software de las aplicaciones tecnológicas de la Subdirección Red Nacional de Información", 
"3. Diseñar e implementar estándares gráficos de estilo para implementación transversal en las diferentes soluciones tecnológicas administradas por la Subdirección Red Nacional de Información",  
"4. Realizar la documentación técnica del funcionamiento y administración de las diferentes soluciones tecnológicas y procedimientos implementados en la Red Nacional de Información", 
"5. Implementar, documentar e integrar objetos de base de datos, según se requiera para la automatización de las herramientas tecnológicas del Registro Único de Víctimas y las soluciones tecnológicas administradas por la Subdirección Red Nacional de Información",  
"6. Gestionar los requerimientos registrados en Aranda en términos de solución de incidencias o requerimientos a las soluciones tecnológicas administradas por la Subdirección Red Nacional de Información", 
"7. Asistir a las reuniones programadas para tratar temas relacionados con el desarrollo del objeto del contrato y las demás que sean requeridas por el supervisor",  
"8. Utilizar e implementar las herramientas suministradas por la unidad para ciclo de vida del software y control del código fuente y documentación, de conformidad a las metodologías definidas por la Oficina de Tecnologías de la Información",  
"9. Entregar al supervisor del contrato todos los documentos, scripts, informes, manuales, procedimientos, instructivos y otros desarrollados en cumplimiento del objeto contractual de acuerdo con los lineamientos de gestión documental", 
"10. Cargar mensualmente en la ruta dispuesta por la Subdirección todos los documentos que den cuenta de la gestión realizada en el contrato",  
"11. Cumplir las demás actividades relacionadas con el objeto del contrato que sean acordadas con el supervisor"
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
"1. Supervisar el rendimiento de las bases de datos, identificando cuellos de botella o problemas de rendimiento y tomando medidas correctivas en articulación con la Oficina de Tecnologías, para el funcionamiento óptimo de las soluciones tecnológicas administradas por la Subdirección Red Nacional de Información",  
"2. Realizar el diseño, desarrollo e implementación Back end de las bases de datos y de los servicios WEB en las soluciones tecnológicas que se requieran para su correcto funcionamiento",  
"3. Implementar y documentar mejoras de los objetos de BD para optimizar el rendimiento o respuesta de las soluciones tecnológicas",  "4. Realizar la parametrización necesaria para la integración y despliegue de las soluciones tecnológicas del portal Vivanto tanto en ambiente de pruebas como en producción",  
"5. Realizar la parametrización de niveles de acceso, políticas, roles y perfiles de las diferentes soluciones tecnológicas administradas por la Subdirección Red Nacional de Información",  
"6. Acompañar los ejercicios de despliegue de soluciones tecnológicas en articulación con la Oficina de Tecnologías en términos de administración y publicación de servidores de aplicación",
"7. Gestionar los requerimientos registrados en Aranda en términos de solución de incidencias o requerimientos a las soluciones tecnológicas administradas por la Subdirección Red Nacional de Información",  
"8. Procesar, implementar y documentar medidas de seguridad para proteger la integridad, confiabilidad y confidencialidad de los datos utilizados para el procedimiento de Instrumentalización, de acuerdo con su naturaleza, calidad y contexto",
"9. Hacer la documentación de las soluciones tecnológicas generadas en la Subdirección Red Nacional de Información para el procedimiento de Instrumentalización de acuerdo con la metodología de Software seleccionada", 
"10. Asistir a las reuniones programadas para tratar temas relacionados con el desarrollo del objeto del contrato y las demás que sean requeridas por el supervisor",  
"11. Utilizar e implementar las herramientas suministradas por la unidad para el ciclo de vida del software y control del código fuente y documentación, de conformidad a las metodologías definidas por la Oficina de Tecnologías de la Información", 
"12. Entregar al supervisor del contrato todos los documentos, scripts, informes, manuales, procedimientos, instructivos y otros desarrollados en cumplimiento del objeto contractual de acuerdo con los lineamientos de gestión documental",  
"13. Cargar mensualmente en la ruta dispuesta por la Subdirección todos los documentos que den cuenta de la gestión realizada en el contrato",  
"14. Cumplir las demás actividades relacionadas con el objeto del contrato que sean acordadas con el supervisor"
],

"Fabio Raul Mesa Sanabria": [
"1. Acompañar técnica, operativa y conceptualmente a la Subdirección de la Red Nacional de Información, para proponer y gestionar estrategias que contribuyan a la mejora continua del modelo integrado de fuentes de información",  
"2. Apoyar la planeación y ejecución de la migración de datos hacia el modelo integrado de fuentes de información", 
"3. Apoyar la definición, desarrollo e implementación de los procedimientos de acceso a bases de datos del modelo integrado de fuentes de información de acuerdo con las necesidades de la Unidad",  "4. Apoyar la elaboración y ejecución de una(s) propuesta(s) de mejora en las soluciones tecnológicas para la automatización del procedimiento de mediciones que estén a cargo de la Subdirección Red Nacional de Información", 
"5. Apoyar la construcción de documentos cuantitativos y cualitativos estratégicos para dar respuesta a entes de control o solicitudes internas o externas en el marco de la política pública de población víctima",  
"6. Apoyar la elaboración de documentos estratégicos de la Subdirección Red Nacional de Información", 
"7. Apoyar el diseño e implementación de las soluciones tecnológicas que genere la Subdirección Red Nacional de Información para el procedimiento de Instrumentalización",  
"8. Apoyar técnicamente los procedimientos de transformación de datos ajustados a los lineamientos de estándares y estrategias establecidas en el Gobierno de Datos", 
"9. Desarrollar e implementar soluciones tecnológicas que soporten la automatización de las mediciones y la disposición de información de las bases de datos que se requieran por las áreas de LA UNIDAD", 
"10. Realizar el procesamiento, validación, transformación y estandarización de fuentes de información, orientadas a garantizar la integración al Modelo Integrado e interoperabilidad con otros sistemas de información", 
"11. Asistir a las reuniones programadas para tratar temas relacionados con el desarrollo del objeto del contrato y las demás que sean requeridas por el supervisor", 
"12. Entregar al supervisor del contrato todos los documentos, scripts, informes, manuales, procedimientos, instructivos y otros desarrollados en cumplimiento del objeto contractual de acuerdo con los lineamientos de gestión documental", 
"13. Cargar mensualmente en la ruta dispuesta por la Subdirección todos los documentos que den cuenta de la gestión realizada en el contrato", 
"14. Utilizar e implementar las herramientas suministradas por la unidad para ciclo de vida del software y control del código fuente y documentación, de conformidad a las metodologías definidas por la Oficina de Tecnologías de la Información", 
"15. Cumplir las demás actividades relacionadas con el objeto del contrato que sean acordadas con el supervisor"
],

"Fredy Andres Mora Guerrero": [
"1. ",
"2. ",
"3. "
],

"GABRIEL DARIO VILLA ACEVEDO": [
"1. Definir, planear y estandarizar una arquitectura técnica escalable, robusta, flexible y segura acorde a las necesidades de la Subdirección Red Nacional de información considerando la integración e interoperabilidad con sistemas existentes en la Unidad para las víctimas",  
"2. Realizar la arquitectura de las diferentes integraciones al portal de aplicaciones VIVANTO",  
"3. Llevar a cabo la implementación del proyecto Nuevo RUV siguiendo las metodologías establecidas por la OTI y respetando el cronograma definido",  
"4. Construir y documentar patrones arquitectónicos como MVC (Modelo-vistacontrolador), microservicios, capas, cliente-servidor, componentes, entre otros, para los sistemas de información desarrollados por la Subdirección Red Nacional de Información",  
"5. Realizar el desarrollo y/o actualización de los nuevos módulos o aplicaciones que requieran las herramientas tecnológicas administradas por la Subdirección Red Nacional de Información según metodologías definidas",  
"6. Analizar los requerimientos y transformación de requisitos en especificaciones técnicas de las soluciones tecnológicas desarrolladas por la Subdirección Red Nacional de Información",  
"7. Apoyar en la solución de incidencias o soportes necesarios para las soluciones tecnológicas de la Subdirección Red Nacional de Información", 
"8. Hacer la documentación de las soluciones tecnológicas generadas en la Subdirección Red Nacional de Información para el procedimiento de Instrumentalización, de acuerdo con la metodología de Software seleccionada", 
"9. Asistir a las reuniones programadas para tratar temas relacionados con el desarrollo del objeto del contrato y las demás que sean requeridas por el supervisor",  
"10. Entregar al supervisor del contrato todos los documentos, scripts, informes, manuales, procedimientos, instructivos y otros desarrollados en cumplimiento del objeto contractual de acuerdo con los lineamientos de gestión documental", 
"11. Cargar mensualmente en la ruta dispuesta por la Subdirección todos los documentos que den cuenta de la gestión realizada en el contrato",  
"12. Utilizar las herramientas suministradas por la unidad para ciclo de vida del software, control del código fuente y documentación, de conformidad con las metodologías o lineamientos definidos por la Oficina de Tecnologías de la Información",
"13. Cumplir las demás actividades relacionadas con el objeto del contrato que sean acordadas con el supervisor"
],

"Ivan Camilo Cristancho Perez": [
"1. Implementar, documentar y realizar mejoras continuas en los procesos de gestión de bases de datos, asegurando que se mantengan actualizados y optimizados a medida que crecen las necesidades",
"2. Realizar la documentación técnica del funcionamiento y administración de las diferentes soluciones tecnológicas y procedimientos implementados en la Subdirección Red Nacional de Información",  
"3. Estructurar y apoyar la implementación de instrumentos para la automatización de las herramientas y soluciones tecnológicas administradas por la Subdirección Red Nacional de Información",
"4. Gestionar los requerimientos registrados en Aranda en términos de solución de incidencias o requerimientos a las soluciones tecnológicas administradas por la Subdirección Red Nacional de Información",  
"5. Asistir a las reuniones programadas para tratar temas relacionados con el desarrollo del objeto del contrato y las demás que sean requeridas por el supervisor",
"6. Cargar mensualmente en la ruta dispuesta por la Subdirección todos los documentos que den cuenta de la gestión realizada en el contrato",  "7. Cumplir las demás actividades relacionadas con el objeto del contrato que sean acordadas con el supervisor "
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

" JHOAN MANUEL RAMIREZ PIRAZAN": [
"1. 1. Diseñar y desarrollar tableros personalizados que resuman de forma visual la información clave o las necesidades de análisis para la toma de decisiones",  
"2. Escribir y documentar consultas eficientes en M lenguaje y DAX para extraer y transformar datos de manera óptima",  
"3. Generar reportes o informes interactivos y visualizaciones utilizando Power BI para presentar datos de manera efectiva",  
"4. Brindar capacitación y soporte a usuarios internos para que puedan utilizar Power BI de manera efectiva",  
"5. Automatizar procesos de actualización de datos y generación de informes para agilizar el flujo de trabajo y la entrega de información actualizada",  
"6. Brindar el soporte técnico y mantenimiento de software de los tableros administrados por la Subdirección Red Nacional de Información",  
"7. Integrar y configurar elementos de bases de datos según sea necesario para automatizar tableros en Power BI en la Subdirección de la Red Nacional de Información",  
"8. Elaborar y actualizar regularmente manuales detallados que describan el proceso operativo de migración de fuentes de datos, consultas, procedimientos y actualización de paneles",  
"9. Procesar, implementar y documentar medidas de seguridad para proteger la integridad, confiabilidad y confidencialidad de los datos utilizados para el procedimiento de Instrumentalización, de acuerdo con su naturaleza, calidad y contexto", 
"10. Asistir a las reuniones programadas para tratar temas relacionados con el desarrollo del objeto del contrato y las demás que sean requeridas por el supervisor", 
"11. Utilizar e implementar las herramientas suministradas por la unidad para el ciclo de vida del software y control del código fuente y documentación, de conformidad a las metodologías definidas por la Oficina de Tecnologías de la Información",  
"12. Entregar al supervisor del contrato todos los documentos, scripts, informes, manuales, procedimientos, instructivos y otros desarrollados en cumplimiento del objeto contractual de acuerdo con los lineamientos de gestión documental",
"13. Cargar mensualmente en la ruta dispuesta por la Subdirección todos los documentos que den cuenta de la gestión realizada en el contrato",  
"14. Cumplir las demás actividades relacionadas con el objeto del contrato que sean acordadas con el supervisor "
],


"JORGE ANDRES GONZALEZ CETINA": [
"1. Acompañar técnica, operativa y conceptualmente a la Subdirección de la Red Nacional de Información, en la orientación del procedimiento de instrumentalización de la información para la vigencia 2025",  
"2. Hacer seguimiento y generar reportes de los avances, los problemas, los riesgos identificados y las estrategias desarrolladas para mitigarlos, documentando las lecciones aprendidas y manteniendo el buen curso de los proyectos de la Subdirección, así como, evaluar sus resultados",  
"3. Monitorear la asignación de actividades y el seguimiento a compromisos y/o requerimientos realizados al equipo del proyecto ",  
"4. Gestionar la documentación de los manuales de las aplicaciones y sistemas de información, que sirvan en la generación de insumos para el procedimiento de instrumentalización de la Información de la Subdirección en concordancia con los lineamientos definidos por el sistema integrado de gestión",  
"5. Coordinar los espacios de articulación para apoyar la socialización de las herramientas tecnológicas de la SRNI a las demás dependencias de la UARIV, las entidades que conforman la Red Nacional de Información y el SNARIV",  
"6. Apoyar las actividades relacionadas con la revisión de insumos e informes, la elaboración de actas o ayudas de memoria de las reuniones en las que participe el equipo de instrumentalización de la SRNI",  
"7. Apoyar la construcción de documentos cuantitativos y cualitativos para dar respuesta a entes de control o solicitudes internas o externas en el marco de la política pública de población víctima", 
"8. Apoyar la elaboración de documentos estratégicos de la Subdirección Red Nacional de Información",
"9. Planificar el diseño e implementación de las aplicaciones que genere la Subdirección Red Nacional de Información para el procedimiento de Instrumentalización de la Información", 
"10. Acompañar técnica, operativa y conceptualmente a la Subdirección de la Red Nacional de Información, para proponer y gestionar estrategias que contribuyan a la mejora continua de las actividades que se desarrollan al interior del procedimiento de Instrumentalización de la Información",  
"11. Utilizar, administrar y disponer las herramientas suministradas por la unidad para ciclo de vida del software, control del código fuente y documentación, de conformidad con las metodologías o lineamientos definidos por la Oficina de Tecnologías de la Información", 
"12. Asistir a las reuniones programadas para tratar temas relacionados con el desarrollo del objeto del contrato y las demás que sean requeridas por el supervisor", 
"13. Entregar al supervisor del contrato todos los documentos, scripts, informes, manuales, procedimientos, instructivos y otros desarrollados en cumplimiento del objeto contractual de acuerdo con los lineamientos de gestión documental", 
"14. Cargar mensualmente en la ruta dispuesta por la Subdirección todos los documentos que den cuenta de la gestión realizada en el contrato", 
"15. Cumplir las demás actividades relacionadas con el objeto del contrato que sean acordadas con el supervisor"
],

"Jorge Tomas Barreiro": [
"1. Actualizar los módulos de acuerdo con el Ciclo de Vida del Desarrollo de Software (SDLC) para las soluciones tecnológicas que generó la Subdirección Red Nacional de Información en el procedimiento de Instrumentalización",  
"2. Procesar, implementar y documentar medidas de seguridad para proteger la integridad, confiabilidad y confidencialidad de los datos utilizados para el procedimiento de Instrumentalización, de acuerdo con su naturaleza, calidad y contexto",  
"3. Realizar el procesamiento, validación, transformación y estandarización de fuentes de información, orientadas a garantizar la integración al Modelo Integrado e interoperabilidad con otros sistemas de información",  
"4. Realizar las actividades de actualización de módulos, documentación técnica y soporte para las aplicaciones y soluciones tecnológicas SRNI", 
"5. Crear, diseñar y documentar la estructura de la solución tecnológica planteada para garantizar la eficiencia, integridad y seguridad de la información", 
"6. Realizar el desarrollo y/o actualización de los nuevos módulos/o aplicaciones que requieran las herramientas tecnológicas administradas por la Subdirección Red Nacional de Información según metodologías definidas",  
"7. Asistir a las reuniones programadas para tratar temas relacionados con el desarrollo del objeto del contrato y las demás que sean requeridas por el supervisor", 
"8. Utilizar e implementar las herramientas suministradas por la unidad para ciclo de vida del software y control del código fuente y documentación, de conformidad a las metodologías definidas por la Oficina de Tecnologías de la Información", 
"9. Cargar mensualmente en la ruta dispuesta por la Subdirección todos los documentos que den cuenta de la gestión realizada en el contrato",  "10. Cumplir las demás actividades relacionadas con el objeto del contrato que sean acordadas con el supervisor"
],

"Julian Alberto Siachoque Granados": [
"1. Apoyar la creación, diseño y documentación de la estructura de bases de datos para garantizar la eficiencia, integridad y seguridad de los datos utilizados en los procedimientos de instrumentalización de la información y análisis", 
"2. Apoyar la creación y documentación de modelos de datos que reflejen con precisión la información que se desea analizar, considerando las relaciones entre los diferentes conjuntos de datos", 
"3. Realizar y documentar consultas SQL eficientes y optimizarlas para mejorar el rendimiento en la extracción y análisis de datos", 
"4. Apoyar el desarrollo de procesos ETL (Extract, Transform, Load) para la extracción, transformación y carga de datos desde diferentes fuentes hacia el modelo integrado y la base de datos de análisis que permita el análisis eficiente de grandes volúmenes de datos", 
"5. Apoyar la implementación de la estrategia de calidad de datos para garantizar la confidencialidad de la información",  
"6. Brindar soporte técnico, actualización y mantenimiento de software de los reportes de Power BI (tableros de control) y las diferentes aplicaciones tecnológicas de la Subdirección Red Nacional de Información",  
"7. Realizar informes de cifras de víctimas a nivel nacional y víctimas en el exterior a diferentes misionales",  
"8. Procesar, implementar y documentar medidas de seguridad para proteger la integridad, confiabilidad y confidencialidad de los datos utilizados para el procedimiento de Instrumentalización, de acuerdo con su naturaleza, calidad y contexto", 
"9. Procesar, implementar y documentar medidas de seguridad para proteger la integridad, confiabilidad y confidencialidad de los datos utilizados para el procedimiento de Instrumentalización, de acuerdo con su naturaleza, calidad y contexto", 
"10. Utilizar e implementar las herramientas suministradas por la unidad para ciclo de vida del software y control del código fuente y documentación, de conformidad a las metodologías definidas por la Oficina de Tecnologías de la Información", 
"11. Asistir a las reuniones programadas para tratar temas relacionados con el desarrollo del objeto del contrato y las demás que sean requeridas por el supervisor",  
"12. Entregar al supervisor del contrato todos los documentos, scripts, informes, manuales, procedimientos, instructivos y otros desarrollados en cumplimiento del objeto contractual de acuerdo con los lineamientos de gestión documental",  
"13. Cargar mensualmente en la ruta dispuesta por la Subdirección todos los documentos que den cuenta de la gestión realizada en el contrato",  
"14. Cumplir las demás actividades relacionadas con el objeto del contrato que sean acordadas con el supervisor"
],

"Luis Miguel Ramirez": [
"1. ",
"2. ",
"3. "
],

"Luis Silvestre Supelano Beltran": [
"1. Apoyar el Ciclo de Vida del Desarrollo de Software (SDLC) para las soluciones tecnológicas que genere la Subdirección Red Nacional de Información en el procedimiento de Instrumentalización", 
"2. Hacer la documentación de las soluciones tecnológicas generadas en la Subdirección Red Nacional de Información para el procedimiento de Instrumentalización de acuerdo con la metodología de Software seleccionada", 
"3. Apoyar en el desarrollo, mantenimiento, documentación y soporte de las soluciones de software de los sistemas de información en el procedimiento de Instrumentalización", 
"4. Asistir a las reuniones programadas para tratar temas relacionados con el desarrollo del objeto del contrato y las demás que sean requeridas por el supervisor", 
"5. Utilizar e implementar las herramientas suministradas por la unidad para ciclo de vida del software y control del código fuente y documentación, de conformidad a las metodologías definidas por la Oficina de Tecnologías de la Información", 
"6. Cargar mensualmente en la ruta dispuesta por la Subdirección todos los documentos que den cuenta de la gestión realizada en el contrato",  "7. Cumplir las demás actividades relacionadas con el objeto del contrato que sean acordadas con el supervisor"
],


" MARTHA CAROLINA FLOREZ PÉREZ ": [
"1. Hacer un diagnóstico de las fuentes de información internas como externas con el fin de mejorar técnicamente el cálculo de las mediciones a cargo de la SRNI (Í SSV, IGED, MTPI, Indicadores de Riesgo de Mujeres, MITI, SM étnico, mercado laboral, IRV) ",
"2. Preparar las diferentes fuentes de información que se reciban en el proceso de articulación interinstitucional atendiendo los instrumentos de calidad establecidos, previo a la integración en el modelo ",
"3. Apoyar los procesos de integración de datos al modelo integrado tanto en ejecución de ETLS como la elaboración de propuestas de mejora ",
"4. Calcular una muestra aleatoria y representativa para la realización de estrategia de caracterización en Buenaventura  ",
"5. Apoyar la implementación de la estrategia de calidad de datos para el procedimiento de instrumentalización de la información ",
"6. Asistir a las reuniones programadas para tratar temas relacionados con el desarrollo del objeto del contrato y las demás que sean requeridas por el supervisor ",
"7. Entregar al supervisor del contrato todos los documentos, scripts, informes, manuales, procedimientos, instructivos y otros desarrollados en cumplimiento del objeto contractual de acuerdo con los lineamientos de gestión documental",
"8. Cargar mensualmente en la ruta dispuesta por la Subdirección todos los documentos que den cuenta de la gestión realizada en el contrato ",
"9. Cumplir las demás actividades relacionadas con el objeto del contrato que sean acordadas con el supervisor "
],

"OLAF VLADIMIR SANTANILLA SAAVEDRA ": [
"1. Proponer y diseñar soluciones tecnológicas administradas por la Subdirección Red Nacional de Información que soporten la automatización de procesos misionales", 
"2. Realizar la construcción de la diferente documentación de las soluciones tecnológicas administradas por la subdirección Red Nacional de Información",  
"3. Brindar soporte nivel técnico para resolver incidentes de los sistemas de información",  
"4. Realizar el desarrollo y/o actualización de los nuevos módulos y/o aplicaciones que requieran las herramientas tecnológicas administradas por la Subdirección Red Nacional de Información según metodologías definidas",  
"5. Implementar, documentar e integrar objetos de base de datos, según se requiera para la automatización de las herramientas tecnológicas del Registro Único de Víctimas y las soluciones tecnológicas administradas por la Subdirección Red Nacional de Información",  
"6. Gestionar los requerimientos registrados en Aranda en términos de solución de incidencias o requerimientos a las soluciones tecnológicas administradas por la Subdirección Red Nacional de Información",  
"7. Hacer la documentación de las soluciones tecnológicas generadas en la Subdirección Red Nacional de Información para el procedimiento de Instrumentalización de acuerdo con la metodología de Software seleccionada", 
"8. Asistir a las reuniones programadas para tratar temas relacionados con el desarrollo del objeto del contrato y las demás que sean requeridas por el supervisor",  
"9. Utilizar e implementar las herramientas suministradas por la unidad para ciclo de vida del software y control del código fuente y documentación, de conformidad a las metodologías definidas por la Oficina de Tecnologías de la Información",  
"10. Entregar al supervisor del contrato todos los documentos, scripts, informes, manuales, procedimientos, instructivos y otros desarrollados en cumplimiento del objeto contractual de acuerdo con los lineamientos de gestión documental",  
"11.Cargar mensualmente en la ruta dispuesta por la Subdirección todos los documentos que den cuenta de la gestión realizada en el contrato",  "12.Cumplir las demás actividades relacionadas con el objeto del contrato que sean acordadas con el supervisor"
],


"Yovan Alirio Solano Florez": [
"1. Apoyar actividades de desarrollo, mantenimiento, documentación y soporte de las soluciones tecnológicas y aplicativos móviles", 
"2. Realizar la captura, el procesamiento, la transformación y la gestión de calidad de datos de las fuentes recibidas por la entidad en el desarrollo de las mediciones para las soluciones tecnológicas y aplicativos móviles",  
"3. Procesar, implementar y documentar medidas de seguridad para proteger la integridad, confiabilidad y confidencialidad de los datos utilizados para el procedimiento de Instrumentalización, de acuerdo con su naturaleza, calidad y contexto en soluciones tecnológicas y aplicativos móviles",  
"4. Realizar el diseño e implementación de las soluciones tecnológicas y aplicativos móviles que genere la Subdirección Red Nacional de Información para el procedimiento de Instrumentalización de la Información",  
"5. Crear, diseñar y documentar la estructura de bases de datos para garantizar la eficiencia, integridad y seguridad de los datos utilizados en los procedimientos de instrumentalización de la información y análisis tecnológicas y aplicativos móviles", 
"6. Crear y documentar modelos de datos que reflejen con precisión la información que se desea analizar, considerando las relaciones entre los diferentes conjuntos de en datos en las soluciones tecnológicas y aplicativos móviles",  
"7. Asistir a las reuniones programadas para tratar temas relacionados con el desarrollo del objeto del contrato y las demás que sean requeridas por el supervisor",   
"8. Cargar mensualmente en la ruta dispuesta por la Subdirección todos los documentos que den cuenta de la gestión realizada en el contrato",  "9. Cumplir las demás actividades relacionadas con el objeto del contrato que sean acordadas con el supervisor "

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

const ordenMeses = [
"Enero","Febrero","Marzo","Abril","Mayo","Junio",
"Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
]

datos.sort((a,b)=>
ordenMeses.indexOf(a.mes) - ordenMeses.indexOf(b.mes)
)

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

options:{
responsive:true,
scales:{
y:{
beginAtZero:true,
ticks:{
stepSize:1
}
}
}
}

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