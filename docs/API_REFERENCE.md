# AI Engine API Reference

This document provides comprehensive API documentation for the AI Engine, covering all public interfaces, classes, and functions.

## 📚 Table of Contents

- [Core Components](#core-components)
- [Knowledge Management](#knowledge-management)  
- [Agent Framework](#agent-framework)
- [Model Management](#model-management)
- [Tools & Utilities](#tools--utilities)
- [Configuration](#configuration)

## 🧩 Core Components

### Retriever

The main orchestrator for data retrieval operations.

#### Class: `Retriever`

```python
from ai_engine.core.retriever import Retriever

retriever = Retriever(agent_config, graph_db, knowledge_base)
```

**Parameters:**
- `agent_config` (AgentConfig): Configuration object
- `graph_db` (GraphDatabase): Graph database instance  
- `knowledge_base` (KnowledgeBase): Knowledge base instance

#### Methods

##### `retrieval(query, history, meta)`

Orchestrates multi-source data retrieval.

**Parameters:**
- `query` (str): User query
- `history` (list): Conversation history
- `meta` (dict): Query metadata and options

**Returns:**
- `dict`: Combined results from all sources

**Example:**
```python
meta = {
    "db_id": "my_database",
    "use_graph": True,
    "use_web": True,
    "topK": 10
}

results = retriever.retrieval("What is machine learning?", [], meta)
```

##### `construct_query(query, refs, meta)`

Constructs enhanced query with retrieved context.

**Parameters:**
- `query` (str): Original query
- `refs` (dict): Retrieved references
- `meta` (dict): Query metadata

**Returns:**
- `str`: Enhanced query with context

##### `query_knowledgebase(query, history, refs)`

Queries the vector knowledge base.

**Parameters:**
- `query` (str): Search query
- `history` (list): Conversation history
- `refs` (dict): Query references

**Returns:**
- `dict`: Knowledge base search results

**Response Format:**
```json
{
    "results": [
        {
            "id": "doc_123",
            "entity": {
                "text": "Document content...",
                "metadata": {...}
            },
            "distance": 0.85
        }
    ],
    "all_results": [...],
    "rw_query": "Enhanced query",
    "message": "Success"
}
```

##### `query_graph(query, history, refs)`

Queries the graph database for entity relationships.

**Parameters:**
- `query` (str): Search query
- `history` (list): Conversation history  
- `refs` (dict): Query references containing entities

**Returns:**
- `dict`: Graph query results

**Response Format:**
```json
{
    "results": {
        "nodes": [
            {"id": "entity_1", "name": "Python", "type": "Language"}
        ],
        "edges": [
            {"source": "entity_1", "target": "entity_2", "type": "IS_A"}
        ]
    }
}
```

##### `query_web(query, history, refs)`

Performs web search using external APIs.

**Parameters:**
- `query` (str): Search query
- `history` (list): Conversation history
- `refs` (dict): Query references

**Returns:**
- `dict`: Web search results

##### `rewrite_query(query, history, refs)`

Enhances query using various techniques (HyDE, rewriting).

**Parameters:**
- `query` (str): Original query
- `history` (list): Conversation history
- `refs` (dict): Query references

**Returns:**
- `str`: Rewritten/enhanced query

##### `reco_entities(query, history, refs)`

Extracts named entities from the query.

**Parameters:**
- `query` (str): Input query
- `history` (list): Conversation history
- `refs` (dict): Query references

**Returns:**
- `list`: List of extracted entities

### Operators

#### Class: `HyDEOperator`

Implements Hypothetical Document Embeddings for query enhancement.

```python
from ai_engine.core.operators import HyDEOperator

operator = HyDEOperator()
```

##### `execute(llm_handler, user_question, related_context="")`

**Static Method** - Generates hypothetical document for query enhancement.

**Parameters:**
- `llm_handler` (callable): LLM function for text generation
- `user_question` (str): User's question
- `related_context` (str): Additional context

**Returns:**
- `object`: Generated hypothetical document response

**Example:**
```python
from ai_engine.models import select_model

model = select_model("openai", "gpt-4")
result = HyDEOperator.execute(
    llm_handler=model.generate_response,
    user_question="What is quantum computing?",
    related_context=""
)
```

### Indexing

#### Function: `chunk(text, chunk_size=500, chunk_overlap=50)`

Splits text into chunks for processing.

```python
from ai_engine.core.indexing import chunk

chunks = chunk(
    text="Long document text...",
    chunk_size=500,
    chunk_overlap=50
)
```

**Parameters:**
- `text` (str): Text to chunk
- `chunk_size` (int): Maximum chunk size
- `chunk_overlap` (int): Overlap between chunks

**Returns:**
- `list`: List of text chunks with metadata

## 🧠 Knowledge Management

### KnowledgeBase

Main interface for vector knowledge base operations.

#### Class: `KnowledgeBase`

```python
from ai_engine.knowledge_database import KnowledgeBase

kb = KnowledgeBase(agent_config, kb_db_manager)
```

**Parameters:**
- `agent_config` (AgentConfig): Configuration object
- `kb_db_manager` (KBDBManager): Database manager

#### Methods

##### `add_file(db_id, file_path, **kwargs)`

Adds a document to the knowledge base.

**Parameters:**
- `db_id` (str): Database identifier
- `file_path` (str): Path to the document
- `**kwargs`: Additional options

**Returns:**
- `dict`: Processing result

**Example:**
```python
result = kb.add_file(
    db_id="my_database",
    file_path="/path/to/document.pdf",
    chunk_size=500
)
```

##### `query(query, db_id, **kwargs)`

Searches the knowledge base.

**Parameters:**
- `query` (str): Search query
- `db_id` (str): Database to search
- `**kwargs`: Search options

**Keyword Arguments:**
- `distance_threshold` (float): Similarity threshold (default: 0.5)
- `rerank_threshold` (float): Reranking threshold (default: 0.1)
- `max_query_count` (int): Maximum results (default: 20)
- `top_k` (int): Top K results (default: 10)

**Returns:**
- `dict`: Search results

##### `delete_file(db_id, file_id)`

Removes a file from the knowledge base.

**Parameters:**
- `db_id` (str): Database identifier
- `file_id` (str): File identifier

##### `get_file_info(db_id, file_id)`

Retrieves file information.

**Parameters:**
- `db_id` (str): Database identifier
- `file_id` (str): File identifier

**Returns:**
- `dict`: File metadata and information

##### `create_database(db_id)`

Creates a new knowledge base database.

**Parameters:**
- `db_id` (str): Database identifier

##### `delete_database(db_id)`

Deletes a knowledge base database.

**Parameters:**
- `db_id` (str): Database identifier

### GraphDatabase

Interface for graph database operations.

#### Class: `GraphDatabase`

```python
from ai_engine.graph_database import GraphDatabase

graph_db = GraphDatabase(agent_config)
```

#### Methods

##### `get_sample_nodes(entity, limit=10)`

Retrieves nodes related to an entity.

**Parameters:**
- `entity` (str): Entity name
- `limit` (int): Maximum number of nodes

**Returns:**
- `list`: List of related nodes

##### `format_query_results(results)`

Formats graph query results for display.

**Parameters:**
- `results` (list): Raw query results

**Returns:**
- `dict`: Formatted results with nodes and edges

## 🤖 Agent Framework

### AgentManager

Central registry for managing agents.

#### Class: `AgentManager`

```python
from ai_engine.agents import agent_manager

# Get available agents
agents = agent_manager.agents
```

#### Methods

##### `add_agent(agent_id, agent_class)`

Registers a new agent type.

**Parameters:**
- `agent_id` (str): Unique agent identifier
- `agent_class` (class): Agent class

##### `get_agent(agent_id)`

Retrieves an agent class by ID.

**Parameters:**
- `agent_id` (str): Agent identifier

**Returns:**
- `class`: Agent class

##### `get_runnable_agent(agent_id, **kwargs)`

Creates a runnable agent instance.

**Parameters:**
- `agent_id` (str): Agent identifier
- `**kwargs`: Agent initialization parameters

**Returns:**
- `object`: Agent instance

### Built-in Agents

#### ChatbotAgent

Basic conversational agent.

```python
from ai_engine.agents import ChatbotAgent

agent = ChatbotAgent()
response = agent.process(message, context)
```

#### ReActAgent  

Reasoning and Acting agent with tool usage.

```python
from ai_engine.agents import ReActAgent

agent = ReActAgent()
response = agent.process(message, context)
```

## 🔧 Model Management

### Model Selection

#### Function: `select_model(model_provider=None, model_name=None)`

Selects and initializes an AI model.

```python
from ai_engine.models import select_model

model = select_model(
    model_provider="openai",
    model_name="gpt-4"
)
```

**Parameters:**
- `model_provider` (str): Provider name (openai, ollama, anthropic, etc.)
- `model_name` (str): Model name

**Returns:**
- `object`: Initialized model instance

**Supported Providers:**
- `openai`: OpenAI models (GPT-4, GPT-3.5-turbo)
- `anthropic`: Anthropic Claude models
- `ollama`: Local Ollama models
- `deepseek`: DeepSeek models
- `qwen`: Qwen models
- `custom`: Custom model configurations

### Model Classes

#### BaseModel Interface

All models implement these methods:

##### `generate_response(prompt, **kwargs)`

Generates a response to a prompt.

**Parameters:**
- `prompt` (str): Input prompt
- `**kwargs`: Model-specific options

**Returns:**
- `object`: Model response

##### `stream_response(prompt, **kwargs)`

Generates streaming response.

**Parameters:**
- `prompt` (str): Input prompt
- `**kwargs`: Model-specific options

**Returns:**
- `generator`: Streaming response

## 🛠️ Tools & Utilities

### Tools Registration

#### Decorator: `@regist_tool`

Registers functions as available tools.

```python
from ai_engine.agents.tools_factory import regist_tool

@regist_tool(
    title="Custom Tool",
    description="Description of the tool",
    return_direct=False
)
def my_custom_tool(input_param: str) -> str:
    """Tool implementation"""
    return f"Processed: {input_param}"
```

**Parameters:**
- `title` (str): Human-readable tool name
- `description` (str): Tool description
- `return_direct` (bool): Whether to return results directly
- `args_schema` (BaseModel): Pydantic schema for arguments

### OCR Processing

#### Class: `OcrProcessor`

```python
from ai_engine.tools import OcrProcessor

ocr = OcrProcessor()
text = ocr.process_image("/path/to/image.jpg")
```

#### Methods

##### `process_image(image_path, **kwargs)`

Extracts text from images.

**Parameters:**
- `image_path` (str): Path to image file
- `**kwargs`: Processing options

**Returns:**
- `str`: Extracted text

### Web Search

#### Class: `WebSearcher`

```python
from ai_engine.utils.web_search import WebSearcher

searcher = WebSearcher()
results = searcher.search("query", max_results=5)
```

#### Methods

##### `search(query, max_results=5)`

Performs web search.

**Parameters:**
- `query` (str): Search query
- `max_results` (int): Maximum results

**Returns:**
- `list`: Search results

## ⚙️ Configuration

### AgentConfig

Central configuration management.

#### Class: `AgentConfig`

```python
from ai_engine.configs.agent import AgentConfig

config = AgentConfig()
```

#### Methods

##### `add_item(key, default, des=None, choices=None)`

Adds a configuration item.

**Parameters:**
- `key` (str): Configuration key
- `default` (any): Default value
- `des` (str): Description
- `choices` (list): Valid choices

##### `get(key, default=None)`

Gets a configuration value.

**Parameters:**
- `key` (str): Configuration key
- `default` (any): Default if not found

**Returns:**
- `any`: Configuration value

##### `set(key, value)`

Sets a configuration value.

**Parameters:**
- `key` (str): Configuration key
- `value` (any): Value to set

##### `load()`

Loads configuration from file.

##### `save()`

Saves configuration to file.

### Configuration Items

**Core Settings:**
- `provider` (str): Model provider
- `model` (str): Model name
- `workspace` (str): Working directory

**Feature Flags:**
- `enable_kb` (bool): Enable knowledge base
- `enable_graph` (bool): Enable graph database
- `enable_websearch` (bool): Enable web search
- `enable_rerank` (bool): Enable reranking

**Model Settings:**
- `embed_model` (str): Embedding model
- `ranker` (str): Reranking model
- `query_mode` (str): Query enhancement mode

## 🚨 Error Handling

### Common Exceptions

```python
# Configuration errors
class ConfigurationError(Exception): pass

# Model errors  
class ModelNotFoundError(Exception): pass

# Database errors
class DatabaseError(Exception): pass

# Processing errors
class ProcessingError(Exception): pass
```

### Error Response Format

```json
{
    "status": "error",
    "message": "Error description",
    "code": "ERROR_CODE",
    "details": {...}
}
```

## 📊 Response Formats

### Standard Response

```json
{
    "status": "success",
    "data": {...},
    "message": "Operation completed",
    "metadata": {...}
}
```

### Search Results

```json
{
    "results": [
        {
            "id": "result_id",
            "content": "...",
            "score": 0.95,
            "metadata": {...}
        }
    ],
    "total": 10,
    "query_info": {...}
}
```

---

This API reference covers all major components and interfaces of the AI Engine. For specific implementation details, refer to the source code and examples. 