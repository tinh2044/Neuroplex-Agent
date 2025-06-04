"""
Milvus Manager Module

This module provides an interface to the Milvus vector database.
It handles all vector storage operations including:
- Collection management
- Vector insertion and deletion
- Vector similarity search
- Collection statistics
"""

import os
from pymilvus import MilvusClient, MilvusException
from ai_engine.utils import logger
from ai_engine.configs.agent import AgentConfig
class MilvusManager:
    """
    Milvus vector database manager.
    
    Handles all interactions with Milvus including:
    - Connection management
    - Collection operations
    - Vector operations
    - Search functionality
    """
    
    def __init__(self, agent_config: AgentConfig):
        """
        Initialize the Milvus manager.
        
        Sets up connection parameters using environment variables
        or configuration defaults.
        """
        self.client = None
        self.uri = os.getenv('MILVUS_URI', agent_config.get('milvus_uri', "http://localhost:19530/"))
        
    def connect(self) -> bool:
        """
        Connect to Milvus server.
        
        Attempts to establish connection and verify it by listing collections.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = MilvusClient(uri=self.uri)
            self.client.list_collections()
            logger.info("Successfully connected to Milvus at %s", self.uri)
            return True
        except MilvusException as e:
            logger.error("Failed to connect to Milvus with uri: %s, %s", self.uri, e)
            return False
    
    def create_collection(self, collection_name, dimension):
        """
        Create a new collection in Milvus.
        
        If collection already exists, it will be dropped and recreated.
        
        Args:
            collection_name (str): Name for the new collection
            dimension (int): Vector dimension for the collection
        """
        if self.client.has_collection(collection_name=collection_name):
            logger.warning("Collection %s already exists, dropping it", collection_name)
            self.client.drop_collection(collection_name=collection_name)

        self.client.create_collection(
            collection_name=collection_name,
            dimension=dimension
        )
    
    def insert_vectors(self, collection_name, data):
        """
        Insert vectors into a collection.
        
        Args:
            collection_name (str): Target collection name
            data (list): List of dictionaries containing vectors and metadata
            
        Returns:
            dict: Insertion result from Milvus
            
        Raises:
            ValueError: If collection doesn't exist
        """
        if not self.client.has_collection(collection_name=collection_name):
            raise ValueError(f"Collection {collection_name} not found")
        
        return self.client.insert(collection_name=collection_name, data=data)
    
    def search_vectors(self, collection_name, query_vector, limit=3, output_fields=None):
        """
        Search for similar vectors in a collection.
        
        Args:
            collection_name (str): Collection to search in
            query_vector (list): Query vector
            limit (int, optional): Maximum number of results. Defaults to 3
            output_fields (list, optional): Fields to return. Defaults to ["text", "file_id"]
            
        Returns:
            list: Search results sorted by similarity
        """
        if output_fields is None:
            output_fields = ["text", "file_id"]
            
        res = self.client.search(
            collection_name=collection_name,
            data=[query_vector],
            limit=limit,
            output_fields=output_fields
        )
        return res[0] if res else []
    
    def delete_vectors(self, collection_name, filter_expr):
        """
        Delete vectors from a collection using a filter.
        
        Args:
            collection_name (str): Collection to delete from
            filter_expr (str): Expression to filter vectors to delete
            
        Returns:
            dict: Deletion result from Milvus
        """
        return self.client.delete(collection_name=collection_name, filter=filter_expr)
    
    def drop_collection(self, collection_name):
        """
        Delete an entire collection.
        
        Args:
            collection_name (str): Name of collection to drop
            
        Returns:
            dict: Operation result from Milvus
        """
        return self.client.drop_collection(collection_name=collection_name)
    
    def get_collection_info(self, collection_name):
        """
        Get information about a collection.
        
        Args:
            collection_name (str): Name of the collection
            
        Returns:
            dict: Collection information including:
                - name: Collection name
                - row_count: Number of vectors
                - status: Collection status
                - error_message: Error if any occurred
        """
        try:
            collection = self.client.describe_collection(collection_name)
            collection.update(self.client.get_collection_stats(collection_name))
            return collection
        except MilvusException as e:
            logger.warning(f"Failed to get collection {collection_name} info: {e}")
            return {
                "name": collection_name,
                "row_count": 0,
                "status": "Error",
                "error_message": str(e)
            }
    
    def list_collections(self):
        """
        Get list of all collections.
        
        Returns:
            list: Names of all collections in Milvus
        """
        return self.client.list_collections()
    
    def query_vectors(self, collection_name, filter_expr=None, output_fields=None, limit=None):
        """
        Query vectors using filters.
        
        Args:
            collection_name (str): Collection to query
            filter_expr (str, optional): Filter expression
            output_fields (list, optional): Fields to return
            limit (int, optional): Maximum number of results
            
        Returns:
            list: Query results from Milvus
        """
        return self.client.query(
            collection_name=collection_name,
            filter=filter_expr,
            output_fields=output_fields,
            limit=limit
        )