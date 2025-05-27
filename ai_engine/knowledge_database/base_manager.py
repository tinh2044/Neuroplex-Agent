"""
Base Database Manager Module

This module provides the base database management functionality using SQLAlchemy.
It handles database connections, session management, and basic operations that are
common across all specialized database managers.
"""

import os
import pathlib
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ai_engine import agent_config
from ai_engine.models.knowledge import Base
from ai_engine.utils import logger


class BaseDBManager:
    """
    Base database manager with shared logic for all database operations.
    
    This class provides common database functionality including:
    - Database connection management
    - Session handling
    - Table creation
    - Safe object-to-dictionary conversion
    
    All specialized database managers should inherit from this class.
    """

    def __init__(self):
        """
        Initialize the database manager.
        
        Sets up the database connection, creates session factory,
        and ensures required tables exist.
        """
        self.db_path = os.path.join(agent_config.workspace, "data", "knowledge.db")
        self.ensure_db_dir()

        # Create SQLAlchemy engine
        self.engine = create_engine(f"sqlite:///{self.db_path}")

        # Create session factory
        self.Session = sessionmaker(bind=self.engine)

        # Ensure tables exist
        self.create_tables()

    def ensure_db_dir(self):
        """
        Ensure the database directory exists.
        
        Creates the directory structure if it doesn't exist.
        """
        db_dir = os.path.dirname(self.db_path)
        pathlib.Path(db_dir).mkdir(parents=True, exist_ok=True)

    def create_tables(self):
        """
        Create all database tables defined in the models.
        
        Uses SQLAlchemy's metadata to create tables if they don't exist.
        """
        Base.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self):
        """
        Context manager for database sessions.
        
        Provides automatic commit/rollback handling and ensures
        proper session cleanup.
        
        Yields:
            SQLAlchemy session object
            
        Raises:
            Exception: Any database operation error
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            session.close()

    def _to_dict_safely(self, obj):
        """
        Convert an SQLAlchemy object to dictionary safely.
        
        Args:
            obj: SQLAlchemy model instance
            
        Returns:
            dict: Dictionary representation of the object,
                  or None if object is None
        """
        if obj is None:
            return None
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return obj