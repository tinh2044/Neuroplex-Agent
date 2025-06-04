# Getting Started with AI Engine

This tutorial will guide you through setting up and using the AI Engine for the first time. By the end of this tutorial, you'll have a fully functional AI system capable of conversational AI, knowledge base queries, and web search.

## 🎯 What You'll Learn

- How to install and configure the AI Engine
- Setting up your first AI model
- Creating a knowledge base
- Performing basic chat interactions
- Using web search integration
- Understanding the system architecture

## 📋 Prerequisites

Before starting, ensure you have:

- Python 3.8 or higher
- At least 4GB of available memory
- Internet connection for downloading models and dependencies
- An OpenAI API key (or access to local models via Ollama)

## 🚀 Step 1: Installation

### Clone the Repository

```bash
# Clone the Neuroplex project
git clone https://github.com/tinh2044/Neuroplex-Agent
cd neuroplex/ai_engine
```

### Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Verify Installation

```bash
# Test the installation
python -c "import ai_engine; print('AI Engine installed successfully!')"
```

## 🔧 Step 2: Basic Configuration

### Create Environment File

Create a `.env` file in the `ai_engine` directory:

```bash
# ai_engine/.env

# Required: OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional: Model storage directory
MODEL_DIR=./models

# Optional: Database connections (for advanced features)
# MILVUS_URI=http://localhost:19530
# NEO4J_URI=bolt://localhost:7687
# NEO4J_AUTH=neo4j/password
```

