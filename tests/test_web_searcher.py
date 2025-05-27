"""
Test module for the WebSearcher class.

This module contains unit tests for the WebSearcher class functionality,
including initialization, search operations, and result formatting.
Tests cover both successful scenarios and error handling.
"""

import os
import unittest
from unittest.mock import patch
from ai_engine.utils.web_search import WebSearcher


class TestWebSearcher(unittest.TestCase):
    """
    Test suite for WebSearcher class.
    
    Tests the initialization, search functionality, and result formatting
    of the WebSearcher class. Includes tests for both successful operations
    and error handling scenarios.
    """

    def setUp(self):
        """
        Set up test environment before each test.
        
        Creates a mock environment with a fake Tavily API key.
        """
        self.patcher = patch.dict(os.environ, {"TAVILY_API_KEY": "fake-api-key"})
        self.patcher.start()

    def tearDown(self):
        """
        Clean up test environment after each test.
        
        Removes the mock environment patch.
        """
        self.patcher.stop()

    @patch("ai_engine.utils.web_search.TavilyClient")
    def test_initialization_with_api_key(self, MockClient):
        """
        Test WebSearcher initialization with API key.
        
        Verifies that WebSearcher properly initializes when a valid
        API key is present in the environment.
        
        Args:
            MockClient: Mock object for TavilyClient
        """
        ws = WebSearcher()
        self.assertEqual(ws.client, MockClient.return_value)

    def test_initialization_without_api_key(self):
        """
        Test WebSearcher initialization without API key.
        
        Verifies that WebSearcher raises ValueError when no API key
        is present in the environment.
        """
        os.environ.pop("TAVILY_API_KEY", None)
        with self.assertRaises(ValueError):
            WebSearcher()

    @patch("ai_engine.utils.web_search.TavilyClient")
    def test_search_success(self, MockClient):
        """
        Test successful search operation.
        
        Verifies that search method properly processes and returns
        results when the API call is successful.
        
        Args:
            MockClient: Mock object for TavilyClient
        """
        mock_instance = MockClient.return_value
        mock_instance.search.return_value = {
            "results": [
                {
                    "title": "Test Title",
                    "content": "Some content here",
                    "url": "http://example.com",
                    "score": 0.9,
                }
            ]
        }

        ws = WebSearcher()
        results = ws.search("test query")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Test Title")

    @patch("ai_engine.utils.web_search.TavilyClient")
    def test_search_exception_handling(self, MockClient):
        """
        Test search error handling.
        
        Verifies that search method properly handles exceptions
        by returning an empty list.
        
        Args:
            MockClient: Mock object for TavilyClient
        """
        mock_instance = MockClient.return_value
        mock_instance.search.side_effect = Exception("Simulated error")

        ws = WebSearcher()
        results = ws.search("trigger error")

        self.assertEqual(results, [])

    def test_format_search_results(self):
        """
        Test search results formatting.
        
        Verifies that format_search_results properly formats
        search results into a readable string.
        """
        ws = WebSearcher()
        results = [
            {
                "title": "Sample Title",
                "content": "This is a sample.",
                "url": "http://example.com",
                "score": 0.8,
            }
        ]

        formatted = ws.format_search_results(results)
        self.assertIn("Sample Title", formatted)
        self.assertIn("http://example.com", formatted)

    def test_format_empty_results(self):
        """
        Test empty results formatting.
        
        Verifies that format_search_results properly handles
        empty result lists.
        """
        ws = WebSearcher()
        formatted = ws.format_search_results([])
        self.assertEqual(formatted, "No related web search results found.")


if __name__ == "__main__":
    unittest.main()
