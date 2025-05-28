"""
Unit tests for the DatabaseManager class.
"""

import unittest
from unittest.mock import patch, MagicMock
import os

from ai_engine.knowledge_database.database_manager import DatabaseManager
from ai_engine.models.knowledge import KnowledgeDatabase, KnowledgeFile
from ai_engine.configs.agent import AgentConfig

class TestDatabaseManager(unittest.TestCase):
    """Test cases for DatabaseManager."""

    def setUp(self):
        """Set up test environment."""
        self.agent_config = AgentConfig()
        self.agent_config.workspace = 'test_workspace'
        self.manager = DatabaseManager(self.agent_config)

    def tearDown(self):
        """Clean up test environment."""
        # Close database connections
        if hasattr(self, 'manager'):
            if hasattr(self.manager, 'Session'):
                session = self.manager.Session()
                session.close()
            if hasattr(self.manager, 'engine'):
                self.manager.engine.dispose()
            
        # Clean up any test files
        test_db_path = os.path.join('test_workspace', 'data', 'knowledge.db')
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

    def test_get_all_databases(self):
        """Test retrieving all databases."""
        # Mock session and query
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = [
            MagicMock(as_dict=lambda: {"uid": "test1", "name": "Test DB 1"}),
            MagicMock(as_dict=lambda: {"uid": "test2", "name": "Test DB 2"})
        ]

        with patch.object(self.manager, 'get_session') as mock_get_session:
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            result = self.manager.get_all_databases()
            
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["uid"], "test1")
            self.assertEqual(result[1]["name"], "Test DB 2")

    def test_get_database_by_id(self):
        """Test retrieving a specific database."""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = MagicMock(
            as_dict=lambda: {"uid": "test1", "name": "Test DB"}
        )

        with patch.object(self.manager, 'get_session') as mock_get_session:
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            result = self.manager.get_database_by_id("test1")
            
            self.assertIsNotNone(result)
            self.assertEqual(result["uid"], "test1")
            self.assertEqual(result["name"], "Test DB")

    def test_create_database(self):
        """Test database creation."""
        mock_session = MagicMock()
        
        with patch.object(self.manager, 'get_session') as mock_get_session:
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            result = self.manager.create_database(
                db_id="test1",
                name="Test DB",
                description="Test description",
                embed_model="test_model",
                dimension=128
            )
            
            self.assertEqual(result["uid"], "test1")
            self.assertEqual(result["name"], "Test DB")
            self.assertEqual(result["description"], "Test description")
            self.assertEqual(result["embedding"], "test_model")
            self.assertEqual(result["dimension"], 128)
            self.assertEqual(result["metadata"], {})
            self.assertEqual(result["files"], {})

    def test_delete_database(self):
        """Test database deletion."""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = MagicMock()

        with patch.object(self.manager, 'get_session') as mock_get_session:
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            result = self.manager.delete_database("test1")
            
            self.assertTrue(result)
            mock_session.delete.assert_called_once()

    def test_delete_nonexistent_database(self):
        """Test deletion of non-existent database."""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = None

        with patch.object(self.manager, 'get_session') as mock_get_session:
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            result = self.manager.delete_database("nonexistent")
            
            self.assertFalse(result)
            mock_session.delete.assert_not_called()


if __name__ == '__main__':
    unittest.main() 