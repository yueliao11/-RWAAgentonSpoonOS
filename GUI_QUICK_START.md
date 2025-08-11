# 🚀 RWA Yield Optimizer GUI - Quick Start Guide

## 📋 Overview

The RWA Yield Optimizer now includes a professional web-based GUI interface built with Streamlit and SQLite database for persistent data storage. This guide provides the fastest way to get the GUI running.

## ⚡ Quick Deployment (5 Minutes)

### Option 1: One-Click Deployment

#### Linux/macOS:
```bash
# 1. Clone and deploy
git clone https://github.com/XSpoonAi/spoon-core.git
cd spoon-core
./deploy_gui.sh

# 2. Start GUI
./start_gui.sh
```

#### Windows:
```cmd
# 1. Clone and deploy
git clone https://github.com/XSpoonAi/spoon-core.git
cd spoon-core
deploy_gui.bat

# 2. Start GUI
start_gui.bat
```

### Option 2: Docker Deployment
```bash
# Quick Docker setup
git clone https://github.com/XSpoonAi/spoon-core.git
cd spoon-core

# Create .env with your API keys
cp .env.example .env
# Edit .env file

# Start with Docker
docker-compose -f docker-compose-gui.yml up -d

# Access at http://localhost:8501
```

## 🔑 API Keys Configuration

Edit the `.env` file with your API keys:
```bash
# Required for AI predictions
OPENAI_API_KEY=your-openrouter-api-key-here
ANTHROPIC_API_KEY=your-openrouter-api-key-here
```

Get your OpenRouter API key from: https://openrouter.ai

## 🖥️ GUI Features

### 📊 Dashboard
- **Real-time Protocol Overview**: Live TVL and APY data
- **Market Summary Cards**: Key metrics for all RWA protocols
- **Interactive Charts**: APY comparison and risk analysis
- **One-click Data Refresh**: Update all protocol data

### 🔍 Protocol Analysis
- **Detailed Protocol Metrics**: APY, risk score, TVL, asset type
- **Risk Visualization**: Interactive gauge with color coding
- **Historical Charts**: Time-series data analysis
- **Protocol Comparison**: Side-by-side analysis

### 🤖 AI Predictions
- **Multi-Model Ensemble**: GPT-4, Claude 3.5, Gemini Pro
- **Confidence Scoring**: AI model agreement and reliability
- **Prediction History**: Track accuracy over time
- **Risk Factor Analysis**: Comprehensive risk assessment

### 💼 Portfolio Optimizer
- **Investment Parameters**: Amount and risk tolerance
- **Visual Allocations**: Interactive pie charts and graphs
- **Portfolio Metrics**: Expected APY, Sharpe ratio, diversification
- **Detailed Reports**: Professional optimization analysis

### ⚙️ Settings
- **API Configuration**: Secure key management
- **Application Preferences**: Theme, refresh intervals
- **Data Management**: Database cleanup and statistics

## 🗄️ Database Features

### SQLite Integration
- **Persistent Storage**: All data saved locally
- **Historical Tracking**: Protocol performance over time
- **Prediction History**: AI prediction accuracy tracking
- **Portfolio Sessions**: Save and compare optimizations

### Data Management
- **Automatic Cleanup**: Old data removed after 90 days
- **Backup Support**: Easy database backup and restore
- **Performance Optimized**: Indexed queries for fast access

## 📊 Usage Examples

### 1. Quick Protocol Analysis
1. Open GUI at http://localhost:8501
2. Go to "Protocol Analysis" page
3. Select protocol (e.g., Centrifuge)
4. View detailed metrics and risk assessment

### 2. AI Yield Prediction
1. Navigate to "AI Predictions" page
2. Select protocol and timeframe
3. Click "Get AI Prediction"
4. Review ensemble results and confidence scores

### 3. Portfolio Optimization
1. Go to "Portfolio Optimizer" page
2. Enter investment amount and risk tolerance
3. Click "Optimize Portfolio"
4. Review allocation recommendations

### 4. Data Refresh
1. From Dashboard, click "Refresh All Data"
2. Wait for API calls to complete
3. View updated metrics across all pages

## 🔧 Technical Architecture

### Frontend Stack
- **Streamlit**: Web framework for data applications
- **Plotly**: Interactive charts and visualizations
- **Pandas**: Data processing and analysis

