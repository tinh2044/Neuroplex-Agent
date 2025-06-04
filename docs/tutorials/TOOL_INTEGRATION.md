# Tool Integration

## Overview

The AI Engine provides a comprehensive tool system that enables agents to interact with external services, APIs, and utilities. This tutorial covers creating custom tools, integrating existing tools, and building powerful tool-enabled agents.

## What You'll Learn

- Understanding the tool architecture
- Creating custom tools from scratch
- Integrating external APIs and services
- Building tool-enabled agents
- Advanced tool patterns and best practices
- Error handling and debugging tools
- Performance optimization for tools

## Prerequisites

- AI Engine installed and configured
- Python 3.8+ environment
- Basic understanding of APIs and web services
- Knowledge of the agent framework

## Tool Architecture

```
Tool System Architecture
├── Tool Registry
├── Tool Factory
├── Base Tool Classes
├── Tool Execution Engine
├── Result Processing
└── Error Handling
```

## Understanding Tools

### 1. Tool Types in AI Engine

```python
# Built-in tool types
from ai_engine.tools.base import BaseTool, WebSearchTool, OCRTool
from ai_engine.tools.registry import ToolRegistry

# List available tools
registry = ToolRegistry()
available_tools = registry.list_tools()

print("Available tools:")
for tool_name, tool_class in available_tools.items():
    print(f"- {tool_name}: {tool_class.__doc__}")
```

### 2. Basic Tool Structure

```python
from ai_engine.tools.base import BaseTool
from typing import Dict, Any, Optional
import requests

class ExampleTool(BaseTool):
    """Example tool demonstrating basic structure"""
    
    name = "example_tool"
    description = "An example tool that demonstrates the basic structure"
    
    def __init__(self, config=None):
        super().__init__(config)
        self.api_key = config.get('EXAMPLE_API_KEY') if config else None
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        try:
            # Tool implementation
            result = self._perform_operation(kwargs)
            
            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.name,
                    "execution_time": self._get_execution_time()
                }
            }
        except Exception as e:
            return self._handle_error(e)
    
    def _perform_operation(self, params):
        """Override this method with actual tool logic"""
        return f"Tool executed with params: {params}"
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate input parameters"""
        required_params = self.get_required_parameters()
        return all(param in kwargs for param in required_params)
    
    def get_required_parameters(self) -> list:
        """Return list of required parameters"""
        return []
    
    def get_optional_parameters(self) -> list:
        """Return list of optional parameters"""
        return []
```

## Creating Custom Tools

### 1. Simple API Integration Tool

```python
class WeatherTool(BaseTool):
    """Tool for getting weather information"""
    
    name = "weather_lookup"
    description = "Get current weather information for a specified location"
    
    def __init__(self, config=None):
        super().__init__(config)
        self.api_key = config.get('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    def execute(self, location: str, units: str = "metric") -> Dict[str, Any]:
        """Get weather for a location"""
        if not self.validate_parameters(location=location):
            return self._handle_error("Location parameter is required")
        
        try:
            # Make API request
            params = {
                "q": location,
                "appid": self.api_key,
                "units": units
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            weather_data = response.json()
            
            # Process the response
            result = {
                "location": weather_data["name"],
                "country": weather_data["sys"]["country"],
                "temperature": weather_data["main"]["temp"],
                "description": weather_data["weather"][0]["description"],
                "humidity": weather_data["main"]["humidity"],
                "pressure": weather_data["main"]["pressure"]
            }
            
            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.name,
                    "api_source": "OpenWeatherMap"
                }
            }
            
        except requests.exceptions.RequestException as e:
            return self._handle_error(f"API request failed: {str(e)}")
        except KeyError as e:
            return self._handle_error(f"Unexpected API response format: {str(e)}")
    
    def get_required_parameters(self) -> list:
        return ["location"]
    
    def get_optional_parameters(self) -> list:
        return ["units"]

# Register the tool
registry.register_tool("weather", WeatherTool)
```

### 2. Database Query Tool

