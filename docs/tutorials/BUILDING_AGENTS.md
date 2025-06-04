# Building Custom Agents

This tutorial will teach you how to create custom agents in the AI Engine. Agents are the core components that provide intelligent behavior and can be customized for specific tasks and domains.

## 🎯 What You'll Learn

- Understanding the agent architecture
- Creating your first custom agent
- Implementing different agent types
- Adding tools and capabilities to agents
- Managing agent state and memory
- Building multi-agent systems
- Testing and deploying agents

## 🏗️ Agent Architecture Overview

### Core Components

The AI Engine uses a modular agent architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                        Agent Manager                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Chatbot   │  │   ReAct     │  │   Custom Agents     │  │
│  │   Agent     │  │   Agent     │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                       Base Agent                            │
│  • Memory Management  • Tool Integration  • State Tracking  │
├─────────────────────────────────────────────────────────────┤
│                     Tool System                             │
│  • Knowledge Base • Web Search • OCR • Custom Tools        │
├─────────────────────────────────────────────────────────────┤
│                     Model Layer                             │
│  • OpenAI • Anthropic • Ollama • Custom Models             │
└─────────────────────────────────────────────────────────────┘
```

### Agent Types

**1. Chatbot Agent**: Simple conversational AI for general Q&A
**2. ReAct Agent**: Reasoning and Acting agent that can use tools
**3. Custom Agents**: Specialized agents for specific domains

## 🚀 Creating Your First Custom Agent

### Step 1: Basic Agent Structure

Create a new file `my_agent.py`:

```python
# my_agent.py
from ai_engine.agents.base import BaseAgent
from ai_engine.configs.agent import AgentConfig
from ai_engine.models import select_model

class MyCustomAgent(BaseAgent):
    """A simple custom agent"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.name = "My Custom Agent"
        self.description = "A specialized agent for custom tasks"
        
        # Initialize the language model
        self.model = select_model(config.provider, config.model)
        
        # Custom initialization
        self.specialty = "customer service"
        self.greeting = "Hello! I'm your customer service assistant."
    
    def run(self, user_input: str, **kwargs) -> str:
        """Process user input and return response"""
        try:
            # Add custom processing logic here
            processed_input = self._preprocess_input(user_input)
            
            # Generate response using the model
            response = self._generate_response(processed_input)
            
            # Post-process the response
            final_response = self._postprocess_response(response)
            
            return final_response
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def _preprocess_input(self, user_input: str) -> str:
        """Preprocess user input"""
        # Add custom preprocessing logic
        # e.g., normalize text, extract entities, etc.
        
        # Add context based on agent's specialty
        context = f"As a {self.specialty} agent, please help with: {user_input}"
        return context
    
    def _generate_response(self, processed_input: str) -> str:
        """Generate response using the language model"""
        # Create a more specific prompt for your agent
        prompt = f"""
        You are a helpful {self.specialty} assistant.
        Your role is to provide excellent customer support.
        
        User query: {processed_input}
        
        Please provide a helpful, professional response:
        """
        
        response = self.model.invoke(prompt)
        return response
    
    def _postprocess_response(self, response: str) -> str:
        """Post-process the model response"""
        # Add custom post-processing
        # e.g., format output, add disclaimers, etc.
        
        # Add a friendly signature
        if not response.endswith("😊"):
            response += " 😊"
        
        return response
```

### Step 2: Register Your Agent

Update the `AgentManager` to include your custom agent:

```python
# agent_registry.py
from ai_engine.agents import AgentManager
from my_agent import MyCustomAgent
from ai_engine.configs.agent import AgentConfig

def register_custom_agents():
    """Register custom agents with the manager"""
    config = AgentConfig()
    config.load()
    
    # Create agent manager
    manager = AgentManager()
    
    # Create and register your custom agent
    custom_agent = MyCustomAgent(config)
    manager.add_agent("my_custom", custom_agent)
    
    return manager

# Test your agent
if __name__ == "__main__":
    manager = register_custom_agents()
    
    # Get your custom agent
    agent = manager.get_agent("my_custom")
    
    # Test conversation
    print("🤖 Testing Custom Agent")
    print("-" * 30)
    
    test_queries = [
        "Hello, I need help with my order",
        "How can I return a product?",
        "What are your business hours?"
    ]
    
    for query in test_queries:
        print(f"\n👤 User: {query}")
        response = agent.run(query)
        print(f"🤖 Agent: {response}")
```

## 🧠 Advanced Agent Features

### Adding Memory to Your Agent

```python
# memory_agent.py
from ai_engine.agents.base import BaseAgent
from ai_engine.configs.agent import AgentConfig
from ai_engine.models import select_model
from typing import List, Dict
import json
from datetime import datetime

class MemoryAgent(BaseAgent):
    """Agent with conversation memory"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.name = "Memory Agent"
        self.model = select_model(config.provider, config.model)
        
        # Initialize memory
        self.conversation_history: List[Dict] = []
        self.user_profile: Dict = {}
        self.max_history_length = 10
    
    def run(self, user_input: str, user_id: str = None, **kwargs) -> str:
        """Process input with memory"""
        # Store user input in memory
        self._add_to_memory("user", user_input, user_id)
        
        # Build context from memory
        context = self._build_context()
        
        # Generate response with context
        response = self._generate_response_with_context(user_input, context)
        
        # Store agent response in memory
        self._add_to_memory("agent", response, user_id)
        
        return response
    
    def _add_to_memory(self, role: str, content: str, user_id: str = None):
        """Add message to conversation memory"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        }
        
        self.conversation_history.append(message)
        
        # Maintain memory size
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history.pop(0)
    
    def _build_context(self) -> str:
        """Build context from conversation history"""
        if not self.conversation_history:
            return ""
        
        context_parts = []
        for msg in self.conversation_history[-5:]:  # Last 5 messages
            role = msg["role"].title()
            content = msg["content"]
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    def _generate_response_with_context(self, user_input: str, context: str) -> str:
        """Generate response using conversation context"""
        prompt = f"""
        You are a helpful AI assistant with memory of the conversation.
        
        Previous conversation:
        {context}
        
        Current user input: {user_input}
        
        Please provide a response that considers the conversation history:
        """
        
        return self.model.invoke(prompt)
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation"""
        if not self.conversation_history:
            return "No conversation history."
        
        history_text = self._build_context()
        
        prompt = f"""
        Please provide a brief summary of this conversation:
        
        {history_text}
        
        Summary:
        """
        
        return self.model.invoke(prompt)
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.conversation_history.clear()
        self.user_profile.clear()
