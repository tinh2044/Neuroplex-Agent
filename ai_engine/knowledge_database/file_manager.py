"""
File Manager Module

This module provides specialized functionality for managing files within
the knowledge base. It handles CRUD operations for files and their
associated metadata.
"""

from sqlalchemy.orm import joinedload

from ai_engine.models.knowledge import KnowledgeFile
from .base_manager import BaseDBManager
from ai_engine.configs.agent import AgentConfig

class FileManager(BaseDBManager):
    """
    Knowledge File operations manager.
    
    Handles all file-level operations including:
    - Adding new files to the knowledge base
    - Updating file status
    - Deleting files
    - Retrieving file information
    """
    def __init__(self, agent_config: AgentConfig):
        super().__init__(agent_config)

    def add_file(self, db_id, uid, filename, path, kind, state="waiting"):
        """
        Add a new file to the knowledge base.
        
        Args:
            db_id (str): ID of the database to add the file to
            uid (str): Unique identifier for the file
            filename (str): Original name of the file
            path (str): Path where the file is stored
            kind (str): Type/extension of the file
            state (str, optional): Initial processing status. Defaults to "waiting"
            
        Returns:
            dict: Added file information including:
                - uid: File identifier
                - filename: Original file name
                - path: File path
                - type: File type
                - status: Processing status
                - created_at: Creation timestamp
                - nodes: Empty list of nodes
        """
        with self.get_session() as session:
            file = KnowledgeFile(
                uid=uid,
                repo_uid=db_id,
                filename=filename,
                path=path,
                kind=kind,
                state=state
            )
            session.add(file)
            session.flush()

            # Return a dictionary instead of an object to avoid lazy loading issues after session closing
            return file.as_dict()

    def update_file_status(self, file_id, status):
        """
        Update the processing status of a file.
        
        Args:
            file_id (str): ID of the file to update
            status (str): New status value
            
        Returns:
            bool: True if file was found and updated, False otherwise
        """
        with self.get_session() as session:
            file = session.query(KnowledgeFile).filter_by(uid=file_id).first()
            if file:
                file.state = status
                return True
            return False

    def delete_file(self, file_id):
        """
        Delete a file and its associated data.
        
        This operation will cascade delete all associated nodes.
        
        Args:
            file_id (str): ID of the file to delete
            
        Returns:
            bool: True if file was found and deleted, False otherwise
        """
        with self.get_session() as session:
            file = session.query(KnowledgeFile).filter_by(uid=file_id).first()
            if file:
                session.delete(file)
                return True
            return False

    def get_files_by_database(self, db_id):
        """
        Get all files associated with a database.
        
        Uses eager loading to fetch associated nodes along with the file
        information to avoid N+1 query problems.
        
        Args:
            db_id (str): ID of the database
            
        Returns:
            list: List of dictionaries containing file information
        """
        with self.get_session() as session:
            files = session.query(KnowledgeFile).options(
                joinedload(KnowledgeFile.content_blocks)
            ).filter_by(repo_uid=db_id).all()
            return [file.as_dict() for file in files]

    def get_file_by_id(self, file_id):
        """
        Get information about a specific file.
        
        Uses eager loading to fetch associated nodes along with the file
        information.
        
        Args:
            file_id (str): ID of the file
            
        Returns:
            dict: File information if found, None otherwise
        """
        with self.get_session() as session:
            file = session.query(KnowledgeFile).options(
                joinedload(KnowledgeFile.content_blocks)
            ).filter_by(uid=file_id).first()
            return file.as_dict() if file else None