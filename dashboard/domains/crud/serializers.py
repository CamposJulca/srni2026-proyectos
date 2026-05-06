from dashboard.crud_config import FK_MODELOS


def opciones_fk(modelo, campo_display="nombre"):
    try:
        qs = modelo.objects.all().order_by(campo_display)
        return [
            {"id": obj.pk, "label": str(getattr(obj, campo_display, None) or obj)}
            for obj in qs
        ]
    except Exception:
        return [{"id": obj.pk, "label": str(obj)} for obj in modelo.objects.all()]


def serializar_fila(obj, columnas):
    fila = {"id": obj.pk}
    for col in columnas:
        if "__" in col:
            partes = col.split("__")
            val = obj
            for parte in partes:
                val = getattr(val, parte, None)
                if val is None:
                    break
        else:
            val = getattr(obj, col, None)
        if hasattr(val, "isoformat"):
            val = val.isoformat()
        fila[col] = str(val) if val is not None else None
    return fila


def campo_meta_dict(campo):
    data = dict(campo)
    if data["type"] == "fk":
        fk_modelo = FK_MODELOS.get(data.get("fk_modelo"))
        data["opciones"] = opciones_fk(fk_modelo) if fk_modelo else []
    elif data["type"] == "choice":
        data["opciones"] = data.get("opciones_fijas", [])
    return data


def detalle_dict(obj, campos):
    datos = {"id": obj.pk}
    for campo in campos:
        val = getattr(obj, campo["name"], None)
        if hasattr(val, "isoformat"):
            val = val.isoformat()
        datos[campo["name"]] = val
    return datos
