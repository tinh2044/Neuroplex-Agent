# AI Engine Documentation

Welcome to the AI Engine documentation! This comprehensive guide will help you understand, configure, deploy, and extend the AI Engine - a powerful multi-model AI platform with knowledge management capabilities.

## 🚀 Quick Start

The AI Engine is the core processing component of Neuroplex, providing:
- **Multi-model AI Support**: OpenAI, Anthropic, Google, Ollama, and more
- **Knowledge Management**: Vector search with Milvus and graph database with Neo4j
- **Agent Framework**: Modular agent system for custom implementations
- **Tools Integration**: Web search, OCR, and external service connectors

### Instant Setup

```bash
# 1. Configure environment
cp ai_engine/.env.example ai_engine/.env
# Edit .env with your API keys

# 2. Start services
cd docker
docker-compose up -d

# 3. Verify installation
curl http://localhost:5000/health
```

## 📚 Documentation Structure

### Core Documentation
- **[Architecture](ARCHITECTURE.md)** - System design and component overview
- **[API Reference](API_REFERENCE.md)** - Complete API documentation
- **[Configuration](CONFIGURATION.md)** - Configuration options and settings

### Getting Started
- **[Development Guide](DEVELOPMENT_GUIDE.md)** - Setup development environment
- **[User Guide](USER_GUIDE.md)** - End-user functionality guide
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment

### Examples & Extensions
- **[Code Examples](examples/)** - Practical usage examples
- **[Custom Agents](examples/custom_agents.py)** - Building custom agents
- **[Knowledge Base Operations](examples/knowledge_base_ops.py)** - Working with knowledge base
- **[Graph Database Operations](examples/graph_database_ops.py)** - Graph database usage

## 🏗️ System Overview

```
AI Engine Architecture
├── Core Components
│   ├── Retriever          # Data retrieval and query processing
│   ├── Operators           # Query enhancement (HyDE, etc.)
│   └── Indexing           # Document processing and chunking
├── Knowledge Management
│   ├── Knowledge Base      # Vector storage (Milvus)
│   └── Graph Database      # Relationship mapping (Neo4j)
├── Agent Framework
│   ├── ChatBot Agent       # Conversational AI
│   ├── ReAct Agent         # Reasoning and Acting
│   └── Agent Manager       # Agent lifecycle management
├── Models
│   ├── Chat Models         # LLM integrations
│   ├── Embedding Models    # Vector embeddings
│   └── Rerank Models       # Result reranking
└── Tools & Utilities
    ├── Web Search          # Tavily integration
    ├── OCR Processing      # Document text extraction
    └── Utils               # Logging, prompts, helpers
```

## 🔧 Key Features

### Multi-Model Support
- **Commercial APIs**: OpenAI GPT-4, Anthropic Claude, Google models
- **Chinese Models**: Qwen, DeepSeek, Baichuan
- **Local Deployment**: Ollama integration for privacy
- **Custom Models**: Flexible custom model integration

### Knowledge Management
- **Vector Search**: Semantic search with multiple embedding models
- **Graph Relationships**: Neo4j-powered knowledge graphs
- **Document Processing**: PDF, TXT, MD, DOCX, images with OCR
- **Query Enhancement**: HyDE, query rewriting, entity recognition

### Agent Framework
- **Modular Design**: Pluggable agent architecture
- **Built-in Agents**: ChatBot, ReAct (Reasoning + Acting)
- **Custom Extensions**: Easy custom agent development
- **Tool Integration**: Extensible tool ecosystem

## 🎯 Common Use Cases

### 1. Document Q&A System
```python
from ai_engine import knowledge_base, retriever

# Add documents
knowledge_base.add_file("my_db", "/path/to/document.pdf")

# Query with context
query = "What are the key findings?"
result = retriever(query, history=[], meta={"db_id": "my_db"})
```

### 2. Multi-Source Information Retrieval
```python
# Enable multiple sources
meta = {
    "db_id": "my_kb",
    "use_graph": True,
    "use_web": True
}

# Get comprehensive results
response = retriever(query, history, meta)
# Results include: knowledge base + graph + web search
```

### 3. Custom Agent Development
```python
from ai_engine.agents import BaseAgent

class MyCustomAgent(BaseAgent):
    def process(self, message, context):
        # Your custom logic here
        return response
```

## 🚦 Quick Links

- **[Installation & Setup](DEVELOPMENT_GUIDE.md#installation)** - Get started in 5 minutes
- **[Configuration Options](CONFIGURATION.md)** - Customize your setup
- **[API Endpoints](API_REFERENCE.md)** - Complete API reference
- **[Troubleshooting](DEVELOPMENT_GUIDE.md#troubleshooting)** - Common issues and solutions

## 🤝 Contributing

We welcome contributions! Please check our development guide for:
- Code style guidelines
- Testing requirements
- Pull request process
- Issue reporting

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

---

**Need Help?** 
- 📖 Check the [User Guide](USER_GUIDE.md) for detailed functionality
- 🔧 See [Development Guide](DEVELOPMENT_GUIDE.md) for technical setup
- 🏗️ Read [Architecture](ARCHITECTURE.md) for system design 