```python
class DatabaseQueryTool(BaseTool):
    """Tool for querying databases"""
    
    name = "database_query"
    description = "Execute SQL queries on configured databases"
    
    def __init__(self, config=None):
        super().__init__(config)
        self.connection_string = config.get('DATABASE_URL')
        self.allowed_operations = ['SELECT']  # Security restriction
    
    def execute(self, query: str, database: str = "default") -> Dict[str, Any]:
        """Execute a database query"""
        if not self.validate_query_safety(query):
            return self._handle_error("Query not allowed for security reasons")
        
        try:
            import sqlite3  # or your preferred database driver
            
            # Connect to database
            conn = sqlite3.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Execute query
            cursor.execute(query)
            
            # Fetch results
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                # Convert to list of dictionaries
                formatted_results = [
                    dict(zip(columns, row)) for row in results
                ]
            else:
                formatted_results = {"affected_rows": cursor.rowcount}
            
            conn.close()
            
            return {
                "success": True,
                "result": formatted_results,
                "metadata": {
                    "tool_name": self.name,
                    "query": query,
                    "database": database
                }
            }
            
        except Exception as e:
            return self._handle_error(f"Database query failed: {str(e)}")
    
    def validate_query_safety(self, query: str) -> bool:
        """Validate query for security"""
        query_upper = query.strip().upper()
        
        # Only allow SELECT statements
        if not query_upper.startswith('SELECT'):
            return False
        
        # Block dangerous keywords
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']
        return not any(keyword in query_upper for keyword in dangerous_keywords)
    
    def get_required_parameters(self) -> list:
        return ["query"]

# Register the tool
registry.register_tool("database_query", DatabaseQueryTool)
```

### 3. File Processing Tool

```python
class FileProcessorTool(BaseTool):
    """Tool for processing various file types"""
    
    name = "file_processor"
    description = "Process and extract information from files"
    
    def __init__(self, config=None):
        super().__init__(config)
        self.max_file_size = config.get('MAX_FILE_SIZE', 10 * 1024 * 1024)  # 10MB
        self.allowed_extensions = ['.txt', '.pdf', '.docx', '.csv', '.json']
    
    def execute(self, file_path: str, operation: str = "extract_text") -> Dict[str, Any]:
        """Process a file based on the specified operation"""
        
        if not self._validate_file(file_path):
            return self._handle_error("File validation failed")
        
        try:
            if operation == "extract_text":
                result = self._extract_text(file_path)
            elif operation == "get_metadata":
                result = self._get_metadata(file_path)
            elif operation == "convert_to_json":
                result = self._convert_to_json(file_path)
            else:
                return self._handle_error(f"Unknown operation: {operation}")
            
            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.name,
                    "operation": operation,
                    "file_path": file_path
                }
            }
            
        except Exception as e:
            return self._handle_error(f"File processing failed: {str(e)}")
    
    def _validate_file(self, file_path: str) -> bool:
        """Validate file before processing"""
        import os
        
        # Check if file exists
        if not os.path.exists(file_path):
            return False
        
        # Check file size
        if os.path.getsize(file_path) > self.max_file_size:
            return False
        
        # Check file extension
        _, ext = os.path.splitext(file_path)
        return ext.lower() in self.allowed_extensions
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from various file types"""
        import os
        
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif ext == '.pdf':
            # Use OCR tool for PDF processing
            from ai_engine.tools.ocr import OCRProcessor
            ocr = OCRProcessor()
            return ocr.extract_text_from_pdf(file_path)
        elif ext == '.docx':
            from docx import Document
            doc = Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        else:
            raise ValueError(f"Text extraction not supported for {ext} files")
    
    def _get_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get file metadata"""
        import os
        from datetime import datetime
        
        stat = os.stat(file_path)
        
        return {
            "filename": os.path.basename(file_path),
            "size_bytes": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "extension": os.path.splitext(file_path)[1].lower()
        }
    
    def get_required_parameters(self) -> list:
        return ["file_path"]
    
    def get_optional_parameters(self) -> list:
        return ["operation"]

# Register the tool
registry.register_tool("file_processor", FileProcessorTool)
```

## Tool-Enabled Agents

