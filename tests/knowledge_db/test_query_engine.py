"""
Unit tests for the QueryEngine class.
"""

import unittest
from unittest.mock import patch, MagicMock

from ai_engine.knowledge_database.query_engine import QueryEngine
from ai_engine.configs.agent import AgentConfig


class TestQueryEngine(unittest.TestCase):
    """Test cases for QueryEngine."""

    def setUp(self):
        """Set up test environment."""
        self.mock_config = MagicMock(spec=AgentConfig)
        self.mock_config.enable_rerank = True
        
        self.mock_milvus = MagicMock()
        self.mock_embedding = MagicMock()
        self.mock_db = MagicMock()
        
        self.engine = QueryEngine(
            self.mock_milvus,
            self.mock_embedding,
            self.mock_db,
            self.mock_config
        )

    def test_search(self):
        """Test basic vector similarity search."""
        # Setup mocks
        self.mock_embedding.encode_single_text.return_value = [0.1, 0.2]
        self.mock_milvus.search_vectors.return_value = [
            {"id": 1, "distance": 0.8}
        ]
        
        # Execute search
        result = self.engine.search("test query", "test_collection", limit=3)
        
        # Verify results
        self.assertEqual(result, [{"id": 1, "distance": 0.8}])
        self.mock_embedding.encode_single_text.assert_called_once_with("test query")
        self.mock_milvus.search_vectors.assert_called_once_with(
            "test_collection", [0.1, 0.2], 3
        )

    def test_advanced_query_with_rerank(self):
        """Test advanced query with reranking enabled."""
        # Setup mocks
        self.mock_embedding.encode_single_text.return_value = [0.1, 0.2]
        self.mock_milvus.search_vectors.return_value = [
            {
                "distance": 0.8,
                "entity": {
                    "file_id": "file1",
                    "text": "test text 1"
                }
            },
            {
                "distance": 0.6,
                "entity": {
                    "file_id": "file2",
                    "text": "test text 2"
                }
            }
        ]
        self.mock_db.get_file_by_id.side_effect = [
            {"uid": "file1", "filename": "test1.txt"},
            {"uid": "file2", "filename": "test2.txt"}
        ]
        self.mock_embedding.compute_rerank_scores.return_value = [0.9, 0.7]
        
        # Execute query
        result = self.engine.advanced_query(
            "test query",
            "test_db",
            distance_threshold=0.5,
            rerank_threshold=0.1,
            max_query_count=5,
            top_k=2
        )
        
        # Verify results
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(len(result["all_results"]), 2)
        self.assertEqual(result["results"][0]["rerank_score"], 0.9)
        self.assertEqual(result["results"][1]["rerank_score"], 0.7)
        
        # Verify mock calls
        self.mock_embedding.encode_single_text.assert_called_once_with("test query")
        self.mock_milvus.search_vectors.assert_called_once()
        self.mock_db.get_file_by_id.assert_any_call("file1")
        self.mock_db.get_file_by_id.assert_any_call("file2")
        self.mock_embedding.compute_rerank_scores.assert_called_once_with(
            "test query",
            ["test text 1", "test text 2"]
        )

    def test_advanced_query_without_rerank(self):
        """Test advanced query with reranking disabled."""
        # Setup mocks
        self.mock_config.enable_rerank = False
        self.mock_embedding.encode_single_text.return_value = [0.1, 0.2]
        self.mock_milvus.search_vectors.return_value = [
            {
                "distance": 0.8,
                "entity": {
                    "file_id": "file1",
                    "text": "test text"
                }
            }
        ]
        self.mock_db.get_file_by_id.return_value = {
            "uid": "file1",
            "filename": "test.txt"
        }
        
        # Execute query
        result = self.engine.advanced_query(
            "test query",
            "test_db",
            distance_threshold=0.5
        )
        
        # Verify results
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(len(result["all_results"]), 1)
        self.assertNotIn("rerank_score", result["results"][0])
        
        # Verify mock calls
        self.mock_embedding.compute_rerank_scores.assert_not_called()

    def test_create_retriever(self):
        """Test creating a retriever function."""
        # Setup mocks
        self.mock_embedding.encode_single_text.return_value = [0.1, 0.2]
        self.mock_milvus.search_vectors.return_value = [
            {
                "distance": 0.8,
                "entity": {
                    "file_id": "file1",
                    "text": "test text"
                }
            }
        ]
        self.mock_db.get_file_by_id.return_value = {
            "uid": "file1",
            "filename": "test.txt"
        }
        self.mock_embedding.reranker = None
        self.mock_config.enable_rerank = False
        
        # Create retriever
        retriever = self.engine.create_retriever(
            "test_db",
            distance_threshold=0.5,  # Changed to ensure result passes threshold
            rerank_threshold=0.2,
            max_query_count=10,
            top_k=5
        )
        
        # Execute retriever
        results = retriever("test query")
        
        # Verify results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["distance"], 0.8)
        
        # Verify mock calls
        self.mock_embedding.encode_single_text.assert_called_once_with("test query")
        self.mock_milvus.search_vectors.assert_called_once()
        self.mock_db.get_file_by_id.assert_called_once_with("file1")


if __name__ == '__main__':
    unittest.main() 