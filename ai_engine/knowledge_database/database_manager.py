"""
Database Manager Module

This module provides specialized functionality for managing knowledge databases.
It handles CRUD operations for knowledge base databases and their metadata.
"""

from sqlalchemy.orm import joinedload

from ai_engine.models.knowledge import KnowledgeDatabase, KnowledgeFile
from .base_manager import BaseDBManager


class DatabaseManager(BaseDBManager):
    """
    Knowledge Database operations manager.
    
    Handles all database-level operations including:
    - Creating new knowledge databases
    - Retrieving database information
    - Deleting databases
    - Managing database metadata
    """

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
                joinedload(KnowledgeDatabase.files)
            ).all()

            # Convert to dictionary and return, avoid subsequent lazy loading
            return [self._to_dict_safely(db) for db in databases]

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
                joinedload(KnowledgeDatabase.files).joinedload(KnowledgeFile.nodes)
            ).filter_by(db_id=db_id).first()

            # Convert to dictionary and return, avoid subsequent lazy loading
            return self._to_dict_safely(db) if db else None

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
                - db_id: Database identifier
                - name: Database name
                - description: Database description
                - embed_model: Embedding model name
                - dimension: Vector dimension
                - metadata: Additional metadata
                - files: Empty files dictionary
        """
        with self.get_session() as session:
            db = KnowledgeDatabase(
                db_id=db_id,
                name=name,
                description=description,
                embed_model=embed_model,
                dimension=dimension,
                meta_info=metadata or {}  
            )
            session.add(db)
            session.flush()  

            db_dict = {
                "db_id": db_id,
                "name": name,
                "description": description,
                "embed_model": embed_model,
                "dimension": dimension,
                "metadata": metadata or {}, 
                "files": {}
            }
            return db_dict

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
            db = session.query(KnowledgeDatabase).filter_by(db_id=db_id).first()
            if db:
                session.delete(db)
                return True
            return False