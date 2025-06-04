# AI Engine Configuration Guide

This guide covers all configuration options for the AI Engine, from basic setup to advanced customization.

## 🎯 Configuration Overview

The AI Engine uses a layered configuration system:
```
Environment Variables → .env File → YAML Config → Runtime Config → Default Values
```

### Configuration Sources

1. **Environment Variables**: System-level settings
2. **`.env` File**: Local environment configuration
3. **YAML Files**: Model and feature definitions
4. **Runtime Config**: Dynamic settings via API
5. **Default Values**: Built-in fallbacks

## ⚙️ Environment Configuration

### Required Environment Variables

#### Core Settings

```bash
# ai_engine/.env

# Model Storage
MODEL_DIR=/path/to/models                    # Local model storage directory

# Database Connections
MILVUS_URI=http://localhost:19530            # Vector database
NEO4J_URI=bolt://localhost:7687              # Graph database
NEO4J_AUTH=neo4j/password                    # Graph database credentials
```

#### AI Model APIs

**OpenAI Configuration:**
```bash
OPENAI_API_KEY=sk-your-openai-key
OPENAI_API_BASE=https://api.openai.com/v1   # Optional: custom endpoint
OPENAI_ORG_ID=org-your-organization-id      # Optional: organization
```

**Anthropic Configuration:**
```bash
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
ANTHROPIC_API_BASE=https://api.anthropic.com # Optional: custom endpoint
```

**Chinese Model Providers:**
```bash
# DeepSeek
DEEPSEEK_API_KEY=sk-your-deepseek-key
DEEPSEEK_API_BASE=https://api.deepseek.com

# Qwen/Alibaba
QWEN_API_KEY=sk-your-qwen-key
QWEN_API_BASE=https://dashscope.aliyuncs.com

# Baichuan
BAICHUAN_API_KEY=your-baichuan-key
BAICHUAN_API_BASE=https://api.baichuan-ai.com
```

**Local Model Services:**
```bash
# Ollama
OLLAMA_HOST=http://localhost:11434          # Local Ollama server

# Custom OpenAI-compatible APIs
CUSTOM_API_BASE=http://your-server:8000/v1
CUSTOM_API_KEY=your-custom-key
```

#### External Services

```bash
# Web Search (Tavily)
TAVILY_API_KEY=tvly-your-tavily-key

# Other APIs
GOOGLE_API_KEY=your-google-key              # For Google models
HUGGINGFACE_TOKEN=hf_your-token             # For HuggingFace models
```

#### Optional Settings

```bash
# Logging
LOG_LEVEL=INFO                              # DEBUG, INFO, WARNING, ERROR
LOG_FILE=/path/to/logs/ai_engine.log

# Performance
MAX_WORKERS=4                               # Concurrent processing
CACHE_SIZE=1000                             # Model cache size
REQUEST_TIMEOUT=30                          # API request timeout (seconds)

# Security
API_RATE_LIMIT=100                          # Requests per minute
ALLOWED_ORIGINS=http://localhost:3000       # CORS origins
```

## 📋 Agent Configuration

### AgentConfig Class

The `AgentConfig` class manages all runtime configuration:

```python
from ai_engine.configs.agent import AgentConfig

config = AgentConfig()
```

### Core Configuration Items

#### Model Settings

```python
# Primary model configuration
config.provider = "openai"                  # Model provider
config.model = "gpt-4"                      # Model name
config.embed_model = "openai/text-embedding-ada-002"  # Embedding model
config.ranker = "ollama/bge-reranker-v2-m3" # Reranking model
```

**Available Providers:**
- `openai`: OpenAI models (GPT-4, GPT-3.5-turbo)
- `anthropic`: Anthropic Claude models
- `ollama`: Local Ollama models
- `deepseek`: DeepSeek models
- `qwen`: Qwen/Alibaba models
- `google`: Google models (Gemini)
- `huggingface`: HuggingFace models
- `custom`: Custom model configurations

#### Feature Flags

```python
# Enable/disable major features
config.enable_kb = True                     # Knowledge base
config.enable_graph = True                  # Graph database
config.enable_websearch = True              # Web search
config.enable_rerank = False                # Result reranking
```

#### Query Enhancement

```python
# Query processing modes
config.query_mode = "off"                   # off, on, hyde

# Query enhancement options:
# - "off": No query enhancement
# - "on": Basic query rewriting
# - "hyde": HyDE (Hypothetical Document Embeddings)
```

