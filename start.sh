#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="$ROOT_DIR/.runtime"
BACKEND_PID_FILE="$RUNTIME_DIR/backend.pid"
FRONTEND_PID_FILE="$RUNTIME_DIR/frontend.pid"
BACKEND_LOG_FILE="$RUNTIME_DIR/backend.log"
FRONTEND_LOG_FILE="$RUNTIME_DIR/frontend.log"

mkdir -p "$RUNTIME_DIR"

is_running() {
  local pid_file="$1"
  if [[ ! -f "$pid_file" ]]; then
    return 1
  fi
  local pid
  pid="$(cat "$pid_file" 2>/dev/null || true)"
  if [[ -z "${pid}" ]]; then
    return 1
  fi
  if kill -0 "$pid" >/dev/null 2>&1; then
    return 0
  fi
  return 1
}

if is_running "$BACKEND_PID_FILE"; then
  echo "后端已在运行，PID: $(cat "$BACKEND_PID_FILE")"
  exit 1
fi

if is_running "$FRONTEND_PID_FILE"; then
  echo "前端已在运行，PID: $(cat "$FRONTEND_PID_FILE")"
  exit 1
fi

(
  cd "$ROOT_DIR/backend"
  nohup python3 main.py >"$BACKEND_LOG_FILE" 2>&1 &
  echo $! >"$BACKEND_PID_FILE"
)

(
  cd "$ROOT_DIR/frontend"
  nohup npm run dev >"$FRONTEND_LOG_FILE" 2>&1 &
  echo $! >"$FRONTEND_PID_FILE"
)

sleep 2

if ! is_running "$BACKEND_PID_FILE"; then
  echo "后端启动失败，请检查日志: $BACKEND_LOG_FILE"
  exit 1
fi

if ! is_running "$FRONTEND_PID_FILE"; then
  echo "前端启动失败，请检查日志: $FRONTEND_LOG_FILE"
  exit 1
fi

echo "启动成功"
echo "后端: http://localhost:8000 (PID: $(cat "$BACKEND_PID_FILE"))"
echo "前端: http://localhost:5173 (PID: $(cat "$FRONTEND_PID_FILE"))"
