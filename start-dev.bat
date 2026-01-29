@echo off
echo 🚀 启动电商图片生成器 - 开发模式
echo.

REM 检查是否在项目根目录
if not exist "backend" (
    echo ❌ 错误: 请在项目根目录运行此脚本
    exit /b 1
)
if not exist "frontend" (
    echo ❌ 错误: 请在项目根目录运行此脚本
    exit /b 1
)

REM 检查Python虚拟环境
if not exist "backend\venv" (
    echo 📦 创建Python虚拟环境...
    cd backend
    python -m venv venv
    cd ..
)

REM 检查后端依赖
if not exist "backend\venv\Scripts\uvicorn.exe" (
    echo 📦 安装后端依赖...
    cd backend
    call venv\Scripts\activate
    pip install -r requirements.txt
    call deactivate
    cd ..
)

REM 检查前端依赖
if not exist "frontend\node_modules" (
    echo 📦 安装前端依赖...
    cd frontend
    call npm install
    cd ..
)

REM 检查环境变量
if not exist "backend\.env" (
    echo ⚠️  警告: backend\.env 文件不存在
    echo 请复制 backend\.env.example 并配置API密钥
    exit /b 1
)

echo.
echo ✅ 环境检查完成
echo.
echo 启动服务...
echo.

REM 启动后端
echo 🔧 启动后端服务 (http://localhost:8000)...
cd backend
start /B cmd /c "call venv\Scripts\activate && python main.py"
cd ..

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端
echo 🎨 启动前端服务 (http://localhost:5173)...
cd frontend
start /B cmd /c "npm run dev"
cd ..

echo.
echo ✨ 服务已启动!
echo.
echo 📍 前端地址: http://localhost:5173
echo 📍 后端地址: http://localhost:8000
echo 📍 API文档: http://localhost:8000/docs
echo.
echo 按任意键停止所有服务...
pause >nul

REM 停止服务
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1
echo 🛑 服务已停止
