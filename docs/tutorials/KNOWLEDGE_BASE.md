# Working with Knowledge Base

## Overview

The Knowledge Base is a core component of the AI Engine that enables intelligent document storage, retrieval, and querying using vector embeddings. This tutorial will guide you through setting up, managing, and querying your knowledge base effectively.

## What You'll Learn

- How to set up and configure a knowledge base
- Document ingestion and indexing strategies
- Advanced querying techniques
- Knowledge base management and optimization
- Integration with agents and tools
- Best practices for document organization

## Prerequisites

- AI Engine installed and configured
- Basic understanding of vector databases
- Python 3.8+ environment
- Documents to index (PDF, TXT, DOCX, etc.)

## Knowledge Base Architecture

```
Knowledge Base System
├── Vector Database (Milvus/Chroma)
├── Embedding Models
├── Document Processors
├── Indexing Pipeline
└── Retrieval Engine
```

## Setting Up Your Knowledge Base

### 1. Choose Your Vector Database

#### Option A: Milvus (Recommended for Production)
```bash
# Start Milvus using Docker
docker-compose up -d milvus-standalone
```

#### Option B: Chroma (Good for Development)
```bash
pip install chromadb
```

### 2. Configure Knowledge Base Settings

Create or update your `.env` file:

```env
# Vector Database Configuration
VECTOR_DB_TYPE=milvus  # or 'chroma'
MILVUS_HOST=localhost
MILVUS_PORT=19530
CHROMA_PERSIST_DIRECTORY=./data/chroma

# Embedding Configuration
EMBEDDING_MODEL=text-embedding-ada-002
EMBEDDING_PROVIDER=openai
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### 3. Initialize Knowledge Base

```python
from ai_engine.core.knowledge_base import KnowledgeBase
from ai_engine.configs.agent import AgentConfig

# Load configuration
config = AgentConfig()

# Initialize knowledge base
kb = KnowledgeBase(config)

# Verify connection
if kb.health_check():
    print("Knowledge base initialized successfully!")
else:
    print("Failed to connect to knowledge base")
```

## Document Ingestion

### 1. Single Document Processing

```python
from ai_engine.core.indexing import DocumentProcessor

# Initialize document processor
processor = DocumentProcessor(config)

# Process a single document
document_path = "path/to/your/document.pdf"
result = processor.process_document(document_path)

if result.success:
    print(f"Document processed: {result.document_id}")
    print(f"Chunks created: {result.chunk_count}")
else:
    print(f"Error processing document: {result.error}")
```

### 2. Batch Document Processing

```python
import os
from pathlib import Path

def process_directory(directory_path):
    """Process all documents in a directory"""
    processed = []
    failed = []
    
    for file_path in Path(directory_path).rglob("*"):
        if file_path.suffix.lower() in ['.pdf', '.txt', '.docx', '.md']:
            try:
                result = processor.process_document(str(file_path))
                if result.success:
                    processed.append(file_path.name)
                else:
                    failed.append((file_path.name, result.error))
            except Exception as e:
                failed.append((file_path.name, str(e)))
    
    return processed, failed

# Process all documents in a directory
docs_dir = "path/to/documents"
processed, failed = process_directory(docs_dir)

print(f"Successfully processed: {len(processed)} documents")
print(f"Failed to process: {len(failed)} documents")
```

### 3. Advanced Document Processing

```python
# Custom processing options
processing_options = {
    "chunk_size": 800,
    "chunk_overlap": 150,
    "include_metadata": True,
    "extract_tables": True,
    "ocr_enabled": True,  # For scanned PDFs
    "language": "en"
}

result = processor.process_document(
    document_path,
    options=processing_options
)
```

## Querying the Knowledge Base

### 1. Basic Text Search

```python
from ai_engine.core.retriever import Retriever

# Initialize retriever
retriever = Retriever(config)

