"""
Test cases for admin routes (/admin)
"""
import pytest
from backend.models.token_model import AgentToken


class TestAdminTokenRoutes:
    """Test class for admin token management routes"""

    def test_get_empty_tokens(self, client):
        """Test getting tokens when database is empty"""
        response = client.get("/admin/tokens")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_token(self, client, sample_token_data):
        """Test creating a new token"""
        response = client.post("/admin/tokens", json=sample_token_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["agent_id"] == sample_token_data["agent_id"]
        assert data["name"] == sample_token_data["name"]
        assert "token" in data
        assert "created_at" in data
        assert len(data["token"]) == 32  # Default token length

    def test_get_tokens_after_creation(self, client, sample_token_data):
        """Test getting tokens after creating one"""
        # Create token first
        create_response = client.post("/admin/tokens", json=sample_token_data)
        assert create_response.status_code == 200
        
        # Get all tokens
        response = client.get("/admin/tokens")
        assert response.status_code == 200
        
        tokens = response.json()
        assert len(tokens) == 1
        assert tokens[0]["agent_id"] == sample_token_data["agent_id"]

    def test_get_tokens_filtered_by_agent_id(self, client, sample_token_data):
        """Test getting tokens filtered by agent_id"""
        # Create token first
        create_response = client.post("/admin/tokens", json=sample_token_data)
        assert create_response.status_code == 200
        
        # Get tokens filtered by agent_id
        response = client.get(f"/admin/tokens?agent_id={sample_token_data['agent_id']}")
        assert response.status_code == 200
        
        tokens = response.json()
        assert len(tokens) == 1
        assert tokens[0]["agent_id"] == sample_token_data["agent_id"]

    def test_get_tokens_filtered_by_nonexistent_agent_id(self, client):
        """Test getting tokens filtered by non-existent agent_id"""
        response = client.get("/admin/tokens?agent_id=nonexistent")
        assert response.status_code == 200
        assert response.json() == []

    def test_delete_token(self, client, sample_token_data):
        """Test deleting a token"""
        # Create token first
        create_response = client.post("/admin/tokens", json=sample_token_data)
        assert create_response.status_code == 200
        token_id = create_response.json()["id"]
        
        # Delete token
        response = client.delete(f"/admin/tokens/{token_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "message" in data

    def test_delete_nonexistent_token(self, client):
        """Test deleting a non-existent token"""
        response = client.delete("/admin/tokens/999")
        assert response.status_code == 404
        assert "Token not found" in response.json()["detail"]

    def test_verify_valid_token(self, client, sample_token_data):
        """Test verifying a valid token"""
        # Create token first
        create_response = client.post("/admin/tokens", json=sample_token_data)
        assert create_response.status_code == 200
        token_data = create_response.json()
        
        # Verify token
        verify_data = {
            "agent_id": token_data["agent_id"],
            "token": token_data["token"]
        }
        response = client.post("/admin/verify_token", json=verify_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "message" in data

    def test_verify_invalid_token(self, client):
        """Test verifying an invalid token"""
        verify_data = {
            "agent_id": "test-agent",
            "token": "invalid-token"
        }
        response = client.post("/admin/verify_token", json=verify_data)
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]

    def test_verify_wrong_agent_id(self, client, sample_token_data):
        """Test verifying token with wrong agent_id"""
        # Create token first
        create_response = client.post("/admin/tokens", json=sample_token_data)
        assert create_response.status_code == 200
        token_data = create_response.json()
        
        # Verify with wrong agent_id
        verify_data = {
            "agent_id": "wrong-agent-id",
            "token": token_data["token"]
        }
        response = client.post("/admin/verify_token", json=verify_data)
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]


class TestAdminTokensIntegration:
    """Integration tests for token management workflow"""

    def test_full_token_lifecycle(self, client, sample_token_data):
        """Test complete token lifecycle: create -> verify -> delete"""
        # Step 1: Create token
        create_response = client.post("/admin/tokens", json=sample_token_data)
        assert create_response.status_code == 200
        token_data = create_response.json()
        token_id = token_data["id"]
        
        # Step 2: Verify token works
        verify_data = {
            "agent_id": token_data["agent_id"],
            "token": token_data["token"]
        }
        verify_response = client.post("/admin/verify_token", json=verify_data)
        assert verify_response.status_code == 200
        
        # Step 3: Check token appears in list
        list_response = client.get("/admin/tokens")
        assert list_response.status_code == 200
        tokens = list_response.json()
        assert len(tokens) == 1
        assert tokens[0]["id"] == token_id
        
        # Step 4: Delete token
        delete_response = client.delete(f"/admin/tokens/{token_id}")
        assert delete_response.status_code == 200
        
        # Step 5: Verify token no longer works
        verify_after_delete = client.post("/admin/verify_token", json=verify_data)
        assert verify_after_delete.status_code == 401
        
        # Step 6: Check token list is empty
        final_list_response = client.get("/admin/tokens")
        assert final_list_response.status_code == 200
        assert final_list_response.json() == []

    def test_multiple_tokens_same_agent(self, client):
        """Test creating multiple tokens for the same agent"""
        agent_id = "multi-token-agent"
        
        # Create multiple tokens
        for i in range(3):
            token_data = {
                "agent_id": agent_id,
                "name": f"Token {i+1}"
            }
            response = client.post("/admin/tokens", json=token_data)
            assert response.status_code == 200
        
        # Check all tokens are listed
        response = client.get(f"/admin/tokens?agent_id={agent_id}")
        assert response.status_code == 200
        tokens = response.json()
        assert len(tokens) == 3
        
        # Verify all tokens have unique token values
        token_values = [token["token"] for token in tokens]
        assert len(set(token_values)) == 3  # All unique


class TestAdminValidation:
    """Test validation and edge cases"""

    def test_create_token_missing_fields(self, client):
        """Test creating token with missing required fields"""
        # Missing name
        incomplete_data = {"agent_id": "test-agent"}
        response = client.post("/admin/tokens", json=incomplete_data)
        assert response.status_code == 422  # Validation error
        
        # Missing agent_id
        incomplete_data = {"name": "Test Token"}
        response = client.post("/admin/tokens", json=incomplete_data)
        assert response.status_code == 422  # Validation error

    def test_verify_token_missing_fields(self, client):
        """Test verifying token with missing fields"""
        # Missing token
        incomplete_data = {"agent_id": "test-agent"}
        response = client.post("/admin/verify_token", json=incomplete_data)
        assert response.status_code == 422  # Validation error
        
        # Missing agent_id
        incomplete_data = {"token": "some-token"}
        response = client.post("/admin/verify_token", json=incomplete_data)
        assert response.status_code == 422  # Validation error 