"""
Database Manager Module

This module provides specialized functionality for managing knowledge databases.
It handles CRUD operations for knowledge base databases and their metadata.
"""

from sqlalchemy.orm import joinedload
from typing import Optional, Dict, Any, List
from datetime import datetime

from ai_engine.models.knowledge import KnowledgeDatabase, KnowledgeFile
from .base_manager import BaseDBManager
from ai_engine.configs.agent import AgentConfig

class DatabaseManager(BaseDBManager):
    """
    Knowledge Database operations manager.
    
    Handles all database-level operations including:
    - Creating new knowledge databases
    - Retrieving database information
    - Deleting databases
    - Managing database metadata
    """

    def __init__(self, agent_config: AgentConfig):
        """Initialize the database manager.
        
        Args:
            agent_config: Agent configuration object containing database settings.
        """
        super().__init__(agent_config)
        self._knowledge_models = None
        self._agent_config = agent_config
        self._setup_database()

    @property
    def knowledge_models(self):
        """Lazy load knowledge models."""
        if self._knowledge_models is None:
            from ai_engine.models.knowledge import KnowledgeDatabase, KnowledgeFile
            self._knowledge_models = (KnowledgeDatabase, KnowledgeFile)
        return self._knowledge_models

    @property
    def agent_config(self):
        """Lazy load agent config."""
        if self._agent_config is None:
            from ai_engine import agent_config
            self._agent_config = agent_config
        return self._agent_config

    def _setup_database(self):
        """Set up the database connection and tables."""
        KnowledgeDatabase, KnowledgeFile = self.knowledge_models
        # Rest of the setup code...

    def get_all_databases(self):
        """
        Get all registered knowledge bases.
        
        Uses eager loading to fetch associated files along with the database
        information to avoid N+1 query problems.
        
        Returns:
            list: List of dictionaries containing database information
        """
        with self.get_session() as session:
            # Use eager loading to load associated files
            databases = session.query(KnowledgeDatabase).options(
                joinedload(KnowledgeDatabase.related_files)
            ).all()

            # Convert to dictionary and return, avoid subsequent lazy loading
            return [db.as_dict() for db in databases]

    def get_database_by_id(self, db_id):
        """
        Get knowledge base by ID.
        
        Uses eager loading to fetch the complete database information
        including associated files and nodes.
        
        Args:
            db_id (str): The unique identifier of the database
            
        Returns:
            dict: Database information if found, None otherwise
        """
        with self.get_session() as session:
            # Use eager loading to load associated files
            db = session.query(KnowledgeDatabase).options(
                joinedload(KnowledgeDatabase.related_files).joinedload(KnowledgeFile.content_blocks)
            ).filter_by(uid=db_id).first()

            # Convert to dictionary and return, avoid subsequent lazy loading
            return db.as_dict() if db else None

    def create_database(self, db_id, name, description, embed_model=None, dimension=None, metadata=None):
        """
        Create a new knowledge database.
        
        Args:
            db_id (str): Unique identifier for the database
            name (str): Human-readable name for the database
            description (str): Description of the database's purpose
            embed_model (str, optional): Name of the embedding model to use
            dimension (int, optional): Vector dimension for the embeddings
            metadata (dict, optional): Additional metadata for the database
            
        Returns:
            dict: Created database information including:
                - uid: Database identifier
                - name: Database name
                - description: Database description
                - embedding: Embedding model name
                - dimension: Vector dimension
                - metadata: Additional metadata
                - files: Empty files dictionary
        """
        with self.get_session() as session:
            db = KnowledgeDatabase(
                uid=db_id,
                name=name,
                description=description,
                embedding=embed_model,
                dimension=dimension,
                metadata_extra=metadata or {}
            )
            session.add(db)
            session.flush()
            return db.as_dict()

    def delete_database(self, db_id):
        """
        Delete a knowledge database.
        
        This operation will cascade delete all associated files and nodes.
        
        Args:
            db_id (str): ID of the database to delete
            
        Returns:
            bool: True if database was found and deleted, False otherwise
        """
        with self.get_session() as session:
            db = session.query(KnowledgeDatabase).filter_by(uid=db_id).first()
            if db:
                session.delete(db)
                return True
            return False