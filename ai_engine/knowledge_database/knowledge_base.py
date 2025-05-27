"""
Knowledge Base Module

This module provides the main interface for the knowledge base system.
It integrates all components including:
- Database management
- Document processing
- Vector storage (Milvus)
- Embedding and reranking
- Query processing
"""

import os
import shutil
import traceback
from ai_engine import agent_config
from ai_engine.utils import logger, hashstr
from ai_engine.utils.kb2sqlite import json2sqlite

from ai_engine.knowledge_database import kb_db_manager 
from ai_engine.knowledge_database.milvus_manager import MilvusManager
from ai_engine.knowledge_database.document_processor import DocumentProcessor
from ai_engine.knowledge_database.embedding_manager import EmbeddingManager
from ai_engine.knowledge_database.query_engine import QueryEngine


class KnowledgeBase:
    """
    Main knowledge base system interface.
    
    Provides a unified interface for:
    - Creating and managing knowledge bases
    - Processing and storing documents
    - Vector similarity search
    - Result reranking
    - Data migration
    """

    def __init__(self):
        """
        Initialize the knowledge base system.
        
        Sets up all required components:
        - Database manager
        - Milvus vector store
        - Document processor
        - Embedding manager
        - Query engine
        """
        self.work_dir = os.path.join(agent_config.workspace, "data")
        
        self.db_manager = kb_db_manager
        self.milvus_manager = MilvusManager()
        self.doc_processor = DocumentProcessor()
        self.embedding_manager = EmbeddingManager()
        
        self.query_engine = QueryEngine(
            self.milvus_manager, 
            self.embedding_manager, 
            self.db_manager
        )
        
        self._check_migration()
        self._initialize()

    def _check_migration(self):
        """
        Check and perform data migration if needed.
        
        Migrates data from old JSON format to SQLite if necessary.
        """
        json_path = os.path.join(self.work_dir, "database.json")
        if os.path.exists(json_path):
            logger.info("Detected old JSON format, migrating to SQLite...")
            try:
                result = json2sqlite()
                if result:
                    logger.info("Migration successful")
                else:
                    logger.warning("Migration failed or not needed")
            except Exception as e:
                logger.error(f"Migration error: {e}")

    def _initialize(self):
        """
        Initialize the knowledge base system.
        
        Checks configuration and establishes connection to Milvus.
        
        Raises:
            ConnectionError: If cannot connect to Milvus
        """
        if not agent_config.enable_kb:
            logger.warning("Knowledge base is disabled")
            return

        if not self.milvus_manager.connect():
            raise ConnectionError("Failed to connect to Milvus")

    def restart(self):
        """Restart the knowledge base system."""
        self._initialize()

    def create_database(self, database_name, description, dimension=None):
        """
        Create a new knowledge base database.
        
        Args:
            database_name (str): Name for the new database
            description (str): Description of the database
            dimension (int, optional): Vector dimension. If not provided,
                                    uses embedding model's dimension
            
        Returns:
            dict: Created database information
        """
        dimension = dimension or self.embedding_manager.get_dimension()
        db_id = f"kb_{hashstr(database_name, with_salt=True)}"

        db_dict = self.db_manager.create_database(
            db_id=db_id,
            name=database_name,
            description=description,
            embed_model=self.embedding_manager.get_model_name(),
            dimension=dimension
        )

        self._ensure_db_folders(db_id)
        self.milvus_manager.create_collection(db_id, dimension)

        return db_dict

    def get_databases(self):
        """
        Get all registered knowledge bases.
        
        Returns:
            dict: Dictionary containing list of databases with their
                 Milvus collection information
                 
        Raises:
            AssertionError: If knowledge base is not enabled
        """
        assert agent_config.enable_kb, "Knowledge base is not enabled"

        databases = self.db_manager.get_all_databases()
        databases_with_milvus = []
        
        for db in databases:
            db_copy = db.copy()
            try:
                milvus_info = self.milvus_manager.get_collection_info(db["db_id"])
                db_copy["metadata"] = milvus_info
            except Exception as e:
                logger.warning(f"Failed to get Milvus info for {db['name']}: {e}")
                db_copy.update({
                    "row_count": 0,
                    "status": "Disconnected",
                    "error": str(e)
                })
            
            databases_with_milvus.append(db_copy)

        return {"databases": databases_with_milvus}

    def delete_database(self, db_id):
        """
        Delete a knowledge base database.
        
        Removes:
        - Milvus collection
        - Database records
        - Associated files
        
        Args:
            db_id (str): ID of the database to delete
            
        Returns:
            dict: Success message
        """
        self.milvus_manager.drop_collection(db_id)
        self.db_manager.delete_database(db_id)
        
        db_folder = os.path.join(self.work_dir, db_id)
        if os.path.exists(db_folder):
            shutil.rmtree(db_folder)

        return {"message": "Successfully deleted"}

    def add_files(self, db_id, files, params=None):
        """
        Add files to a knowledge base.
        
        Process and store files in the knowledge base, including:
        - Document processing
        - Text chunking
        - Vector encoding
        - Metadata storage
        
        Args:
            db_id (str): ID of the target database
            files (list): List of file paths to process
            params (dict, optional): Processing parameters
            
        Returns:
            dict: Status message if error occurs
        """
        db = self.db_manager.get_database_by_id(db_id)
        if not db:
            return {"message": "Database not found", "status": "failed"}

        if not self.embedding_manager.check_model_compatibility(db['embed_model']):
            error_msg = f"Model mismatch: current={self.embedding_manager.get_model_name()}, required={db['embed_model']}"
            logger.error(error_msg)
            return {"message": error_msg, "status": "failed"}

        file_chunks = self.doc_processor.process_files(files, params)
        
        for file_id, chunk_info in file_chunks.items():
            try:
                self.db_manager.add_file(
                    db_id=db_id,
                    file_id=file_id,
                    filename=chunk_info["filename"],
                    path=chunk_info["path"],
                    file_type=chunk_info["type"],
                    status="processing"
                )

                self._add_documents_to_milvus(
                    file_id=file_id,
                    collection_name=db_id,
                    docs=[node["text"] for node in chunk_info["nodes"]],
                    chunk_infos=chunk_info["nodes"]
                )

                self.db_manager.update_file_status(file_id, "done")

            except Exception as e:
                logger.error(f"Failed to add file {file_id}: {e}\n{traceback.format_exc()}")
                self.db_manager.update_file_status(file_id, "failed")

    def _add_documents_to_milvus(self, file_id, collection_name, docs, chunk_infos):
        """
        Add document chunks to Milvus vector store.
        
        Args:
            file_id (str): ID of the source file
            collection_name (str): Name of the Milvus collection
            docs (list): List of text chunks
            chunk_infos (list): List of chunk metadata
            
        Returns:
            dict: Milvus insertion result
        """
        import random
        
        vectors = self.embedding_manager.encode_texts(docs)
        
        data = []
        for i, (doc, vector, chunk_info) in enumerate(zip(docs, vectors, chunk_infos)):
            data.append({
                "id": int(random.random() * 1e12),
                "vector": vector,
                "text": doc,
                "hash": hashstr(doc, with_salt=True),
                "file_id": file_id,
                **chunk_info
            })
        
        return self.milvus_manager.insert_vectors(collection_name, data)

    def delete_file(self, db_id, file_id):
        """
        Delete a file from the knowledge base.
        
        Removes:
        - Vector data from Milvus
        - File records from database
        
        Args:
            db_id (str): ID of the database
            file_id (str): ID of the file to delete
        """
        self.milvus_manager.delete_vectors(db_id, f"file_id == '{file_id}'")
        self.db_manager.delete_file(file_id)

    def query(self, query, db_id, **kwargs):
        """
        Search the knowledge base.
        
        Args:
            query (str): Search query
            db_id (str): ID of the database to search
            **kwargs: Additional search parameters
            
        Returns:
            dict: Search results with optional reranking
        """
        return self.query_engine.advanced_query(query, db_id, **kwargs)

    def get_retriever_by_db_id(self, db_id):
        """
        Get a retriever function for a specific database.
        
        Args:
            db_id (str): ID of the database
            
        Returns:
            callable: Retriever function for the database
        """
        return self.query_engine.create_retriever(db_id)

    def get_retrievers(self):
        """
        Get all available retrievers.
        
        Returns:
            dict: Dictionary mapping database IDs to their retrievers
        """
        retrievers = {}
        for db in self.db_manager.get_all_databases():
            if self.embedding_manager.check_model_compatibility(db["embed_model"]):
                retrievers[db["db_id"]] = {
                    "name": db["name"],
                    "description": db["description"],
                    "retriever": self.get_retriever_by_db_id(db["db_id"]),
                    "embed_model": db["embed_model"],
                }
            else:
                logger.warning(f"Model mismatch for {db['name']}")
        return retrievers

    # Utility methods
    def _ensure_db_folders(self, db_id):
        """
        Ensure required database folders exist.
        
        Args:
            db_id (str): ID of the database
            
        Returns:
            tuple: Paths to database and uploads folders
        """
        db_folder = os.path.join(self.work_dir, db_id)
        uploads_folder = os.path.join(db_folder, "uploads")
        os.makedirs(db_folder, exist_ok=True)
        os.makedirs(uploads_folder, exist_ok=True)
        return db_folder, uploads_folder

    def get_db_upload_path(self, db_id=None):
        """
        Get the upload folder path for a database.
        
        Args:
            db_id (str, optional): Database ID. If not provided,
                                 uses default path
            
        Returns:
            str: Path to the uploads folder
        """
        _, uploads_folder = self._ensure_db_folders(db_id)
        return uploads_folder

    def get_database_info(self, db_id):
        """
        Get detailed information about a database.
        
        Args:
            db_id (str): ID of the database
            
        Returns:
            dict: Database information including Milvus stats,
                 or None if database not found
        """
        db_dict = self.db_manager.get_database_by_id(db_id)
        if db_dict is None:
            return None
        
        db_copy = db_dict.copy()
        try:
            milvus_info = self.milvus_manager.get_collection_info(db_id)
            db_copy.update(milvus_info)
        except Exception as e:
            logger.warning(f"Failed to get Milvus info for {db_id}: {e}")
            db_copy.update({
                "row_count": 0,
                "status": "Disconnected",
                "error": str(e)
            })
        return db_copy