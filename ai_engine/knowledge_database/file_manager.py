"""
File Manager Module

This module provides specialized functionality for managing files within
the knowledge base. It handles CRUD operations for files and their
associated metadata.
"""

from sqlalchemy.orm import joinedload

from ai_engine.models.knowledge import KnowledgeFile
from .base_manager import BaseDBManager


class FileManager(BaseDBManager):
    """
    Knowledge File operations manager.
    
    Handles all file-level operations including:
    - Adding new files to the knowledge base
    - Updating file status
    - Deleting files
    - Retrieving file information
    """

    def add_file(self, db_id, file_id, filename, path, file_type, status="waiting"):
        """
        Add a new file to the knowledge base.
        
        Args:
            db_id (str): ID of the database to add the file to
            file_id (str): Unique identifier for the file
            filename (str): Original name of the file
            path (str): Path where the file is stored
            file_type (str): Type/extension of the file
            status (str, optional): Initial processing status. Defaults to "waiting"
            
        Returns:
            dict: Added file information including:
                - file_id: File identifier
                - filename: Original file name
                - path: File path
                - type: File type
                - status: Processing status
                - created_at: Creation timestamp
                - nodes: Empty list of nodes
        """
        with self.get_session() as session:
            file = KnowledgeFile(
                file_id=file_id,
                database_id=db_id,
                filename=filename,
                path=path,
                file_type=file_type,
                status=status
            )
            session.add(file)
            session.flush()

            # Return a dictionary instead of an object to avoid lazy loading issues after session closing
            return {
                "file_id": file_id,
                "filename": filename,
                "path": path,
                "type": file_type,
                "status": status,
                "created_at": file.created_at.timestamp() if file.created_at else None,
                "nodes": []
            }

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
            file = session.query(KnowledgeFile).filter_by(file_id=file_id).first()
            if file:
                file.status = status
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
            file = session.query(KnowledgeFile).filter_by(file_id=file_id).first()
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
                joinedload(KnowledgeFile.nodes)
            ).filter_by(database_id=db_id).all()
            return [self._to_dict_safely(file) for file in files]

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
                joinedload(KnowledgeFile.nodes)
            ).filter_by(file_id=file_id).first()
            return self._to_dict_safely(file) if file else None