# Simple query
query = "What are the benefits of machine learning?"
results = retriever.query_knowledge_base(
    query=query,
    top_k=5,
    score_threshold=0.7
)

# Display results
for i, result in enumerate(results, 1):
    print(f"Result {i}:")
    print(f"Score: {result.score:.3f}")
    print(f"Source: {result.metadata.get('source', 'Unknown')}")
    print(f"Content: {result.content[:200]}...")
    print("-" * 50)
```

### 2. Advanced Querying with Filters

```python
# Query with metadata filters
filtered_results = retriever.query_knowledge_base(
    query="artificial intelligence applications",
    top_k=10,
    filters={
        "document_type": "research_paper",
        "date_created": {"$gte": "2023-01-01"},
        "category": {"$in": ["AI", "ML", "DL"]}
    }
)
```

### 3. Semantic Search with Reranking

```python
# Enable semantic reranking for better results
enhanced_results = retriever.query_knowledge_base(
    query="How to implement neural networks?",
    top_k=20,
    rerank=True,
    rerank_top_k=5,
    include_context=True
)
```

## Knowledge Base Management

### 1. Document Management

```python
# List all documents
documents = kb.list_documents()
print(f"Total documents: {len(documents)}")

# Get document details
doc_id = "your-document-id"
doc_info = kb.get_document(doc_id)
print(f"Document: {doc_info.title}")
print(f"Chunks: {doc_info.chunk_count}")
print(f"Size: {doc_info.size_bytes} bytes")

# Update document metadata
kb.update_document_metadata(doc_id, {
    "category": "technical",
    "priority": "high",
    "tags": ["python", "tutorial"]
})

# Delete a document
kb.delete_document(doc_id)
```

### 2. Collection Management

```python
# Create a new collection
collection_name = "research_papers"
kb.create_collection(
    name=collection_name,
    description="Academic research papers",
    embedding_model="text-embedding-ada-002"
)

# Switch to a specific collection
kb.set_active_collection(collection_name)

# List all collections
collections = kb.list_collections()
for collection in collections:
    print(f"Collection: {collection.name}")
    print(f"Documents: {collection.document_count}")
    print(f"Created: {collection.created_at}")
```

### 3. Backup and Restore

```python
# Create backup
backup_path = "backups/kb_backup_2024.tar.gz"
kb.create_backup(backup_path)

# Restore from backup
kb.restore_from_backup(backup_path)
```

## Integration with Agents

### 1. Knowledge-Aware Agent

```python
from ai_engine.agents.chatbot_agent import ChatbotAgent

class KnowledgeAgent(ChatbotAgent):
    def __init__(self, config):
        super().__init__(config)
        self.retriever = Retriever(config)
    
    def process_query(self, user_input):
        # Retrieve relevant knowledge
        context = self.retriever.query_knowledge_base(
            query=user_input,
            top_k=3
        )
        
        # Enhance prompt with retrieved context
        enhanced_prompt = self._build_context_prompt(user_input, context)
        
        # Generate response
        response = self.model.generate(enhanced_prompt)
        
        return {
            "response": response,
            "sources": [chunk.metadata for chunk in context],
            "confidence": self._calculate_confidence(context)
        }
    
    def _build_context_prompt(self, query, context):
        context_text = "\n".join([chunk.content for chunk in context])
        return f"""
        Context from knowledge base:
        {context_text}
        
        User question: {query}
        
        Please provide a comprehensive answer based on the context above.
        """

# Use the knowledge-aware agent
agent = KnowledgeAgent(config)
response = agent.process_query("Explain quantum computing principles")
```

### 2. Multi-Modal Knowledge Agent

```python
class MultiModalKnowledgeAgent(KnowledgeAgent):
    def process_image_query(self, image_path, text_query=None):
        # OCR processing for images
        from ai_engine.tools.ocr import OCRProcessor
        
        ocr = OCRProcessor()
        extracted_text = ocr.process_image(image_path)
        
        # Combine with text query if provided
        combined_query = f"{text_query}\n\nExtracted text: {extracted_text}"
        
        # Query knowledge base
        return self.process_query(combined_query)
