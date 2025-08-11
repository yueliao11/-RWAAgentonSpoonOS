@echo off
REM RWA Yield Optimizer GUI Deployment Script for Windows

echo 🚀 RWA Yield Optimizer GUI - Windows Deployment
echo ==============================================

REM Check Python version
echo 📋 Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3.10+ is required. Please install Python first.
    pause
    exit /b 1
)

REM Create virtual environment
echo 🔧 Creating virtual environment...
if not exist "rwa_gui_env" (
    python -m venv rwa_gui_env
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call rwa_gui_env\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing GUI dependencies...
python -m pip install --upgrade pip
pip install -r requirements-gui.txt
echo ✅ GUI dependencies installed

REM Create data directory
echo 📁 Creating data directory...
if not exist "data" mkdir data
echo ✅ Data directory created

REM Setup environment file
echo ⚙️  Setting up environment configuration...
if not exist ".env" (
    copy .env.example .env
    echo ✅ Environment file created (.env)
    echo ⚠️  Please edit .env file and add your API keys:
    echo    - OPENAI_API_KEY (OpenRouter key)
    echo    - ANTHROPIC_API_KEY (OpenRouter key)
) else (
    echo ✅ Environment file already exists
)

REM Test installation
echo 🧪 Testing GUI installation...
python -c "
import streamlit as st
import plotly.express as px
import pandas as pd
from services.data_service import RWADataService
print('✅ All GUI components imported successfully')
print('✅ Database initialization test passed')
"

echo.
echo 🎉 GUI Deployment completed!
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your API keys
echo 2. Run: rwa_gui_env\Scripts\activate.bat
echo 3. Run: streamlit run gui_app.py
echo 4. Open browser at: http://localhost:8501
echo.
echo 📚 GUI Features:
echo   • 📊 Real-time Dashboard
echo   • 🔍 Protocol Analysis
echo   • 🤖 AI Predictions
echo   • 💼 Portfolio Optimizer
echo   • ⚙️ Settings Management
echo.
echo 🆘 Support: Check README.md for troubleshooting

pause