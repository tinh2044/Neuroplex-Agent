"""
QueryManager - Handles query operations

This module handles all query-related operations for the graph database system.
"""
from typing import List, Dict, Any, Optional

from ai_engine.graph_database.exceptions import QueryError
from ai_engine.graph_database.managers.connection_manager import Neo4jConnectionManager
from ai_engine.utils.logging import logger

class QueryManager:
    """
    Manages query operations for the graph database.

    Example:
        >>> query_mgr = QueryManager(connection_manager)
        >>> query_mgr.get_sample_nodes()
    """
    def __init__(self, connection_manager: Neo4jConnectionManager) -> None:
        """
        Initialize the query manager.

        Args:
            connection_manager (Neo4jConnectionManager): The connection manager instance.
        """
        self.connection_manager = connection_manager

    def get_sample_nodes(self, num: int = 50, db_name: Optional[str] = None) -> List[Any]:
        """
        Get a sample of nodes and relationships from the database.

        Args:
            num (int): Number of samples to retrieve.
            db_name (Optional[str]): Database name to use.
        Returns:
            List[Any]: List of sample nodes and relationships.
        Raises:
            QueryError: If operation fails.
        """
        db_name = db_name or self.connection_manager.db_name
        session = self.connection_manager.get_session()
        def query(tx, num):
            result = tx.run("MATCH (n)-[r]->(m) RETURN n, r, m LIMIT $num", num=int(num))
            return result.values()
        try:
            result = session.execute_read(query, num)
            logger.info("Retrieved %d sample nodes from database '%s'.", len(result), db_name)
            return result
        except Exception as e:
            logger.error("Failed to get sample nodes: %s", e)
            raise QueryError(f"Failed to get sample nodes: {e}") from e
        finally:
            session.close()

    def query_by_similarity(self, embedding: List[float], top_k: int = 10, db_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Query nodes by vector similarity.

        Args:
            embedding (List[float]): Embedding vector to query.
            top_k (int): Number of top similar nodes to return.
            db_name (Optional[str]): Database name to use.
        Returns:
            List[Dict[str, Any]]: List of similar nodes and scores.
        Raises:
            QueryError: If operation fails.
        """
        db_name = db_name or self.connection_manager.db_name
        session = self.connection_manager.get_session()
        def query(tx, embedding, top_k):
            result = tx.run("""
            CALL db.index.vector.queryNodes('entityEmbeddings', $top_k, $embedding)
            YIELD node AS similarEntity, score
            RETURN similarEntity.name AS name, score
            """, embedding=embedding, top_k=top_k)
            return result.values()
        try:
            result = session.execute_read(query, embedding, top_k)
            logger.info("Queried %d similar nodes by embedding in database '%s'.", len(result), db_name)
            return result
        except Exception as e:
            logger.error("Failed to query by similarity: %s", e)
            raise QueryError(f"Failed to query by similarity: {e}") from e
        finally:
            session.close()

    def query_specific_entity(self, entity_name: str, hops: int = 2, limit: int = 100, db_name: Optional[str] = None) -> List[Any]:
        """
        Query the triple information of the specified entity (undirected relationship).

        Args:
            entity_name (str): Name of the entity to query.
            hops (int): Number of hops for the relationship.
            limit (int): Maximum number of results.
            db_name (Optional[str]): Database name to use.
        Returns:
            List[Any]: List of triples.
        Raises:
            QueryError: If operation fails.
        """
        db_name = db_name or self.connection_manager.db_name
        session = self.connection_manager.get_session()
        def query(tx, entity_name, hops, limit):
            query_str = f"""
            MATCH (n {{name: $entity_name}})-[r*1..{hops}]-(m)
            RETURN n AS n, r, m AS m
            LIMIT $limit
            """
            result = tx.run(query_str, entity_name=entity_name, limit=limit)
            return result.values()
        try:
            result = session.execute_read(query, entity_name, hops, limit)
            logger.info("Queried specific entity '%s' in database '%s'.", entity_name, db_name)
            return result
        except Exception as e:
            logger.error("Failed to query specific entity: %s", e)
            raise QueryError(f"Failed to query specific entity: {e}") from e
        finally:
            session.close() 