#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="$ROOT_DIR/.runtime"
BACKEND_PID_FILE="$RUNTIME_DIR/backend.pid"
FRONTEND_PID_FILE="$RUNTIME_DIR/frontend.pid"

stop_by_pid_file() {
  local name="$1"
  local pid_file="$2"

  if [[ ! -f "$pid_file" ]]; then
    echo "$name 未运行"
    return 0
  fi

  local pid
  pid="$(cat "$pid_file" 2>/dev/null || true)"
  if [[ -z "$pid" ]]; then
    rm -f "$pid_file"
    echo "$name PID 文件无效，已清理"
    return 0
  fi

  if ! kill -0 "$pid" >/dev/null 2>&1; then
    rm -f "$pid_file"
    echo "$name 进程不存在，已清理 PID 文件"
    return 0
  fi

  kill "$pid" >/dev/null 2>&1 || true

  for _ in {1..10}; do
    if ! kill -0 "$pid" >/dev/null 2>&1; then
      rm -f "$pid_file"
      echo "$name 已停止"
      return 0
    fi
    sleep 1
  done

  kill -9 "$pid" >/dev/null 2>&1 || true
  rm -f "$pid_file"
  echo "$name 已强制停止"
}

stop_by_port() {
  local name="$1"
  local port="$2"

  local pids
  pids="$(netstat -tlnp 2>/dev/null | grep ":$port " | grep "LISTEN" | awk '{print $7}' | cut -d'/' -f1 | sort -u || true)"
  
  if [[ -z "$pids" ]]; then
    pids="$(netstat -ano 2>/dev/null | grep -E ":(0\.)?0\.$port |:$port " | grep "LISTENING" | awk '{print $5}' | sort -u || true)"
  fi
  
  if [[ -z "$pids" ]]; then
    pids="$(ss -tlnp 2>/dev/null | grep ":$port " | grep "LISTEN" | awk '{print $6}' | cut -d'=' -f2 | cut -d',' -f1 | sort -u || true)"
  fi

  if [[ -z "$pids" ]]; then
    echo "$name (端口 $port) 未运行"
    return 0
  fi

  for pid in $pids; do
    pid="${pid//$'\r'/}"
    if [[ -n "$pid" ]] && [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" >/dev/null 2>&1; then
      echo "找到 $name 进程 (PID: $pid, 端口: $port)"
      kill "$pid" >/dev/null 2>&1 || true
      
      for _ in {1..5}; do
        if ! kill -0 "$pid" >/dev/null 2>&1; then
          echo "$name (PID: $pid) 已停止"
          break
        fi
        sleep 1
      done

      if kill -0 "$pid" >/dev/null 2>&1; then
        kill -9 "$pid" >/dev/null 2>&1 || true
        echo "$name (PID: $pid) 已强制停止"
      fi
    fi
  done
}

stop_by_pid_file "后端" "$BACKEND_PID_FILE" || true
stop_by_pid_file "前端" "$FRONTEND_PID_FILE" || true

BACKEND_PORT=8000
FRONTEND_PORT=5173

stop_by_port "后端" "$BACKEND_PORT"
stop_by_port "前端" "$FRONTEND_PORT"

echo "终止完成"
