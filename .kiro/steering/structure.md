# Project Structure & Organization

## Root Directory Layout

```
spoon-core/
├── main.py                     # CLI entry point - start here
├── config.json                 # Runtime configuration (auto-generated)
├── .env.example               # Environment template
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Package configuration
├── alembic.ini               # Database migration config
├── api/                      # REST API endpoints
├── cli/                      # CLI command implementations
├── spoon_ai/                 # Core framework package
├── examples/                 # Usage examples and demos
├── doc/                      # Documentation
└── tests/                    # Test suite
```

## Core Package Structure (`spoon_ai/`)

### Agent System
- `agents/` - Agent implementations and base classes
  - `base.py` - BaseAgent abstract class with state management
  - `react.py` - ReAct agent implementation
  - `spoon_react.py` - SpoonOS-specific ReAct agent
  - `spoon_react_mcp.py` - MCP-enabled ReAct agent
  - `graph_agent.py` - Graph-based workflow agents
  - `custom_agent.py` - Custom agent templates

### LLM Infrastructure
- `llm/` - Unified LLM management system
  - `manager.py` - LLMManager with fallback and load balancing
  - `interface.py` - Provider interface definitions
  - `registry.py` - Provider registration system
  - `providers/` - Individual LLM provider implementations
  - `monitoring.py` - Request logging and metrics
  - `config.py` - Configuration management

### Tool System
- `tools/` - Tool definitions and management
  - `base.py` - BaseTool abstract class
  - `tool_manager.py` - Tool registration and execution
  - `mcp_tool.py` - MCP protocol tool wrapper
  - `crypto_tools.py` - Cryptocurrency and DeFi tools
  - `rwa_tools.py` - Real-World Asset protocol tools

### Configuration & Management
- `config/` - Configuration system
  - `manager.py` - Unified configuration management
  - `models.py` - Configuration data models
  - `mcp_manager.py` - MCP server configuration

### Supporting Systems
- `retrieval/` - RAG and document processing
- `monitoring/` - System monitoring and alerts
- `social_media/` - Social platform integrations
- `trade/` - Blockchain trading utilities
- `utils/` - Common utilities and helpers

## Key Architectural Patterns

### Agent Pattern
- All agents inherit from `BaseAgent` in `spoon_ai/agents/base.py`
- State management through `AgentState` enum
- Memory system via `Memory` class
- Async execution with step-based processing

### Tool Pattern
- Tools inherit from `BaseTool` in `spoon_ai/tools/base.py`
- Pydantic-based parameter validation
- Async execution with `execute()` method
- Registration via `ToolManager`

### LLM Provider Pattern
- Providers implement `LLMProviderInterface`
- Registration via `@register_provider` decorator
- Unified response format through `LLMResponse`
- Automatic fallback and load balancing

### Configuration Pattern
- Hybrid system: `.env` → `config.json`
- Environment variables for initial setup
- Runtime configuration in `config.json`
- Provider-specific configuration sections

## File Naming Conventions

- **Snake case** for Python files: `my_agent.py`
- **Lowercase** for directories: `spoon_ai/agents/`
- **Descriptive names** for modules: `portfolio_optimizer_agent.py`
- **Test files** prefixed with `test_`: `test_agents.py`

## Import Patterns

```python
# Core framework imports
from spoon_ai.agents import BaseAgent, SpoonReactAI
from spoon_ai.tools import BaseTool, ToolManager
from spoon_ai.llm import LLMManager, ConfigurationManager
from spoon_ai.chat import ChatBot

# Specific implementations
from spoon_ai.agents.react import ReactAgent
from spoon_ai.tools.crypto_tools import CryptoPowerDataTool
from spoon_ai.llm.providers import OpenAIProvider
```

## Configuration Hierarchy

1. **Environment Variables** (`.env`) - Initial setup
2. **Runtime Config** (`config.json`) - Active configuration
3. **CLI Commands** - Runtime modifications
4. **Code Defaults** - Fallback values

## Entry Points

- **CLI**: `python main.py` → `cli/commands.py` → `SpoonAICLI`
- **API**: `api/rwa_api.py` (FastAPI endpoints)
- **Examples**: `examples/agent/` for agent demos
- **Tests**: `pytest tests/` for test execution

## Development Workflow

1. **Configuration**: Copy `.env.example` → `.env`
2. **Development**: Modify code in `spoon_ai/`
3. **Testing**: Add tests in `tests/`
4. **Examples**: Create demos in `examples/`
5. **Documentation**: Update `doc/` as needed