### 1. Creating a Tool-Enabled Agent

```python
from ai_engine.agents.base_agent import BaseAgent

class ToolEnabledAgent(BaseAgent):
    """Agent that can use tools to enhance its capabilities"""
    
    def __init__(self, config):
        super().__init__(config)
        self.tool_registry = ToolRegistry()
        self.available_tools = self._load_tools()
    
    def _load_tools(self) -> Dict[str, BaseTool]:
        """Load and initialize available tools"""
        tools = {}
        
        # Load built-in tools
        tools['weather'] = WeatherTool(self.config)
        tools['database'] = DatabaseQueryTool(self.config)
        tools['file_processor'] = FileProcessorTool(self.config)
        
        # Load custom tools from registry
        for tool_name, tool_class in self.tool_registry.list_tools().items():
            if tool_name not in tools:
                tools[tool_name] = tool_class(self.config)
        
        return tools
    
    def process_query(self, user_input: str) -> Dict[str, Any]:
        """Process user query and determine if tools are needed"""
        
        # Analyze query to determine tool usage
        tool_analysis = self._analyze_tool_requirements(user_input)
        
        if tool_analysis["requires_tools"]:
            # Execute required tools
            tool_results = self._execute_tools(tool_analysis["tools"])
            
            # Enhance prompt with tool results
            enhanced_prompt = self._build_tool_enhanced_prompt(
                user_input, 
                tool_results
            )
            
            # Generate response with tool context
            response = self.model.generate(enhanced_prompt)
            
            return {
                "response": response,
                "tool_results": tool_results,
                "tools_used": list(tool_results.keys())
            }
        else:
            # Standard response without tools
            response = self.model.generate(user_input)
            return {"response": response}
    
    def _analyze_tool_requirements(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine which tools might be needed"""
        
        # Simple keyword-based analysis (can be enhanced with LLM)
        tool_keywords = {
            'weather': ['weather', 'temperature', 'rain', 'sunny', 'cloudy'],
            'database': ['query', 'data', 'database', 'select', 'records'],
            'file_processor': ['file', 'document', 'read', 'extract', 'process']
        }
        
        required_tools = []
        query_lower = query.lower()
        
        for tool_name, keywords in tool_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                required_tools.append(tool_name)
        
        return {
            "requires_tools": len(required_tools) > 0,
            "tools": required_tools,
            "confidence": len(required_tools) / len(tool_keywords)
        }
    
    def _execute_tools(self, tool_names: list) -> Dict[str, Any]:
        """Execute specified tools"""
        results = {}
        
        for tool_name in tool_names:
            if tool_name in self.available_tools:
                tool = self.available_tools[tool_name]
                
                # Extract parameters from context (simplified)
                params = self._extract_tool_parameters(tool_name)
                
                # Execute tool
                result = tool.execute(**params)
                results[tool_name] = result
            else:
                results[tool_name] = {
                    "success": False,
                    "error": f"Tool '{tool_name}' not available"
                }
        
        return results
    
    def _extract_tool_parameters(self, tool_name: str) -> Dict[str, Any]:
        """Extract parameters for tool execution from context"""
        # This is a simplified implementation
        # In practice, you'd use LLM to extract parameters from user query
        
        if tool_name == "weather":
            return {"location": "New York"}  # Default for demo
        elif tool_name == "database":
            return {"query": "SELECT COUNT(*) FROM users"}  # Default query
        elif tool_name == "file_processor":
            return {"file_path": "/tmp/sample.txt", "operation": "extract_text"}
        
        return {}
    
    def _build_tool_enhanced_prompt(self, original_query: str, tool_results: Dict[str, Any]) -> str:
        """Build prompt enhanced with tool results"""
        
        tool_context = "Tool Results:\n"
        for tool_name, result in tool_results.items():
            if result["success"]:
                tool_context += f"- {tool_name}: {result['result']}\n"
            else:
                tool_context += f"- {tool_name}: Error - {result.get('error', 'Unknown error')}\n"
        
        enhanced_prompt = f"""
        {tool_context}
        
        User Query: {original_query}
        
        Please provide a comprehensive response using the tool results above when relevant.
        """
        
        return enhanced_prompt

# Use the tool-enabled agent
agent = ToolEnabledAgent(config)
response = agent.process_query("What's the weather like in London today?")
```

