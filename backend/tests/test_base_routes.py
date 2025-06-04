"""
Tests for base routes
"""
import os
import sys
import pytest
from unittest.mock import patch, Mock

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestBaseRoutes:
    """Test cases for base routes"""
    
    def test_index_route(self, client):
        """Test the index route"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Backend is running"
    
    def test_get_config(self, client, mock_ai_components):
        """Test getting configuration"""
        response = client.get("/config")
        assert response.status_code == 200
        data = response.json()
        assert "config" in data
    
    def test_update_config(self, client, mock_ai_components):
        """Test updating configuration"""
        config_data = {
            "model": "new-model",
            "temperature": 0.7
        }
        response = client.post("/config", json=config_data)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Configuration updated successfully"
    
    def test_restart_services(self, client, mock_ai_components):
        """Test restarting services"""
        response = client.post("/restart")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Services restarted successfully"
    
    def test_get_logs(self, client):
        """Test getting logs"""
        response = client.get("/logs")
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert isinstance(data["logs"], list)


class TestBaseRoutesErrorHandling:
    """Test error handling for base routes"""

    @patch('backend.routers.base.agent_config.get_safe_config')
    def test_get_config_error(self, mock_get_config, client):
        """Test get config with error"""
        mock_get_config.side_effect = Exception("Config error")
        
        response = client.get("/config")
        # Should still return 200 but with error in response or handle gracefully
        # Adjust based on your actual error handling

    @patch('backend.routers.base.knowledge_base.restart')
    def test_restart_error(self, mock_restart, client):
        """Test restart with error"""
        mock_restart.side_effect = Exception("Restart error")
        
        response = client.post("/restart")
        # Adjust based on your actual error handling 