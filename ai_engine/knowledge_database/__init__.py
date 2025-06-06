"""
This file is responsible for handling the knowledge base related requests.
It includes endpoints for creating, deleting, querying, and uploading databases, documents, and files.
"""
import os
import shutil
import json
import time
import random
import traceback
from ai_engine.utils import logger, hashstr
from ai_engine.configs.agent import AgentConfig
from .milvus_manager import MilvusManager
from .document_processor import DocumentProcessor
from .embedding_manager import EmbeddingManager
from .query_engine import QueryEngine
from .kb_db_manager import KBDBManager

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

    def __init__(self, agent_config: AgentConfig, kb_db_manager: KBDBManager):
        """
        Initialize the knowledge base system.
        
        Sets up all required components:
        - Database manager
        - Milvus vector store
        - Document processor
        - Embedding manager
        - Query engine
        """
        self.agent_config = agent_config
        
        self.work_dir = os.path.join(str(agent_config.workspace), "data")
        
        self.db_manager = kb_db_manager
        self.milvus_manager = MilvusManager(agent_config)
        self.doc_processor = DocumentProcessor()
        self.embedding_manager = EmbeddingManager(agent_config)
        
        self.query_engine = QueryEngine(
            self.milvus_manager, 
            self.embedding_manager, 
            self.db_manager,
            agent_config
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
                result = self.json2sqlite()
                if result:
                    logger.info("Migration successful")
                else:
                    logger.warning("Migration failed or not needed")
            except Exception as e:
                logger.error("Migration error: %s", e)

    def _initialize(self):
        """
        Initialize the knowledge base system.
        
        Checks configuration and establishes connection to Milvus.
        
        Raises:
            ConnectionError: If cannot connect to Milvus
        """
        if not self.agent_config.enable_kb:
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
        print(self.agent_config.enable_kb)
        assert self.agent_config.enable_kb, "Knowledge base is not enabled"

        databases = self.db_manager.get_all_databases()
        databases_with_milvus = []
        
        for db in databases:
            db_copy = db.copy()
            try:
                milvus_info = self.milvus_manager.get_collection_info(db["db_id"])
                db_copy["metadata"] = milvus_info
            except Exception as e:
                logger.warning("Failed to get Milvus info for %s: %s", db['name'], e)
                db_copy.update({
                    "row_count": 0,
                    "status": "Disconnected",
                    "error": str(e)
                })
            
            databases_with_milvus.append(db_copy)

        return {"databases": databases_with_milvus}
    
    def get_file_info(self, db_id, file_id):
        """
        Get file information including nodes.
        
        Args:
            db_id (str): Database ID
            file_id (str): File ID

        Returns:
            dict: File information with nodes
        """
        file_record = self.db_manager.get_file_by_id(file_id)
        if not file_record:
            raise Exception(f"File not found: {file_id}")

        nodes = file_record.get("nodes", [])

        if len(nodes) == 0:
            nodes = self.milvus_manager.query_vectors(
                collection_name=db_id,
                filter_expr=f"file_id == '{file_id}'",
                output_fields=None
            )
            for node in nodes:
                node.pop("vector")

        nodes.sort(key=lambda x: x.get("start_char_idx") or x.get("metadata", {}).get("chunk_idx", 0))
        return {"lines": nodes}

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
                logger.error("Failed to add file %s: %s\n%s", file_id, e, traceback.format_exc())
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
            logger.warning("Failed to get Milvus info for %s: %s", db_id, e)
            db_copy.update({
                "row_count": 0,
                "status": "Disconnected",
                "error": str(e)
            })
        return db_copy
    
    def json2sqlite(self):
        """Migrate knowledge base data from JSON to SQLite"""
        # Original JSON file path
        json_path = os.path.join(self.agent_config.workspace, "data", "database.json")

        if not os.path.exists(json_path):
            logger.info("Original JSON file not found: %s, no need to migrate", json_path)
            return False

        try:
            # Read JSON file
            with open(json_path, "r", encoding='utf-8') as f:
                data = json.load(f)

            if not data or "databases" not in data or not data["databases"]:
                logger.info("JSON file does not contain database information, no need to migrate")
                return False

            # Start migration
            logger.info("Start migrating knowledge base data, total %s databases", len(data['databases']))

            # Iterate over all databases
            for db_info in data["databases"]:
                db_id = db_info["db_id"]
                name = db_info["name"]
                description = db_info["description"]
                embed_model = db_info.get("embed_model")
                dimension = db_info.get("dimension")
                metadata = db_info.get("metadata", {})

                logger.info("Processing database: %s (ID: %s), metadata type: %s", name, db_id, type(metadata))

                # Check if database already exists
                existing_db = self.db_manager.get_database_by_id(db_id)
                if existing_db:
                    logger.info("Database %s (ID: %s) already exists, skipping creation", name, db_id)
                    continue

                # Create database
                db = self.db_manager.create_database(
                    db_id=db_id,
                    name=name,
                    description=description,
                    embed_model=embed_model,
                    dimension=dimension,
                    metadata=metadata  # This will be stored as meta_info in kb_db_manager
                )

                # Process files
                files = db_info.get("files", {})
                if isinstance(files, list):
                    files = {f["file_id"]: f for f in files}

                for file_id, file_info in files.items():
                    # Add file
                    self.db_manager.add_file(
                        db_id=db_id,
                        file_id=file_id,
                        filename=file_info["filename"],
                        path=file_info["path"],
                        file_type=file_info["type"],
                        status=file_info["status"]
                    )

                    # Process nodes
                    nodes = file_info.get("nodes", [])
                    for node in nodes:
                        node_metadata = node.get("metadata", {})
                        if node_metadata is None:
                            node_metadata = {}
                        logger.debug("Node metadata type: %s", type(node_metadata))

                        self.db_manager.add_node(
                            file_id=file_id,
                            text=node["text"],
                            hash_value=node.get("hash"),
                            start_char_idx=node.get("start_char_idx"),
                            end_char_idx=node.get("end_char_idx"),
                            metadata=node_metadata  # This will be stored as meta_info in kb_db_manager
                        )

                logger.info("Database %s (ID: %s) migration completed, total %s files", name, db_id, len(files))

            # Backup original JSON file
            backup_path = json_path + f".bak.{int(time.time())}"
            os.rename(json_path, backup_path)
            logger.info("Migration completed, original JSON file backed up to: %s", backup_path)

            return True

        except Exception as e:
            logger.error("Migration failed: %s", e)
            logger.error(traceback.format_exc())
            return False