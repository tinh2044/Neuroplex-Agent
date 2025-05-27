"""
Document Processor Module

This module handles the processing of various document types into chunks
suitable for knowledge base storage and retrieval. It supports multiple
file formats and provides text chunking functionality.
"""

import os
import time
from ai_engine.utils import hashstr, logger
from ai_engine.core.indexing import chunk, read_text


class DocumentProcessor:
    """
    Document processing and chunking manager.
    
    Handles the conversion of various document types into text chunks
    that can be stored in the knowledge base. Supports multiple file
    formats including PDF, TXT, MD, and DOCX.
    """
    
    def __init__(self):
        """Initialize the document processor."""
        pass
    
    def process_files(self, files, params=None):
        """
        Convert files into chunks suitable for knowledge base storage.
        
        Processes multiple files, converting each into a series of text chunks
        based on the file type and chunking parameters.
        
        Args:
            files (list): List of file paths to process
            params (dict, optional): Parameters for the chunking process
            
        Returns:
            dict: Dictionary mapping file IDs to file information including:
                - file_id: Unique identifier for the file
                - filename: Original file name
                - path: File path
                - type: File type
                - status: Processing status
                - created_at: Timestamp
                - nodes: List of text chunks
                - error: Error message if processing failed
        """
        file_infos = {}
        for file in files:
            file_id = "file_" + hashstr(file + str(time.time()))
            file_type = file.split(".")[-1].lower()
            
            try:
                if file_type == "pdf":
                    texts = read_text(file)
                    nodes = chunk(texts, params=params)
                else:
                    nodes = chunk(file, params=params)
                
                file_infos[file_id] = {
                    "file_id": file_id,
                    "filename": os.path.basename(file),
                    "path": file,
                    "type": file_type,
                    "status": "waiting",
                    "created_at": time.time(),
                    "nodes": [node.dict() for node in nodes]
                }
            except Exception as e:
                logger.error(f"Failed to process file {file}: {e}")
                file_infos[file_id] = {
                    "file_id": file_id,
                    "filename": os.path.basename(file),
                    "path": file,
                    "type": file_type,
                    "status": "failed",
                    "error": str(e),
                    "created_at": time.time(),
                    "nodes": []
                }
        
        return file_infos
    
    def process_url(self, url, params=None):
        """
        Process content from a URL into chunks.
        
        Args:
            url (str): URL to process
            params (dict, optional): Parameters for the chunking process
            
        Raises:
            NotImplementedError: URL processing is not yet implemented
        """
        raise NotImplementedError("URL processing not implemented yet")
    
    def validate_file_type(self, file_path):
        """
        Check if a file type is supported for processing.
        
        Args:
            file_path (str): Path to the file to validate
            
        Returns:
            bool: True if file type is supported, False otherwise
        """
        supported_types = ['pdf', 'txt', 'md', 'docx']
        file_type = file_path.split(".")[-1].lower()
        return file_type in supported_types
