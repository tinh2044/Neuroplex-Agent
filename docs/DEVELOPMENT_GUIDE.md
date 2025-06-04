# AI Engine Development Guide

This guide provides comprehensive instructions for setting up a development environment and contributing to the AI Engine project.

## 🚀 Quick Start

### Prerequisites

**Required Software:**
- **Python 3.8+** (recommended: 3.11+)
- **Docker & Docker Compose** (for services)
- **Git** (for version control)
- **Node.js 16+** (for frontend development)

**Recommended Tools:**
- **VS Code** with Python extension
- **Postman** or **curl** for API testing
- **Neo4j Desktop** for graph database management

### Environment Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/tinh2044/Neuroplex-Agent
cd Neuroplex-Agent
```

#### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r ai_engine/requirements.txt
```

#### 3. Configure Environment Variables

```bash
# Copy environment template
cp ai_engine/.env.example ai_engine/.env

# Edit configuration
nano ai_engine/.env
```

**Essential Environment Variables:**
```bash
# Model Directory
MODEL_DIR=D:/Huggingface

# AI Model APIs (choose at least one)
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
DEEPSEEK_API_KEY=sk-your-deepseek-key
QWEN_API_KEY=sk-your-qwen-key

# Optional Services
TAVILY_API_KEY=tvly-your-tavily-key  # Web search
```

#### 4. Start Infrastructure Services

```bash
cd docker
docker-compose up -d milvus-standalone neo4j ollama
```

**Services Started:**
- **Milvus**: Vector database (port 19530)
- **Neo4j**: Graph database (port 7474, 7687)
- **Ollama**: Local model server (port 11434)

#### 5. Install Local Models (Optional)

```bash
# Pull popular models
docker exec -it ollama ollama pull llama3.1:8b
docker exec -it ollama ollama pull qwen2:7b
docker exec -it ollama ollama pull bge-m3
```

#### 6. Verify Installation

```bash
# Test AI Engine imports
python -c "from ai_engine import agent_config, knowledge_base; print('AI Engine loaded successfully')"

# Test API connection (if backend is running)
curl http://localhost:5000/health
```

## 🏗️ Development Architecture

### Project Structure

```
ai_engine/
├── __init__.py              # Main module initialization
├── .env                     # Environment configuration
├── configs/
│   └── agent.py            # Agent configuration management
├── core/                   # Core processing components
│   ├── retriever.py        # Main retrieval orchestrator
│   ├── operators.py        # Query enhancement operators
│   ├── indexing.py         # Document processing & chunking
│   └── history.py          # Conversation history management
├── agents/                 # Agent framework
│   ├── __init__.py         # Agent manager
│   ├── registry.py         # Agent registration
│   ├── tools_factory.py    # Tool registration system
│   ├── chatbot/            # Basic chat agent
│   └── react/              # ReAct agent implementation
├── knowledge_database/     # Vector knowledge management
│   ├── __init__.py         # KnowledgeBase class
│   ├── kb_db_manager.py    # Database operations
│   ├── document_processor.py # Document parsing
│   ├── milvus_manager.py   # Vector storage
│   └── embedding_manager.py # Embedding generation
├── graph_database/         # Graph knowledge management
│   ├── __init__.py         # GraphDatabase class
│   └── managers/           # Graph operation managers
├── models/                 # AI model integrations
│   ├── __init__.py         # Model selection
│   ├── chat_model.py       # LLM implementations
│   └── rerank_model.py     # Reranking models
├── tools/                  # External tool integrations
│   ├── __init__.py
│   ├── ocr.py             # OCR processing
│   └── oneke.py           # Custom tool
├── utils/                  # Utility functions
│   ├── logging.py         # Logging configuration
│   ├── web_search.py      # Web search integration
│   └── prompts.py         # Prompt templates
└── static/                 # Static configuration files
    ├── config.json        # Default configuration
    └── models.yaml        # Model definitions
```

### Development Workflow

#### 1. Code Organization

**Follow these principles:**
- **Modular Design**: Each component has a single responsibility
- **Configuration-Driven**: Use AgentConfig for all settings
- **Error Handling**: Comprehensive error handling with logging
- **Type Hints**: Use Python type hints for better code clarity

#### 2. Adding New Features

