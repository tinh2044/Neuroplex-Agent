"""
Node Manager Module

This module provides functionality for managing knowledge nodes/chunks.
It handles CRUD operations for text chunks and their metadata within
the knowledge base.
"""

from ai_engine.models.knowledge import KnowledgeNode
from .base_manager import BaseDBManager
from ai_engine.configs.agent import AgentConfig

class NodeManager(BaseDBManager):
    """
    Knowledge Node operations manager.
    
    Handles all node-level operations including:
    - Adding new text chunks
    - Retrieving nodes by file
    - Searching nodes by content
    - Managing node metadata
    """
    def __init__(self, agent_config: AgentConfig):
        super().__init__(agent_config)

    def add_node(self, file_id, text, hash_value=None, start_char_idx=None, end_char_idx=None, metadata=None):
        """
        Add a new knowledge node/chunk.
        
        Args:
            file_id (str): ID of the file this node belongs to
            text (str): The actual text content of the node
            hash_value (str, optional): Hash of the text content
            start_char_idx (int, optional): Starting character index in original file
            end_char_idx (int, optional): Ending character index in original file
            metadata (dict, optional): Additional metadata for the node
            
        Returns:
            dict: Created node information including:
                - id: Node identifier
                - file_id: Parent file ID
                - text: Node content
                - hash: Content hash
                - start_char_idx: Start index
                - end_char_idx: End index
                - metadata: Additional metadata
        """
        with self.get_session() as session:
            node = KnowledgeNode(
                file_uid=file_id,
                content_text=text,
                hash=hash_value,
                start_pos=start_char_idx,
                end_pos=end_char_idx,
                metadata_extra=metadata or {}
            )
            session.add(node)
            session.flush()

            return node.as_dict()

    def get_nodes_by_file(self, file_id):
        """
        Get all nodes/chunks from a specific file.
        
        Args:
            file_id (str): ID of the file
            
        Returns:
            list: List of node information dictionaries
        """
        with self.get_session() as session:
            nodes = session.query(KnowledgeNode).filter_by(file_uid=file_id).all()
            return [node.as_dict() for node in nodes]

    def get_nodes_by_filter(self, file_id=None, search_text=None, limit=100):
        """
        Search for nodes/chunks using filters.
        
        Args:
            file_id (str, optional): Filter by specific file
            search_text (str, optional): Filter by text content
            limit (int, optional): Maximum number of results. Defaults to 100
            
        Returns:
            list: List of matching node information dictionaries
        """
        with self.get_session() as session:
            query = session.query(KnowledgeNode)
            if file_id:
                query = query.filter_by(file_uid=file_id)
            if search_text:
                query = query.filter(KnowledgeNode.content_text.like(f"%{search_text}%"))
            nodes = query.limit(limit).all()
            return [node.as_dict() for node in nodes]