```

## Performance Optimization

### 1. Indexing Optimization

```python
# Optimize index performance
kb.optimize_index()

# Rebuild index with new parameters
kb.rebuild_index(
    embedding_model="text-embedding-3-large",
    index_type="IVF_FLAT",
    metric_type="COSINE"
)
```

### 2. Caching Strategy

```python
from ai_engine.utils.cache import QueryCache

# Enable query caching
cache = QueryCache(max_size=1000, ttl=3600)  # 1 hour TTL

def cached_query(query, **kwargs):
    cache_key = f"{query}_{hash(str(kwargs))}"
    
    if cache.exists(cache_key):
        return cache.get(cache_key)
    
    results = retriever.query_knowledge_base(query, **kwargs)
    cache.set(cache_key, results)
    
    return results
```

### 3. Monitoring and Analytics

```python
# Query analytics
stats = kb.get_query_statistics()
print(f"Total queries: {stats.total_queries}")
print(f"Average response time: {stats.avg_response_time}ms")
print(f"Cache hit rate: {stats.cache_hit_rate}%")

# Performance metrics
metrics = kb.get_performance_metrics()
print(f"Index size: {metrics.index_size_mb}MB")
print(f"Memory usage: {metrics.memory_usage_mb}MB")
print(f"Query throughput: {metrics.queries_per_second} QPS")
```

## Best Practices

### 1. Document Organization

- **Categorize documents** by type, domain, or topic
- **Use consistent naming conventions** for files and metadata
- **Regular cleanup** of outdated or duplicate content
- **Version control** for important documents

### 2. Query Optimization

- **Use specific keywords** rather than vague terms
- **Include context** in your queries when possible
- **Experiment with different chunk sizes** for your use case
- **Monitor query performance** and adjust parameters

### 3. Maintenance

```python
# Regular maintenance script
def daily_maintenance():
    # Clean up temporary files
    kb.cleanup_temp_files()
    
    # Update document statistics
    kb.update_statistics()
    
    # Check index health
    health = kb.check_index_health()
    if not health.is_healthy:
        print(f"Index issues detected: {health.issues}")
    
    # Backup if needed
    if should_backup():
        kb.create_backup(f"daily_backup_{date.today()}.tar.gz")

# Schedule daily maintenance
import schedule
schedule.every().day.at("02:00").do(daily_maintenance)
```

## Troubleshooting

### Common Issues

1. **Low retrieval quality**
   - Adjust chunk size and overlap
   - Try different embedding models
   - Add more diverse training data

2. **Slow query performance**
   - Optimize index parameters
   - Enable caching
   - Consider upgrading hardware

3. **Out of memory errors**
   - Reduce batch size during indexing
   - Use streaming for large documents
   - Increase system memory

### Debug Mode

```python
# Enable debug logging
import logging
logging.getLogger('ai_engine.knowledge_base').setLevel(logging.DEBUG)

# Query with debug information
results = retriever.query_knowledge_base(
    query="debug query",
    debug=True
)

# Analyze query execution
for step in results.debug_info:
    print(f"Step: {step.name}")
    print(f"Duration: {step.duration}ms")
    print(f"Details: {step.details}")
```

## Next Steps

- Explore the [Graph Database Tutorial](GRAPH_DATABASE.md)
- Learn about [Tool Integration](TOOL_INTEGRATION.md)
- Review the [API Reference](../API_REFERENCE.md)
- Check out advanced examples in `/examples/knowledge_base/`

## Additional Resources

- [Knowledge Base Configuration Reference](../configuration/KNOWLEDGE_BASE.md)
- [Embedding Models Comparison](../guides/EMBEDDING_MODELS.md)
- [Performance Tuning Guide](../guides/PERFORMANCE_TUNING.md) 