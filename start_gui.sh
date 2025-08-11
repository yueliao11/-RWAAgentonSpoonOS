#!/bin/bash
# Quick start script for RWA Yield Optimizer GUI

echo "🚀 Starting RWA Yield Optimizer GUI..."
echo "======================================"

# Check if virtual environment exists
if [ ! -d "rwa_gui_env" ]; then
    echo "❌ GUI environment not found. Please run ./deploy_gui.sh first"
    exit 1
fi

# Activate virtual environment
source rwa_gui_env/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys before using AI features"
fi

# Start Streamlit application
echo "🌐 Starting Streamlit server..."
echo "📱 GUI will open at: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

streamlit run gui_app.py