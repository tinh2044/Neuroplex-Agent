"""Graph Database Package - Modular Neo4j Interface"""

from ai_engine.graph_database.graph_database_manager import GraphDatabaseManager
from ai_engine.graph_database.managers import (
    Neo4jConnectionManager,
    EntityManager, 
    EmbeddingManager,
    QueryManager,
    MetadataManager,
    DataTransformer
)

# Backward compatibility
GraphDatabase = GraphDatabaseManager

__all__ = [
    'GraphDatabaseManager',
    'GraphDatabase',
    'Neo4jConnectionManager',
    'EntityManager',
    'EmbeddingManager', 
    'QueryManager',
    'MetadataManager',
    'DataTransformer'
] 