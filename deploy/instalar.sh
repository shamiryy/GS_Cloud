#!/usr/bin/env bash
set -euo pipefail
# Execute como root via Azure Run Command após definir o DNS real.
: "${API_DOMAIN:?Defina API_DOMAIN com o DNS público do IP Azure}"
apt-get update
apt-get install -y python3 python3-venv git caddy curl ca-certificates
id tarefas >/dev/null 2>&1 || useradd --system --home /opt/tarefas --shell /usr/sbin/nologin tarefas
if [ ! -d /opt/tarefas/.git ]; then
  git clone https://github.com/shamiryy/api-tarefas-fastapi-sqlite.git /opt/tarefas
fi
cd /opt/tarefas
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
install -d -m 700 -o tarefas -g tarefas /var/lib/tarefas
chown -R root:root /opt/tarefas
chmod -R a+rX /opt/tarefas
install -m 644 deploy/tarefas.service /etc/systemd/system/tarefas.service
printf '%s {\n reverse_proxy 127.0.0.1:8000\n}\n' "$API_DOMAIN" > /etc/caddy/Caddyfile
caddy validate --config /etc/caddy/Caddyfile
systemctl daemon-reload
systemctl enable --now tarefas caddy
systemctl reload caddy
for attempt in $(seq 1 30); do
  if curl --fail --silent http://127.0.0.1:8000/health; then break; fi
  sleep 2
done
curl --fail --silent http://127.0.0.1:8000/health
systemctl is-active tarefas caddy