#### Processing Settings

```python
# Text processing
config.chunk_size = 500                     # Document chunk size
config.chunk_overlap = 50                   # Chunk overlap
config.max_tokens = 2000                    # Max response tokens

# Search parameters
config.top_k = 10                           # Top K search results
config.distance_threshold = 0.5             # Similarity threshold
config.rerank_threshold = 0.1               # Reranking threshold
```

#### System Settings

```python
# Workspace and paths
config.workspace = "saves"                  # Working directory
config.device = "cpu"                       # cpu, cuda

# File paths
config.config_path = "ai_engine/static/config.json"
config.model_path = "ai_engine/static/models.yaml"
```

### Configuration File Management

#### Loading Configuration

```python
# Load from file
config = AgentConfig(config_path="custom_config.json")
config.load()

# Load with custom paths
config = AgentConfig(
    config_path="configs/agent.json",
    model_path="configs/models.yaml",
    private_path="configs/private.yml"
)
```

#### Saving Configuration

```python
# Save current configuration
config.save()

# Save to specific path
config.config_path = "new_config.json"
config.save()
```

#### Configuration Validation

```python
# Add configuration item with validation
config.add_item(
    key="custom_setting",
    default="default_value",
    des="Description of the setting",
    choices=["option1", "option2", "option3"]  # Valid choices
)

# Validate configuration
try:
    config.validate()
    print("Configuration is valid")
except ValueError as e:
    print(f"Configuration error: {e}")
```

## 🤖 Model Configuration

### Model Definition Files

#### `ai_engine/static/models.yaml`

Main model definitions:

```yaml
MODEL_NAMES:
  openai:
    default: "gpt-4"
    models:
      - "gpt-4"
      - "gpt-4-turbo"
      - "gpt-3.5-turbo"
    env: ["OPENAI_API_KEY"]
    base_url: "https://api.openai.com/v1"
    
  anthropic:
    default: "claude-3-sonnet-20240229"
    models:
      - "claude-3-sonnet-20240229"
      - "claude-3-haiku-20240307"
    env: ["ANTHROPIC_API_KEY"]
    base_url: "https://api.anthropic.com"
    
  ollama:
    default: "llama3.1:8b"
    list_models: true  # Auto-discover available models
    base_url: "http://localhost:11434"

EMBED_MODEL_INFO:
  openai:
    default: "text-embedding-ada-002"
    models:
      - "text-embedding-ada-002"
      - "text-embedding-3-small"
      - "text-embedding-3-large"
    
  ollama:
    default: "bge-m3"
    models:
      - "bge-m3"
      - "nomic-embed-text"

RERANKER_LIST:
  ollama:
    default: "bge-reranker-v2-m3"
    models:
      - "bge-reranker-v2-m3"
```

#### `ai_engine/static/models.private.yml`

Private model configurations (not committed to version control):

```yaml
MODEL_NAMES:
  custom_provider:
    default: "custom-model"
    models:
      - "custom-model-1"
      - "custom-model-2"
    env: ["CUSTOM_API_KEY"]
    base_url: "https://your-custom-api.com/v1"
    api_key: "your-secret-key"

EMBED_MODEL_INFO:
  custom_embed:
    default: "custom-embedding"
    models:
      - "custom-embedding"
```

### Custom Model Integration

#### Adding New Model Provider

1. **Update models.yaml:**
```yaml
MODEL_NAMES:
  my_provider:
    default: "my-model"
    models: ["my-model", "my-other-model"]
    env: ["MY_PROVIDER_API_KEY"]
    base_url: "https://api.myprovider.com/v1"
```

2. **Add Environment Variable:**
```bash
MY_PROVIDER_API_KEY=your-api-key
```

3. **Update Model Selection Logic (optional):**
```python
# In ai_engine/models/__init__.py
def select_model(model_provider=None, model_name=None):
    # ... existing code ...
    
    if model_provider == "my_provider":
        return MyProviderModel(model_name, model_info)
```

#### Custom Model Class

```python
# ai_engine/models/my_provider.py
from ai_engine.models.chat_model import OpenAIBase

class MyProviderModel(OpenAIBase):
    def __init__(self, model_name, api_key=None, base_url=None):
        super().__init__(api_key, base_url, model_name)
        # Custom initialization
    
    def generate_response(self, prompt, **kwargs):
        # Custom implementation
        pass
```