**For new core components:**
```python
# ai_engine/core/my_component.py
from ai_engine.utils.logging import logger
from ai_engine.configs.agent import AgentConfig

class MyComponent:
    def __init__(self, agent_config: AgentConfig):
        self.config = agent_config
        logger.info("MyComponent initialized")
    
    def process(self, input_data):
        """Process input data"""
        logger.debug(f"Processing: {input_data}")
        # Implementation here
        return result
```

**For new agents:**
```python
# ai_engine/agents/my_agent/agent.py
from ai_engine.agents.base import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "my_agent"
        self.description = "My custom agent"
    
    def process(self, message, context):
        # Agent logic here
        return response

# Register in ai_engine/agents/__init__.py
from ai_engine.agents.my_agent import MyAgent
agent_manager.add_agent("my_agent", MyAgent)
```

**For new tools:**
```python
# ai_engine/tools/my_tool.py
from ai_engine.agents.tools_factory import regist_tool
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    input_text: str = Field(description="Input text to process")

@regist_tool(
    title="My Custom Tool",
    description="Description of what the tool does",
    args_schema=MyToolInput
)
def my_tool(input_text: str) -> str:
    """Process input text with my custom logic"""
    result = f"Processed: {input_text}"
    return result
```

#### 3. Configuration Management

**Adding new configuration options:**
```python
# In AgentConfig.__init__()
self.add_item("my_new_option", "default_value", 
              des="Description of the option",
              choices=["option1", "option2"])  # Optional
```

**Using configuration in code:**
```python
def my_function():
    config = AgentConfig()
    if config.my_new_option == "option1":
        # Do something
        pass
```

#### 4. Database Integration

**Working with Knowledge Base:**
```python
from ai_engine import knowledge_base

# Add document
result = knowledge_base.add_file(
    db_id="my_database",
    file_path="/path/to/document.pdf"
)

# Query knowledge base
results = knowledge_base.query(
    query="search query",
    db_id="my_database",
    top_k=10
)
```

**Working with Graph Database:**
```python
from ai_engine import graph_db

# Get related nodes
nodes = graph_db.get_sample_nodes("entity_name", limit=10)

# Format results
formatted = graph_db.format_query_results(nodes)
```

## 🧪 Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=ai_engine --cov-report=html

# Run specific test file
pytest tests/test_retriever.py

# Run with verbose output
pytest -v -s
```

### Writing Tests

**Test structure:**
```python
# tests/test_my_component.py
import pytest
from ai_engine.core.my_component import MyComponent
from ai_engine.configs.agent import AgentConfig

class TestMyComponent:
    def setup_method(self):
        """Setup before each test"""
        self.config = AgentConfig()
        self.component = MyComponent(self.config)
    
    def test_process_happy_path(self):
        """Test successful processing"""
        result = self.component.process("test input")
        assert result is not None
        assert "expected" in result
    
    def test_process_error_handling(self):
        """Test error handling"""
        with pytest.raises(ValueError):
            self.component.process(None)
```

**Mocking dependencies:**
```python
from unittest.mock import Mock, patch

@patch('ai_engine.models.select_model')
def test_with_mocked_model(mock_select_model):
    mock_model = Mock()
    mock_model.generate_response.return_value = "mocked response"
    mock_select_model.return_value = mock_model
    
    # Test code here
```

### Integration Testing

**Testing with real services:**
```python
# tests/integration/test_knowledge_base.py
import pytest
from ai_engine import knowledge_base

@pytest.mark.integration
class TestKnowledgeBaseIntegration:
    def test_add_and_query_document(self):
        """Test full document lifecycle"""
        # Add document
        result = knowledge_base.add_file("test_db", "test_document.txt")
        assert result["status"] == "success"
        
        # Query document
        query_result = knowledge_base.query("test query", "test_db")
        assert len(query_result["results"]) > 0
```

Run integration tests:
```bash
pytest -m integration  # Run only integration tests
pytest -m "not integration"  # Skip integration tests
```

## 🔧 Debugging

### Logging Configuration

```python
# Enable debug logging
import logging
from ai_engine.utils.logging import logger

logger.setLevel(logging.DEBUG)

# Log component behavior
logger.debug("Processing query: %s", query)
logger.info("Retrieved %d results", len(results))
logger.warning("Model response was empty")
logger.error("Failed to process document: %s", error)
```

### Common Debugging Scenarios

**1. Model Connection Issues**
```python
# Test model connectivity
from ai_engine.models import select_model

