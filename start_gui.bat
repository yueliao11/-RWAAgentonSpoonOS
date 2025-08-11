@echo off
REM Quick start script for RWA Yield Optimizer GUI

echo 🚀 Starting RWA Yield Optimizer GUI...
echo ======================================

REM Check if virtual environment exists
if not exist "rwa_gui_env" (
    echo ❌ GUI environment not found. Please run deploy_gui.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call rwa_gui_env\Scripts\activate.bat

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found. Creating from template...
    copy .env.example .env
    echo 📝 Please edit .env file with your API keys before using AI features
)

REM Start Streamlit application
echo 🌐 Starting Streamlit server...
echo 📱 GUI will open at: http://localhost:8501
echo 🛑 Press Ctrl+C to stop the server
echo.

streamlit run gui_app.py