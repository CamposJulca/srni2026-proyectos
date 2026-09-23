#!/usr/bin/env bash
# Instala o actualiza el SRNI Dashboard en Analiticarni (usuario rni, sin sudo).
# Uso:  bash instalar.sh            (desde cualquier carpeta)
# Idempotente: si ya existe, actualiza código, dependencias, migraciones y estáticos.
set -euo pipefail

BASE="$HOME/servers/srni-dashboard"
APP="$BASE/app"
VENV="$BASE/venv"
ENVF="$BASE/srni-dashboard.env"
DATOS="$BASE/datos"
REPO="${REPO:-https://github.com/CamposJulca/srni2026-proyectos.git}"
RAMA="${RAMA:-despliegue-sinapsis}"
PUERTO=8089

echo "==> Carpetas"
mkdir -p "$BASE" "$DATOS/media"
chmod 700 "$DATOS"

echo "==> Código ($RAMA)"
if [ -d "$APP/.git" ]; then
  git -C "$APP" fetch -q origin "$RAMA"
  git -C "$APP" checkout -q "$RAMA"
  git -C "$APP" pull -q --ff-only origin "$RAMA"
else
  git clone -q -b "$RAMA" "$REPO" "$APP"
fi
git -C "$APP" log -1 --format='    commit %h  %ad  %s' --date=short

echo "==> Entorno virtual y dependencias"
[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
"$VENV/bin/pip" install -q --upgrade pip
"$VENV/bin/pip" install -q -r "$APP/requirements.txt"

echo "==> Variables de entorno"
if [ ! -f "$ENVF" ]; then
  KEY=$("$VENV/bin/python" -c 'import secrets; print(secrets.token_urlsafe(50))')
  sed "s|__GENERADA_POR_INSTALAR_SH__|$KEY|" "$APP/deploy/srni-dashboard.env.example" > "$ENVF"
  echo "    creado $ENVF"
fi
chmod 600 "$ENVF"

echo "==> Migraciones y estáticos"
set -a; . "$ENVF"; set +a
cd "$APP"
"$VENV/bin/python" manage.py migrate --noinput
"$VENV/bin/python" manage.py collectstatic --noinput -v0
"$VENV/bin/python" manage.py check --deploy --fail-level ERROR

echo "==> Servicio systemd --user"
mkdir -p "$HOME/.config/systemd/user"
cp "$APP/deploy/srni-dashboard.service" "$HOME/.config/systemd/user/srni-dashboard.service"
systemctl --user daemon-reload
systemctl --user enable -q srni-dashboard.service
systemctl --user restart srni-dashboard.service
sleep 3
systemctl --user --no-pager --lines=0 status srni-dashboard.service | head -5

echo "==> Prueba local"
curl -s -o /dev/null -w "    /srni-dashboard/login/ -> HTTP %{http_code}\n" "http://127.0.0.1:$PUERTO/srni-dashboard/login/"
