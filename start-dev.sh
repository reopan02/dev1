#!/bin/bash

echo "🚀 启动电商图片生成器 - 开发模式"
echo ""

# 检查是否在项目根目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查Python虚拟环境
if [ ! -d "backend/venv" ]; then
    echo "📦 创建Python虚拟环境..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# 检查后端依赖
if [ ! -f "backend/venv/bin/uvicorn" ]; then
    echo "📦 安装后端依赖..."
    cd backend
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
    cd ..
fi

# 检查前端依赖
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 安装前端依赖..."
    cd frontend
    npm install
    cd ..
fi

# 检查环境变量
if [ ! -f "backend/.env" ]; then
    echo "⚠️  警告: backend/.env 文件不存在"
    echo "请复制 backend/.env.example 并配置API密钥"
    exit 1
fi

echo ""
echo "✅ 环境检查完成"
echo ""
echo "启动服务..."
echo ""

# 创建日志目录
mkdir -p logs

# 启动后端
echo "🔧 启动后端服务 (http://localhost:8000)..."
cd backend
source venv/bin/activate
nohup python main.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../logs/backend.pid
deactivate
cd ..

# 等待后端启动
sleep 3

# 启动前端
echo "🎨 启动前端服务 (http://localhost:5173)..."
cd frontend
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../logs/frontend.pid
cd ..

echo ""
echo "✨ 服务已启动!"
echo ""
echo "📍 前端地址: http://localhost:5173"
echo "📍 后端地址: http://localhost:8000"
echo "📍 API文档: http://localhost:8000/docs"
echo ""
echo "📝 日志文件:"
echo "   后端: logs/backend.log"
echo "   前端: logs/frontend.log"
echo ""
echo "🔍 查看日志: tail -f logs/backend.log 或 tail -f logs/frontend.log"
echo "🛑 停止服务: ./stop-dev.sh 或 kill \$(cat logs/backend.pid logs/frontend.pid)"
echo ""
echo "✅ 服务已在后台运行，关闭终端不会影响服务"
