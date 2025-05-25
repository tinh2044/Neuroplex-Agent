"""
GraphDatabaseManager - Facade for modular graph database system

This module provides the main interface for interacting with the modular graph database system.
"""
from typing import Optional, List, Dict, Any
import logging

from .config import GraphDatabaseConfig
from .managers import (
    Neo4jConnectionManager,
    EntityManager,
    EmbeddingManager,
    QueryManager,
    MetadataManager,
    DataTransformer
)

logger = logging.getLogger(__name__)

class GraphDatabaseManager:
    """
    Facade for the modular graph database system. Composes all managers and exposes the main API.

    Example:
        >>> db = GraphDatabaseManager()
        >>> db.add_entities([...])
    """
    def __init__(self, config: Optional[GraphDatabaseConfig] = None) -> None:
        """
        Initialize the graph database manager and all sub-managers.

        Args:
            config (Optional[GraphDatabaseConfig]): Configuration object.
        """
        self.config = config or GraphDatabaseConfig()
        self.connection_manager = Neo4jConnectionManager(self.config)
        self.entity_manager = EntityManager(self.connection_manager)
        self.embedding_manager = EmbeddingManager(self.connection_manager)
        self.query_manager = QueryManager(self.connection_manager)
        self.metadata_manager = MetadataManager()
        self.data_transformer = DataTransformer()

    # --- Entity Operations ---
    def add_entities(self, triples: List[Dict[str, Any]], db_name: Optional[str] = None) -> None:
        """Add entity triples to the database."""
        return self.entity_manager.add_entities(triples, db_name)

    def delete_entity(self, entity_name: Optional[str] = None, db_name: Optional[str] = None) -> None:
        """Delete specified entity or all entities if entity_name is None."""
        return self.entity_manager.delete_entity(entity_name, db_name)

    def get_entities_without_embedding(self, db_name: Optional[str] = None) -> List[str]:
        """Get a list of entity names without embeddings."""
        return self.entity_manager.get_entities_without_embedding(db_name)

    # --- Embedding Operations ---
    def set_embed_model(self, embed_model: Any) -> None:
        """Set the embedding model to use."""
        return self.embedding_manager.set_embed_model(embed_model)

    def get_embedding(self, text: str) -> List[float]:
        """Get the embedding vector for a single text/entity."""
        return self.embedding_manager.get_embedding(text)

    def get_batch_embeddings(self, texts: List[str], batch_size: int = 40) -> List[List[float]]:
        """Get embedding vectors for a batch of texts/entities."""
        return self.embedding_manager.get_batch_embeddings(texts, batch_size)

    def create_vector_index(self, dimension: int, db_name: Optional[str] = None) -> None:
        """Create a vector index for entity embeddings in the database."""
        return self.embedding_manager.create_vector_index(dimension, db_name)

    def add_embeddings_to_entities(self, entity_embedding_pairs: List[tuple], db_name: Optional[str] = None) -> int:
        """Add embedding vectors to entities in the database."""
        return self.embedding_manager.add_embeddings_to_entities(entity_embedding_pairs, db_name)

    # --- Query Operations ---
    def get_sample_nodes(self, num: int = 50, db_name: Optional[str] = None) -> List[Any]:
        """Get a sample of nodes and relationships from the database."""
        return self.query_manager.get_sample_nodes(num, db_name)

    def query_by_similarity(self, embedding: List[float], top_k: int = 10, db_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query nodes by vector similarity."""
        return self.query_manager.query_by_similarity(embedding, top_k, db_name)

    def query_specific_entity(self, entity_name: str, hops: int = 2, limit: int = 100, db_name: Optional[str] = None) -> List[Any]:
        """Query the triple information of the specified entity (undirected relationship)."""
        return self.query_manager.query_specific_entity(entity_name, hops, limit, db_name)

    # --- Metadata Operations ---
    def save_graph_info(self, graph_info: Dict[str, Any]) -> bool:
        """Save the graph database information to a JSON file."""
        return self.metadata_manager.save_graph_info(graph_info)

    def load_graph_info(self) -> Optional[Dict[str, Any]]:
        """Load the graph database information from a JSON file."""
        return self.metadata_manager.load_graph_info()

    # --- Data Transformation ---
    def clean_embeddings_from_triples(self, triples: List[Any]) -> List[Any]:
        """Remove embedding data from triples for serialization or display."""
        return self.data_transformer.clean_embeddings_from_triples(triples)

    def format_query_results(self, results: List[Any]) -> Dict[str, Any]:
        """Format raw query results into a node/edge graph structure."""
        return self.data_transformer.format_query_results(results)

    # --- Connection Management ---
    def connect(self) -> None:
        """Establish a connection to the Neo4j database."""
        return self.connection_manager.connect()

    def disconnect(self) -> None:
        """Close the Neo4j database connection."""
        return self.connection_manager.disconnect()

    def is_connected(self) -> bool:
        """Check if the connection to Neo4j is open."""
        return self.connection_manager.is_connected()

    def get_session(self):
        """Get a new session for the current database."""
        return self.connection_manager.get_session()

    def create_database(self, db_name: str) -> str:
        """Create a new database if it does not exist."""
        return self.connection_manager.create_database(db_name)

    def use_database(self, db_name: str) -> None:
        """Switch to the specified database."""
        return self.connection_manager.use_database(db_name)

    # --- Backward Compatibility Layer ---
    # Add deprecated methods or aliases here as needed 