"""
EntityManager - Handles entity CRUD operations

This module handles all entity-related database operations for the graph database system.
"""
from typing import List, Dict, Optional, Any

from ai_engine.graph_database.exceptions import QueryError
from ai_engine.graph_database.managers.connection_manager import Neo4jConnectionManager
from ai_engine.utils.logging import logger


class EntityManager:
    """
    Manages CRUD operations for entities in the graph database.

    Example:
        >>> entity_mgr = EntityManager(connection_manager)
        >>> entity_mgr.add_entities([...])
    """
    def __init__(self, connection_manager: Neo4jConnectionManager) -> None:
        """
        Initialize the entity manager.

        Args:
            connection_manager (Neo4jConnectionManager): The connection manager instance.
        """
        self.connection_manager = connection_manager

    def add_entities(self, triples: List[Dict[str, Any]], db_name: Optional[str] = None) -> None:
        """
        Add entity triples to the database.

        Args:
            triples (List[Dict[str, Any]]): List of triples with 'h', 't', 'r'.
            db_name (Optional[str]): Database name to use.
        Raises:
            QueryError: If operation fails.
        """
        db_name = db_name or self.connection_manager.db_name
        session = self.connection_manager.get_session()
        def create(tx, triples):
            for triple in triples:
                h = triple['h']
                t = triple['t']
                r = triple['r']
                query = (
                    "MERGE (a:Entity {name: $h}) "
                    "MERGE (b:Entity {name: $t}) "
                    "MERGE (a)-[:" + r.replace(" ", "_") + "]->(b)"
                )
                tx.run(query, h=h, t=t)
        try:
            session.execute_write(create, triples)
            logger.info("Added %d entities to database '%s'.", len(triples), db_name)
        except Exception as e:
            logger.error("Failed to add entities: %s", e)
            raise QueryError(f"Failed to add entities: {e}") from e
        finally:
            session.close()

    def delete_entity(self, entity_name: Optional[str] = None, db_name: Optional[str] = None) -> None:
        """
        Delete specified entity or all entities if entity_name is None.

        Args:
            entity_name (Optional[str]): Name of the entity to delete.
            db_name (Optional[str]): Database name to use.
        Raises:
            QueryError: If operation fails.
        """
        db_name = db_name or self.connection_manager.db_name
        session = self.connection_manager.get_session()
        def _delete_specific_entity(tx, entity_name):
            query = """
            MATCH (n {name: $entity_name})
            DETACH DELETE n
            """
            tx.run(query, entity_name=entity_name)
        def _delete_all_entities(tx):
            query = """
            MATCH (n)
            DETACH DELETE n
            """
            tx.run(query)
        try:
            if entity_name:
                session.execute_write(_delete_specific_entity, entity_name)
                logger.info("Deleted entity '%s' from database '%s'.", entity_name, db_name)
            else:
                session.execute_write(_delete_all_entities)
                logger.info("Deleted all entities from database '%s'.", db_name)
        except Exception as e:
            logger.error("Failed to delete entity(ies): %s", e)
            raise QueryError(f"Failed to delete entity(ies): {e}") from e
        finally:
            session.close()

    def get_entities_without_embedding(self, db_name: Optional[str] = None) -> List[str]:
        """
        Get a list of entity names without embeddings.

        Args:
            db_name (Optional[str]): Database name to use.
        Returns:
            List[str]: List of entity names without embeddings.
        Raises:
            QueryError: If operation fails.
        """
        db_name = db_name or self.connection_manager.db_name
        session = self.connection_manager.get_session()
        def query(tx):
            result = tx.run("""
            MATCH (n:Entity)
            WHERE n.embedding IS NULL
            RETURN n.name AS name
            """)
            return [record["name"] for record in result]
        try:
            result = session.execute_read(query)
            logger.info("Found %d entities without embeddings in database '%s'.", len(result), db_name)
            return result
        except Exception as e:
            logger.error("Failed to get entities without embedding: %s", e)
            raise QueryError(f"Failed to get entities without embedding: {e}") from e
        finally:
            session.close() 