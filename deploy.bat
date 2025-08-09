@echo off
REM RWA Platform Deployment Script for Windows
REM Windows一键部署脚本

echo 🚀 RWA Yield Analysis Platform - Windows Deployment
echo ==================================================

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
if not exist "rwa_env" (
    python -m venv rwa_env
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call rwa_env\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo ✅ Dependencies installed

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
echo 🧪 Testing installation...
python -c "
import asyncio
from simple_rwa_agent import SimpleRWAAgent

async def test():
    try:
        agent = SimpleRWAAgent()
        print('✅ RWA Agent initialized successfully')
        return True
    except Exception as e:
        print(f'❌ Test failed: {e}')
        return False

result = asyncio.run(test())
if result:
    print('🎉 Installation test passed!')
else:
    print('⚠️  Installation test failed - check your configuration')
"

echo.
echo 🎉 Deployment completed!
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your API keys
echo 2. Run: rwa_env\Scripts\activate.bat
echo 3. Run: python complete_s_level_demo.py (for demo)
echo 4. Run: python simple_rwa_agent.py (for interactive use)
echo.
echo 📚 Documentation: README.md
echo 🆘 Support: https://github.com/XSpoonAi/spoon-core/issues

pause