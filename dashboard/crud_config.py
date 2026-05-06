from .models import (
    Actividad,
    Asignacion,
    Colaborador,
    CuentaCobro,
    Modulo,
    Obligacion,
    Procedimiento,
    Proyecto,
    Rol,
)


TABLA_META = {
    "colaborador": {
        "modelo": Colaborador,
        "label": "Colaboradores",
        "buscar_en": ["nombre", "cedula"],
        "filtro_colaborador": False,
        "campos": [
            {"name": "nombre", "label": "Nombre completo", "type": "text", "required": True},
            {"name": "cedula", "label": "Cédula", "type": "text"},
            {"name": "procedimiento_id", "label": "Procedimiento", "type": "fk", "fk_modelo": "Procedimiento"},
            {"name": "fecha_inicio", "label": "Fecha inicio", "type": "date"},
            {"name": "fecha_fin", "label": "Fecha fin", "type": "date"},
            {"name": "honorarios", "label": "Honorarios", "type": "number"},
            {"name": "objeto", "label": "Objeto contrato", "type": "textarea"},
        ],
        "columnas_lista": ["nombre", "cedula", "procedimiento__nombre", "fecha_inicio", "fecha_fin", "honorarios"],
    },
    "obligacion": {
        "modelo": Obligacion,
        "label": "Obligaciones",
        "buscar_en": ["descripcion"],
        "filtro_colaborador": True,
        "campos": [
            {"name": "colaborador_id", "label": "Colaborador", "type": "fk", "required": True, "fk_modelo": "Colaborador"},
            {"name": "descripcion", "label": "Descripción", "type": "textarea", "required": True},
        ],
        "columnas_lista": ["colaborador__nombre", "descripcion"],
    },
    "actividad": {
        "modelo": Actividad,
        "label": "Actividades",
        "buscar_en": ["descripcion", "actividad_id"],
        "filtro_colaborador": True,
        "campos": [
            {"name": "obligacion_id", "label": "Obligación", "type": "fk", "required": True, "fk_modelo": "Obligacion"},
            {"name": "actividad_id", "label": "ID actividad", "type": "text"},
            {"name": "descripcion", "label": "Descripción", "type": "textarea", "required": True},
            {"name": "fecha_inicio", "label": "Fecha inicio", "type": "date"},
            {"name": "fecha_fin", "label": "Fecha fin", "type": "date"},
            {"name": "progreso", "label": "Progreso (%)", "type": "number"},
            {
                "name": "estado",
                "label": "Estado",
                "type": "choice",
                "opciones_fijas": [
                    {"id": "pendiente", "label": "Pendiente"},
                    {"id": "en_curso", "label": "En curso"},
                    {"id": "completada", "label": "Completada"},
                ],
            },
            {"name": "orden", "label": "Orden", "type": "number"},
        ],
        "columnas_lista": ["obligacion__colaborador__nombre", "actividad_id", "descripcion", "estado", "progreso"],
    },
    "cuenta_cobro": {
        "modelo": CuentaCobro,
        "label": "Cuentas de cobro",
        "buscar_en": ["numero_cuenta", "estado", "colaborador__nombre"],
        "filtro_colaborador": True,
        "campos": [
            {"name": "colaborador_id", "label": "Colaborador", "type": "fk", "required": True, "fk_modelo": "Colaborador"},
            {"name": "periodo", "label": "Periodo (día 1 del mes)", "type": "date", "required": True},
            {"name": "numero_cuenta", "label": "Número cuenta", "type": "text"},
            {"name": "fecha_radicacion", "label": "Fecha radicación", "type": "date"},
            {"name": "valor_cobrado", "label": "Valor cobrado", "type": "number", "required": True},
            {
                "name": "estado",
                "label": "Estado",
                "type": "choice",
                "opciones_fijas": [
                    {"id": "borrador", "label": "Borrador"},
                    {"id": "radicada", "label": "Radicada"},
                    {"id": "aprobada", "label": "Aprobada"},
                    {"id": "pagada", "label": "Pagada"},
                    {"id": "rechazada", "label": "Rechazada"},
                ],
            },
            {"name": "observaciones", "label": "Observaciones", "type": "textarea"},
        ],
        "columnas_lista": ["colaborador__nombre", "periodo", "numero_cuenta", "valor_cobrado", "estado", "fecha_radicacion"],
    },
    "asignacion": {
        "modelo": Asignacion,
        "label": "Asignaciones",
        "buscar_en": [],
        "filtro_colaborador": False,
        "campos": [
            {"name": "colaborador_id", "label": "Colaborador", "type": "fk", "required": True, "fk_modelo": "Colaborador"},
            {"name": "rol_id", "label": "Rol", "type": "fk", "required": True, "fk_modelo": "Rol"},
            {"name": "modulo_id", "label": "Módulo", "type": "fk", "required": True, "fk_modelo": "Modulo"},
        ],
        "columnas_lista": ["colaborador__nombre", "rol__nombre", "modulo__nombre", "modulo__proyecto__nombre"],
    },
    "modulo": {
        "modelo": Modulo,
        "label": "Módulos",
        "buscar_en": ["nombre", "referente"],
        "filtro_colaborador": False,
        "campos": [
            {"name": "proyecto_id", "label": "Proyecto", "type": "fk", "required": True, "fk_modelo": "Proyecto"},
            {"name": "nombre", "label": "Nombre", "type": "text", "required": True},
            {"name": "referente", "label": "Referente", "type": "text"},
        ],
        "columnas_lista": ["nombre", "proyecto__nombre", "referente"],
    },
    "rol": {
        "modelo": Rol,
        "label": "Roles",
        "buscar_en": ["nombre"],
        "filtro_colaborador": False,
        "campos": [
            {"name": "nombre", "label": "Nombre", "type": "text", "required": True},
        ],
        "columnas_lista": ["nombre"],
    },
}


FK_MODELOS = {
    "Procedimiento": Procedimiento,
    "Colaborador": Colaborador,
    "Proyecto": Proyecto,
    "Modulo": Modulo,
    "Rol": Rol,
    "Obligacion": Obligacion,
    "Actividad": Actividad,
    "CuentaCobro": CuentaCobro,
}

