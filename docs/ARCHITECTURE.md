# AI Engine Architecture

This document provides a comprehensive overview of the AI Engine architecture, explaining how different components work together to deliver a powerful AI platform with knowledge management capabilities.

## 🏗️ System Overview

The AI Engine is designed with a modular, scalable architecture that supports multiple AI models, knowledge sources, and agent types. The system follows a layered approach with clear separation of concerns.

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Vue.js)                      │
├─────────────────────────────────────────────────────────────┤
│                    Backend (FastAPI)                       │
├─────────────────────────────────────────────────────────────┤
│                      AI Engine                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │    Core     │ │   Agents    │ │      Models         │   │
│  │ Components  │ │ Framework   │ │   Management        │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│           Knowledge Management Layer                        │
│  ┌─────────────────┐         ┌─────────────────────────┐   │
│  │ Vector Database │         │    Graph Database       │   │
│  │    (Milvus)     │         │      (Neo4j)           │   │
│  └─────────────────┘         └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Core Components

### 1. Retriever (`ai_engine/core/retriever.py`)

The Retriever is the central orchestrator for data retrieval operations.

**Key Responsibilities:**
- **Query Processing**: Handles user queries and coordinates retrieval from multiple sources
- **Multi-Source Integration**: Combines results from knowledge base, graph database, and web search
- **Query Enhancement**: Implements query rewriting and HyDE (Hypothetical Document Embeddings)
- **Entity Recognition**: Extracts entities for graph database queries

**Architecture:**
```python
class Retriever:
    def __init__(self, agent_config, graph_db, knowledge_base):
        self._agent_config = agent_config
        self._graph_database = graph_db
        self._knowledge_base = knowledge_base
        
    def retrieval(self, query, history, meta):
        # Orchestrates all retrieval operations
        refs = {
            "entities": self.reco_entities(query, history, refs),
            "knowledge_base": self.query_knowledgebase(query, history, refs),
            "graph_base": self.query_graph(query, history, refs),
            "web_search": self.query_web(query, history, refs)
        }
        return refs
```

### 2. Operators (`ai_engine/core/operators.py`)

Operators implement query enhancement techniques.

**HyDE Operator:**
- Generates hypothetical documents that would answer the query
- Uses these documents to improve retrieval relevance
- Implements the HyDE research paper methodology

### 3. Indexing (`ai_engine/core/indexing.py`)

Handles document processing and text chunking.

**Features:**
- **Smart Chunking**: Adaptive text segmentation
- **Multi-format Support**: PDF, TXT, MD, DOCX, images
- **Metadata Preservation**: Maintains document structure information

## 🧠 Knowledge Management Layer

### Vector Database (Milvus)

**Purpose**: Semantic search through vector embeddings

**Components:**
- **Embedding Manager**: Generates and manages text embeddings
- **Collection Manager**: Organizes documents into searchable collections
- **Query Engine**: Performs similarity search with configurable thresholds

**Data Flow:**
```
Document → Chunking → Embedding → Vector Storage → Similarity Search
```

### Graph Database (Neo4j)

**Purpose**: Relationship mapping and graph traversal

**Components:**
- **Entity Extraction**: Identifies entities from text
- **Relationship Mapping**: Creates connections between entities
- **Graph Traversal**: Finds related information through graph paths
- **Visualization**: Provides interactive graph exploration

**Graph Structure:**
```
(Entity)-[RELATIONSHIP]->(Entity)
(Beijing)-[CAPITAL_OF]->(China)
(Python)-[IS_A]->(Programming Language)
```

## 🤖 Agent Framework

### Agent Manager (`ai_engine/agents/__init__.py`)

Central registry for managing all agent types.

```python
class AgentManager:
    def __init__(self):
        self.agents = {}
    
    def add_agent(self, agent_id, agent_class):
        self.agents[agent_id] = agent_class
    
    def get_runnable_agent(self, agent_id, **kwargs):
        agent_class = self.get_agent(agent_id)
        return agent_class()
```

### Built-in Agents

**1. ChatBot Agent (`ai_engine/agents/chatbot/`)**
- General conversational AI
- Context-aware responses
- Memory management

**2. ReAct Agent (`ai_engine/agents/react/`)**
- Reasoning and Acting paradigm
- Tool usage capabilities
- Multi-step problem solving

### Agent Lifecycle

```
Registration → Initialization → Configuration → Execution → Cleanup
```

