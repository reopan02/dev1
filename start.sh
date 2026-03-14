#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="$ROOT_DIR/.runtime"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_VENV_DIR="$BACKEND_DIR/venv"
BACKEND_PYTHON_BIN="$BACKEND_VENV_DIR/bin/python"
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
  pid="${pid//$'\r'/}"
  if [[ -z "${pid}" ]]; then
    return 1
  fi
  kill -0 "$pid" >/dev/null 2>&1
}

if is_running "$BACKEND_PID_FILE"; then
  echo "后端已在运行，PID: $(cat "$BACKEND_PID_FILE")"
  exit 1
fi

if is_running "$FRONTEND_PID_FILE"; then
  echo "前端已在运行，PID: $(cat "$FRONTEND_PID_FILE")"
  exit 1
fi

echo "准备后端虚拟环境..."
if [[ ! -x "$BACKEND_PYTHON_BIN" ]]; then
  (cd "$BACKEND_DIR" && python3 -m venv venv)
fi

echo "安装后端依赖..."
(
  cd "$BACKEND_DIR"
  "$BACKEND_PYTHON_BIN" -m ensurepip --upgrade >/dev/null 2>&1 || true
  "$BACKEND_PYTHON_BIN" -m pip install --upgrade pip >/dev/null
  "$BACKEND_PYTHON_BIN" -m pip install -r requirements.txt
)

echo "安装前端依赖..."
(cd "$FRONTEND_DIR" && npm install)

echo "启动后端..."
(
  cd "$BACKEND_DIR"
  nohup "$BACKEND_PYTHON_BIN" -m uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}" >"$BACKEND_LOG_FILE" 2>&1 &
  echo $! >"$BACKEND_PID_FILE"
)

echo "启动前端..."
(
  cd "$FRONTEND_DIR"
  nohup npm run dev >"$FRONTEND_LOG_FILE" 2>&1 &
  echo $! >"$FRONTEND_PID_FILE"
)

for _ in {1..6}; do
  sleep 1
  if ! is_running "$BACKEND_PID_FILE"; then
    break
  fi
done

if ! is_running "$BACKEND_PID_FILE"; then
  rm -f "$BACKEND_PID_FILE" "$FRONTEND_PID_FILE"
  echo "后端启动失败，请检查日志: $BACKEND_LOG_FILE"
  exit 1
fi

if ! is_running "$FRONTEND_PID_FILE"; then
  if is_running "$BACKEND_PID_FILE"; then
    kill "$(cat "$BACKEND_PID_FILE")" >/dev/null 2>&1 || true
  fi
  rm -f "$BACKEND_PID_FILE" "$FRONTEND_PID_FILE"
  echo "前端启动失败，请检查日志: $FRONTEND_LOG_FILE"
  exit 1
fi

echo "服务已启动"
echo "后端: http://localhost:8000 (PID: $(cat "$BACKEND_PID_FILE"))"
echo "前端: http://localhost:5173 (PID: $(cat "$FRONTEND_PID_FILE"))"
