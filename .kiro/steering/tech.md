# Technology Stack & Build System

## Core Technologies

- **Python 3.10+**: Primary development language
- **FastAPI**: Web framework for API endpoints
- **Pydantic**: Data validation and settings management
- **SQLAlchemy**: Database ORM
- **AsyncIO**: Asynchronous programming foundation

## LLM & AI Infrastructure

- **Multi-Provider LLM Support**: OpenAI, Anthropic, DeepSeek, Gemini
- **Unified LLM Architecture**: Provider-agnostic interface with fallback chains
- **Prompt Caching**: Anthropic model optimization for cost reduction
- **Response Normalization**: Consistent response handling across providers

## Web3 & Blockchain

- **Web3.py**: Ethereum blockchain interaction
- **RPC Integration**: Multiple blockchain network support
- **DeFi Protocol APIs**: Centrifuge, Goldfinch, Maple Finance, Credix
- **Blockchain Explorers**: Etherscan, custom scan URLs

## Agent Framework

- **ReAct Architecture**: Reasoning and Action agent pattern
- **MCP (Model Context Protocol)**: Dynamic tool discovery via stdio/http/websocket
- **Graph System**: LangGraph-inspired workflow orchestration
- **State Management**: Comprehensive session and memory persistence

## Development Tools

- **Package Manager**: pip (uv recommended for faster installs)
- **Environment Management**: python-dotenv for configuration
- **CLI Framework**: prompt_toolkit for interactive interface
- **Testing**: pytest with comprehensive test suite
- **Build System**: setuptools with pyproject.toml

## Common Commands

### Installation & Setup
```bash
# Clone and setup
git clone https://github.com/XSpoonAi/spoon-core.git
cd spoon-core

# Virtual environment
python -m venv spoon-env
source spoon-env/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
# OR for faster install:
uv pip install -r requirements.txt
```

### Running the Application
```bash
# Start interactive CLI
python main.py

# Start with server mode (not implemented)
python main.py --server --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_agents.py
pytest tests/test_llm_manager_integration.py

# Run with verbose output
pytest -v
```

### Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
# Fill in API keys and settings in .env file
# Runtime config managed in config.json
```

## Key Dependencies

- **aiohttp**: Async HTTP client/server
- **anthropic**: Anthropic Claude API client
- **openai**: OpenAI API client
- **fastmcp**: Model Context Protocol implementation
- **web3**: Ethereum blockchain interaction
- **prompt_toolkit**: Interactive CLI framework
- **pydantic**: Data validation and serialization
- **sqlalchemy**: Database ORM
- **python-dotenv**: Environment variable management