## 🔧 Model Management

### Model Selection (`ai_engine/models/__init__.py`)

**Supported Providers:**
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude models
- **Local**: Ollama integration
- **Chinese**: Qwen, DeepSeek
- **Custom**: User-defined models

**Selection Logic:**
```python
def select_model(model_provider=None, model_name=None):
    if model_provider == "openai":
        return OpenModel(model_name)
    elif model_provider == "ollama":
        return OllamaModel(model_name)
    elif model_provider == "custom":
        return CustomModel(model_info)
    else:
        return OpenAIBase(api_key, base_url, model_name)
```

### Model Types

**1. Chat Models**
- Handle conversational interactions
- Support streaming responses
- Context window management

**2. Embedding Models**
- Generate vector representations
- Support multiple embedding providers
- Configurable dimensions

**3. Rerank Models**
- Improve search result relevance
- Post-processing optimization
- Threshold-based filtering

## 🛠️ Tools Integration

### Web Search (`ai_engine/utils/web_search.py`)

**Features:**
- Tavily API integration
- Configurable result count
- Error handling and fallbacks

### OCR Processing (`ai_engine/tools/ocr.py`)

**Capabilities:**
- EasyOCR integration
- PaddleOCR support
- Multi-language text extraction
- Image preprocessing

### Tools Factory (`ai_engine/agents/tools_factory.py`)

**Purpose**: Dynamic tool registration and management

```python
@regist_tool(title="Knowledge Base Search", description="Search knowledge base")
def search_knowledge_base(query: str, db_id: str):
    return knowledge_base.query(query, db_id)
```

## ⚙️ Configuration Management

### Agent Configuration (`ai_engine/configs/agent.py`)

**Key Features:**
- **Centralized Settings**: Single configuration point
- **Environment Integration**: Automatic .env loading
- **Model Configuration**: Dynamic model loading from YAML
- **Validation**: Type checking and constraint validation

**Configuration Hierarchy:**
```
Environment Variables → .env File → YAML Config → Default Values
```

### Configuration Items

```python
class AgentConfig(BaseConfig):
    def __init__(self):
        self.add_item("provider", "ollama", choices=["ollama", "openai", ...])
        self.add_item("model", "llama3.1:8b", des="Model name")
        self.add_item("enable_kb", True, des="Whether to use knowledge base")
        self.add_item("enable_graph", True, des="Whether to use graph")
        self.add_item("enable_websearch", True, des="Whether to use web search")
```

## 🔄 Data Flow

### Query Processing Flow

```
1. User Query → 2. Entity Recognition → 3. Query Rewriting → 4. Multi-Source Retrieval
                                                                  ├── Knowledge Base
                                                                  ├── Graph Database  
                                                                  └── Web Search
5. Result Fusion → 6. Reranking → 7. Response Generation → 8. User Response
```

### Document Processing Flow

```
1. Document Upload → 2. Format Detection → 3. Text Extraction → 4. Chunking
5. Embedding Generation → 6. Vector Storage → 7. Metadata Indexing → 8. Search Ready
```

## 🚀 Scalability Considerations

### Horizontal Scaling

**Vector Database**: Milvus supports distributed deployment
**Graph Database**: Neo4j clustering for high availability
**Model Serving**: Load balancing across multiple model instances

### Performance Optimization

**Caching**: Results caching for frequently accessed data
**Async Processing**: Non-blocking operations for better throughput
**Connection Pooling**: Efficient database connection management

## 🔒 Security Architecture

### API Security
- Token-based authentication
- Request rate limiting
- Input validation and sanitization

### Data Security
- Encrypted connections to databases
- Secure API key management
- Privacy-preserving local model options

## 🎯 Extension Points

### Custom Agents
- Implement `BaseAgent` interface
- Register through `AgentManager`
- Configure through agent configuration

### Custom Tools
- Use `@regist_tool` decorator
- Automatic registration and discovery
- Pydantic schema validation

### Custom Models
- Implement model interface
- Add to model configuration
- Support for custom API endpoints

## 📊 Monitoring and Observability

### Logging
- Structured logging with configurable levels
- Component-specific log filtering
- Performance metrics collection

### Health Checks
- Service health monitoring
- Database connectivity checks
- Model availability verification

---

This architecture supports the AI Engine's goals of flexibility, scalability, and extensibility while maintaining clear separation of concerns and ease of development. 