### 2. Advanced Tool Chain Agent

```python
class ToolChainAgent(ToolEnabledAgent):
    """Agent that can chain multiple tools together"""
    
    def process_complex_query(self, user_input: str) -> Dict[str, Any]:
        """Process queries that require multiple tool executions"""
        
        # Plan tool execution sequence
        execution_plan = self._create_execution_plan(user_input)
        
        # Execute tools in sequence
        execution_results = []
        context = {"user_query": user_input}
        
        for step in execution_plan:
            tool_name = step["tool"]
            parameters = step["parameters"]
            
            # Resolve parameter references from previous steps
            resolved_params = self._resolve_parameters(parameters, context)
            
            # Execute tool
            tool_result = self.available_tools[tool_name].execute(**resolved_params)
            
            # Add result to context
            context[f"{tool_name}_result"] = tool_result
            execution_results.append({
                "step": step["step"],
                "tool": tool_name,
                "result": tool_result
            })
        
        # Generate final response
        final_prompt = self._build_chain_prompt(user_input, execution_results)
        response = self.model.generate(final_prompt)
        
        return {
            "response": response,
            "execution_plan": execution_plan,
            "execution_results": execution_results
        }
    
    def _create_execution_plan(self, query: str) -> list:
        """Create a plan for tool execution"""
        # This would typically use an LLM to create the plan
        # Simplified example:
        
        if "file" in query.lower() and "weather" in query.lower():
            return [
                {
                    "step": 1,
                    "tool": "file_processor",
                    "parameters": {"file_path": "{file_path}", "operation": "extract_text"}
                },
                {
                    "step": 2,
                    "tool": "weather",
                    "parameters": {"location": "{extracted_location}"}
                }
            ]
        
        return []
    
    def _resolve_parameters(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve parameter references from context"""
        resolved = {}
        
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
                # This is a reference to a context variable
                ref_key = value[1:-1]  # Remove braces
                resolved[key] = context.get(ref_key, value)
            else:
                resolved[key] = value
        
        return resolved

# Use the tool chain agent
chain_agent = ToolChainAgent(config)
response = chain_agent.process_complex_query("Read the file data.txt and get weather for the city mentioned in it")
```

## Advanced Tool Patterns

### 1. Async Tool Execution

```python
import asyncio
from typing import List

class AsyncTool(BaseTool):
    """Base class for asynchronous tools"""
    
    async def execute_async(self, **kwargs) -> Dict[str, Any]:
        """Async version of execute method"""
        try:
            result = await self._perform_async_operation(kwargs)
            return {
                "success": True,
                "result": result,
                "metadata": {"tool_name": self.name}
            }
        except Exception as e:
            return self._handle_error(e)
    
    async def _perform_async_operation(self, params):
        """Override this method with async implementation"""
        raise NotImplementedError

class AsyncWeatherTool(AsyncTool):
    """Async version of weather tool"""
    
    name = "async_weather"
    description = "Async weather lookup tool"
    
    async def _perform_async_operation(self, params):
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://api.openweathermap.org/data/2.5/weather",
                params={
                    "q": params["location"],
                    "appid": self.api_key
                }
            ) as response:
                return await response.json()

class AsyncToolAgent(BaseAgent):
    """Agent that can execute tools asynchronously"""
    
    async def process_query_async(self, user_input: str) -> Dict[str, Any]:
        """Process query with async tool execution"""
        
        # Identify required tools
        required_tools = self._identify_tools(user_input)
        
        # Execute tools concurrently
        tasks = []
        for tool_name in required_tools:
            tool = self.available_tools[tool_name]
            if hasattr(tool, 'execute_async'):
                params = self._extract_tool_parameters(tool_name)
                tasks.append(tool.execute_async(**params))
        
        # Wait for all tools to complete
        tool_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and generate response
        return self._process_async_results(user_input, tool_results)
```

