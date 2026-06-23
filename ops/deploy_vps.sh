#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/dragon-mcp-pay-agent"
REPO_URL="https://github.com/bozhouDev/dragon-mcp-pay-agent.git"
SERVICE_NAME="dragon-mcp-pay-agent"
SERVICE_PORT="8021"
NGINX_SITE="/etc/nginx/sites-enabled/aitoday"

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y python3-venv python3-pip git

mkdir -p /opt
if [ -d "${APP_DIR}/.git" ]; then
  git -C "${APP_DIR}" fetch origin main
  git -C "${APP_DIR}" reset --hard origin/main
else
  git clone "${REPO_URL}" "${APP_DIR}"
fi

cd "${APP_DIR}"
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"

cat >/etc/dragon-mcp-pay-agent.env <<ENV
DRAGON_PAYMENT_MODE=mock
ENV
chmod 600 /etc/dragon-mcp-pay-agent.env

cat >"/etc/systemd/system/${SERVICE_NAME}.service" <<SERVICE
[Unit]
Description=Dragon MCP Pay Agent A2MCP demo service
After=network.target

[Service]
Type=simple
WorkingDirectory=${APP_DIR}
EnvironmentFile=/etc/dragon-mcp-pay-agent.env
ExecStart=${APP_DIR}/.venv/bin/uvicorn apps.service.main:app --host 127.0.0.1 --port ${SERVICE_PORT}
Restart=always
RestartSec=3
User=root

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable "${SERVICE_NAME}"
systemctl restart "${SERVICE_NAME}"

python3 - <<'PY'
from pathlib import Path

site = Path("/etc/nginx/sites-enabled/aitoday")
text = site.read_text(encoding="utf-8")
marker = "    # 前端服务 - Next.js应用 (端口3000)"
block = """    # Dragon MCP Pay Agent A2MCP demo service
    location /dragon-mcp/ {
        proxy_pass http://127.0.0.1:8021/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_read_timeout 60s;
    }

"""

if "location /dragon-mcp/" not in text:
    if marker not in text:
        raise SystemExit(f"nginx insertion marker not found: {marker}")
    backup = site.with_suffix(site.suffix + ".bak-dragon")
    backup.write_text(text, encoding="utf-8")
    site.write_text(text.replace(marker, block + marker), encoding="utf-8")
PY

nginx -t
systemctl reload nginx
systemctl --no-pager --full status "${SERVICE_NAME}" | sed -n '1,18p'
curl -fsS "http://127.0.0.1:${SERVICE_PORT}/health"

