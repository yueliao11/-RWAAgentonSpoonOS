# 🖥️ RWA Yield Optimizer - GUI Deployment Guide

## 📋 Overview

This guide provides complete instructions for deploying the RWA Yield Optimizer GUI interface with SQLite database storage. The GUI provides an intuitive web-based interface for analyzing RWA protocols, AI predictions, and portfolio optimization.

## 🏗️ Architecture Overview

```
RWA Yield Optimizer GUI Architecture
├── Frontend: Streamlit Web Interface
├── Backend: Python Async Services
├── Database: SQLite with Persistent Storage
├── Data Sources: DeFiLlama API + AI Models
└── Deployment: Local/Docker/Cloud Options
```

### 🔧 Technology Stack

- **Frontend**: Streamlit + Plotly (Interactive Charts)
- **Backend**: Python 3.10+ with AsyncIO
- **Database**: SQLite (Persistent Data Storage)
- **Visualization**: Plotly Express, Matplotlib
- **Deployment**: Docker, Local, Cloud-ready

## 📦 Installation Options

### Option 1: Automated Deployment (Recommended)

#### Linux/macOS:
```bash
# Clone repository
git clone https://github.com/XSpoonAi/spoon-core.git
cd spoon-core

# Run automated GUI deployment
./deploy_gui.sh

# Follow the prompts and configure API keys
```

#### Windows:
```cmd
# Clone repository
git clone https://github.com/XSpoonAi/spoon-core.git
cd spoon-core

# Run automated GUI deployment
deploy_gui.bat

# Follow the prompts and configure API keys
```

### Option 2: Manual Installation

#### Step 1: Environment Setup
```bash
# Create virtual environment
python3 -m venv rwa_gui_env

# Activate environment
source rwa_gui_env/bin/activate  # Linux/macOS
# OR
rwa_gui_env\Scripts\activate.bat  # Windows

# Install dependencies
pip install -r requirements-gui.txt
```

#### Step 2: Database Setup
```bash
# Create data directory
mkdir -p data

# Database will be automatically initialized on first run
```

#### Step 3: Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
nano .env  # or use your preferred editor
```

Required environment variables:
```bash
OPENAI_API_KEY=your-openrouter-api-key-here
ANTHROPIC_API_KEY=your-openrouter-api-key-here
```

### Option 3: Docker Deployment

#### Quick Docker Setup:
```bash
# Clone repository
git clone https://github.com/XSpoonAi/spoon-core.git
cd spoon-core

# Create .env file with API keys
cp .env.example .env
# Edit .env with your keys

# Build and run with Docker Compose
docker-compose -f docker-compose-gui.yml up -d

# Access at http://localhost:8501
```

#### Manual Docker Build:
```bash
# Build Docker image
docker build -f Dockerfile.gui -t rwa-gui .

# Run container
docker run -d \
  --name rwa-gui \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -e OPENAI_API_KEY=your-key \
  -e ANTHROPIC_API_KEY=your-key \
  rwa-gui
```

## 🚀 Running the Application

### Local Development
```bash
# Activate virtual environment
source rwa_gui_env/bin/activate

# Start Streamlit application
streamlit run gui_app.py

# Application will open at: http://localhost:8501
```

### Production Deployment
```bash
# Run with custom configuration
streamlit run gui_app.py \
  --server.port=8501 \
  --server.address=0.0.0.0 \
  --server.headless=true
```

## 🖥️ GUI Features Overview

### 📊 Dashboard Page
- **Real-time Protocol Metrics**: Live TVL, APY, and performance indicators
- **Market Summary**: Overview of all 5 RWA protocols
- **Interactive Charts**: APY comparison and risk-return analysis
- **Quick Refresh**: One-click data updates

### 🔍 Protocol Analysis Page
- **Protocol Selector**: Choose from Centrifuge, Goldfinch, Maple, Credix, TrueFi
- **Detailed Metrics**: APY, risk score, TVL, asset type, lock periods
- **Risk Visualization**: Interactive risk gauge with color coding
- **Historical Charts**: Time-series data with zoom and pan capabilities

### 🤖 AI Predictions Page
- **Multi-Model Predictions**: GPT-4, Claude 3.5, Gemini Pro ensemble
- **Timeframe Selection**: 30d, 90d, 180d prediction horizons
- **Confidence Scoring**: AI model confidence and agreement metrics
- **Prediction History**: Track prediction accuracy over time

### 💼 Portfolio Optimizer Page
- **Investment Parameters**: Amount and risk tolerance configuration
- **Visual Allocations**: Interactive pie charts and bar graphs
- **Portfolio Metrics**: Expected APY, Sharpe ratio, diversification score
- **Detailed Reports**: Comprehensive optimization analysis

### ⚙️ Settings Page
- **API Configuration**: Secure API key management
- **Application Settings**: Theme, refresh intervals, preferences
- **Data Management**: Database cleanup and statistics

## 🗄️ Database Schema

### SQLite Tables Structure

#### protocol_data
```sql
CREATE TABLE protocol_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    protocol TEXT NOT NULL,
    current_apy REAL NOT NULL,
    risk_score REAL NOT NULL,
    asset_type TEXT NOT NULL,
    tvl REAL NOT NULL,
    active_pools INTEGER DEFAULT 0,
    min_investment REAL DEFAULT 1000.0,
    lock_period TEXT DEFAULT 'flexible',
    change_1d REAL DEFAULT 0.0,
    change_7d REAL DEFAULT 0.0,
    timestamp TEXT NOT NULL,
    UNIQUE(protocol, timestamp)
);
```

#### ai_predictions
```sql
CREATE TABLE ai_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    protocol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    predicted_apy REAL NOT NULL,
    confidence REAL NOT NULL,
    model_name TEXT NOT NULL,
    reasoning TEXT,
    risk_factors TEXT,
    timestamp TEXT NOT NULL
);
```

#### portfolio_allocations
```sql
CREATE TABLE portfolio_allocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    protocol TEXT NOT NULL,
    allocation_amount REAL NOT NULL,
    allocation_percentage REAL NOT NULL,
    expected_apy REAL NOT NULL,
    risk_score REAL NOT NULL,
    timestamp TEXT NOT NULL
);
```

## 📊 Performance Optimization

### Caching Strategy
- **Streamlit Cache**: Automatic caching of data loading functions
- **Database Indexing**: Optimized queries with proper indexes
- **Lazy Loading**: Charts and data loaded on demand
- **Session State**: Efficient state management across pages

### Expected Performance
- **Initial Load**: < 3 seconds
- **Data Refresh**: < 2 seconds (cached)
- **Chart Rendering**: < 1 second
- **Memory Usage**: < 200MB typical
- **Database Size**: ~10MB per month of data

## 🔒 Security Features

### API Key Management
- **Secure Storage**: API keys stored in database with encryption
- **Environment Variables**: Support for .env file configuration
- **Session Isolation**: User sessions are isolated and secure

### Data Protection
- **Input Validation**: All user inputs validated and sanitized
- **Error Handling**: Graceful error handling without data exposure
- **Database Security**: SQLite with proper access controls

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Solution: Install missing dependencies
pip install -r requirements-gui.txt

# Or install specific packages
pip install streamlit plotly pandas
```