### 2. Tool Caching and Optimization

```python
from functools import lru_cache
from typing import Tuple
import hashlib
import json

class CachedTool(BaseTool):
    """Tool with result caching capabilities"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.cache_ttl = config.get('TOOL_CACHE_TTL', 3600)  # 1 hour
        self.cache = {}
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute with caching"""
        
        # Generate cache key
        cache_key = self._generate_cache_key(kwargs)
        
        # Check cache
        if self._is_cache_valid(cache_key):
            cached_result = self.cache[cache_key]
            cached_result["metadata"]["from_cache"] = True
            return cached_result
        
        # Execute tool
        result = super().execute(**kwargs)
        
        # Cache successful results
        if result.get("success", False):
            self._cache_result(cache_key, result)
        
        return result
    
    def _generate_cache_key(self, params: Dict[str, Any]) -> str:
        """Generate a unique cache key for parameters"""
        # Sort parameters for consistent hashing
        sorted_params = json.dumps(params, sort_keys=True)
        return hashlib.md5(sorted_params.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached result is still valid"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key]["metadata"]["cached_at"]
        current_time = time.time()
        
        return (current_time - cached_time) < self.cache_ttl
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache the result"""
        result["metadata"]["cached_at"] = time.time()
        self.cache[cache_key] = result.copy()

class OptimizedWeatherTool(CachedTool, WeatherTool):
    """Weather tool with caching and optimization"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.request_limiter = self._create_rate_limiter()
    
    def _create_rate_limiter(self):
        """Create rate limiter for API calls"""
        from time import time, sleep
        
        class RateLimiter:
            def __init__(self, max_calls=60, time_window=60):
                self.max_calls = max_calls
                self.time_window = time_window
                self.calls = []
            
            def wait_if_needed(self):
                now = time()
                # Remove old calls outside time window
                self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
                
                if len(self.calls) >= self.max_calls:
                    sleep_time = self.time_window - (now - self.calls[0])
                    if sleep_time > 0:
                        sleep(sleep_time)
                
                self.calls.append(now)
        
        return RateLimiter()
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute with rate limiting and caching"""
        
        # Check cache first
        cache_key = self._generate_cache_key(kwargs)
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        # Apply rate limiting for API calls
        self.request_limiter.wait_if_needed()
        
        # Execute with caching
        return super().execute(**kwargs)
```

## Error Handling and Debugging

### 1. Comprehensive Error Handling

```python
class RobustTool(BaseTool):
    """Tool with comprehensive error handling"""
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute with robust error handling"""
        
        try:
            # Validate inputs
            validation_result = self._validate_inputs(kwargs)
            if not validation_result["valid"]:
                return self._create_error_response(
                    "validation_error",
                    validation_result["message"]
                )
            
            # Execute with timeout
            result = self._execute_with_timeout(kwargs)
            
            # Validate outputs
            if not self._validate_outputs(result):
                return self._create_error_response(
                    "output_validation_error",
                    "Tool output validation failed"
                )
            
            return result
            
        except TimeoutError:
            return self._create_error_response("timeout", "Tool execution timed out")
        except ConnectionError as e:
            return self._create_error_response("connection_error", str(e))
        except ValueError as e:
            return self._create_error_response("value_error", str(e))
        except Exception as e:
            return self._create_error_response("unexpected_error", str(e))
    
    def _validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input parameters"""
        required = self.get_required_parameters()
        missing = [param for param in required if param not in inputs]
        
        if missing:
            return {
                "valid": False,
                "message": f"Missing required parameters: {missing}"
            }
        
        return {"valid": True}
    
    def _execute_with_timeout(self, kwargs, timeout=30):
        """Execute with timeout protection"""
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Tool execution timed out")
        
        # Set timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            result = self._perform_operation(kwargs)
            signal.alarm(0)  # Cancel timeout
            return result
        except TimeoutError:
            signal.alarm(0)
            raise
    
    def _create_error_response(self, error_type: str, message: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "success": False,
            "error": {
                "type": error_type,
                "message": message,
                "tool_name": self.name,
                "timestamp": time.time()
            }
        }

# Tool debugging utilities
class ToolDebugger:
    """Utilities for debugging tools"""
    
    @staticmethod
    def trace_tool_execution(tool: BaseTool, **kwargs):
        """Trace tool execution for debugging"""
        
        print(f"Executing tool: {tool.name}")
        print(f"Parameters: {kwargs}")
        
        start_time = time.time()
        result = tool.execute(**kwargs)
        execution_time = time.time() - start_time
        
        print(f"Execution time: {execution_time:.2f}s")
        print(f"Success: {result.get('success', False)}")
        
        if result.get('success'):
            print(f"Result: {result['result']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        return result
    
    @staticmethod
    def validate_tool_interface(tool_class):
        """Validate tool implements required interface"""
        required_methods = ['execute', 'get_required_parameters']
        required_attributes = ['name', 'description']
        
        issues = []
        
        for method in required_methods:
            if not hasattr(tool_class, method):
                issues.append(f"Missing method: {method}")
        
        for attr in required_attributes:
            if not hasattr(tool_class, attr):
                issues.append(f"Missing attribute: {attr}")
        
        if issues:
            print(f"Tool validation issues for {tool_class.__name__}:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"Tool {tool_class.__name__} passes validation")
        
        return len(issues) == 0
```

