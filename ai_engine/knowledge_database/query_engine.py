"""
Query Engine Module

This module provides advanced search functionality for the knowledge base.
It combines vector similarity search with reranking to provide accurate
and relevant search results.
"""

from ai_engine import agent_config
from ai_engine.utils import logger


class QueryEngine:
    """
    Search and retrieval logic handler.
    
    Provides advanced search functionality including:
    - Vector similarity search
    - Result filtering
    - Reranking
    - Retriever function creation
    """
    
    def __init__(self, milvus_manager, embedding_manager, db_manager):
        """
        Initialize the query engine.
        
        Args:
            milvus_manager: Manager for vector operations
            embedding_manager: Manager for text encoding
            db_manager: Manager for database operations
        """
        self.milvus_manager = milvus_manager
        self.embedding_manager = embedding_manager
        self.db_manager = db_manager
        
        # Default thresholds
        self.default_distance_threshold = 0.5
        self.default_rerank_threshold = 0.1
        self.default_max_query_count = 20
    
    def search(self, query, collection_name, limit=3):
        """
        Perform basic vector similarity search.
        
        Args:
            query (str): Search query
            collection_name (str): Collection to search in
            limit (int, optional): Maximum number of results. Defaults to 3
            
        Returns:
            list: Search results sorted by similarity
        """
        query_vector = self.embedding_manager.encode_single_text(query)
        return self.milvus_manager.search_vectors(collection_name, query_vector, limit)
    
    def advanced_query(self, query, db_id, **kwargs):
        """
        Perform advanced search with filtering and reranking.
        
        Args:
            query (str): Search query
            db_id (str): Database to search in
            **kwargs: Additional parameters including:
                - distance_threshold: Minimum similarity score
                - rerank_threshold: Minimum reranking score
                - max_query_count: Maximum number of initial results
                - top_k: Maximum number of final results
            
        Returns:
            dict: Search results including:
                - results: Filtered and reranked results
                - all_results: All initial results before filtering
        """
        distance_threshold = kwargs.get("distance_threshold", self.default_distance_threshold)
        rerank_threshold = kwargs.get("rerank_threshold", self.default_rerank_threshold)
        max_query_count = kwargs.get("max_query_count", self.default_max_query_count)
        top_k = kwargs.get("top_k", None)
        
        # Initial search
        all_results = self.search(query, db_id, limit=max_query_count)
        all_results = [dict(r) for r in all_results]
        
        # Add file information
        for res in all_results:
            file = self.db_manager.get_file_by_id(res["entity"]["file_id"])
            if file:
                res["file"] = file
        
        # Filter by distance threshold
        filtered_results = [r for r in all_results if r["distance"] > distance_threshold]
        
        # Apply reranking if enabled
        if agent_config.enable_rerank and len(filtered_results) > 0 and self.embedding_manager.reranker:
            texts = [r["entity"]["text"] for r in filtered_results]
            rerank_scores = self.embedding_manager.compute_rerank_scores(query, texts)
            
            for i, r in enumerate(filtered_results):
                r["rerank_score"] = rerank_scores[i]
            
            filtered_results.sort(key=lambda x: x["rerank_score"], reverse=True)
            filtered_results = [res for res in filtered_results 
                              if res["rerank_score"] > rerank_threshold]
        
        # Apply top_k limit
        if top_k:
            filtered_results = filtered_results[:top_k]
        
        return {
            "results": filtered_results,
            "all_results": all_results,
        }
    
    def create_retriever(self, db_id, **params):
        """
        Create a retriever function for a database.
        
        Args:
            db_id (str): Database to create retriever for
            **params: Search parameters including:
                - distance_threshold: Minimum similarity score
                - rerank_threshold: Minimum reranking score
                - max_query_count: Maximum number of initial results
                - top_k: Maximum number of final results
            
        Returns:
            callable: Function that takes a query string and returns search results
        """
        retriever_params = {
            "distance_threshold": params.get("distance_threshold", self.default_distance_threshold),
            "rerank_threshold": params.get("rerank_threshold", self.default_rerank_threshold),
            "max_query_count": params.get("max_query_count", self.default_max_query_count),
            "top_k": params.get("top_k", 10),
        }
        
        def retriever(query):
            response = self.advanced_query(query, db_id, **retriever_params)
            return response["results"]
        
        return retriever
