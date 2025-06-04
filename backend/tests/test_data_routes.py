"""
Tests for data routes
"""
import os
import sys
import pytest
from unittest.mock import patch, Mock
from io import BytesIO

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDataRoutes:
    """Test cases for database management routes with knowledge base mocking"""
    
    @patch('ai_engine.knowledge_base')
    def test_get_databases(self, mock_kb, client):
        """Test retrieving all databases"""
        mock_kb.get_databases.return_value = {
            "databases": [
                {"name": "test_db1", "description": "Test database 1"},
                {"name": "test_db2", "description": "Test database 2"}
            ],
            "message": "success"
        }
        
        response = client.get("/data/databases")
        assert response.status_code == 200
        data = response.json()
        assert "databases" in data
        assert len(data["databases"]) == 2
    
    @patch('ai_engine.knowledge_base')
    def test_create_database(self, mock_kb, client, sample_database_data):
        """Test creating a new database"""
        mock_kb.create_database.return_value = {
            "database": sample_database_data,
            "message": "Database created successfully"
        }
        
        response = client.post("/data/databases", json=sample_database_data)
        assert response.status_code == 200
        data = response.json()
        assert "database" in data
        assert data["database"]["database_name"] == sample_database_data["database_name"]
    
    @patch('ai_engine.knowledge_base')
    def test_delete_database(self, mock_kb, client):
        """Test deleting a database"""
        database_name = "test_db_to_delete"
        mock_kb.delete_database.return_value = {
            "message": "Database deleted successfully"
        }
        
        response = client.delete(f"/data/databases/{database_name}")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Database deleted successfully"
    
    @patch('ai_engine.knowledge_base')
    def test_get_documents(self, mock_kb, client):
        """Test retrieving documents from a database"""
        database_name = "test_db"
        mock_kb.get_documents.return_value = {
            "documents": [
                {"id": "doc1", "title": "Document 1", "content": "Content 1"},
                {"id": "doc2", "title": "Document 2", "content": "Content 2"}
            ],
            "message": "success"
        }
        
        response = client.get(f"/data/databases/{database_name}/documents")
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert len(data["documents"]) == 2
    
    @patch('ai_engine.knowledge_base')
    def test_delete_document(self, mock_kb, client):
        """Test deleting a document from a database"""
        database_name = "test_db"
        document_id = "doc_to_delete"
        mock_kb.delete_document.return_value = {
            "message": "Document deleted successfully"
        }
        
        response = client.delete(f"/data/databases/{database_name}/documents/{document_id}")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Document deleted successfully"
    
    @patch('ai_engine.knowledge_base')
    def test_upload_file(self, mock_kb, client):
        """Test uploading a file to a database"""
        database_name = "test_db"
        mock_kb.add_document.return_value = {
            "document": {"id": "new_doc", "title": "test.txt"},
            "message": "File uploaded successfully"
        }
        
        # Create a test file
        file_content = b"This is test file content"
        files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
        
        response = client.post(f"/data/databases/{database_name}/upload", files=files)
        assert response.status_code == 200
        data = response.json()
        assert "document" in data
        assert "message" in data
    
    @patch('ai_engine.knowledge_base')
    def test_query_database(self, mock_kb, client):
        """Test querying a database"""
        database_name = "test_db"
        query_data = {"query": "test query", "limit": 5}
        mock_kb.query.return_value = {
            "results": [
                {"document": "doc1", "score": 0.95, "content": "Relevant content 1"},
                {"document": "doc2", "score": 0.87, "content": "Relevant content 2"}
            ],
            "message": "Query successful"
        }
        
        response = client.post(f"/data/databases/{database_name}/query", json=query_data)
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 2
    
    def test_create_database_missing_fields(self, client):
        """Test creating a database with missing required fields"""
        incomplete_data = {"database_name": "test_db"}  # Missing required fields
        response = client.post("/data/databases", json=incomplete_data)
        assert response.status_code in [400, 422]
    
    @patch('ai_engine.knowledge_base')
    def test_delete_nonexistent_database(self, mock_kb, client):
        """Test deleting a non-existent database"""
        mock_kb.delete_database.side_effect = Exception("Database not found")
        
        response = client.delete("/data/databases/nonexistent_db")
        assert response.status_code in [404, 500]
    
    def test_upload_without_file(self, client):
        """Test uploading without providing a file"""
        database_name = "test_db"
        response = client.post(f"/data/databases/{database_name}/upload")
        assert response.status_code in [400, 422]
    
    @patch('ai_engine.knowledge_base')
    def test_query_database_error(self, mock_kb, client):
        """Test database query when knowledge base raises an error"""
        database_name = "test_db"
        query_data = {"query": "test query"}
        mock_kb.query.side_effect = Exception("Query error")
        
        response = client.post(f"/data/databases/{database_name}/query", json=query_data)
        assert response.status_code in [500, 200]  # Depending on error handling 