#### 2. Database Errors
```bash
# Solution: Check data directory permissions
mkdir -p data
chmod 755 data

# Reset database if corrupted
rm data/rwa_optimizer.db
# Restart application to recreate
```

#### 3. API Connection Issues
```bash
# Solution: Check API keys in .env file
cat .env

# Verify keys are properly set
echo $OPENAI_API_KEY
```

#### 4. Port Already in Use
```bash
# Solution: Use different port
streamlit run gui_app.py --server.port=8502

# Or kill existing process
lsof -ti:8501 | xargs kill -9
```

#### 5. Streamlit Not Found
```bash
# Solution: Ensure virtual environment is activated
source rwa_gui_env/bin/activate

# Reinstall Streamlit
pip install --upgrade streamlit
```

### Performance Issues

#### Slow Loading
- Check internet connection for API calls
- Clear Streamlit cache: `st.cache_data.clear()`
- Restart application to reset session state

#### Memory Usage
- Monitor with: `htop` or Task Manager
- Restart application if memory usage > 500MB
- Consider reducing data retention period

## 🚀 Deployment Environments

### Local Development
```bash
# Development mode with hot reload
streamlit run gui_app.py --server.runOnSave=true
```

### Production Server
```bash
# Production mode
streamlit run gui_app.py \
  --server.port=8501 \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableCORS=false \
  --server.enableXsrfProtection=true
```

### Cloud Deployment

#### Streamlit Cloud
1. Push code to GitHub repository
2. Connect to Streamlit Cloud
3. Configure secrets for API keys
4. Deploy automatically

#### Heroku
```bash
# Create Procfile
echo "web: streamlit run gui_app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# Deploy to Heroku
heroku create rwa-yield-optimizer
git push heroku main
```

#### AWS/GCP/Azure
- Use Docker container deployment
- Configure load balancer for scaling
- Set up persistent storage for database

## 📈 Monitoring & Maintenance

### Health Checks
```bash
# Check application health
curl http://localhost:8501/_stcore/health

# Monitor database size
ls -lh data/rwa_optimizer.db

# Check memory usage
ps aux | grep streamlit
```

### Regular Maintenance
```bash
# Clean old data (run monthly)
python3 -c "
from services.data_service import RWADataService
service = RWADataService()
service.cleanup_old_data(days=90)
print('✅ Old data cleaned')
"

# Backup database
cp data/rwa_optimizer.db data/backup_$(date +%Y%m%d).db
```

### Log Monitoring
```bash
# View Streamlit logs
tail -f ~/.streamlit/logs/streamlit.log

# Application logs (if configured)
tail -f logs/rwa_gui.log
```

## 🔄 Updates & Upgrades

### Update Application
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements-gui.txt --upgrade

# Restart application
streamlit run gui_app.py
```

### Database Migration
```bash
# Backup current database
cp data/rwa_optimizer.db data/backup_before_migration.db

# Run migration (if needed)
python3 database/migrate.py

# Verify migration
python3 -c "from services.data_service import RWADataService; print('✅ Database OK')"
```

## 📞 Support & Resources

### Documentation
- **Full README**: [README.md](README.md)
- **API Documentation**: [API_DOCS.md](API_DOCS.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Community Support
- **GitHub Issues**: [Report Issues](https://github.com/XSpoonAi/spoon-core/issues)
- **Discord Community**: [Join Discord](https://discord.gg/spoonos)
- **Email Support**: support@spoonos.ai

### Quick Reference Commands

```bash
# Start GUI
streamlit run gui_app.py

# Install dependencies
pip install -r requirements-gui.txt

# Reset database
rm data/rwa_optimizer.db

# Check logs
tail -f ~/.streamlit/logs/streamlit.log

# Update application
git pull && pip install -r requirements-gui.txt --upgrade
```

---

## 🎉 Success Indicators

You'll know the GUI deployment is successful when you see:

✅ **Streamlit server starts without errors**  
✅ **Database initializes automatically**  
✅ **All 5 pages load correctly**  
✅ **Data refresh works from Dashboard**  
✅ **Charts render properly**  
✅ **Settings save successfully**  

**🚀 Ready to analyze RWA yields with professional GUI interface!**

---

*Built with ❤️ using Streamlit and SQLite - Professional RWA analysis made accessible*