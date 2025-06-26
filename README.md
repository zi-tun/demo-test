# LangGraph Multi-Agent Orchestration

A sophisticated multi-agent system built with LangGraph that intelligently routes user requests to specialized AI agents based on intent classification. This implementation demonstrates hierarchical agent coordination with a supervisor agent managing domain-specific agents for research, coding, writing, and data analysis tasks.

## 🚀 Features

- **Intelligent Agent Routing**: LLM-powered intent classification routes requests to the most suitable agent
- **Multi-Domain Expertise**: Specialized agents for research, code, writing, and data analysis
- **Graceful Degradation**: Robust error handling with fallback mechanisms
- **Centralized State Management**: Consistent conversation context across agent handoffs
- **Flexible LLM Support**: Compatible with OpenAI GPT and Anthropic Claude models
- **Interactive CLI**: User-friendly command-line interface with session management

## 🏗️ Architecture

```
┌─────────────────┐
│ Supervisor Agent │ ──── Intent Classification ──── LLM-based routing
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │ Routing   │
    │ Decision  │
    └─────┬─────┘
          │
   ┌──────┼──────┐
   │      │      │
   ▼      ▼      ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Research│ │  Code  │ │Writing │ │  Data  │
│ Agent  │ │ Agent  │ │ Agent  │ │ Agent  │
└────────┘ └────────┘ └────────┘ └────────┘
```

## 📋 Prerequisites

- Python 3.8+
- API key for OpenAI or Anthropic (or both)

## 🛠️ Installation & Setup

### 1. Clone and Install
```bash
git clone <repository-url>
cd demo-mcp
pip install -r requirements.txt
```

### 2. Configure API Keys

The system requires at least one LLM provider API key to function without demo mode.

#### Option A: Interactive Setup (Recommended)
```bash
python setup.py
```

#### Option B: Manual Setup
```bash
cp .env.example .env
# Edit .env with your API keys
```

**Where to Get API Keys:**
- **OpenAI**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys) (Recommended)
- **Anthropic**: [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)

**Example .env configuration:**
```env
# Required: Choose at least one
OPENAI_API_KEY=sk-your-actual-openai-key-here
# ANTHROPIC_API_KEY=your-actual-anthropic-key-here

# Set to false to use real APIs (default: true for demo)
DEMO_MODE=false

# Optional: specify preferred model
DEFAULT_MODEL=gpt-4o-mini
```

### 3. Verify Setup
```bash
python check_tokens.py
```

📖 **Need help with API keys?** See [API_TOKENS_GUIDE.md](API_TOKENS_GUIDE.md) for detailed instructions.

## 🎯 Usage

### Interactive Mode (Recommended)

Start the interactive CLI:

```bash
python main.py
```

Example conversation:
```
🤖 LangGraph Multi-Agent Orchestration System
==================================================
Available agents: Research, Code, Writing, Data, Supervisor
Type 'help' for commands, 'quit' to exit

👤 You: Can you help me write a Python function to calculate fibonacci numbers?

🔄 Processing...
🤖 Assistant: I'll help you with that coding request. Let me route this to our Code Agent.

Here's a Python function to calculate Fibonacci numbers with multiple approaches:

```python
def fibonacci_recursive(n):
    """Calculate nth Fibonacci number using recursion (simple but inefficient)."""
    if n <= 1:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)

def fibonacci_iterative(n):
    """Calculate nth Fibonacci number using iteration (efficient)."""
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def fibonacci_memoized(n, memo={}):
    """Calculate nth Fibonacci number with memoization (efficient for recursion)."""
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    
    memo[n] = fibonacci_memoized(n - 1, memo) + fibonacci_memoized(n - 2, memo)
    return memo[n]

# Example usage
print(f"10th Fibonacci number: {fibonacci_iterative(10)}")  # Output: 55
```

💻 **Execution Note**: Please test the code in your development environment and adjust as needed for your specific use case.

🔧 **Task Context**: General Coding in Python
```

### Single Query Mode

Process a single query and exit:

```bash
python main.py --query "What are the latest trends in artificial intelligence?"
```

### Available Commands (Interactive Mode)

- `help` - Show available commands and tips
- `status` - Display system status and agent usage
- `agents` - List all agents and their capabilities  
- `clear` - Clear session history
- `quit` - Exit the application

## 🤖 Agent Capabilities

### 🔍 Research Agent
- Information gathering and fact-checking
- Academic and scientific literature review
- Market research and competitive analysis
- Historical and background research
- Knowledge synthesis and summarization

### 💻 Code Agent  
- Multi-language programming support (Python, JavaScript, Java, etc.)
- Code debugging and optimization
- Architecture and design patterns
- API development and testing
- Algorithm implementation

### ✍️ Writing Agent
- Content creation (blogs, articles, documentation)
- Business communication and proposals
- Technical writing and user guides
- Creative writing and storytelling
- Editing and proofreading

### 📊 Data Agent
- Statistical analysis and modeling
- Data visualization and charting
- Database queries and manipulation
- Exploratory data analysis (EDA)
- Predictive modeling insights

## ⚙️ Configuration

The system can be configured via environment variables in your `.env` file:

```env
# LLM Provider (required - choose one or both)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
DEFAULT_MODEL=gpt-4o-mini

# Application Settings  
LOG_LEVEL=INFO
MAX_RETRIES=3
TIMEOUT_SECONDS=30

# Agent Configuration
ENABLE_RESEARCH_AGENT=true
ENABLE_CODE_AGENT=true  
ENABLE_WRITING_AGENT=true
ENABLE_DATA_AGENT=true

# Advanced Settings
LLM_TEMPERATURE=0.7
INTENT_CONFIDENCE_THRESHOLD=0.7
ENABLE_MEMORY=true
ENABLE_FALLBACK=true
```

## 🔧 Development

### Project Structure

```
demo-mcp/
├── agents/                 # Agent implementations
│   ├── base_agent.py      # Abstract base agent class
│   ├── supervisor.py      # Main orchestrator agent  
│   ├── research_agent.py  # Research and information gathering
│   ├── code_agent.py      # Programming assistance
│   ├── writing_agent.py   # Content creation
│   └── data_agent.py      # Data analysis and visualization
├── core/                   # Core system components
│   ├── state.py           # Centralized state management
│   ├── intent_classifier.py # LLM-based intent detection
│   └── graph_builder.py   # LangGraph workflow construction
├── utils/                  # Utility modules
│   ├── llm_client.py      # LLM provider abstraction
│   └── error_handler.py   # Error handling and graceful degradation
├── config/                 # Configuration management
│   └── settings.py        # Pydantic settings with env support
├── tests/                  # Test suite
├── main.py                # CLI entry point
├── requirements.txt       # Python dependencies
└── .env.example          # Environment template
```

### Adding New Agents

1. Create a new agent class inheriting from `BaseAgent`
2. Implement required methods: `get_system_prompt()` and `process_request()`
3. Register the agent in `MultiAgentGraphBuilder`
4. Add routing logic in the supervisor agent
5. Update intent classification patterns

### Running Tests

```bash
pytest tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph) for workflow orchestration
- Uses [LangChain](https://github.com/langchain-ai/langchain) for LLM abstractions
- Powered by OpenAI GPT and Anthropic Claude models

## 📞 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check the documentation in the `/docs` folder
- Review example usage in the CLI help system

---

**Note**: This implementation demonstrates DOD-5088 requirements for LangGraph agent orchestration with multi-agent coordination and intelligent routing based on user intent classification.
