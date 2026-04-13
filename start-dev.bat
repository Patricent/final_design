@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"

echo [1/3] 数据库迁移...
fd\Scripts\python.exe backend\manage.py migrate
if errorlevel 1 (
  echo 迁移失败，请检查 MySQL 是否已启动、库是否已创建、backend\.env 配置是否正确。
  pause
  exit /b 1
)

echo [2/3] 启动后端 http://127.0.0.1:8000 ...
start "final_design - Django" /D "%~dp0" cmd /k fd\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8000

echo [3/3] 启动前端 http://127.0.0.1:5173 ...
start "final_design - Vite" /D "%~dp0frontend" cmd /k npm run dev -- --host 127.0.0.1 --port 5173

echo.
echo 已打开两个新窗口：后端与前端。浏览器访问 http://127.0.0.1:5173
echo 关闭对应窗口即可停止服务。
pause
