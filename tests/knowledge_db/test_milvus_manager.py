"""
Unit tests for the MilvusManager class.
"""

import unittest
from unittest.mock import patch, MagicMock

from ai_engine.knowledge_database.milvus_manager import MilvusManager, MilvusException
from ai_engine.configs.agent import AgentConfig


class TestMilvusManager(unittest.TestCase):
    """Test cases for MilvusManager."""

    def setUp(self):
        """Set up test environment."""
        self.mock_config = MagicMock(spec=AgentConfig)
        self.mock_config.get.return_value = "http://localhost:19530"
        self.manager = MilvusManager(self.mock_config)

    @patch('ai_engine.knowledge_database.milvus_manager.MilvusClient')
    def test_connect_success(self, mock_client_class):
        """Test successful connection to Milvus."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        result = self.manager.connect()
        
        self.assertTrue(result)
        mock_client.list_collections.assert_called_once()
        mock_client_class.assert_called_once_with(uri="http://localhost:19530")

    @patch('ai_engine.knowledge_database.milvus_manager.MilvusClient')
    def test_connect_failure(self, mock_client_class):
        """Test failed connection to Milvus."""
        mock_client_class.side_effect = MilvusException("Connection failed")
        
        result = self.manager.connect()
        
        self.assertFalse(result)

    def test_create_collection(self):
        """Test collection creation."""
        self.manager.client = MagicMock()
        self.manager.client.has_collection.return_value = False
        
        self.manager.create_collection("test_collection", 128)
        
        self.manager.client.create_collection.assert_called_once_with(
            collection_name="test_collection",
            dimension=128
        )

    def test_create_collection_existing(self):
        """Test creation of already existing collection."""
        self.manager.client = MagicMock()
        self.manager.client.has_collection.return_value = True
        
        self.manager.create_collection("test_collection", 128)
        
        self.manager.client.drop_collection.assert_called_once_with(
            collection_name="test_collection"
        )
        self.manager.client.create_collection.assert_called_once()

    def test_insert_vectors(self):
        """Test vector insertion."""
        self.manager.client = MagicMock()
        self.manager.client.has_collection.return_value = True
        
        data = [{"id": 1, "vector": [0.1, 0.2], "text": "test"}]
        self.manager.insert_vectors("test_collection", data)
        
        self.manager.client.insert.assert_called_once_with(
            collection_name="test_collection",
            data=data
        )

    def test_insert_vectors_no_collection(self):
        """Test vector insertion with non-existent collection."""
        self.manager.client = MagicMock()
        self.manager.client.has_collection.return_value = False
        
        with self.assertRaises(ValueError):
            self.manager.insert_vectors("nonexistent", [])

    def test_search_vectors(self):
        """Test vector similarity search."""
        self.manager.client = MagicMock()
        mock_results = [[{"id": 1, "distance": 0.8}]]
        self.manager.client.search.return_value = mock_results
        
        result = self.manager.search_vectors(
            "test_collection",
            [0.1, 0.2],
            limit=3,
            output_fields=["text", "file_id"]
        )
        
        self.assertEqual(result, mock_results[0])
        self.manager.client.search.assert_called_once_with(
            collection_name="test_collection",
            data=[[0.1, 0.2]],
            limit=3,
            output_fields=["text", "file_id"]
        )

    def test_delete_vectors(self):
        """Test vector deletion."""
        self.manager.client = MagicMock()
        
        self.manager.delete_vectors("test_collection", "file_id == 'test'")
        
        self.manager.client.delete.assert_called_once_with(
            collection_name="test_collection",
            filter="file_id == 'test'"
        )

    def test_drop_collection(self):
        """Test collection deletion."""
        self.manager.client = MagicMock()
        
        self.manager.drop_collection("test_collection")
        
        self.manager.client.drop_collection.assert_called_once_with(
            collection_name="test_collection"
        )

    def test_get_collection_info_success(self):
        """Test getting collection information."""
        self.manager.client = MagicMock()
        mock_info = {"name": "test_collection", "row_count": 100}
        self.manager.client.describe_collection.return_value = mock_info
        self.manager.client.get_collection_stats.return_value = {"stats": "test"}
        
        result = self.manager.get_collection_info("test_collection")
        
        self.assertEqual(result["name"], "test_collection")
        self.assertEqual(result["row_count"], 100)
        self.assertEqual(result["stats"], "test")

    def test_get_collection_info_error(self):
        """Test getting information for non-existent collection."""
        self.manager.client = MagicMock()
        self.manager.client.describe_collection.side_effect = MilvusException("Not found")
        
        result = self.manager.get_collection_info("nonexistent")
        
        self.assertEqual(result["name"], "nonexistent")
        self.assertEqual(result["row_count"], 0)
        self.assertEqual(result["status"], "Error")
        self.assertIn("error_message", result)

    def test_list_collections(self):
        """Test listing all collections."""
        self.manager.client = MagicMock()
        mock_collections = ["collection1", "collection2"]
        self.manager.client.list_collections.return_value = mock_collections
        
        result = self.manager.list_collections()
        
        self.assertEqual(result, mock_collections)
        self.manager.client.list_collections.assert_called_once()

    def test_query_vectors(self):
        """Test vector querying."""
        self.manager.client = MagicMock()
        
        self.manager.query_vectors(
            "test_collection",
            filter_expr="test_filter",
            output_fields=["field1", "field2"],
            limit=10
        )
        
        self.manager.client.query.assert_called_once_with(
            collection_name="test_collection",
            filter="test_filter",
            output_fields=["field1", "field2"],
            limit=10
        )


if __name__ == '__main__':
    unittest.main() 