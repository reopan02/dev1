#!/bin/bash

echo "🛑 停止电商图片生成器服务..."
echo ""

# 检查PID文件是否存在
if [ ! -f "logs/backend.pid" ] && [ ! -f "logs/frontend.pid" ]; then
    echo "❌ 未找到运行中的服务"
    exit 1
fi

# 停止后端
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "🔧 停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null
        rm logs/backend.pid
    else
        echo "⚠️  后端服务未运行"
        rm logs/backend.pid 2>/dev/null
    fi
fi

# 停止前端
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "🎨 停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null
        rm logs/frontend.pid
    else
        echo "⚠️  前端服务未运行"
        rm logs/frontend.pid 2>/dev/null
    fi
fi

# 清理可能的子进程
pkill -f "uvicorn.*main:app" 2>/dev/null
pkill -f "vite" 2>/dev/null

echo ""
echo "✅ 服务已停止"