## 🔧 Advanced Configuration

### Runtime Configuration

#### Dynamic Configuration Updates

```python
# Update configuration at runtime
from ai_engine import agent_config

# Change model provider
agent_config.provider = "anthropic"
agent_config.model = "claude-3-sonnet-20240229"

# Update feature flags
agent_config.enable_websearch = False
agent_config.query_mode = "hyde"

# Save changes
agent_config.save()
```

#### Configuration via API

```python
# RESTful configuration updates
import requests

config_update = {
    "provider": "openai",
    "model": "gpt-4",
    "enable_kb": True,
    "top_k": 15
}

response = requests.post(
    "http://localhost:5000/api/config",
    json=config_update
)
```

### Environment-Specific Configuration

#### Development Configuration

```bash
# .env.development
ENVIRONMENT=development
LOG_LEVEL=DEBUG
ENABLE_DEBUG_TOOLS=true

# Use local services
MILVUS_URI=http://localhost:19530
NEO4J_URI=bolt://localhost:7687

# Use free/local models for development
DEFAULT_PROVIDER=ollama
DEFAULT_MODEL=llama3.1:8b
```

#### Production Configuration

```bash
# .env.production
ENVIRONMENT=production
LOG_LEVEL=INFO
ENABLE_DEBUG_TOOLS=false

# Use production services
MILVUS_URI=https://prod-milvus.example.com
NEO4J_URI=bolt://prod-neo4j.example.com:7687

# Use production-grade models
DEFAULT_PROVIDER=openai
DEFAULT_MODEL=gpt-4
```

#### Testing Configuration

```bash
# .env.test
ENVIRONMENT=test
LOG_LEVEL=WARNING

# Use test databases
MILVUS_URI=http://test-milvus:19530
NEO4J_URI=bolt://test-neo4j:7687

# Use mock models for testing
DEFAULT_PROVIDER=mock
DEFAULT_MODEL=mock-model
```

### Performance Configuration

#### Database Optimization

```python
# Milvus configuration
MILVUS_CONFIG = {
    "collection_params": {
        "metric_type": "COSINE",        # Similarity metric
        "index_type": "IVF_FLAT",       # Index type
        "nlist": 1024                   # Index parameter
    },
    "search_params": {
        "nprobe": 10                    # Search parameter
    }
}

# Neo4j configuration
NEO4J_CONFIG = {
    "connection_pool_size": 50,
    "max_retry_time": 30,
    "initial_retry_delay": 1,
    "max_retry_delay": 16
}
```

#### Model Optimization

```python
# Model performance settings
MODEL_CONFIG = {
    "temperature": 0.7,                 # Response randomness
    "max_tokens": 2000,                 # Response length limit
    "top_p": 0.9,                       # Nucleus sampling
    "frequency_penalty": 0.0,           # Repetition penalty
    "presence_penalty": 0.0,            # Topic penalty
    "timeout": 30,                      # Request timeout
    "max_retries": 3                    # Retry attempts
}
```

#### Caching Configuration

```python
# Enable various caching layers
CACHE_CONFIG = {
    "enable_model_cache": True,         # Cache model responses
    "enable_embedding_cache": True,     # Cache embeddings
    "enable_search_cache": True,        # Cache search results
    "cache_ttl": 3600,                  # Cache time-to-live (seconds)
    "max_cache_size": 1000              # Maximum cache entries
}
```

## 🔒 Security Configuration

### API Security

```bash
# Authentication
JWT_SECRET_KEY=your-jwt-secret-key
API_KEY_REQUIRED=true
ADMIN_API_KEY=your-admin-key

# Rate limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000

# CORS settings
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
ALLOWED_METHODS=GET,POST,PUT,DELETE
ALLOWED_HEADERS=Content-Type,Authorization
```

### Data Security

```bash
# Encryption
ENCRYPTION_KEY=your-encryption-key
ENCRYPT_SENSITIVE_DATA=true

# Data retention
LOGS_RETENTION_DAYS=30
CACHE_RETENTION_HOURS=24
USER_DATA_RETENTION_DAYS=365

# Privacy
ANONYMIZE_LOGS=true
ENABLE_GDPR_COMPLIANCE=true
DATA_EXPORT_ENABLED=true
```

### Model Security

