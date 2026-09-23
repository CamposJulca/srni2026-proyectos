# Despliegue del SRNI Dashboard en Analiticarni (Sinapsis)

URL: `https://sinapsis.unidadvictimas.gov.co/srni-dashboard/`

| Elemento | Valor |
|---|---|
| Servidor | Analiticarni `30.0.1.107`, usuario `rni` |
| Carpeta | `~/servers/srni-dashboard/` (`app/` código, `venv/`, `datos/` base y evidencias, `srni-dashboard.env`) |
| Servicio | `systemctl --user {status,restart} srni-dashboard` |
| Puerto | `127.0.0.1:8089` (solo local; se publica por nginx) |
| Prefijo | `SCRIPT_NAME=/srni-dashboard` en `srni-dashboard.env` |
| Logs | `journalctl --user -u srni-dashboard -f` |

## Instalar o actualizar

```bash
curl -fsSL https://raw.githubusercontent.com/CamposJulca/srni2026-proyectos/despliegue-sinapsis/deploy/instalar.sh -o /tmp/instalar_srni.sh
bash /tmp/instalar_srni.sh
```

El instalador es idempotente: clona o actualiza la rama `despliegue-sinapsis`,
instala dependencias, crea el `.env` (con `DJANGO_SECRET_KEY` aleatoria, permisos 600)
si no existe, aplica migraciones, recolecta estáticos y reinicia el servicio.

## Datos

`datos/db.sqlite3` y `datos/media/` viven fuera del código. La carpeta `data/`
del repositorio (cédulas, honorarios, clausulados) **no** se copia al servidor.

Respaldo en caliente de la base:

```bash
~/servers/srni-dashboard/venv/bin/python -c "import sqlite3; s=sqlite3.connect('$HOME/servers/srni-dashboard/datos/db.sqlite3'); d=sqlite3.connect('$HOME/servers/srni-dashboard/datos/respaldo_$(date +%F).sqlite3'); s.backup(d)"
```

## nginx

Bloque en `deploy/nginx-location.conf`, dentro del `server` de
`/etc/nginx/sites-available/sinapsis.unidadvictimas.gov.co`. Requiere `sudo`:
respaldar el archivo, pegar el bloque, `sudo nginx -t` y `sudo systemctl reload nginx`.

## Sin prefijo (desarrollo local)

Sin `SCRIPT_NAME` la aplicación funciona en la raíz como antes
(`python manage.py runserver`).
