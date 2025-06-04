"""
Tests for chat routes
"""
import os
import sys
import pytest
import json
from unittest.mock import patch, Mock, AsyncMock
from langchain_core.messages import AIMessageChunk

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestChatRoutes:
    """Test cases for chat routes with AI component mocking"""
    
    def test_chat_index(self, client):
        """Test the chat index route"""
        response = client.get("/chat/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    @patch('ai_engine.agent_config')
    @patch('ai_engine.retriever')
    @patch('ai_engine.graph_db')
    @patch('ai_engine.models.select_model')
    def test_chat_call(self, mock_model, mock_graph, mock_retriever, mock_config, client, sample_chat_data):
        """Test chat call with mocked AI components"""
        # Configure mocks
        mock_config.get_safe_config.return_value = {"model": "test-model"}
        mock_retriever.return_value = ("modified query", [])
        
        # Mock model response
        mock_model_instance = Mock()
        mock_model_instance.model_name = "test-model"
        mock_model_instance.generate_response.return_value = "Test response from AI"
        mock_model.return_value = mock_model_instance
        
        response = client.post("/chat/", json=sample_chat_data)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "model" in data
        assert data["model"] == "test-model"
    
    @patch('ai_engine.executor')
    def test_get_tools(self, mock_executor, client):
        """Test getting available tools"""
        # Mock tools response
        mock_executor.return_value.get_available_tools.return_value = [
            {"name": "calculator", "description": "Basic calculator"},
            {"name": "web_search", "description": "Web search tool"}
        ]
        
        response = client.get("/chat/tools")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert isinstance(data["tools"], list)
    
    @patch('ai_engine.agent_config')
    def test_get_agents(self, mock_config, client):
        """Test getting available agents"""
        # Mock agents response
        mock_config.__getitem__.return_value = {
            "agent1": {"name": "Assistant", "description": "General assistant"},
            "agent2": {"name": "Analyst", "description": "Data analyst"}
        }
        
        response = client.get("/chat/agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
    
    @patch('ai_engine.models.select_model')
    def test_chat_stream_response(self, mock_model, client, sample_chat_data):
        """Test chat streaming response"""
        # Mock streaming model
        mock_model_instance = Mock()
        mock_model_instance.model_name = "test-model"
        mock_model_instance.generate_response.return_value = "Streaming response"
        mock_model.return_value = mock_model_instance
        
        # Add streaming flag to data
        stream_data = sample_chat_data.copy()
        stream_data["stream"] = True
        
        response = client.post("/chat/", json=stream_data)
        assert response.status_code == 200
    
    def test_chat_with_invalid_data(self, client):
        """Test chat with invalid request data"""
        invalid_data = {"invalid": "data"}
        response = client.post("/chat/", json=invalid_data)
        # Should return validation error
        assert response.status_code in [400, 422]
    
    @patch('ai_engine.models.select_model')
    def test_chat_model_error(self, mock_model, client, sample_chat_data):
        """Test chat when model raises an error"""
        mock_model.side_effect = Exception("Model error")
        
        response = client.post("/chat/", json=sample_chat_data)
        # Should handle error gracefully
        assert response.status_code in [500, 200]  # Depending on error handling
    
    def test_chat_missing_query(self, client):
        """Test chat with missing query field"""
        data = {"meta": {"use_web": False}, "history": []}
        response = client.post("/chat/", json=data)
        assert response.status_code in [400, 422]


class TestChatStreamingRoutes:
    """Test streaming chat functionality"""

    @patch('backend.routers.chat.select_model')
    @patch('backend.routers.chat.retriever')
    def test_chat_post_without_retrieval(self, mock_retriever, mock_select_model, client):
        """Test chat POST without knowledge base retrieval"""
        # Mock model
        mock_model = Mock()
        mock_model.model_name = "test-model"
        
        # Create mock streaming response
        def mock_generate_response(*args, **kwargs):
            yield AIMessageChunk(content="Hello")
            yield AIMessageChunk(content=" there!")
        
        mock_model.generate_response = mock_generate_response
        mock_select_model.return_value = mock_model
        
        chat_data = {
            "query": "Hello",
            "meta": {},
            "history": []
        }
        
        response = client.post("/chat/", json=chat_data)
        assert response.status_code == 200
        
        # Check streaming response
        content = b''.join(response.iter_content())
        lines = content.decode().strip().split('\n')
        assert len(lines) > 0
        
        # Parse last line (should be finished status)
        last_line = json.loads(lines[-1])
        assert last_line["meta"]["server_model_name"] == "test-model"

    @patch('backend.routers.chat.select_model')
    @patch('backend.routers.chat.retriever')
    def test_chat_post_with_retrieval(self, mock_retriever, mock_select_model, client):
        """Test chat POST with knowledge base retrieval"""
        # Mock retriever
        mock_retriever.return_value = ("modified query", ["ref1", "ref2"])
        
        # Mock model
        mock_model = Mock()
        mock_model.model_name = "test-model"
        
        def mock_generate_response(*args, **kwargs):
            yield AIMessageChunk(content="Response based on knowledge")
        
        mock_model.generate_response = mock_generate_response
        mock_select_model.return_value = mock_model
        
        chat_data = {
            "query": "What is AI?",
            "meta": {
                "use_web": True,
                "db_id": "test_db"
            },
            "history": []
        }
        
        response = client.post("/chat/", json=chat_data)
        assert response.status_code == 200
        
        # Verify retriever was called
        mock_retriever.assert_called_once()

    @patch('backend.routers.chat.agent_manager')
    def test_chat_agent_endpoint(self, mock_agent_manager, client):
        """Test chat with specific agent"""
        # Mock agent
        mock_agent = Mock()
        
        def mock_stream_messages(*args, **kwargs):
            yield AIMessageChunk(content="Agent response"), {"step": 1}
            yield AIMessageChunk(content=" complete"), {"step": 2}
        
        mock_agent.stream_messages = mock_stream_messages
        mock_agent_manager.get_runnable_agent.return_value = mock_agent
        
        agent_data = {
            "query": "Hello agent",
            "history": [],
            "config": {"model": "gpt-4"},
            "meta": {}
        }
        
        response = client.post("/chat/agent/test_agent", json=agent_data)
        assert response.status_code == 200
        
        # Check streaming response
        content = b''.join(response.iter_content())
        lines = content.decode().strip().split('\n')
        assert len(lines) > 0


class TestChatErrorHandling:
    """Test error handling in chat routes"""

    @patch('backend.routers.chat.select_model')
    def test_chat_model_error(self, mock_select_model, client):
        """Test chat with model error"""
        mock_model = Mock()
        mock_model.model_name = "test-model"
        mock_model.generate_response.side_effect = Exception("Model error")
        mock_select_model.return_value = mock_model
        
        chat_data = {
            "query": "Hello",
            "meta": {},
            "history": []
        }
        
        response = client.post("/chat/", json=chat_data)
        assert response.status_code == 200
        
        # Check that error is handled in streaming response
        content = b''.join(response.iter_content())
        lines = content.decode().strip().split('\n')
        
        # Should contain error status
        error_found = False
        for line in lines:
            if line.strip():
                data = json.loads(line)
                if data.get("status") == "error":
                    error_found = True
                    break
        assert error_found

    @patch('backend.routers.chat.retriever')
    @patch('backend.routers.chat.select_model')
    def test_chat_retriever_error(self, mock_select_model, mock_retriever, client):
        """Test chat with retriever error"""
        mock_retriever.side_effect = Exception("Retriever error")
        
        mock_model = Mock()
        mock_model.model_name = "test-model"
        mock_select_model.return_value = mock_model
        
        chat_data = {
            "query": "Hello",
            "meta": {"use_web": True},
            "history": []
        }
        
        response = client.post("/chat/", json=chat_data)
        assert response.status_code == 200
        
        # Check that retriever error is handled
        content = b''.join(response.iter_content())
        lines = content.decode().strip().split('\n')
        
        error_found = False
        for line in lines:
            if line.strip():
                data = json.loads(line)
                if data.get("status") == "error" and "Retriever error" in data.get("message", ""):
                    error_found = True
                    break
        assert error_found

    @patch('backend.routers.chat.agent_manager')
    def test_chat_agent_not_found(self, mock_agent_manager, client):
        """Test chat with non-existent agent"""
        mock_agent_manager.get_runnable_agent.side_effect = Exception("Agent not found")
        
        agent_data = {
            "query": "Hello",
            "history": [],
            "config": {},
            "meta": {}
        }
        
        response = client.post("/chat/agent/nonexistent_agent", json=agent_data)
        assert response.status_code == 200
        
        # Check that agent error is handled
        content = b''.join(response.iter_content())
        lines = content.decode().strip().split('\n')
        
        error_found = False
        for line in lines:
            if line.strip():
                data = json.loads(line)
                if data.get("status") == "error":
                    error_found = True
                    break
        assert error_found


class TestChatValidation:
    """Test input validation for chat routes"""

    def test_chat_post_missing_query(self, client):
        """Test chat POST with missing query"""
        chat_data = {
            "meta": {},
            "history": []
        }
        
        response = client.post("/chat/", json=chat_data)
        assert response.status_code == 422  # Validation error

    def test_chat_call_missing_query(self, client):
        """Test chat call with missing query"""
        chat_data = {
            "meta": {}
        }
        
        response = client.post("/chat/call", json=chat_data)
        assert response.status_code == 422  # Validation error

    def test_chat_agent_missing_fields(self, client):
        """Test agent chat with missing required fields"""
        # Missing query
        agent_data = {
            "history": [],
            "config": {},
            "meta": {}
        }
        
        response = client.post("/chat/agent/test_agent", json=agent_data)
        assert response.status_code == 422  # Validation error 