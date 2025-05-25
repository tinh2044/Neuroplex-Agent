"""
Custom exceptions for the modular graph database system.
"""

class GraphDatabaseError(Exception):
    """Base exception for all graph database errors."""
    

class Neo4jConnectionError(GraphDatabaseError):
    """Raised when a connection error occurs."""
    

class QueryError(GraphDatabaseError):
    """Raised when a query operation fails."""
    

class EmbeddingError(GraphDatabaseError):
    """Raised when an embedding operation fails."""
    