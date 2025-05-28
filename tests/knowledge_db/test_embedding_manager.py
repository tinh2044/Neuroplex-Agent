"""
Unit tests for the EmbeddingManager class.
"""

import unittest
from unittest.mock import patch, MagicMock

from ai_engine.knowledge_database.embedding_manager import EmbeddingManager
from ai_engine.configs.agent import AgentConfig
from ai_engine import agent_config

class TestEmbeddingManager(unittest.TestCase):
    """Test cases for EmbeddingManager."""

    def setUp(self):
        """Set up test environment."""
        self.mock_config = MagicMock(spec=AgentConfig)
        self.mock_config.enable_kb = True
        self.mock_config.enable_rerank = True
        self.mock_config.embed_model = "test_model"
        
        self.manager = EmbeddingManager(self.mock_config)

    @patch('ai_engine.knowledge_database.embedding_manager.initialize_embedding')
    @patch('ai_engine.knowledge_database.embedding_manager.initialize_reranker')
    def test_initialize_models(self, mock_init_reranker, mock_init_embedding):
        """Test model initialization."""
        # Setup mock embedding model
        mock_embed_model = MagicMock()
        mock_embed_model.embed_model_fullname = "test_model"
        mock_init_embedding.return_value = mock_embed_model
        
        # Setup mock reranker
        mock_reranker = MagicMock()
        mock_init_reranker.return_value = mock_reranker
        
        # Re-initialize models
        self.manager._initialize_models()
        
        # Verify results
        self.assertIsNotNone(self.manager.embed_model)
        self.assertIsNotNone(self.manager.reranker)
        mock_init_embedding.assert_called_once_with(self.mock_config)
        mock_init_reranker.assert_called_once_with(self.mock_config)

    def test_encode_texts_no_model(self):
        """Test encoding texts without initialized model."""
        self.manager.embed_model = None
        with self.assertRaises(ValueError):
            self.manager.encode_texts(["test"])

    def test_encode_texts(self):
        """Test encoding multiple texts."""
        mock_model = MagicMock()
        mock_model.batch_encode.return_value = [[0.1, 0.2], [0.3, 0.4]]
        self.manager.embed_model = mock_model

        result = self.manager.encode_texts(["test1", "test2"])

        self.assertEqual(len(result), 2)
        mock_model.batch_encode.assert_called_once_with(["test1", "test2"])

    def test_encode_single_text(self):
        """Test encoding single text."""
        mock_model = MagicMock()
        mock_model.batch_encode.return_value = [[0.1, 0.2]]
        self.manager.embed_model = mock_model

        result = self.manager.encode_single_text("test")

        self.assertEqual(result, [0.1, 0.2])
        mock_model.batch_encode.assert_called_once_with(["test"])

    def test_get_dimension(self):
        """Test getting embedding dimension."""
        mock_model = MagicMock()
        mock_model.get_dimension.return_value = 128
        self.manager.embed_model = mock_model

        result = self.manager.get_dimension()

        self.assertEqual(result, 128)
        mock_model.get_dimension.assert_called_once()

    def test_get_dimension_no_model(self):
        """Test getting dimension without model."""
        self.manager.embed_model = None
        result = self.manager.get_dimension()
        self.assertIsNone(result)

    def test_get_model_name(self):
        """Test getting model name."""
        mock_model = MagicMock()
        mock_model.embed_model_fullname = "test_model"
        self.manager.embed_model = mock_model

        result = self.manager.get_model_name()

        self.assertEqual(result, "test_model")

    def test_get_model_name_no_model(self):
        """Test getting model name without model."""
        self.manager.embed_model = None
        result = self.manager.get_model_name()
        self.assertIsNone(result)

    def test_compute_rerank_scores(self):
        """Test computing rerank scores."""
        mock_reranker = MagicMock()
        mock_reranker.compute_score.return_value = [0.8, 0.6]
        self.manager.reranker = mock_reranker

        result = self.manager.compute_rerank_scores("query", ["text1", "text2"])

        self.assertEqual(result, [0.8, 0.6])
        mock_reranker.compute_score.assert_called_once_with(["query", ["text1", "text2"]], normalize=False)

    def test_compute_rerank_scores_no_reranker(self):
        """Test computing rerank scores without reranker."""
        self.manager.reranker = None
        result = self.manager.compute_rerank_scores("query", ["text"])
        self.assertIsNone(result)

    def test_check_model_compatibility(self):
        """Test model compatibility check."""
        mock_model = MagicMock()
        mock_model.embed_model_fullname = "test_model"
        self.manager.embed_model = mock_model

        self.assertTrue(self.manager.check_model_compatibility("test_model"))
        self.assertFalse(self.manager.check_model_compatibility("other_model"))


if __name__ == '__main__':
    unittest.main() 