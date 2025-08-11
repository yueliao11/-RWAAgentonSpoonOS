#!/bin/bash
# Enhanced GUI startup script

echo "🚀 Starting Enhanced RWA Yield Optimizer GUI..."
echo "=============================================="

# Check virtual environment
if [ ! -d "rwa_gui_env" ]; then
    echo "❌ GUI environment not found. Please run ./deploy_gui.sh first"
    exit 1
fi

# Activate virtual environment
source rwa_gui_env/bin/activate

# Check .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys before using AI features"
fi

# Start enhanced GUI
echo "🌐 Starting Enhanced Streamlit server..."
echo "🎨 Features: Dark theme, 3D charts, Real-time updates"
echo "📱 GUI will open at: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

streamlit run gui_app_enhanced.py --server.headless=true
