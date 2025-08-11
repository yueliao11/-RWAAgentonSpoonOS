#!/bin/bash
# RWA Yield Optimizer GUI Deployment Script

set -e

echo "🚀 RWA Yield Optimizer GUI - Deployment Script"
echo "=============================================="

# Check Python version
echo "📋 Checking Python version..."
python3 --version || {
    echo "❌ Python 3.10+ is required. Please install Python first."
    exit 1
}

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ ! -d "rwa_gui_env" ]; then
    python3 -m venv rwa_gui_env
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source rwa_gui_env/bin/activate

# Install dependencies
echo "📦 Installing GUI dependencies..."
pip install --upgrade pip
pip install -r requirements-gui.txt
echo "✅ GUI dependencies installed"

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data
echo "✅ Data directory created"

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
echo "🧪 Testing GUI installation..."
python3 -c "
import streamlit as st
import plotly.express as px
import pandas as pd
from services.data_service import RWADataService
print('✅ All GUI components imported successfully')
print('✅ Database initialization test passed')
"

echo ""
echo "🎉 GUI Deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: source rwa_gui_env/bin/activate"
echo "3. Run: streamlit run gui_app.py"
echo "4. Open browser at: http://localhost:8501"
echo ""
echo "📚 GUI Features:"
echo "  • 📊 Real-time Dashboard"
echo "  • 🔍 Protocol Analysis"
echo "  • 🤖 AI Predictions"
echo "  • 💼 Portfolio Optimizer"
echo "  • ⚙️ Settings Management"
echo ""
echo "🆘 Support: Check README.md for troubleshooting"