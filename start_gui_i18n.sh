#!/bin/bash
# RWA Yield Optimizer GUI 启动脚本 (带i18n支持)
# RWA Yield Optimizer GUI Startup Script (with i18n support)

echo "🚀 启动RWA收益优化器GUI (国际化版本)"
echo "🚀 Starting RWA Yield Optimizer GUI (i18n version)"
echo "=========================================="

# 检查虚拟环境
if [ -d "rwa_gui_env" ]; then
    echo "✅ 找到虚拟环境 rwa_gui_env"
    echo "✅ Found virtual environment rwa_gui_env"
    source rwa_gui_env/bin/activate
else
    echo "⚠️  未找到虚拟环境，使用系统Python"
    echo "⚠️  Virtual environment not found, using system Python"
fi

# 检查依赖
echo "🔍 检查依赖项..."
echo "🔍 Checking dependencies..."

python -c "import streamlit" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Streamlit 已安装"
else
    echo "❌ Streamlit 未安装，请运行: pip install streamlit"
    exit 1
fi

python -c "from utils.i18n import t" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ i18n 模块正常"
else
    echo "❌ i18n 模块有问题"
    exit 1
fi

# 启动应用
echo ""
echo "🌐 启动支持中英文切换的GUI应用..."
echo "🌐 Starting GUI application with Chinese-English switching..."
echo "📱 应用将在浏览器中打开: http://localhost:8501"
echo "📱 Application will open in browser: http://localhost:8501"
echo ""
echo "💡 提示: 在设置页面可以切换语言"
echo "💡 Tip: You can switch language in Settings page"
echo ""

# 启动streamlit应用
streamlit run gui_app_enhanced.py --server.port=8501 --server.headless=false