### Backend Integration
- **Async Services**: Non-blocking API calls
- **SQLite Database**: Persistent data storage
- **Caching Layer**: Optimized performance

### Data Flow
```
GUI Interface → Data Service → RWA Agent → APIs
     ↓              ↓            ↓         ↓
SQLite DB ← Data Processing ← Real Data ← DeFiLlama/AI
```

## 🚀 Performance Metrics

- **Load Time**: < 3 seconds initial load
- **Data Refresh**: < 2 seconds for cached data
- **Chart Rendering**: < 1 second interactive charts
- **Memory Usage**: < 200MB typical operation
- **Database Size**: ~10MB per month of data

## 🔒 Security Features

- **API Key Encryption**: Secure storage in database
- **Input Validation**: All user inputs sanitized
- **Session Isolation**: User sessions are isolated
- **Error Handling**: No sensitive data in error messages

## 🐛 Troubleshooting

### Common Issues

#### GUI Won't Start
```bash
# Check virtual environment
source rwa_gui_env/bin/activate
pip install -r requirements-gui.txt

# Check Python version
python3 --version  # Should be 3.10+
```

#### Database Errors
```bash
# Reset database
rm data/rwa_optimizer.db
# Restart GUI to recreate
```

#### API Connection Issues
```bash
# Check .env file
cat .env
# Verify API keys are set correctly
```

#### Port Already in Use
```bash
# Use different port
streamlit run gui_app.py --server.port=8502

# Or kill existing process
lsof -ti:8501 | xargs kill -9
```

### Performance Issues

#### Slow Loading
- Check internet connection
- Clear browser cache
- Restart Streamlit server

#### Memory Usage
- Monitor with system tools
- Restart if memory > 500MB
- Reduce data retention period

## 📱 Browser Compatibility

### Supported Browsers
- **Chrome**: ✅ Recommended
- **Firefox**: ✅ Full support
- **Safari**: ✅ Full support
- **Edge**: ✅ Full support

### Mobile Support
- **Responsive Design**: Adapts to mobile screens
- **Touch Friendly**: Optimized for touch interaction
- **Performance**: Optimized for mobile browsers

## 🔄 Updates & Maintenance

### Update Application
```bash
# Pull latest changes
git pull origin main

# Update dependencies
source rwa_gui_env/bin/activate
pip install -r requirements-gui.txt --upgrade

# Restart GUI
./start_gui.sh
```

### Database Maintenance
```bash
# Backup database
cp data/rwa_optimizer.db data/backup_$(date +%Y%m%d).db

# Clean old data (optional)
python3 -c "
from services.data_service import RWADataService
service = RWADataService()
service.cleanup_old_data(days=90)
print('✅ Database cleaned')
"
```

## 📞 Support & Resources

### Quick Commands
```bash
# Start GUI
./start_gui.sh

# Deploy GUI
./deploy_gui.sh

# Check status
curl http://localhost:8501/_stcore/health

# View logs
tail -f ~/.streamlit/logs/streamlit.log
```

### Documentation
- **Full Guide**: [GUI_DEPLOYMENT_GUIDE.md](GUI_DEPLOYMENT_GUIDE.md)
- **Project README**: [README.md](README.md)
- **API Documentation**: Check individual Python files

### Community
- **GitHub Issues**: [Report Problems](https://github.com/XSpoonAi/spoon-core/issues)
- **Discord**: [Join Community](https://discord.gg/spoonos)
- **Email**: support@spoonos.ai

## 🎉 Success Checklist

✅ **GUI starts without errors**  
✅ **Database initializes automatically**  
✅ **All 5 pages load correctly**  
✅ **Data refresh works from Dashboard**  
✅ **Charts render properly**  
✅ **Settings save successfully**  
✅ **API keys configured**  

## 🏆 Next Steps

1. **Configure API Keys**: Add your OpenRouter keys for AI features
2. **Refresh Data**: Click refresh on Dashboard to get live data
3. **Explore Features**: Try each page to understand capabilities
4. **Optimize Portfolio**: Use the optimizer with your investment amount
5. **Track Performance**: Monitor predictions and portfolio over time

---

**🚀 Ready to analyze RWA yields with professional GUI interface!**

*Built with ❤️ using Streamlit, SQLite, and modern web technologies*