"""
Unit tests for the KnowledgeBase class.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from ai_engine.knowledge_database import KnowledgeBase
from ai_engine.knowledge_database.kb_db_manager import KBDBManager
from ai_engine.configs.agent import AgentConfig


class TestKnowledgeBase(unittest.TestCase):
    """Test cases for KnowledgeBase."""

    def setUp(self):
        """Set up test environment."""
        # Mock config
        self.mock_config = MagicMock(spec=AgentConfig)
        self.mock_config.enable_kb = True
        self.mock_config.workspace = "test_workspace"
        
        # Mock dependencies
        self.mock_db_manager = MagicMock(spec=KBDBManager)
        self.mock_milvus_manager = MagicMock()
        self.mock_doc_processor = MagicMock()
        self.mock_embedding_manager = MagicMock()
        self.mock_query_engine = MagicMock()
        
        # Create patches
        self.patches = [
            patch('ai_engine.knowledge_database.MilvusManager', return_value=self.mock_milvus_manager),
            patch('ai_engine.knowledge_database.DocumentProcessor', return_value=self.mock_doc_processor),
            patch('ai_engine.knowledge_database.EmbeddingManager', return_value=self.mock_embedding_manager),
            patch('ai_engine.knowledge_database.QueryEngine', return_value=self.mock_query_engine),
            patch('ai_engine.knowledge_database.hashstr', return_value='d6d59f83')
        ]
        
        # Start patches
        for p in self.patches:
            p.start()
            
        self.kb = KnowledgeBase(self.mock_config, self.mock_db_manager)

    def tearDown(self):
        """Clean up test environment."""
        # Stop patches
        for p in self.patches:
            p.stop()

    def test_initialization(self):
        """Test knowledge base initialization."""
        self.assertEqual(self.kb.work_dir, os.path.join("test_workspace", "data"))
        self.assertEqual(self.kb.db_manager, self.mock_db_manager)
        self.assertEqual(self.kb.milvus_manager, self.mock_milvus_manager)
        self.assertEqual(self.kb.doc_processor, self.mock_doc_processor)
        self.assertEqual(self.kb.embedding_manager, self.mock_embedding_manager)
        self.assertEqual(self.kb.query_engine, self.mock_query_engine)

    def test_create_database(self):
        """Test database creation."""
        # Mock dependencies
        self.mock_embedding_manager.get_dimension.return_value = 128
        self.mock_embedding_manager.get_model_name.return_value = "test_model"
        self.mock_db_manager.create_database.return_value = {
            "db_id": "kb_d6d59f83",
            "name": "Test DB",
            "description": "Test description",
            "embed_model": "test_model",
            "dimension": 128,
            "meta_info": {"key": "value"}
        }

        # Create database
        result = self.kb.create_database(
            database_name="Test DB",
            description="Test description"
        )

        # Verify results
        self.assertEqual(result["db_id"], "kb_d6d59f83")
        self.assertEqual(result["name"], "Test DB")
        self.assertEqual(result["embed_model"], "test_model")
        self.assertEqual(result["dimension"], 128)
        self.assertEqual(result["meta_info"], {"key": "value"})
        self.mock_milvus_manager.create_collection.assert_called_once_with(
            "kb_d6d59f83", 128
        )

    def test_get_databases(self):
        """Test retrieving all databases."""
        # Mock dependencies
        self.mock_db_manager.get_all_databases.return_value = [
            {
                "db_id": "db1",
                "name": "DB 1",
                "embed_model": "test_model",
                "meta_info": {}
            },
            {
                "db_id": "db2",
                "name": "DB 2",
                "embed_model": "test_model",
                "meta_info": {"type": "docs"}
            }
        ]
        self.mock_milvus_manager.get_collection_info.return_value = {
            "row_count": 100,
            "status": "Active"
        }

        # Get databases
        result = self.kb.get_databases()

        # Verify results
        self.assertIn("databases", result)
        self.assertEqual(len(result["databases"]), 2)
        self.assertEqual(result["databases"][0]["metadata"]["row_count"], 100)
        self.assertEqual(result["databases"][0]["db_id"], "db1")
        self.assertEqual(result["databases"][1]["db_id"], "db2")
        self.assertEqual(result["databases"][1]["meta_info"]["type"], "docs")

    def test_delete_database(self):
        """Test database deletion."""
        result = self.kb.delete_database("test_db")

        self.mock_milvus_manager.drop_collection.assert_called_once_with("test_db")
        self.mock_db_manager.delete_database.assert_called_once_with("test_db")
        self.assertEqual(result["message"], "Successfully deleted")

    def test_add_files(self):
        """Test adding files to database."""
        # Mock dependencies
        self.mock_db_manager.get_database_by_id.return_value = {
            "db_id": "test_db",
            "embed_model": "test_model"
        }
        self.mock_embedding_manager.check_model_compatibility.return_value = True
        self.mock_doc_processor.process_files.return_value = {
            "file1": {
                "filename": "test.txt",
                "path": "/path/to/test.txt",
                "type": "txt",
                "nodes": [
                    {
                        "text": "Test content",
                        "start_char_idx": 0,
                        "end_char_idx": 12,
                        "meta_info": {}
                    }
                ]
            }
        }
        self.mock_embedding_manager.encode_texts.return_value = [[0.1, 0.2]]

        # Add files
        self.kb.add_files("test_db", ["test.txt"])

        # Verify calls
        self.mock_db_manager.add_file.assert_called_once()
        self.mock_db_manager.update_file_status.assert_called_with("file1", "done")

    def test_add_files_model_mismatch(self):
        """Test adding files with incompatible model."""
        # Mock dependencies
        self.mock_db_manager.get_database_by_id.return_value = {
            "db_id": "test_db",
            "embed_model": "other_model"
        }
        self.mock_embedding_manager.check_model_compatibility.return_value = False
        self.mock_embedding_manager.get_model_name.return_value = "test_model"

        # Add files
        result = self.kb.add_files("test_db", ["test.txt"])

        # Verify result
        self.assertEqual(result["status"], "failed")
        self.assertIn("Model mismatch", result["message"])
        self.mock_db_manager.add_file.assert_not_called()

    def test_query(self):
        """Test database querying."""
        # Mock query result
        mock_result = {
            "results": [
                {
                    "distance": 0.8,
                    "entity": {"text": "Result 1"},
                    "rerank_score": 0.9,
                    "file": {"filename": "test1.txt"}
                }
            ],
            "all_results": [
                {
                    "distance": 0.8,
                    "entity": {"text": "Result 1"},
                    "file": {"filename": "test1.txt"}
                },
                {
                    "distance": 0.6,
                    "entity": {"text": "Result 2"},
                    "file": {"filename": "test2.txt"}
                }
            ]
        }
        self.mock_query_engine.advanced_query.return_value = mock_result

        # Perform query
        result = self.kb.query(
            "test query",
            "test_db",
            top_k=1,
            distance_threshold=0.5,
            rerank_threshold=0.1
        )

        # Verify results
        self.assertEqual(result, mock_result)
        self.mock_query_engine.advanced_query.assert_called_once_with(
            "test query",
            "test_db",
            top_k=1,
            distance_threshold=0.5,
            rerank_threshold=0.1
        )

    def test_get_retrievers(self):
        """Test getting all retrievers."""
        # Mock dependencies
        self.mock_db_manager.get_all_databases.return_value = [
            {
                "db_id": "db1",
                "name": "DB 1",
                "description": "Test DB",
                "embed_model": "test_model",
                "meta_info": {"type": "docs"}
            }
        ]
        self.mock_embedding_manager.check_model_compatibility.return_value = True
        mock_retriever = MagicMock()
        self.mock_query_engine.create_retriever.return_value = mock_retriever

        # Get retrievers
        result = self.kb.get_retrievers()

        # Verify results
        self.assertIn("db1", result)
        self.assertEqual(result["db1"]["name"], "DB 1")
        self.assertEqual(result["db1"]["retriever"], mock_retriever)
        self.assertEqual(result["db1"]["embed_model"], "test_model")

    def test_get_database_info(self):
        """Test getting database information."""
        # Mock dependencies
        self.mock_db_manager.get_database_by_id.return_value = {
            "db_id": "test_db",
            "name": "Test DB",
            "embed_model": "test_model",
            "meta_info": {"type": "docs"}
        }
        self.mock_milvus_manager.get_collection_info.return_value = {
            "row_count": 100,
            "status": "Active"
        }

        # Get database info
        result = self.kb.get_database_info("test_db")

        # Verify results
        self.assertEqual(result["name"], "Test DB")
        self.assertEqual(result["row_count"], 100)
        self.assertEqual(result["status"], "Active")
        self.assertEqual(result["meta_info"]["type"], "docs")


if __name__ == '__main__':
    unittest.main() 