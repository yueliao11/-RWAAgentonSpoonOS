#!/bin/bash
# RWA Platform Deployment Script
# 一键部署脚本

set -e

echo "🚀 RWA Yield Analysis Platform - Deployment Script"
echo "=================================================="

# Check Python version
echo "📋 Checking Python version..."
python3 --version || {
    echo "❌ Python 3.10+ is required. Please install Python first."
    exit 1
}

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ ! -d "rwa_env" ]; then
    python3 -m venv rwa_env
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source rwa_env/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Setup environment file
echo "⚙️  Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Environment file created (.env)"
    echo "⚠️  Please edit .env file and add your API keys:"
    echo "   - OPENAI_API_KEY (OpenRouter key)"
    echo "   - ANTHROPIC_API_KEY (OpenRouter key)"
else
    echo "✅ Environment file already exists"
fi

# Test installation
echo "🧪 Testing installation..."
python3 -c "
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

echo ""
echo "🎉 Deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: source rwa_env/bin/activate"
echo "3. Run: python3 complete_s_level_demo.py (for demo)"
echo "4. Run: python3 simple_rwa_agent.py (for interactive use)"
echo ""
echo "📚 Documentation: README.md"
echo "🆘 Support: https://github.com/XSpoonAi/spoon-core/issues"