```

### Tool-Enabled Agents

```python
# tool_agent.py
from ai_engine.agents.base import BaseAgent
from ai_engine.core.retriever import Retriever
from ai_engine.tools import get_available_tools
from ai_engine.configs.agent import AgentConfig
from ai_engine.models import select_model
from typing import List, Dict, Any

class ToolAgent(BaseAgent):
    """Agent that can use various tools"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.name = "Tool Agent"
        self.model = select_model(config.provider, config.model)
        self.retriever = Retriever(config)
        
        # Initialize available tools
        self.tools = self._initialize_tools()
    
    def _initialize_tools(self) -> Dict[str, Any]:
        """Initialize available tools"""
        tools = {}
        
        # Knowledge Base tool
        if hasattr(self.config, 'enable_kb') and self.config.enable_kb:
            tools['knowledge_search'] = self._search_knowledge_base
        
        # Web Search tool
        if hasattr(self.config, 'enable_websearch') and self.config.enable_websearch:
            tools['web_search'] = self._search_web
        
        # Calculator tool
        tools['calculator'] = self._calculate
        
        # Date/Time tool
        tools['datetime'] = self._get_datetime
        
        return tools
    
    def run(self, user_input: str, **kwargs) -> str:
        """Process input and decide which tools to use"""
        # Determine if tools are needed
        tool_decision = self._decide_tools(user_input)
        
        if tool_decision['use_tools']:
            # Use tools to gather information
            tool_results = self._execute_tools(tool_decision['tools'], user_input)
            
            # Generate response with tool results
            response = self._generate_response_with_tools(user_input, tool_results)
        else:
            # Generate direct response
            response = self.model.invoke(user_input)
        
        return response
    
    def _decide_tools(self, user_input: str) -> Dict:
        """Decide which tools to use based on user input"""
        decision_prompt = f"""
        Given the user input: "{user_input}"
        
        Available tools:
        - knowledge_search: Search internal knowledge base
        - web_search: Search the internet for current information
        - calculator: Perform mathematical calculations
        - datetime: Get current date and time information
        
        Should any tools be used? If yes, which ones?
        
        Respond in this format:
        USE_TOOLS: yes/no
        TOOLS: tool1,tool2 (if applicable)
        REASONING: brief explanation
        """
        
        decision = self.model.invoke(decision_prompt)
        
        # Parse the decision (simplified parsing)
        use_tools = "yes" in decision.lower() and "use_tools: yes" in decision.lower()
        
        tools = []
        if use_tools:
            # Extract tool names (simplified extraction)
            for tool_name in self.tools.keys():
                if tool_name in decision.lower():
                    tools.append(tool_name)
        
        return {
            'use_tools': use_tools,
            'tools': tools,
            'reasoning': decision
        }
    
    def _execute_tools(self, tool_names: List[str], user_input: str) -> Dict:
        """Execute the specified tools"""
        results = {}
        
        for tool_name in tool_names:
            if tool_name in self.tools:
                try:
                    result = self.tools[tool_name](user_input)
                    results[tool_name] = result
                except Exception as e:
                    results[tool_name] = f"Error: {str(e)}"
        
        return results
    
    def _generate_response_with_tools(self, user_input: str, tool_results: Dict) -> str:
        """Generate response using tool results"""
        tool_info = ""
        for tool_name, result in tool_results.items():
            tool_info += f"\n{tool_name}: {result}"
        
        prompt = f"""
        User question: {user_input}
        
        Tool results:
        {tool_info}
        
        Please provide a comprehensive answer using the tool results:
        """
        
        return self.model.invoke(prompt)
    
    # Tool implementations
    def _search_knowledge_base(self, query: str) -> str:
        """Search the knowledge base"""
        try:
            results = self.retriever.search_knowledge_base(query, top_k=3)
            if results:
                return f"Found {len(results)} relevant documents: " + \
                       "; ".join([r['content'][:100] + "..." for r in results])
            else:
                return "No relevant documents found in knowledge base"
        except Exception as e:
            return f"Knowledge base search error: {str(e)}"
    
    def _search_web(self, query: str) -> str:
        """Search the web"""
        try:
            results = self.retriever.search_web(query, max_results=3)
            if results:
                return f"Found {len(results)} web results: " + \
                       "; ".join([r.get('title', 'No title') for r in results])
            else:
                return "No web results found"
        except Exception as e:
            return f"Web search error: {str(e)}"
    
    def _calculate(self, expression: str) -> str:
        """Perform calculation (simple implementation)"""
        try:
            # Extract mathematical expression from user input
            # This is a simplified implementation
            import re
            
            # Find mathematical expressions
            math_pattern = r'[\d\+\-\*/\(\)\.\s]+'
            matches = re.findall(math_pattern, expression)
            
            if matches:
                # Use eval for simple expressions (be careful in production)
                result = eval(matches[0])
                return f"Calculation result: {result}"
            else:
                return "No mathematical expression found"
        except Exception as e:
            return f"Calculation error: {str(e)}"
    
    def _get_datetime(self, query: str) -> str:
        """Get current date/time information"""
        from datetime import datetime
        now = datetime.now()
        return f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
```

## 🔧 Specialized Agent Examples

### Domain Expert Agent

```python
# domain_expert_agent.py
from ai_engine.agents.base import BaseAgent
from ai_engine.configs.agent import AgentConfig
from ai_engine.models import select_model
from typing import Dict, List

class DomainExpertAgent(BaseAgent):
    """Agent specialized for a specific domain"""
    
    def __init__(self, config: AgentConfig, domain: str, expertise_level: str = "expert"):
        super().__init__(config)
        self.domain = domain
        self.expertise_level = expertise_level
        self.name = f"{domain.title()} Expert Agent"
        self.model = select_model(config.provider, config.model)
        
        # Domain-specific knowledge
        self.domain_knowledge = self._load_domain_knowledge()
        self.domain_prompt = self._create_domain_prompt()
    
    def _load_domain_knowledge(self) -> Dict:
        """Load domain-specific knowledge"""
        knowledge_base = {
            "medical": {
                "disclaimers": "I provide general information only. Consult healthcare professionals for medical advice.",
                "keywords": ["symptoms", "treatment", "diagnosis", "medication", "health"],
                "restricted_topics": ["specific medical advice", "drug prescriptions"]
            },
            "legal": {
                "disclaimers": "This is general legal information, not legal advice. Consult a qualified attorney.",
                "keywords": ["law", "legal", "rights", "contract", "regulation"],
                "restricted_topics": ["specific legal advice", "case representation"]
            },
            "financial": {
                "disclaimers": "This is educational information, not financial advice. Consult financial advisors.",
                "keywords": ["investment", "savings", "budget", "taxes", "planning"],
                "restricted_topics": ["specific investment advice", "tax preparation"]
            }
        }
        
        return knowledge_base.get(self.domain, {})
    
    def _create_domain_prompt(self) -> str:
        """Create domain-specific prompt"""
        base_prompt = f"""
        You are a knowledgeable {self.expertise_level} in {self.domain}.
        Your role is to provide helpful, accurate information within your domain.
        """
        
        if self.domain_knowledge.get("disclaimers"):
            base_prompt += f"\n\nIMPORTANT: {self.domain_knowledge['disclaimers']}"
        
        if self.domain_knowledge.get("restricted_topics"):
            restrictions = ", ".join(self.domain_knowledge["restricted_topics"])
            base_prompt += f"\n\nDo not provide: {restrictions}"
        
        return base_prompt
    
    def run(self, user_input: str, **kwargs) -> str:
        """Process domain-specific queries"""
        # Check if query is domain-relevant
        relevance_score = self._check_domain_relevance(user_input)
        
        if relevance_score < 0.3:
            return self._handle_off_topic_query(user_input)
        
        # Process domain-specific query
        response = self._generate_domain_response(user_input)
        
        # Add disclaimers if necessary
        if self.domain_knowledge.get("disclaimers"):
            response += f"\n\n⚠️ {self.domain_knowledge['disclaimers']}"
        
        return response
    
    def _check_domain_relevance(self, user_input: str) -> float:
        """Check if query is relevant to the domain"""
        keywords = self.domain_knowledge.get("keywords", [])
        if not keywords:
            return 1.0  # Assume relevant if no keywords defined
        
        input_lower = user_input.lower()
        keyword_matches = sum(1 for keyword in keywords if keyword in input_lower)
        
        return keyword_matches / len(keywords)
    
    def _handle_off_topic_query(self, user_input: str) -> str:
        """Handle queries outside the domain"""
        return f"""
        I'm specialized in {self.domain} topics. Your question seems to be outside my area of expertise.
        
        For {self.domain}-related questions, I'd be happy to help!
        For other topics, you might want to consult a general assistant or relevant specialist.
        """
    
    def _generate_domain_response(self, user_input: str) -> str:
        """Generate domain-specific response"""
        full_prompt = f"""
        {self.domain_prompt}
        
        User question: {user_input}
        
        Please provide a comprehensive, accurate response within your {self.domain} expertise:
        """
        
        return self.model.invoke(full_prompt)
```

### Multi-Step Task Agent

```python
# task_agent.py
from ai_engine.agents.base import BaseAgent
from ai_engine.configs.agent import AgentConfig
from ai_engine.models import select_model
from typing import List, Dict, Any
import json

class TaskAgent(BaseAgent):
    """Agent that can break down and execute multi-step tasks"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.name = "Task Agent"
        self.model = select_model(config.provider, config.model)
        self.current_task = None
        self.task_state = {}
    
    def run(self, user_input: str, **kwargs) -> str:
        """Execute multi-step task"""
        # Parse the task request
        task_plan = self._create_task_plan(user_input)
        
        if not task_plan["steps"]:
            return "I couldn't break down your request into actionable steps. Could you clarify what you'd like me to help with?"
        
        # Execute the task plan
        results = self._execute_task_plan(task_plan)
        
        # Generate final response
        return self._format_task_results(task_plan, results)
    
    def _create_task_plan(self, user_input: str) -> Dict:
        """Break down user request into steps"""
        planning_prompt = f"""
        Break down this user request into specific, actionable steps:
        
        User request: {user_input}
        
        Create a step-by-step plan in this JSON format:
        {{
            "task_name": "Brief task description",
            "steps": [
                {{"step": 1, "action": "What to do", "type": "information/search/calculation/analysis"}},
                {{"step": 2, "action": "Next action", "type": "type"}}
            ],
            "estimated_time": "time estimate",
            "complexity": "low/medium/high"
        }}
        
        Only return the JSON, no other text.
        """
        
        try:
            plan_response = self.model.invoke(planning_prompt)
            # Parse JSON response
            task_plan = json.loads(plan_response)
            return task_plan
        except Exception as e:
            # Fallback to simple plan
            return {
                "task_name": "Simple task",
                "steps": [{"step": 1, "action": user_input, "type": "information"}],
                "estimated_time": "1 minute",
                "complexity": "low"
            }
    
    def _execute_task_plan(self, task_plan: Dict) -> List[Dict]:
        """Execute each step of the task plan"""
        results = []
        
        for step in task_plan["steps"]:
            step_result = self._execute_step(step)
            results.append({
                "step": step["step"],
                "action": step["action"],
                "result": step_result,
                "status": "completed" if step_result else "failed"
            })
        
        return results
    
    def _execute_step(self, step: Dict) -> str:
        """Execute a single step"""
        step_type = step.get("type", "information")
        action = step["action"]
        
        if step_type == "information":
            return self._handle_information_step(action)
        elif step_type == "search":
            return self._handle_search_step(action)
        elif step_type == "calculation":
            return self._handle_calculation_step(action)
        elif step_type == "analysis":
            return self._handle_analysis_step(action)
        else:
            return self._handle_general_step(action)
    
    def _handle_information_step(self, action: str) -> str:
        """Handle information gathering step"""
        prompt = f"Provide information about: {action}"
        return self.model.invoke(prompt)
    
    def _handle_search_step(self, action: str) -> str:
        """Handle search step"""
        # If retriever is available, use it
        if hasattr(self, 'retriever'):
            try:
                results = self.retriever.search_web(action, max_results=3)
                return f"Found {len(results)} search results"
            except:
                pass
        
        # Fallback to model-based search
        prompt = f"Search for information about: {action}"
        return self.model.invoke(prompt)
    
    def _handle_calculation_step(self, action: str) -> str:
        """Handle calculation step"""
        prompt = f"Perform this calculation or analysis: {action}"
        return self.model.invoke(prompt)
    
    def _handle_analysis_step(self, action: str) -> str:
        """Handle analysis step"""
        prompt = f"Analyze the following: {action}"
        return self.model.invoke(prompt)
    
    def _handle_general_step(self, action: str) -> str:
        """Handle general step"""
        return self.model.invoke(action)
    
    def _format_task_results(self, task_plan: Dict, results: List[Dict]) -> str:
        """Format the final task results"""
        response = f"📋 **{task_plan['task_name']}** - Task completed!\n\n"
        
        for result in results:
            status_icon = "✅" if result["status"] == "completed" else "❌"
            response += f"{status_icon} **Step {result['step']}**: {result['action']}\n"
            response += f"   Result: {result['result'][:200]}{'...' if len(result['result']) > 200 else ''}\n\n"
        
        completed_steps = sum(1 for r in results if r["status"] == "completed")
        response += f"📊 **Summary**: {completed_steps}/{len(results)} steps completed successfully"
        
        return response