try:
    model = select_model("openai", "gpt-4")
    response = model.generate_response("Hello")
    print(f"Model working: {response}")
except Exception as e:
    print(f"Model error: {e}")
```

**2. Database Connection Issues**
```python
# Test Milvus connection
from ai_engine.knowledge_database.milvus_manager import MilvusManager

try:
    manager = MilvusManager()
    collections = manager.list_collections()
    print(f"Milvus collections: {collections}")
except Exception as e:
    print(f"Milvus error: {e}")
```

**3. Configuration Issues**
```python
# Debug configuration loading
from ai_engine.configs.agent import AgentConfig

config = AgentConfig()
print(f"Config items: {config._config_items}")
print(f"Provider: {config.provider}")
print(f"Model: {config.model}")
```

### Performance Profiling

```python
# Profile function execution
import cProfile
import pstats

def profile_function():
    # Your code here
    pass

cProfile.run('profile_function()', 'profile_output')
stats = pstats.Stats('profile_output')
stats.sort_stats('cumulative').print_stats(10)
```

## 🚀 Production Deployment

### Docker Deployment

**Build production image:**
```bash
# Build AI Engine container
docker build -t ai-engine:latest .

# Or use docker-compose
cd docker
docker-compose -f docker-compose.prod.yml up -d
```

**Environment configuration for production:**
```bash
# Production .env
ENVIRONMENT=production
LOG_LEVEL=INFO
MILVUS_URI=production-milvus-uri
NEO4J_URI=production-neo4j-uri
```

### Performance Optimization

**1. Model Caching**
```python
# Enable model caching
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_embedding(text):
    return embedding_model.encode(text)
```

**2. Database Connection Pooling**
```python
# Use connection pooling for better performance
from ai_engine.knowledge_database.milvus_manager import MilvusManager

manager = MilvusManager(pool_size=10)
```

**3. Async Processing**
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def process_documents_async(documents):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=4) as executor:
        tasks = [
            loop.run_in_executor(executor, process_document, doc)
            for doc in documents
        ]
        results = await asyncio.gather(*tasks)
    return results
```

## 🔒 Security Best Practices

### API Key Management

```python
# Never commit API keys to code
# Use environment variables
import os

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")
```

### Input Validation

```python
from pydantic import BaseModel, validator

class QueryInput(BaseModel):
    query: str
    db_id: str
    
    @validator('query')
    def query_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v
    
    @validator('db_id')
    def valid_db_id(cls, v):
        if not v.isalnum():
            raise ValueError('Database ID must be alphanumeric')
        return v
```

### Error Handling

```python
def safe_process(func, *args, **kwargs):
    """Safely execute function with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {e}")
        return {"status": "error", "message": str(e)}
```

## 🤝 Contributing Guidelines

### Code Style

**Follow PEP 8 and use these tools:**
```bash
# Install formatting tools
pip install black isort flake8

# Format code
black ai_engine/
isort ai_engine/

# Check style
flake8 ai_engine/
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature description"

# Push and create PR
git push origin feature/my-new-feature
```

**Commit message format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Adding tests

### Pull Request Process

1. **Fork the repository**
2. **Create feature branch**
3. **Write tests for new functionality**
4. **Ensure all tests pass**
5. **Update documentation**
6. **Submit pull request**

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No breaking changes (or clearly documented)
- [ ] Performance impact considered
- [ ] Security implications reviewed

## 🆘 Troubleshooting

### Common Issues

**1. Import errors**
```bash
# Ensure PYTHONPATH includes ai_engine
export PYTHONPATH="${PYTHONPATH}:/path/to/neuroplex"
```

**2. Model loading failures**
```bash
# Check API keys
echo $OPENAI_API_KEY

# Test connectivity
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

**3. Database connection issues**
```bash
# Check Milvus
curl http://localhost:19530/health

# Check Neo4j
curl http://localhost:7474/browser
```

**4. Memory issues**
```python
# Monitor memory usage
import psutil
print(f"Memory usage: {psutil.virtual_memory().percent}%")
```

### Getting Help

- **Documentation**: Check this guide and API reference
- **Issues**: Create GitHub issue with detailed description
- **Logs**: Include relevant log output
- **Environment**: Specify Python version, OS, and dependencies

---

This development guide provides the foundation for working with the AI Engine. For specific implementation details, refer to the API reference and code examples. 