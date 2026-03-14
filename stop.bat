@echo off
setlocal EnableExtensions

set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"

set "RUNTIME_DIR=%ROOT_DIR%\.runtime"
set "BACKEND_PID_FILE=%RUNTIME_DIR%\backend.pid"
set "FRONTEND_PID_FILE=%RUNTIME_DIR%\frontend.pid"

call :StopByPidFile "backend" "%BACKEND_PID_FILE%"
call :StopByPidFile "frontend" "%FRONTEND_PID_FILE%"

echo stop completed
exit /b 0

:StopByPidFile
set "PROC_NAME=%~1"
set "PID_FILE=%~2"

if not exist "%PID_FILE%" (
  echo %PROC_NAME% not running
  exit /b 0
)

set "PROC_PID="
for /f "usebackq delims=" %%p in ("%PID_FILE%") do set "PROC_PID=%%p"
if "%PROC_PID%"=="" (
  del /q "%PID_FILE%" >nul 2>&1
  echo %PROC_NAME% invalid pid file removed
  exit /b 0
)

powershell -NoProfile -Command "if(Get-Process -Id %PROC_PID% -ErrorAction SilentlyContinue){exit 0}else{exit 1}" >nul 2>&1
if not %errorlevel%==0 (
  del /q "%PID_FILE%" >nul 2>&1
  echo %PROC_NAME% process not found pid file removed
  exit /b 0
)

powershell -NoProfile -Command "Stop-Process -Id %PROC_PID% -ErrorAction SilentlyContinue" >nul 2>&1
timeout /t 1 /nobreak >nul
powershell -NoProfile -Command "if(Get-Process -Id %PROC_PID% -ErrorAction SilentlyContinue){Stop-Process -Id %PROC_PID% -Force -ErrorAction SilentlyContinue}" >nul 2>&1

del /q "%PID_FILE%" >nul 2>&1
echo %PROC_NAME% stopped
exit /b 0