```

## 🚀 Deploying and Testing Agents

### Agent Testing Framework

```python
# test_agents.py
import unittest
from ai_engine.configs.agent import AgentConfig
from my_agent import MyCustomAgent
from memory_agent import MemoryAgent
from tool_agent import ToolAgent

class TestAgents(unittest.TestCase):
    
    def setUp(self):
        """Set up test configuration"""
        self.config = AgentConfig()
        self.config.provider = "openai"
        self.config.model = "gpt-3.5-turbo"
    
    def test_custom_agent(self):
        """Test custom agent functionality"""
        agent = MyCustomAgent(self.config)
        
        # Test basic response
        response = agent.run("Hello, I need help")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        
        # Test agent properties
        self.assertEqual(agent.name, "My Custom Agent")
        self.assertEqual(agent.specialty, "customer service")
    
    def test_memory_agent(self):
        """Test memory agent functionality"""
        agent = MemoryAgent(self.config)
        
        # Test memory persistence
        agent.run("My name is John", user_id="user1")
        response = agent.run("What's my name?", user_id="user1")
        
        self.assertIn("John", response.lower())
        
        # Test memory clearing
        agent.clear_memory()
        self.assertEqual(len(agent.conversation_history), 0)
    
    def test_tool_agent(self):
        """Test tool agent functionality"""
        agent = ToolAgent(self.config)
        
        # Test tool availability
        self.assertIsInstance(agent.tools, dict)
        self.assertIn('calculator', agent.tools)
        self.assertIn('datetime', agent.tools)
        
        # Test basic functionality
        response = agent.run("What time is it?")
        self.assertIsInstance(response, str)

