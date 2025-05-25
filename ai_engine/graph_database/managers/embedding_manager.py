"""
EmbeddingManager - Handles embedding operations

This module handles all embedding-related operations for the graph database system.
"""
from typing import List, Any, Optional

from ai_engine.graph_database.exceptions import EmbeddingError
from ai_engine.graph_database.managers.connection_manager import Neo4jConnectionManager
from ai_engine.utils.logging import logger

class EmbeddingManager:
    """
    Manages embedding operations for entities in the graph database.

    Example:
        >>> embedding_mgr = EmbeddingManager(connection_manager)
        >>> embedding_mgr.get_embedding("entity_name")
    """
    def __init__(self, connection_manager: Neo4jConnectionManager) -> None:
        """
        Initialize the embedding manager.

        Args:
            connection_manager (Neo4jConnectionManager): The connection manager instance.
        """
        self.connection_manager = connection_manager
        # Placeholder for embedding model, should be injected or set externally
        self.embed_model = None

    def set_embed_model(self, embed_model: Any) -> None:
        """
        Set the embedding model to use.

        Args:
            embed_model (Any): The embedding model instance.
        """
        self.embed_model = embed_model

    def get_embedding(self, text: str) -> List[float]:
        """
        Get the embedding vector for a single text/entity.

        Args:
            text (str): The text or entity name.
        Returns:
            List[float]: Embedding vector.
        Raises:
            EmbeddingError: If embedding fails or model is not set.
        """
        if not self.embed_model:
            logger.error("Embedding model is not set.")
            raise EmbeddingError("Embedding model is not set.")
        try:
            return self.embed_model.encode([text])[0]
        except Exception as e:
            logger.error("Failed to get embedding: %s", e)
            raise EmbeddingError(f"Failed to get embedding: {e}") from e

    def get_batch_embeddings(self, texts: List[str], batch_size: int = 40) -> List[List[float]]:
        """
        Get embedding vectors for a batch of texts/entities.

        Args:
            texts (List[str]): List of texts or entity names.
            batch_size (int): Batch size for encoding.
        Returns:
            List[List[float]]: List of embedding vectors.
        Raises:
            EmbeddingError: If embedding fails or model is not set.
        """
        if not self.embed_model:
            logger.error("Embedding model is not set.")
            raise EmbeddingError("Embedding model is not set.")
        try:
            return self.embed_model.batch_encode(texts, batch_size=batch_size)
        except Exception as e:
            logger.error("Failed to get batch embeddings: %s", e)
            raise EmbeddingError(f"Failed to get batch embeddings: {e}") from e

    def create_vector_index(self, dimension: int, db_name: Optional[str] = None) -> None:
        """
        Create a vector index for entity embeddings in the database.

        Args:
            dimension (int): Dimension of the embedding vectors.
            db_name (Optional[str]): Database name to use.
        Raises:
            EmbeddingError: If operation fails.
        """
        db_name = db_name or self.connection_manager.db_name
        session = self.connection_manager.get_session()
        def _index_exists(tx, index_name):
            result = tx.run("SHOW INDEXES")
            for record in result:
                if record["name"] == index_name:
                    return True
            return False
        def _create_vector_index(tx, dimension):
            index_name = "entityEmbeddings"
            if not _index_exists(tx, index_name):
                tx.run(f"""
                CREATE VECTOR INDEX {index_name}
                FOR (n: Entity) ON (n.embedding)
                OPTIONS {{indexConfig: {{
                `vector.dimensions`: {dimension},
                `vector.similarity_function`: 'cosine'
                }} }};
                """)
        try:
            session.execute_write(_create_vector_index, dimension)
            logger.info("Vector index created for dimension %d in database '%s'.", dimension, db_name)
        except Exception as e:
            logger.error("Failed to create vector index: %s", e)
            raise EmbeddingError(f"Failed to create vector index: {e}") from e
        finally:
            session.close()

    def add_embeddings_to_entities(self, entity_embedding_pairs: List[tuple], db_name: Optional[str] = None) -> int:
        """
        Add embedding vectors to entities in the database.

        Args:
            entity_embedding_pairs (List[tuple]): List of (entity_name, embedding) pairs.
            db_name (Optional[str]): Database name to use.
        Returns:
            int: Number of entities updated.
        Raises:
            EmbeddingError: If operation fails.
        """
        db_name = db_name or self.connection_manager.db_name
        session = self.connection_manager.get_session()
        def _set_embedding(tx, entity_name, embedding):
            tx.run("""
            MATCH (e:Entity {name: $name})
            CALL db.create.setNodeVectorProperty(e, 'embedding', $embedding)
            """, name=entity_name, embedding=embedding)
        count = 0
        try:
            for entity_name, embedding in entity_embedding_pairs:
                session.execute_write(_set_embedding, entity_name, embedding)
                count += 1
            logger.info("Added embeddings to %d entities in database '%s'.", count, db_name)
            return count
        except Exception as e:
            logger.error("Failed to add embeddings to entities: %s", e)
            raise EmbeddingError(f"Failed to add embeddings to entities: {e}") from e
        finally:
            session.close() 