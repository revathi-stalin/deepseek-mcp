@echo off
REM DeepSeek Local AI Server - Windows Startup Script

echo ==========================================
echo   DeepSeek Local AI Server
echo ==========================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

REM Create directories
if not exist models mkdir models
if not exist logs mkdir logs

REM Set model path
if not defined MODEL_PATH set MODEL_PATH=models\deepseek-llama.gguf

REM Check if model exists
if not exist "%MODEL_PATH%" (
    echo.
    echo WARNING: Model not found at: %MODEL_PATH%
    echo.
    echo To get started, download a DeepSeek model:
    echo 1. Visit: https://huggingface.co/models
    echo 2. Search for 'deepseek'
    echo 3. Download a GGUF format model
    echo 4. Place it in: models\deepseek-llama.gguf
    echo.
    echo Server will start without a model.
    echo.
)

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

REM Start server
echo.
echo Starting server on http://localhost:8000
echo.
echo Press Ctrl+C to stop
echo.

python main.py --model "%MODEL_PATH%" --host 0.0.0.0 --port 8000

pause
