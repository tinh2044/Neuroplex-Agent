"""
Unit tests for the DocumentProcessor class.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from ai_engine.knowledge_database.document_processor import DocumentProcessor


class TestDocumentProcessor(unittest.TestCase):
    """Test cases for DocumentProcessor."""

    def setUp(self):
        """Set up test environment."""
        self.processor = DocumentProcessor()
        self.test_files = [
            "test1.pdf",
            "test2.txt",
            "test3.md",
            "test4.docx"
        ]

    @patch('ai_engine.knowledge_database.document_processor.read_text')
    @patch('ai_engine.knowledge_database.document_processor.chunk')
    def test_process_files(self, mock_chunk, mock_read_text):
        """Test processing multiple files."""
        # Mock dependencies
        mock_read_text.return_value = ["Test content"]
        mock_chunk.return_value = [
            MagicMock(dict=lambda: {
                "text": "Test chunk",
                "start_char_idx": 0,
                "end_char_idx": 10
            })
        ]

        # Process files
        result = self.processor.process_files(self.test_files)

        # Verify results
        self.assertEqual(len(result), len(self.test_files))
        for file_id, info in result.items():
            self.assertIn("file_id", info)
            self.assertIn("filename", info)
            self.assertIn("path", info)
            self.assertIn("type", info)
            self.assertIn("status", info)
            self.assertIn("created_at", info)
            self.assertIn("nodes", info)
            self.assertEqual(len(info["nodes"]), 1)

    def test_process_files_with_error(self):
        """Test processing files with error handling."""
        with patch('ai_engine.knowledge_database.document_processor.read_text') as mock_read:
            mock_read.side_effect = Exception("Test error")
            
            result = self.processor.process_files(["test.pdf"])
            
            file_info = list(result.values())[0]
            self.assertEqual(file_info["status"], "failed")
            self.assertIn("error", file_info)
            self.assertEqual(len(file_info["nodes"]), 0)

    def test_validate_file_type(self):
        """Test file type validation."""
        valid_files = [
            "test.pdf",
            "test.txt",
            "test.md",
            "test.docx"
        ]
        invalid_files = [
            "test.jpg",
            "test.exe",
            "test.zip"
        ]

        for file in valid_files:
            self.assertTrue(self.processor.validate_file_type(file))

        for file in invalid_files:
            self.assertFalse(self.processor.validate_file_type(file))

    def test_process_url(self):
        """Test URL processing raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            self.processor.process_url("https://example.com")


if __name__ == '__main__':
    unittest.main() 