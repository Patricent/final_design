#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

PY="${ROOT}/fd/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "未找到虚拟环境：${PY}，请先创建或激活 fd 虚拟环境。"
  exit 1
fi

echo "[1/3] 数据库迁移..."
"$PY" "${ROOT}/backend/manage.py" migrate

echo "[2/3] 启动后端 http://127.0.0.1:8000 （后台）..."
(
  cd "$ROOT"
  "$PY" backend/manage.py runserver 127.0.0.1:8000
) &
BACK_PID=$!

cleanup() {
  kill "$BACK_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "[3/3] 启动前端 http://127.0.0.1:5173 ..."
cd "${ROOT}/frontend"
npm run dev -- --host 127.0.0.1 --port 5173