## Testing Tools

### 1. Tool Unit Testing

```python
import unittest
from unittest.mock import Mock, patch

class TestWeatherTool(unittest.TestCase):
    """Test cases for WeatherTool"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = {"OPENWEATHER_API_KEY": "test_key"}
        self.tool = WeatherTool(self.config)
    
    def test_successful_weather_request(self):
        """Test successful weather API request"""
        
        # Mock API response
        mock_response = {
            "name": "London",
            "sys": {"country": "GB"},
            "main": {"temp": 15.5, "humidity": 80, "pressure": 1013},
            "weather": [{"description": "cloudy"}]
        }
        
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status.return_value = None
            
            result = self.tool.execute(location="London")
            
            self.assertTrue(result["success"])
            self.assertEqual(result["result"]["location"], "London")
            self.assertEqual(result["result"]["temperature"], 15.5)
    
    def test_missing_location_parameter(self):
        """Test error handling for missing location"""
        
        result = self.tool.execute()  # No location provided
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    def test_api_error_handling(self):
        """Test handling of API errors"""
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("API Error")
            
            result = self.tool.execute(location="InvalidCity")
            
            self.assertFalse(result["success"])
            self.assertIn("API request failed", result["error"])

class ToolTestRunner:
    """Utility for running tool tests"""
    
    @staticmethod
    def test_all_tools(tool_registry: ToolRegistry):
        """Test all registered tools"""
        
        results = {}
        
        for tool_name, tool_class in tool_registry.list_tools().items():
            print(f"Testing {tool_name}...")
            
            try:
                # Basic interface validation
                if ToolDebugger.validate_tool_interface(tool_class):
                    results[tool_name] = "PASS"
                else:
                    results[tool_name] = "FAIL - Interface validation"
            except Exception as e:
                results[tool_name] = f"FAIL - {str(e)}"
        
        # Print results
        print("\nTool Test Results:")
        for tool_name, result in results.items():
            print(f"  {tool_name}: {result}")
        
        return results

# Run tests
if __name__ == "__main__":
    unittest.main()
```

## Best Practices

### 1. Tool Design Guidelines

- **Single Responsibility**: Each tool should have one clear purpose
- **Parameter Validation**: Always validate inputs before processing
- **Error Handling**: Provide clear, actionable error messages
- **Documentation**: Include comprehensive docstrings and examples
- **Performance**: Consider caching and rate limiting for external APIs
- **Security**: Validate and sanitize all inputs, especially for database/file operations

### 2. Security Considerations