```python
# Content filtering
CONTENT_FILTER_CONFIG = {
    "enable_input_filter": True,        # Filter user inputs
    "enable_output_filter": True,       # Filter AI responses
    "blocked_keywords": ["sensitive"],  # Blocked terms
    "max_input_length": 10000,          # Input length limit
    "enable_pii_detection": True        # Detect personal info
}

# Model access control
MODEL_ACCESS_CONFIG = {
    "require_api_key": True,            # Require API key
    "allowed_models": ["gpt-4"],        # Restrict model access
    "rate_limit_per_model": 50,         # Per-model rate limits
    "enable_usage_tracking": True       # Track model usage
}
```

## 📊 Monitoring Configuration

### Logging Configuration

```python
# Structured logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "json": {
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter"
        }
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler"
        },
        "file": {
            "level": "DEBUG",
            "formatter": "json",
            "class": "logging.FileHandler",
            "filename": "ai_engine.log"
        }
    },
    "loggers": {
        "ai_engine": {
            "handlers": ["default", "file"],
            "level": "DEBUG",
            "propagate": False
        }
    }
}
```

### Metrics Collection

```bash
# Prometheus metrics
ENABLE_METRICS=true
METRICS_PORT=9090
METRICS_ENDPOINT=/metrics

# Health check
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10
ENABLE_HEALTH_ENDPOINT=true
```

## 🛠️ Configuration Management

### Configuration Validation

```python
def validate_configuration():
    """Validate configuration settings"""
    config = AgentConfig()
    
    # Check required environment variables
    required_vars = ["OPENAI_API_KEY", "MILVUS_URI", "NEO4J_URI"]
    for var in required_vars:
        if not os.getenv(var):
            raise ValueError(f"Required environment variable {var} not set")
    
    # Validate model configuration
    if config.provider not in config.models:
        raise ValueError(f"Provider {config.provider} not configured")
    
    # Validate feature dependencies
    if config.enable_rerank and not config.ranker:
        raise ValueError("Reranking enabled but no ranker configured")
    
    return True
```

### Configuration Migration

```python
def migrate_configuration(old_config, new_version):
    """Migrate configuration to new version"""
    if old_config.get("version", "1.0") < "2.0":
        # Migrate v1.0 to v2.0
        old_config["query_enhancement"] = old_config.pop("query_mode", "off")
        old_config["version"] = "2.0"
    
    return old_config
```

### Configuration Backup

```python
def backup_configuration():
    """Backup current configuration"""
    import datetime
    import shutil
    
    config = AgentConfig()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"config_backup_{timestamp}.json"
    
    shutil.copy(config.config_path, backup_path)
    return backup_path
```

## 📋 Configuration Examples

### Minimal Configuration

```bash
# Minimal .env for development
OPENAI_API_KEY=sk-your-key
```

```json
// Minimal config.json
{
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "enable_kb": false,
    "enable_graph": false,
    "enable_websearch": false
}
```

### Full-Featured Configuration

```bash
# Comprehensive .env
MODEL_DIR=/models
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
TAVILY_API_KEY=tvly-your-tavily-key
MILVUS_URI=http://localhost:19530
NEO4J_URI=bolt://localhost:7687
NEO4J_AUTH=neo4j/password
LOG_LEVEL=INFO
```

```json
// Comprehensive config.json
{
    "provider": "openai",
    "model": "gpt-4",
    "embed_model": "openai/text-embedding-ada-002",
    "ranker": "ollama/bge-reranker-v2-m3",
    "enable_kb": true,
    "enable_graph": true,
    "enable_websearch": true,
    "enable_rerank": true,
    "query_mode": "hyde",
    "top_k": 10,
    "distance_threshold": 0.5,
    "rerank_threshold": 0.1,
    "chunk_size": 500,
    "chunk_overlap": 50,
    "max_tokens": 2000
}
```

### Production Configuration

```bash
# Production .env
ENVIRONMENT=production
LOG_LEVEL=WARNING
OPENAI_API_KEY=sk-prod-key
MILVUS_URI=https://prod-milvus.company.com
NEO4J_URI=bolt://prod-neo4j.company.com:7687
NEO4J_AUTH=prod_user/secure_password
RATE_LIMIT_PER_MINUTE=200
ENABLE_METRICS=true
```

---

This configuration guide provides comprehensive coverage of all AI Engine configuration options. For implementation details, see the [Development Guide](DEVELOPMENT_GUIDE.md) and [API Reference](API_REFERENCE.md). 