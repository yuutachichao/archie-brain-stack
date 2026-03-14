#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/archie-brain-stack}"
REPO_URL="${REPO_URL:-}"
BRANCH="${BRANCH:-main}"

if [[ -z "$REPO_URL" ]]; then
  echo "REPO_URL 未設定"
  exit 1
fi

if [[ ! -d "$APP_DIR/.git" ]]; then
  sudo mkdir -p "$APP_DIR"
  sudo chown -R "$USER":"$USER" "$APP_DIR"
  git clone -b "$BRANCH" "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git pull origin "$BRANCH"

if [[ ! -f .env ]]; then
  echo "[警告] 找不到 .env，請先在伺服器建立：$APP_DIR/.env"
  exit 1
fi

docker compose pull || true
docker compose up -d --build

echo "部署完成"
