@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"

echo [0/4] 安装/更新 Python 依赖（含 Pillow，供头像 ImageField 使用）...
REM 必须用与 migrate 相同的 python 调 pip，否则 Pillow 可能装到别的环境
fd\Scripts\python.exe -m pip install -r backend\requirements.txt
if errorlevel 1 (
  echo 依赖安装失败。请在项目根目录手动执行:
  echo   fd\Scripts\python.exe -m pip install -r backend\requirements.txt
  pause
  exit /b 1
)
fd\Scripts\python.exe -c "import PIL" 2>nul
if errorlevel 1 (
  echo Pillow 仍未就绪，尝试单独安装 Pillow...
  fd\Scripts\python.exe -m pip install "Pillow>=10.0.0"
  if errorlevel 1 (
    echo Pillow 安装失败，请检查网络或 pip 源后重试。
    pause
    exit /b 1
  )
  fd\Scripts\python.exe -c "import PIL" 2>nul
  if errorlevel 1 (
    echo 安装后仍无法 import PIL，请确认 fd\Scripts\python.exe 为当前使用的解释器。
    pause
    exit /b 1
  )
)

echo [1/4] 数据库迁移...
fd\Scripts\python.exe backend\manage.py migrate
if errorlevel 1 (
  echo 迁移失败，请检查 MySQL 是否已启动、库是否已创建、backend\.env 配置是否正确。
  echo 若错误与 Pillow 或 ImageField 有关，请在项目根目录执行下面一行后重试本脚本
  echo   fd\Scripts\python.exe -m pip install -r backend\requirements.txt
  pause
  exit /b 1
)

echo [2/4] 启动后端 http://127.0.0.1:8000 ...
start "final_design - Django" /D "%~dp0" cmd /k fd\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8000

echo [3/4] 启动前端 http://127.0.0.1:5173 ...
start "final_design - Vite" /D "%~dp0frontend" cmd /k npm run dev -- --host 127.0.0.1 --port 5173

echo.
echo 已打开两个新窗口：后端与前端。浏览器访问 http://127.0.0.1:5173
echo 关闭对应窗口即可停止服务。
pause