def run_agent_tests():
    """Run all agent tests"""
    unittest.main()

if __name__ == "__main__":
    run_agent_tests()
```

### Agent Performance Monitoring

```python
# agent_monitor.py
import time
import json
from datetime import datetime
from typing import Dict, List, Any

class AgentMonitor:
    """Monitor agent performance and usage"""
    
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "agent_usage": {},
            "error_log": []
        }
        self.request_times = []
    
    def start_request(self, agent_name: str, user_input: str) -> Dict:
        """Start monitoring a request"""
        request_id = f"{agent_name}_{int(time.time())}"
        
        request_context = {
            "request_id": request_id,
            "agent_name": agent_name,
            "user_input": user_input,
            "start_time": time.time(),
            "timestamp": datetime.now().isoformat()
        }
        
        return request_context
    
    def end_request(self, request_context: Dict, response: str, success: bool = True):
        """End monitoring a request"""
        end_time = time.time()
        response_time = end_time - request_context["start_time"]
        
        # Update metrics
        self.metrics["total_requests"] += 1
        self.request_times.append(response_time)
        
        agent_name = request_context["agent_name"]
        if agent_name not in self.metrics["agent_usage"]:
            self.metrics["agent_usage"][agent_name] = 0
        self.metrics["agent_usage"][agent_name] += 1
        
        if success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1
            self._log_error(request_context, response)
        
        # Update average response time
        self.metrics["average_response_time"] = sum(self.request_times) / len(self.request_times)
    
    def _log_error(self, request_context: Dict, error_message: str):
        """Log error details"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_context["request_id"],
            "agent_name": request_context["agent_name"],
            "user_input": request_context["user_input"],
            "error": error_message
        }
        
        self.metrics["error_log"].append(error_entry)
        
        # Keep only last 100 errors
        if len(self.metrics["error_log"]) > 100:
            self.metrics["error_log"].pop(0)
    
    def get_metrics(self) -> Dict:
        """Get current metrics"""
        return self.metrics.copy()
    
    def get_agent_stats(self, agent_name: str) -> Dict:
        """Get statistics for a specific agent"""
        total_requests = self.metrics["agent_usage"].get(agent_name, 0)
        
        if total_requests == 0:
            return {"message": f"No requests found for agent: {agent_name}"}
        
        # Calculate agent-specific error rate
        agent_errors = [e for e in self.metrics["error_log"] if e["agent_name"] == agent_name]
        error_rate = len(agent_errors) / total_requests
        
        return {
            "agent_name": agent_name,
            "total_requests": total_requests,
            "error_rate": error_rate,
            "recent_errors": agent_errors[-5:]  # Last 5 errors
        }

# Usage example
monitor = AgentMonitor()

def monitored_agent_run(agent, user_input: str):
    """Run agent with monitoring"""
    context = monitor.start_request(agent.name, user_input)
    
    try:
        response = agent.run(user_input)
        monitor.end_request(context, response, success=True)
        return response
    except Exception as e:
        monitor.end_request(context, str(e), success=False)
        raise e
```

## 🎯 Best Practices

### 1. Agent Design Principles

- **Single Responsibility**: Each agent should have a clear, focused purpose
- **Modular Design**: Use composition over inheritance
- **Error Handling**: Always handle exceptions gracefully
- **State Management**: Keep agent state predictable and manageable

### 2. Performance Optimization

- **Lazy Loading**: Only initialize resources when needed
- **Caching**: Cache frequently used results
- **Async Operations**: Use async for I/O bound operations
- **Resource Limits**: Set appropriate limits for memory and processing

### 3. Security Considerations

- **Input Validation**: Always validate and sanitize user inputs
- **Output Filtering**: Filter sensitive information from responses
- **Access Control**: Implement proper authentication and authorization
- **Audit Logging**: Log important agent actions

### 4. Testing Strategy

- **Unit Tests**: Test individual agent methods
- **Integration Tests**: Test agent interactions with other components
- **Performance Tests**: Monitor response times and resource usage
- **User Acceptance Tests**: Test real-world usage scenarios

## 🎉 Conclusion

You now have the knowledge to build sophisticated custom agents for the AI Engine. Remember to:

1. Start with simple agents and gradually add complexity
2. Test thoroughly before deployment
3. Monitor performance and user satisfaction
4. Iterate based on feedback and requirements

For more advanced topics, see:
- [Integration Guide](INTEGRATION.md)
- [Knowledge Base Tutorial](KNOWLEDGE_BASE.md)
- [API Reference](../API_REFERENCE.md)

Happy agent building! 🤖 