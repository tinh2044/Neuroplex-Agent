"""
This file is responsible for managing the database.
It is responsible for creating the database and for handling the database operations.
"""
import os
import pathlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.token_model import Base

class DBManager:
    """Database manager"""

    def __init__(self):
        self.db_path = os.path.join("saves", "data", "server.db")
        self.ensure_db_dir()

        self.engine = create_engine(f"sqlite:///{self.db_path}")
        self.Session = sessionmaker(bind=self.engine)

        self.create_tables()

    def ensure_db_dir(self):
        """Ensure database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        pathlib.Path(db_dir).mkdir(parents=True, exist_ok=True)

    def create_tables(self):
        """Create database tables"""
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """Get database session"""
        return self.Session()