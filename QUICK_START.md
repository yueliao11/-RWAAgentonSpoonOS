# 🚀 Quick Start Guide | 快速开始指南

[English](#english-quick-start) | [中文](#中文快速开始)

---

## English Quick Start

### 🎯 5-Minute Setup

#### Option 1: Automated Deployment (Recommended)

**Linux/macOS:**
```bash
# Clone and deploy in one command
git clone https://github.com/XSpoonAi/spoon-core.git
cd spoon-core
./deploy.sh
```

**Windows:**
```cmd
# Clone and deploy in one command
git clone https://github.com/XSpoonAi/spoon-core.git
cd spoon-core
deploy.bat
```

#### Option 2: Manual Setup

```bash
# 1. Clone repository
git clone https://github.com/XSpoonAi/spoon-core.git
cd spoon-core

# 2. Create virtual environment
python3 -m venv rwa_env
source rwa_env/bin/activate  # Windows: rwa_env\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys
```

#### Option 3: Docker Deployment

```bash
# Quick Docker setup
git clone https://github.com/XSpoonAi/spoon-core.git
cd spoon-core

# Create .env file with your API keys
cp .env.example .env

# Run with Docker Compose
docker-compose up -d
```

### 🔑 API Keys Setup

1. Get OpenRouter API key from [openrouter.ai](https://openrouter.ai)
2. Edit `.env` file:
```bash
OPENAI_API_KEY=your-openrouter-key-here
ANTHROPIC_API_KEY=your-openrouter-key-here
```

### 🎮 Run the Platform

#### Complete Demo
```bash
python3 complete_s_level_demo.py
```

#### Interactive Agent
```bash
python3 simple_rwa_agent.py
```

#### Quick Test
```bash
python3 test_rwa_agent_simple.py
```

### 📊 Example Usage

```python
import asyncio
from simple_rwa_agent import SimpleRWAAgent

async def quick_example():
    agent = SimpleRWAAgent()
    
    # Analyze Centrifuge protocol
    result = await agent.analyze_protocol_yields("centrifuge")
    print(result)

asyncio.run(quick_example())
```

---

## 中文快速开始

### 🎯 5分钟部署

#### 方案1: 自动化部署（推荐）

**Linux/macOS:**
```bash
# 一键克隆和部署
git clone https://github.com/XSpoonAi/spoon-core.git
cd spoon-core
./deploy.sh
```

**Windows:**
```cmd
# 一键克隆和部署
git clone https://github.com/XSpoonAi/spoon-core.git
cd spoon-core
deploy.bat
```

#### 方案2: 手动设置

```bash
# 1. 克隆仓库
git clone https://github.com/XSpoonAi/spoon-core.git
cd spoon-core

# 2. 创建虚拟环境
python3 -m venv rwa_env
source rwa_env/bin/activate  # Windows: rwa_env\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境
cp .env.example .env
# 编辑.env文件，填入API密钥
```

#### 方案3: Docker部署

```bash
# Docker快速设置
git clone https://github.com/XSpoonAi/spoon-core.git
cd spoon-core

# 创建.env文件并填入API密钥
cp .env.example .env

# 使用Docker Compose运行
docker-compose up -d
```

### 🔑 API密钥设置

1. 从[openrouter.ai](https://openrouter.ai)获取OpenRouter API密钥
2. 编辑`.env`文件：
```bash
OPENAI_API_KEY=你的openrouter密钥
ANTHROPIC_API_KEY=你的openrouter密钥
```

### 🎮 运行平台

#### 完整演示
```bash
python3 complete_s_level_demo.py
```

#### 交互式代理
```bash
python3 simple_rwa_agent.py
```

#### 快速测试
```bash
python3 test_rwa_agent_simple.py
```

### 📊 使用示例

```python
import asyncio
from simple_rwa_agent import SimpleRWAAgent

async def quick_example():
    agent = SimpleRWAAgent()
    
    # 分析Centrifuge协议
    result = await agent.analyze_protocol_yields("centrifuge")
    print(result)

asyncio.run(quick_example())
```

---

## 🔧 Troubleshooting | 故障排除

### Common Issues | 常见问题

#### Python Version Error
```bash
# Install Python 3.10+
# Ubuntu/Debian
sudo apt update && sudo apt install python3.10

# macOS (with Homebrew)
brew install python@3.10

# Windows: Download from python.org
```

#### API Key Issues
```bash
# Check your .env file
cat .env

# Verify API key format
OPENAI_API_KEY=sk-or-v1-...
```

#### Dependencies Error
```bash
# Upgrade pip first
pip install --upgrade pip

# Install with verbose output
pip install -v -r requirements.txt
```

#### Permission Issues (Linux/macOS)
```bash
# Make deploy script executable
chmod +x deploy.sh

# Run with proper permissions
sudo ./deploy.sh
```

### Getting Help | 获取帮助

- 📚 **Full Documentation**: [README.md](README.md)
- 🐛 **Report Issues**: [GitHub Issues](https://github.com/XSpoonAi/spoon-core/issues)
- 💬 **Community**: [Discord](https://discord.gg/spoonos)
- 📧 **Email**: support@spoonos.ai

---

## 🎉 Success Indicators | 成功指标

You'll know the setup is successful when you see:

✅ Virtual environment created  
✅ Dependencies installed  
✅ Environment configured  
✅ RWA Agent initialized  
✅ Test passed  

成功部署的标志：

✅ 虚拟环境已创建  
✅ 依赖项已安装  
✅ 环境已配置  
✅ RWA代理已初始化  
✅ 测试通过  

**🚀 Ready to analyze RWA yields! | 准备分析RWA收益！**