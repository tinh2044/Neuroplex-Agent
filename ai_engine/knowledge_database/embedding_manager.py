"""
Embedding Manager Module

This module manages text embedding models and reranking functionality.
It provides a unified interface for encoding text into vectors and
computing similarity scores for search results reranking.
"""

from ai_engine.models.embedding import initialize_embedding
from ai_engine.models.rerank_model import initialize_reranker
from ai_engine import agent_config
from ai_engine.utils import logger


class EmbeddingManager:
    """
    Embedding models and reranker manager.
    
    Handles initialization and management of:
    - Text embedding models for vector encoding
    - Reranking models for search result refinement
    - Model compatibility checking
    """
    
    def __init__(self):
        """
        Initialize the embedding manager.
        
        Sets up embedding and reranking models based on configuration.
        """
        self.embed_model = None
        self.reranker = None
        self._initialize_models()
    
    def _initialize_models(self):
        """
        Initialize embedding and reranking models.
        
        Loads and initializes:
        - Text embedding model for vector encoding
        - Reranking model if enabled in configuration
        
        Handles initialization failures gracefully with logging.
        """
        if not agent_config.enable_kb:
            return
        
        try:
            self.embed_model = initialize_embedding(agent_config)
            logger.info(f"Embedding model initialized: {self.embed_model.embed_model_fullname}")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            
        if agent_config.enable_rerank:
            try:
                self.reranker = initialize_reranker(agent_config)
                logger.info("Reranker model initialized")
            except Exception as e:
                logger.error(f"Failed to initialize reranker: {e}")
    
    def encode_texts(self, texts):
        """
        Encode multiple texts into vectors.
        
        Args:
            texts (list): List of texts to encode
            
        Returns:
            list: List of encoded vectors
            
        Raises:
            ValueError: If embedding model is not initialized
        """
        if not self.embed_model:
            raise ValueError("Embedding model not initialized")
        return self.embed_model.batch_encode(texts)
    
    def encode_single_text(self, text):
        """
        Encode a single text into a vector.
        
        Args:
            text (str): Text to encode
            
        Returns:
            list: Encoded vector
        """
        return self.encode_texts([text])[0]
    
    def get_dimension(self):
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            int: Vector dimension if model is initialized,
                 None otherwise
        """
        if not self.embed_model:
            return None
        return self.embed_model.get_dimension()
    
    def get_model_name(self):
        """
        Get the name of the current embedding model.
        
        Returns:
            str: Model name if initialized,
                 None otherwise
        """
        if not self.embed_model:
            return None
        return self.embed_model.embed_model_fullname
    
    def compute_rerank_scores(self, query, texts):
        """
        Compute reranking scores for search results.
        
        Args:
            query (str): Search query
            texts (list): List of texts to rerank
            
        Returns:
            list: Reranking scores if reranker is available,
                  None otherwise
        """
        if not self.reranker:
            return None
        return self.reranker.compute_score([query, texts], normalize=False)
    
    def check_model_compatibility(self, required_model):
        """
        Check if current model is compatible with requirements.
        
        Args:
            required_model (str): Name of the required model
            
        Returns:
            bool: True if models are compatible,
                  False otherwise
        """
        current_model = self.get_model_name()
        return current_model == required_model
