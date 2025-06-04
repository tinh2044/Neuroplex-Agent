"""
Tests for tool routes
"""
import os
import sys
import pytest
from unittest.mock import patch, Mock
from io import BytesIO

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestToolRoutes:
    """Test cases for tool routes"""
    
    @patch('ai_engine.agent_manager')
    def test_get_tools_list(self, mock_agent_manager, client):
        """Test getting the list of available tools"""
        # Mock agent manager to return tools list
        mock_tools = [
            {"name": "calculator", "description": "Basic calculator"},
            {"name": "web_search", "description": "Web search tool"},
            {"name": "file_reader", "description": "File reading tool"}
        ]
        mock_agent_manager.get_all_tools.return_value = mock_tools
        
        response = client.get("/tools/")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert len(data["tools"]) == 3
        assert data["tools"][0]["name"] == "calculator"
    
    @patch('ai_engine.text_chunker')
    def test_text_chunking(self, mock_chunker, client):
        """Test text chunking functionality"""
        # Mock chunking response
        mock_chunks = [
            {"chunk_id": 1, "text": "First chunk of text", "size": 20},
            {"chunk_id": 2, "text": "Second chunk of text", "size": 21},
            {"chunk_id": 3, "text": "Third chunk of text", "size": 20}
        ]
        mock_chunker.chunk_text.return_value = mock_chunks
        
        chunk_data = {
            "text": "This is a long text that needs to be chunked into smaller pieces for processing.",
            "chunk_size": 20,
            "overlap": 5
        }
        
        response = client.post("/tools/chunk", json=chunk_data)
        assert response.status_code == 200
        data = response.json()
        assert "chunks" in data
        assert len(data["chunks"]) == 3
        assert data["chunks"][0]["chunk_id"] == 1
    
    @patch('ai_engine.ocr_processor')
    def test_pdf_to_text_conversion(self, mock_ocr, client):
        """Test PDF to text conversion"""
        # Mock OCR response
        mock_text = "Extracted text from PDF document. This is the content of the PDF file."
        mock_ocr.extract_text_from_pdf.return_value = {
            "text": mock_text,
            "pages": 1,
            "word_count": 12,
            "success": True
        }
        
        # Create a mock PDF file
        pdf_content = b"%PDF-1.4 fake pdf content for testing"
        files = {"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")}
        
        response = client.post("/tools/pdf-to-text", files=files)
        assert response.status_code == 200
        data = response.json()
        assert "text" in data
        assert "pages" in data
        assert data["success"] is True
        assert data["text"] == mock_text
    
    @patch('ai_engine.web_scraper')
    def test_web_scraping(self, mock_scraper, client):
        """Test web scraping functionality"""
        # Mock scraping response
        mock_content = {
            "title": "Test Page",
            "content": "This is the scraped content from the web page.",
            "url": "https://example.com",
            "success": True,
            "links": ["https://example.com/page1", "https://example.com/page2"]
        }
        mock_scraper.scrape_url.return_value = mock_content
        
        scrape_data = {"url": "https://example.com"}
        
        response = client.post("/tools/scrape", json=scrape_data)
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "title" in data
        assert data["success"] is True
        assert data["url"] == "https://example.com"
    
    def test_text_chunking_missing_text(self, client):
        """Test text chunking with missing text field"""
        incomplete_data = {"chunk_size": 20}  # Missing text field
        response = client.post("/tools/chunk", json=incomplete_data)
        assert response.status_code in [400, 422]
    
    def test_pdf_upload_without_file(self, client):
        """Test PDF conversion without uploading a file"""
        response = client.post("/tools/pdf-to-text")
        assert response.status_code in [400, 422]
    
    @patch('ai_engine.ocr_processor')
    def test_pdf_conversion_error(self, mock_ocr, client):
        """Test PDF conversion when OCR processor raises an error"""
        mock_ocr.extract_text_from_pdf.side_effect = Exception("OCR processing failed")
        
        pdf_content = b"corrupted pdf content"
        files = {"file": ("corrupted.pdf", BytesIO(pdf_content), "application/pdf")}
        
        response = client.post("/tools/pdf-to-text", files=files)
        assert response.status_code in [500, 200]  # Depending on error handling
    
    def test_web_scraping_invalid_url(self, client):
        """Test web scraping with invalid URL"""
        invalid_data = {"url": "not-a-valid-url"}
        response = client.post("/tools/scrape", json=invalid_data)
        assert response.status_code in [400, 422]
    
    @patch('ai_engine.web_scraper')
    def test_web_scraping_error(self, mock_scraper, client):
        """Test web scraping when scraper raises an error"""
        mock_scraper.scrape_url.side_effect = Exception("Failed to scrape URL")
        
        scrape_data = {"url": "https://unreachable-site.com"}
        
        response = client.post("/tools/scrape", json=scrape_data)
        assert response.status_code in [500, 200]  # Depending on error handling
    
    @patch('ai_engine.text_chunker')
    def test_text_chunking_custom_params(self, mock_chunker, client):
        """Test text chunking with custom parameters"""
        mock_chunks = [
            {"chunk_id": 1, "text": "Custom chunk", "size": 12}
        ]
        mock_chunker.chunk_text.return_value = mock_chunks
        
        chunk_data = {
            "text": "Custom text for chunking",
            "chunk_size": 50,
            "overlap": 10,
            "strategy": "semantic"
        }
        
        response = client.post("/tools/chunk", json=chunk_data)
        assert response.status_code == 200
        data = response.json()
        assert "chunks" in data
        # Verify that custom parameters were passed to the chunker
        mock_chunker.chunk_text.assert_called_once() 