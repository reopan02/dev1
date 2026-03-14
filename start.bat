@echo off
setlocal EnableExtensions

set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"

set "RUNTIME_DIR=%ROOT_DIR%\.runtime"
set "BACKEND_PID_FILE=%RUNTIME_DIR%\backend.pid"
set "FRONTEND_PID_FILE=%RUNTIME_DIR%\frontend.pid"
set "BACKEND_LOG_FILE=%RUNTIME_DIR%\backend.log"
set "FRONTEND_LOG_FILE=%RUNTIME_DIR%\frontend.log"
set "BACKEND_ERR_FILE=%RUNTIME_DIR%\backend.err.log"
set "FRONTEND_ERR_FILE=%RUNTIME_DIR%\frontend.err.log"

if not exist "%RUNTIME_DIR%" mkdir "%RUNTIME_DIR%"

call :IsRunning "%BACKEND_PID_FILE%"
if %errorlevel%==0 (
  for /f "usebackq delims=" %%p in ("%BACKEND_PID_FILE%") do set "PID=%%p"
  echo backend already running, PID: %PID%
  exit /b 1
)

call :IsRunning "%FRONTEND_PID_FILE%"
if %errorlevel%==0 (
  for /f "usebackq delims=" %%p in ("%FRONTEND_PID_FILE%") do set "PID=%%p"
  echo frontend already running, PID: %PID%
  exit /b 1
)

powershell -NoProfile -Command "$proc = Start-Process -FilePath 'python' -ArgumentList 'main.py' -WorkingDirectory '%ROOT_DIR%\backend' -RedirectStandardOutput '%BACKEND_LOG_FILE%' -RedirectStandardError '%BACKEND_ERR_FILE%' -PassThru; Set-Content -Path '%BACKEND_PID_FILE%' -Value $proc.Id"

powershell -NoProfile -Command "$proc = Start-Process -FilePath 'npm.cmd' -ArgumentList 'run','dev' -WorkingDirectory '%ROOT_DIR%\frontend' -RedirectStandardOutput '%FRONTEND_LOG_FILE%' -RedirectStandardError '%FRONTEND_ERR_FILE%' -PassThru; Set-Content -Path '%FRONTEND_PID_FILE%' -Value $proc.Id"

timeout /t 2 /nobreak >nul

call :IsRunning "%BACKEND_PID_FILE%"
if not %errorlevel%==0 (
  call :StopByPidFile "%FRONTEND_PID_FILE%"
  call :StopByPidFile "%BACKEND_PID_FILE%"
  echo backend start failed, check log: %BACKEND_LOG_FILE%
  exit /b 1
)

call :IsRunning "%FRONTEND_PID_FILE%"
if not %errorlevel%==0 (
  call :StopByPidFile "%FRONTEND_PID_FILE%"
  call :StopByPidFile "%BACKEND_PID_FILE%"
  echo frontend start failed, check log: %FRONTEND_LOG_FILE%
  exit /b 1
)

for /f "usebackq delims=" %%p in ("%BACKEND_PID_FILE%") do set "BACKEND_PID=%%p"
for /f "usebackq delims=" %%p in ("%FRONTEND_PID_FILE%") do set "FRONTEND_PID=%%p"

echo started successfully
echo backend: http://localhost:8000 ^(PID: %BACKEND_PID%^)
echo frontend: http://localhost:5173 ^(PID: %FRONTEND_PID%^)
exit /b 0

:IsRunning
set "PID_FILE=%~1"
if not exist "%PID_FILE%" exit /b 1
set "TMP_PID="
for /f "usebackq delims=" %%p in ("%PID_FILE%") do set "TMP_PID=%%p"
if "%TMP_PID%"=="" exit /b 1
powershell -NoProfile -Command "$procIdText=Get-Content -Path '%PID_FILE%' -ErrorAction SilentlyContinue; if($procIdText -and (Get-Process -Id $procIdText -ErrorAction SilentlyContinue)){exit 0}else{exit 1}" >nul 2>&1
exit /b %errorlevel%

:StopByPidFile
set "PID_FILE=%~1"
if not exist "%PID_FILE%" exit /b 0
set "PROC_PID="
for /f "usebackq delims=" %%p in ("%PID_FILE%") do set "PROC_PID=%%p"
if "%PROC_PID%"=="" (
  del /q "%PID_FILE%" >nul 2>&1
  exit /b 0
)
powershell -NoProfile -Command "if(Get-Process -Id %PROC_PID% -ErrorAction SilentlyContinue){Stop-Process -Id %PROC_PID% -Force -ErrorAction SilentlyContinue}" >nul 2>&1
del /q "%PID_FILE%" >nul 2>&1
exit /b 0