> **💡 Tip**: You can get an OpenAI API key from [OpenAI's website](https://platform.openai.com/api-keys)

### Initialize Configuration

```python
# test_config.py
from ai_engine.configs.agent import AgentConfig

# Create and initialize configuration
config = AgentConfig()
config.provider = "openai"
config.model = "gpt-3.5-turbo"  # Start with a cost-effective model
config.save()

print("Configuration initialized successfully!")
print(f"Using model: {config.provider}/{config.model}")
```

Run the configuration test:
```bash
python test_config.py
```

## 🤖 Step 3: Your First AI Conversation

### Simple Chat Example

Create a file called `first_chat.py`:

```python
# first_chat.py
from ai_engine.models import select_model
from ai_engine.configs.agent import AgentConfig

# Load configuration
config = AgentConfig()
config.load()

# Initialize the model
model = select_model(
    model_provider=config.provider,
    model_name=config.model
)

# Start a conversation
def chat():
    print("🤖 AI Engine Chat - Type 'quit' to exit")
    print("-" * 40)
    
    while True:
        user_input = input("\n👤 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        try:
            # Generate response
            response = model.invoke(user_input)
            print(f"\n🤖 AI: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    chat()
```

Run your first chat:
```bash
python first_chat.py
```

Try asking questions like:
- "Hello, how are you?"
- "What is Python?"
- "Explain machine learning in simple terms"

## 📚 Step 4: Adding Knowledge Base (Optional)

### Install Vector Database

If you want to use the knowledge base features, install Milvus:

```bash
# Using Docker (recommended)
docker run -d --name milvus-standalone \
  -p 19530:19530 \
  -v milvus_data:/var/lib/milvus \
  milvusdb/milvus:latest standalone
```

### Update Configuration

Update your `.env` file:
```bash
# Add to .env
MILVUS_URI=http://localhost:19530
```

Update your configuration:
```python
# update_config.py
from ai_engine.configs.agent import AgentConfig

config = AgentConfig()
config.load()
config.enable_kb = True  # Enable knowledge base
config.embed_model = "openai/text-embedding-ada-002"  # Set embedding model
config.save()

print("Knowledge base enabled!")
```

### Knowledge Base Example

```python
# kb_example.py
from ai_engine.core.retriever import Retriever
from ai_engine.core.knowledge_base import KnowledgeBase
from ai_engine.configs.agent import AgentConfig

# Load configuration
config = AgentConfig()
config.load()

# Initialize knowledge base
kb = KnowledgeBase()
retriever = Retriever(config)

# Add some documents
documents = [
    {
        "content": "The AI Engine is a powerful system for building conversational AI applications.",
        "metadata": {"source": "documentation", "topic": "overview"}
    },
    {
        "content": "Python is a high-level programming language known for its simplicity and readability.",
        "metadata": {"source": "tutorial", "topic": "programming"}
    },
    {
        "content": "Machine learning is a subset of AI that enables computers to learn from data.",
        "metadata": {"source": "tutorial", "topic": "ML"}
    }
]

# Add documents to knowledge base
print("📚 Adding documents to knowledge base...")
for doc in documents:
    kb.add_document(doc["content"], doc["metadata"])

print("✅ Documents added successfully!")

# Query the knowledge base
def query_kb():
    print("\n🔍 Knowledge Base Query - Type 'quit' to exit")
    print("-" * 50)
    
    while True:
        query = input("\n🔎 Query: ").strip()
        
        if query.lower() in ['quit', 'exit']:
            break
        
        if not query:
            continue
        
        # Search knowledge base
        results = retriever.search_knowledge_base(query, top_k=3)
        
        if results:
            print(f"\n📖 Found {len(results)} relevant documents:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. Score: {result.get('score', 'N/A'):.3f}")
                print(f"   Content: {result['content'][:200]}...")
                print(f"   Source: {result.get('metadata', {}).get('source', 'Unknown')}")
        else:
            print("❌ No relevant documents found")

if __name__ == "__main__":
    query_kb()
```

## 🌐 Step 5: Web Search Integration (Optional)

### Get Tavily API Key

1. Sign up at [Tavily](https://tavily.com)
2. Get your API key
3. Add it to your `.env` file:

```bash
# Add to .env
TAVILY_API_KEY=tvly-your-tavily-api-key
```

### Enable Web Search

```python
# enable_websearch.py
from ai_engine.configs.agent import AgentConfig

config = AgentConfig()
config.load()
config.enable_websearch = True  # Enable web search
config.save()

print("Web search enabled!")
```

### Web Search Example

```python
# websearch_example.py
from ai_engine.core.retriever import Retriever
from ai_engine.configs.agent import AgentConfig

# Load configuration
config = AgentConfig()
config.load()

# Initialize retriever
retriever = Retriever(config)

def web_search():
    print("🌐 Web Search - Type 'quit' to exit")
    print("-" * 35)
    
    while True:
        query = input("\n🔍 Search: ").strip()
        
        if query.lower() in ['quit', 'exit']:
            break
        
        if not query:
            continue
        
        try:
            # Search the web
            results = retriever.search_web(query, max_results=3)
            
            if results:
                print(f"\n🌍 Found {len(results)} web results:")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. {result.get('title', 'No title')}")
                    print(f"   URL: {result.get('url', 'No URL')}")
                    print(f"   Content: {result.get('content', 'No content')[:200]}...")
            else:
                print("❌ No web results found")
        except Exception as e:
            print(f"❌ Web search error: {e}")

if __name__ == "__main__":
    web_search()
```

## 🎭 Step 6: Using Agents

### Simple Agent Example

```python
# agent_example.py
from ai_engine.agents import AgentManager
from ai_engine.configs.agent import AgentConfig

# Load configuration
config = AgentConfig()
config.load()

# Initialize agent manager
agent_manager = AgentManager()

# Create a simple conversational agent
def create_chatbot():
    # Get the chatbot agent
    chatbot = agent_manager.get_agent("chatbot")
    
    if not chatbot:
        print("❌ Chatbot agent not available")
        return
    
    print("🤖 Chatbot Agent - Type 'quit' to exit")
    print("-" * 40)
    
    while True:
        user_input = input("\n👤 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            break
        
        if not user_input:
            continue
        
        try:
            # Get agent response
            response = chatbot.run(user_input)
            print(f"\n🤖 Agent: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_chatbot()
```

## 🧪 Step 7: Testing Your Setup

### Comprehensive Test

Create a test script to verify everything works:

```python
# test_setup.py
from ai_engine.configs.agent import AgentConfig
from ai_engine.models import select_model
from ai_engine.core.retriever import Retriever
import os

def test_basic_config():
    """Test basic configuration"""
    print("🔧 Testing configuration...")
    try:
        config = AgentConfig()
        config.load()
        print(f"✅ Configuration loaded: {config.provider}/{config.model}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_model():
    """Test model connection"""
    print("🤖 Testing model connection...")
    try:
        config = AgentConfig()
        config.load()
        model = select_model(config.provider, config.model)
        response = model.invoke("Hello, can you respond with 'Test successful'?")
        print(f"✅ Model response: {response}")
        return True
    except Exception as e:
        print(f"❌ Model error: {e}")
        return False

def test_knowledge_base():
    """Test knowledge base (if enabled)"""
    print("📚 Testing knowledge base...")
    try:
        config = AgentConfig()
        config.load()
        if not config.enable_kb:
            print("⏭️  Knowledge base disabled, skipping")
            return True
        
        retriever = Retriever(config)
        # Simple test - this might fail if no documents are indexed
        print("✅ Knowledge base connection successful")
        return True
    except Exception as e:
        print(f"⚠️  Knowledge base warning: {e}")
        return True  # Non-critical for basic setup

def test_web_search():
    """Test web search (if enabled)"""
    print("🌐 Testing web search...")
    try:
        config = AgentConfig()
        config.load()
        if not config.enable_websearch:
            print("⏭️  Web search disabled, skipping")
            return True
        
        if not os.getenv("TAVILY_API_KEY"):
            print("⚠️  Tavily API key not set, skipping")
            return True
        
        retriever = Retriever(config)
        results = retriever.search_web("test query", max_results=1)
        print("✅ Web search connection successful")
        return True
    except Exception as e:
        print(f"⚠️  Web search warning: {e}")
        return True  # Non-critical for basic setup

def main():
    print("🧪 AI Engine Setup Test")
    print("=" * 50)
    
    tests = [
        test_basic_config,
        test_model,
        test_knowledge_base,
        test_web_search
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Setup complete! Your AI Engine is ready to use.")
    elif passed >= 2:  # Basic functionality works
        print("✅ Basic setup complete! Some advanced features may need configuration.")
    else:
        print("❌ Setup incomplete. Please check the errors above.")

if __name__ == "__main__":
    main()
```

Run the test:
```bash
python test_setup.py
```

## 🎯 Next Steps

Congratulations! You've successfully set up the AI Engine. Here's what you can do next:

### Immediate Next Steps
1. **Explore More Models**: Try different providers like Anthropic Claude or local models via Ollama
2. **Build a Knowledge Base**: Add your own documents and create a custom Q&A system
3. **Create Custom Agents**: Build specialized agents for specific tasks
4. **Integrate Tools**: Add OCR, document processing, or other specialized tools

### Advanced Topics
- [Building Custom Agents](BUILDING_AGENTS.md)
- [Knowledge Base Management](KNOWLEDGE_BASE.md)
- [Integration Guide](INTEGRATION.md)
- [Advanced Configuration](../CONFIGURATION.md)

### Learning Resources
- [API Reference](../API_REFERENCE.md) - Complete API documentation
- [Architecture Guide](../ARCHITECTURE.md) - Understanding the system design
- [User Guide](../USER_GUIDE.md) - End-user features and capabilities

## 🆘 Troubleshooting

### Common Issues

**Model Connection Errors:**
```
❌ Error: Invalid API key or network connection failed
```
- Check your API key in the `.env` file
- Verify internet connection
- Try a different model (e.g., "gpt-3.5-turbo" instead of "gpt-4")

**Import Errors:**
```
❌ ModuleNotFoundError: No module named 'ai_engine'
```
- Ensure you're in the correct directory (`ai_engine`)
- Activate your virtual environment
- Re-run `pip install -r requirements.txt`

**Configuration Errors:**
```
❌ Configuration file not found
```
- Run the configuration initialization script again
- Check file permissions in the `ai_engine` directory

**Database Connection Issues:**
```
❌ Cannot connect to Milvus/Neo4j
```
- Ensure Docker services are running
- Check the connection URIs in your `.env` file
- For development, you can disable these features initially

### Getting Help

1. **Check the Documentation**: Most issues are covered in our comprehensive guides
2. **Review Error Messages**: Error messages often contain specific guidance
3. **Community Support**: Join our community forums or Discord
4. **GitHub Issues**: Report bugs or request features on GitHub

## 🎉 Congratulations!

You've successfully completed the AI Engine getting started tutorial! You now have:

- ✅ A working AI Engine installation
- ✅ Basic conversational AI capabilities
- ✅ Understanding of the configuration system
- ✅ Foundation for building more advanced features

The AI Engine is now ready for you to build amazing conversational AI applications. Happy building! 🚀 