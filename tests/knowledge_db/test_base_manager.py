"""
Unit tests for the BaseDBManager class.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from ai_engine.knowledge_database.base_manager import BaseDBManager
from ai_engine.knowledge_database.database_manager import DatabaseManager
from ai_engine.models.knowledge import Base
from ai_engine.configs.agent import AgentConfig


@patch('ai_engine.knowledge_database.milvus_manager.MilvusClient')
@patch('ai_engine.knowledge_database.KnowledgeBase')
@patch('ai_engine.graph_database.GraphDatabase')
class TestBaseDBManager(unittest.TestCase):
    """Test cases for BaseDBManager."""

    @classmethod
    def setUpClass(cls):
        """Set up test class."""
        # Mock the initialization in __init__.py
        cls.kb_patcher = patch('ai_engine.knowledge_base', MagicMock())
        cls.kb_mock = cls.kb_patcher.start()
        cls.graph_patcher = patch('ai_engine.graph_database', MagicMock())
        cls.graph_mock = cls.graph_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Clean up test class."""
        cls.kb_patcher.stop()
        cls.graph_patcher.stop()

    def setUp(self):
        """Set up test environment."""
        self.test_db_path = "test_knowledge.db"
        self.test_config = AgentConfig()
        self.test_config.workspace = 'test_workspace'
        self.test_config.db_path = self.test_db_path
        self.test_config.enable_kb = True
        
        # Mock the Milvus connection
        self.milvus_patcher = patch('ai_engine.knowledge_database.milvus_manager.MilvusClient')
        self.milvus_mock = self.milvus_patcher.start()
        self.milvus_mock.return_value.connect.return_value = True
        
        # Create managers directly with the test config
        self.base_manager = BaseDBManager(self.test_config)
        self.db_manager = DatabaseManager(self.test_config)

    def tearDown(self):
        """Clean up test environment."""
        # Close database connections
        if hasattr(self, 'base_manager'):
            self.base_manager.Session.close_all()
            self.base_manager.engine.dispose()
        if hasattr(self, 'db_manager'):
            self.db_manager.Session.close_all()
            self.db_manager.engine.dispose()
            
        # Remove test database file
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        self.milvus_patcher.stop()

    def test_init(self, mock_graph_db, mock_kb, mock_milvus):
        """Test initialization of BaseDBManager."""
        self.assertIsNotNone(self.base_manager.engine)
        self.assertIsNotNone(self.base_manager.Session)

    def test_ensure_db_dir(self, mock_graph_db, mock_kb, mock_milvus):
        """Test database directory creation."""
        test_dir = "test_db_dir"
        self.base_manager.db_path = os.path.join(test_dir, "test.db")
        self.base_manager.ensure_db_dir()
        
        self.assertTrue(os.path.exists(test_dir))
        os.rmdir(test_dir)

    def test_create_tables(self, mock_graph_db, mock_kb, mock_milvus):
        """Test table creation."""
        # Create tables
        self.base_manager.create_tables()
        
        # Use existing engine to inspect tables
        inspector = inspect(self.base_manager.engine)
        tables = inspector.get_table_names()
        
        # Check if all tables from Base.metadata are created
        expected_tables = set(Base.metadata.tables.keys())
        self.assertEqual(set(tables), expected_tables)

    def test_get_session(self, mock_graph_db, mock_kb, mock_milvus):
        """Test session context manager."""
        with self.base_manager.get_session() as session:
            self.assertIsInstance(session, Session)
            self.assertTrue(session.is_active)

    def test_get_session_with_error(self, mock_graph_db, mock_kb, mock_milvus):
        """Test session rollback on error."""
        with self.assertRaises(Exception):
            with self.base_manager.get_session() as session:
                raise Exception("Test error")

    def test_to_dict_safely_none(self, mock_graph_db, mock_kb, mock_milvus):
        """Test safe dictionary conversion with None object."""
        result = self.base_manager._to_dict_safely(None)
        self.assertIsNone(result)

    def test_to_dict_safely_with_to_dict(self, mock_graph_db, mock_kb, mock_milvus):
        """Test safe dictionary conversion with object having to_dict method."""
        mock_obj = MagicMock()
        mock_obj.to_dict.return_value = {"key": "value"}
        result = self.base_manager._to_dict_safely(mock_obj)
        self.assertEqual(result, {"key": "value"})

    def test_to_dict_safely_without_to_dict(self, mock_graph_db, mock_kb, mock_milvus):
        """Test safe dictionary conversion with object without to_dict method."""
        class TestObj:
            pass
        obj = TestObj()
        result = self.base_manager._to_dict_safely(obj)
        self.assertEqual(result, obj)


if __name__ == '__main__':
    unittest.main() 