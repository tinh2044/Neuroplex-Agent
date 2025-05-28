"""
Unit tests for the NodeManager class.
"""

import unittest
from unittest.mock import patch, MagicMock

from ai_engine.knowledge_database.node_manager import NodeManager
from ai_engine.models.knowledge import KnowledgeNode
from ai_engine.configs.agent import AgentConfig


class TestNodeManager(unittest.TestCase):
    """Test cases for NodeManager."""

    def setUp(self):
        """Set up test environment."""
        self.mock_config = MagicMock(spec=AgentConfig)
        self.mock_config.workspace = 'test_workspace'
        self.manager = NodeManager(self.mock_config)

    def test_add_node(self):
        """Test adding a new node."""
        mock_session = MagicMock()
        
        with patch.object(self.manager, 'get_session') as mock_get_session:
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            result = self.manager.add_node(
                file_id="test_file",
                text="Test content",
                hash_value="test_hash",
                start_char_idx=0,
                end_char_idx=12,
                metadata={"key": "value"}
            )
            
            self.assertEqual(result["file_id"], "test_file")
            self.assertEqual(result["text"], "Test content")
            self.assertEqual(result["hash"], "test_hash")
            self.assertEqual(result["start_char_idx"], 0)
            self.assertEqual(result["end_char_idx"], 12)
            self.assertEqual(result["metadata"], {"key": "value"})

    def test_add_node_minimal(self):
        """Test adding a node with minimal information."""
        mock_session = MagicMock()
        
        with patch.object(self.manager, 'get_session') as mock_get_session:
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            result = self.manager.add_node(
                file_id="test_file",
                text="Test content"
            )
            
            self.assertEqual(result["file_id"], "test_file")
            self.assertEqual(result["text"], "Test content")
            self.assertIsNone(result["hash"])
            self.assertIsNone(result["start_char_idx"])
            self.assertIsNone(result["end_char_idx"])
            self.assertEqual(result["metadata"], {})

    def test_get_nodes_by_file(self):
        """Test retrieving nodes by file."""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.all.return_value = [
            MagicMock(as_dict=lambda: {
                "id": 1,
                "file_id": "test_file",
                "text": "Node 1"
            }),
            MagicMock(as_dict=lambda: {
                "id": 2,
                "file_id": "test_file",
                "text": "Node 2"
            })
        ]

        with patch.object(self.manager, 'get_session') as mock_get_session:
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            result = self.manager.get_nodes_by_file("test_file")
            
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["text"], "Node 1")
            self.assertEqual(result[1]["text"], "Node 2")
            mock_query.filter_by.assert_called_once_with(file_uid="test_file")

    def test_get_nodes_by_filter_all(self):
        """Test retrieving nodes with no filters."""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [
            MagicMock(as_dict=lambda: {"id": 1, "text": "Node 1"}),
            MagicMock(as_dict=lambda: {"id": 2, "text": "Node 2"})
        ]

        with patch.object(self.manager, 'get_session') as mock_get_session:
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            result = self.manager.get_nodes_by_filter()
            
            self.assertEqual(len(result), 2)
            mock_query.limit.assert_called_once_with(100)

    def test_get_nodes_by_filter_with_file(self):
        """Test retrieving nodes filtered by file."""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [
            MagicMock(as_dict=lambda: {
                "id": 1,
                "file_id": "test_file",
                "text": "Node 1"
            })
        ]

        with patch.object(self.manager, 'get_session') as mock_get_session:
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            result = self.manager.get_nodes_by_filter(file_id="test_file")
            
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["file_id"], "test_file")
            mock_query.filter_by.assert_called_once_with(file_uid="test_file")

    def test_get_nodes_by_filter_with_text(self):
        """Test retrieving nodes filtered by text content."""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [
            MagicMock(as_dict=lambda: {
                "id": 1,
                "text": "Test content"
            })
        ]

        with patch.object(self.manager, 'get_session') as mock_get_session:
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            result = self.manager.get_nodes_by_filter(search_text="Test")
            
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["text"], "Test content")
            mock_query.filter.assert_called_once()


if __name__ == '__main__':
    unittest.main() 