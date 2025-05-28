"""
Unit tests for the FileManager class.
"""

import unittest
from unittest.mock import patch, MagicMock

from ai_engine.knowledge_database.file_manager import FileManager
from ai_engine.models.knowledge import KnowledgeFile
from ai_engine.configs.agent import AgentConfig


class TestFileManager(unittest.TestCase):
    """Test cases for FileManager."""

    def setUp(self):
        """Set up test environment."""
        self.mock_config = MagicMock(spec=AgentConfig)
        self.mock_config.workspace = 'test_workspace'
        self.manager = FileManager(self.mock_config)

    def test_add_file(self):
        """Test adding a new file."""
        mock_session = MagicMock()
        
        with patch.object(self.manager, 'get_session') as mock_get_session:
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            result = self.manager.add_file(
                db_id="test_db",
                uid="test_file",
                filename="test.txt",
                path="/path/to/test.txt",
                kind="txt",
                state="waiting"
            )
            
            self.assertEqual(result["uid"], "test_file")
            self.assertEqual(result["filename"], "test.txt")
            self.assertEqual(result["path"], "/path/to/test.txt")
            self.assertEqual(result["type"], "txt")
            self.assertEqual(result["status"], "waiting")
            self.assertEqual(result["nodes"], [])

    def test_update_file_status(self):
        """Test updating file status."""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = MagicMock()

        with patch.object(self.manager, 'get_session') as mock_get_session:
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            result = self.manager.update_file_status("test_file", "processing")
            
            self.assertTrue(result)
            mock_query.filter_by.assert_called_once_with(uid="test_file")

    def test_update_nonexistent_file_status(self):
        """Test updating status of non-existent file."""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = None

        with patch.object(self.manager, 'get_session') as mock_get_session:
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            result = self.manager.update_file_status("nonexistent", "processing")
            
            self.assertFalse(result)

    def test_delete_file(self):
        """Test file deletion."""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = MagicMock()

        with patch.object(self.manager, 'get_session') as mock_get_session:
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            result = self.manager.delete_file("test_file")
            
            self.assertTrue(result)
            mock_session.delete.assert_called_once()

    def test_delete_nonexistent_file(self):
        """Test deletion of non-existent file."""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = None

        with patch.object(self.manager, 'get_session') as mock_get_session:
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            result = self.manager.delete_file("nonexistent")
            
            self.assertFalse(result)
            mock_session.delete.assert_not_called()

    def test_get_files_by_database(self):
        """Test retrieving files by database."""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.all.return_value = [
            MagicMock(as_dict=lambda: {"uid": "file1", "filename": "test1.txt"}),
            MagicMock(as_dict=lambda: {"uid": "file2", "filename": "test2.txt"})
        ]

        with patch.object(self.manager, 'get_session') as mock_get_session:
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            result = self.manager.get_files_by_database("test_db")
            
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["uid"], "file1")
            self.assertEqual(result[1]["filename"], "test2.txt")

    def test_get_file_by_id(self):
        """Test retrieving specific file."""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = MagicMock(
            as_dict=lambda: {"uid": "test_file", "filename": "test.txt"}
        )

        with patch.object(self.manager, 'get_session') as mock_get_session:
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            result = self.manager.get_file_by_id("test_file")
            
            self.assertIsNotNone(result)
            self.assertEqual(result["uid"], "test_file")
            self.assertEqual(result["filename"], "test.txt")


if __name__ == '__main__':
    unittest.main() 