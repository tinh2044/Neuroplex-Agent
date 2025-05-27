"""
Knowledge Database Package

This package provides a unified interface for managing knowledge bases, including:
- Database management (creation, deletion, querying)
- File management (uploading, processing, deletion)
- Node management (text chunks/blocks management)
- Integration with Milvus vector database
"""

from .database_manager import DatabaseManager
from .file_manager import FileManager
from .node_manager import NodeManager


class KBDBManager:
    """
    Unified Knowledge Base Database Manager - Backward compatible interface
    
    This class provides a unified interface to manage all aspects of the knowledge base:
    - Database operations (create, delete, query)
    - File operations (add, update, delete)
    - Node operations (add, query)
    
    It acts as a facade pattern implementation, delegating operations to specialized managers.
    """
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.file_manager = FileManager()
        self.node_manager = NodeManager()
    
    def get_all_databases(self):
        """Get all registered knowledge databases"""
        return self.db_manager.get_all_databases()
    
    def get_database_by_id(self, db_id):
        """
        Get a specific database by its ID
        
        Args:
            db_id (str): The unique identifier of the database
            
        Returns:
            dict: Database information if found, None otherwise
        """
        return self.db_manager.get_database_by_id(db_id)
    
    def create_database(self, db_id, name, description, embed_model=None, dimension=None, metadata=None):
        """
        Create a new knowledge database
        
        Args:
            db_id (str): Unique identifier for the database
            name (str): Human-readable name for the database
            description (str): Description of the database's purpose
            embed_model (str, optional): Name of the embedding model to use
            dimension (int, optional): Vector dimension for the embeddings
            metadata (dict, optional): Additional metadata for the database
            
        Returns:
            dict: Created database information
        """
        return self.db_manager.create_database(db_id, name, description, embed_model, dimension, metadata)
    
    def delete_database(self, db_id):
        """
        Delete a database and all its associated data
        
        Args:
            db_id (str): ID of the database to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.db_manager.delete_database(db_id)
    
    # Knowledge File operations
    def add_file(self, db_id, file_id, filename, path, file_type, status="waiting"):
        """
        Add a new file to the knowledge base
        
        Args:
            db_id (str): ID of the database to add the file to
            file_id (str): Unique identifier for the file
            filename (str): Original name of the file
            path (str): Path where the file is stored
            file_type (str): Type/extension of the file
            status (str, optional): Initial processing status. Defaults to "waiting"
            
        Returns:
            dict: Added file information
        """
        return self.file_manager.add_file(db_id, file_id, filename, path, file_type, status)
    
    def update_file_status(self, file_id, status):
        """
        Update the processing status of a file
        
        Args:
            file_id (str): ID of the file to update
            status (str): New status value
            
        Returns:
            bool: True if successful, False if file not found
        """
        return self.file_manager.update_file_status(file_id, status)
    
    def delete_file(self, file_id):
        """
        Delete a file and its associated data
        
        Args:
            file_id (str): ID of the file to delete
            
        Returns:
            bool: True if successful, False if file not found
        """
        return self.file_manager.delete_file(file_id)
    
    def get_files_by_database(self, db_id):
        """
        Get all files associated with a database
        
        Args:
            db_id (str): ID of the database
            
        Returns:
            list: List of file information dictionaries
        """
        return self.file_manager.get_files_by_database(db_id)
    
    def get_file_by_id(self, file_id):
        """
        Get information about a specific file
        
        Args:
            file_id (str): ID of the file
            
        Returns:
            dict: File information if found, None otherwise
        """
        return self.file_manager.get_file_by_id(file_id)
    
    # Knowledge Node operations
    def add_node(self, file_id, text, hash_value=None, start_char_idx=None, end_char_idx=None, metadata=None):
        """
        Add a new knowledge node/chunk
        
        Args:
            file_id (str): ID of the file this node belongs to
            text (str): The actual text content of the node
            hash_value (str, optional): Hash of the text content
            start_char_idx (int, optional): Starting character index in original file
            end_char_idx (int, optional): Ending character index in original file
            metadata (dict, optional): Additional metadata for the node
            
        Returns:
            dict: Created node information
        """
        return self.node_manager.add_node(file_id, text, hash_value, start_char_idx, end_char_idx, metadata)
    
    def get_nodes_by_file(self, file_id):
        """
        Get all nodes/chunks from a specific file
        
        Args:
            file_id (str): ID of the file
            
        Returns:
            list: List of node information dictionaries
        """
        return self.node_manager.get_nodes_by_file(file_id)
    
    def get_nodes_by_filter(self, file_id=None, search_text=None, limit=100):
        """
        Search for nodes/chunks using filters
        
        Args:
            file_id (str, optional): Filter by specific file
            search_text (str, optional): Filter by text content
            limit (int, optional): Maximum number of results. Defaults to 100
            
        Returns:
            list: List of matching node information dictionaries
        """
        return self.node_manager.get_nodes_by_filter(file_id, search_text, limit)


# Create singleton instance for backward compatibility
kb_db_manager = KBDBManager()

# Export individual managers for direct use
__all__ = ['KBDBManager', 'DatabaseManager', 'FileManager', 'NodeManager', 'kb_db_manager']