```python
class SecureTool(BaseTool):
    """Base class with security features"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.allowed_domains = config.get('ALLOWED_DOMAINS', [])
        self.max_file_size = config.get('MAX_FILE_SIZE', 10 * 1024 * 1024)
    
    def validate_url(self, url: str) -> bool:
        """Validate URL against allowed domains"""
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        if not self.allowed_domains:
            return True  # No restrictions
        
        return any(domain.endswith(allowed) for allowed in self.allowed_domains)
    
    def sanitize_file_path(self, file_path: str) -> str:
        """Sanitize file path to prevent directory traversal"""
        import os
        
        # Remove any directory traversal attempts
        safe_path = os.path.normpath(file_path)
        
        # Ensure path doesn't go above current directory
        if safe_path.startswith('..'):
            raise ValueError("Directory traversal not allowed")
        
        return safe_path
    
    def validate_sql_query(self, query: str) -> bool:
        """Basic SQL injection protection"""
        
        # Allow only SELECT statements
        if not query.strip().upper().startswith('SELECT'):
            return False
        
        # Block dangerous keywords
        dangerous = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'EXEC', 'EXECUTE']
        query_upper = query.upper()
        
        return not any(keyword in query_upper for keyword in dangerous)
```

## Performance Optimization

### 1. Tool Performance Monitoring

```python
class PerformanceMonitor:
    """Monitor tool performance metrics"""
    
    def __init__(self):
        self.metrics = {}
    
    def record_execution(self, tool_name: str, execution_time: float, success: bool):
        """Record tool execution metrics"""
        
        if tool_name not in self.metrics:
            self.metrics[tool_name] = {
                "total_executions": 0,
                "successful_executions": 0,
                "total_time": 0,
                "average_time": 0,
                "success_rate": 0
            }
        
        metrics = self.metrics[tool_name]
        metrics["total_executions"] += 1
        metrics["total_time"] += execution_time
        
        if success:
            metrics["successful_executions"] += 1
        
        # Update averages
        metrics["average_time"] = metrics["total_time"] / metrics["total_executions"]
        metrics["success_rate"] = metrics["successful_executions"] / metrics["total_executions"]
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        
        report = {
            "total_tools": len(self.metrics),
            "tools": self.metrics,
            "summary": {
                "slowest_tool": self._find_slowest_tool(),
                "most_reliable_tool": self._find_most_reliable_tool(),
                "overall_success_rate": self._calculate_overall_success_rate()
            }
        }
        
        return report
    
    def _find_slowest_tool(self) -> str:
        """Find the tool with highest average execution time"""
        if not self.metrics:
            return None
        
        return max(self.metrics.keys(), key=lambda x: self.metrics[x]["average_time"])
    
    def _find_most_reliable_tool(self) -> str:
        """Find the tool with highest success rate"""
        if not self.metrics:
            return None
        
        return max(self.metrics.keys(), key=lambda x: self.metrics[x]["success_rate"])
    
    def _calculate_overall_success_rate(self) -> float:
        """Calculate overall success rate across all tools"""
        if not self.metrics:
            return 0
        
        total_executions = sum(m["total_executions"] for m in self.metrics.values())
        total_successes = sum(m["successful_executions"] for m in self.metrics.values())
        
        return total_successes / total_executions if total_executions > 0 else 0

# Integrate performance monitoring
monitor = PerformanceMonitor()

class MonitoredTool(BaseTool):
    """Tool with performance monitoring"""
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute with performance monitoring"""
        
        start_time = time.time()
        result = super().execute(**kwargs)
        execution_time = time.time() - start_time
        
        # Record metrics
        monitor.record_execution(
            self.name, 
            execution_time, 
            result.get("success", False)
        )
        
        return result
```

## Next Steps

- Explore [Multi-Modal Processing Tutorial](MULTIMODAL.md)
- Learn about [Advanced Agent Patterns](ADVANCED_AGENTS.md)
- Review the [API Reference](../API_REFERENCE.md)
- Check out tool examples in `/examples/tools/`

## Additional Resources

- [Tool Registry Documentation](../configuration/TOOL_REGISTRY.md)
- [Security Guidelines](../guides/SECURITY.md)
- [Performance Optimization Guide](../guides/PERFORMANCE.md)
- [Third-party Tool Integrations](../integrations/) 