@echo off
REM ============================================================
REM Docker Agent Web UI 启动脚本 (Windows)
REM ============================================================

setlocal enabledelayedexpansion

echo [INFO] Docker Agent Web UI 启动脚本
echo.

REM 设置工作目录
if not defined COZE_WORKSPACE_PATH (
    set COZE_WORKSPACE_PATH=%~dp0..
)

REM 设置环境变量
if not defined API_BASE_URL (
    set API_BASE_URL=http://localhost:8000
)

if not defined K8S_NAMESPACE (
    set K8S_NAMESPACE=fjn
)

echo [INFO] 工作目录: %COZE_WORKSPACE_PATH%
echo [INFO] API 地址: %API_BASE_URL%
echo [INFO] K8S 命名空间: %K8S_NAMESPACE%
echo.

REM 切换到工作目录
cd /d "%COZE_WORKSPACE_PATH%"

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 未安装或不在 PATH 中
    pause
    exit /b 1
)

REM 检查 streamlit
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [INFO] 安装 streamlit...
    pip install streamlit
    if errorlevel 1 (
        echo [ERROR] 安装 streamlit 失败
        pause
        exit /b 1
    )
)

REM 启动 Streamlit
echo [INFO] 启动 Docker Agent Web UI...
echo [INFO] Web UI 即将在浏览器中打开...
echo.

streamlit run src/web_ui.py ^
    --server.port 8501 ^
    --server.address 0.0.0.0 ^
    --server.headless true ^
    --server.fileWatcherType poll ^
    --browser.gatherUsageStats false

pause
