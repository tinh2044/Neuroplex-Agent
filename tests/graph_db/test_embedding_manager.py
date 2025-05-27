import pytest
from unittest.mock import MagicMock
from ai_engine.graph_database.managers.embedding_manager import EmbeddingManager
from ai_engine.graph_database.managers.connection_manager import Neo4jConnectionManager

@pytest.fixture
def mock_connection_manager():
    mgr = Neo4jConnectionManager()
    mgr.get_session = MagicMock()
    return mgr

@pytest.fixture
def embedding_manager(mock_connection_manager):
    return EmbeddingManager(mock_connection_manager)

def test_set_embed_model(embedding_manager):
    """Test setting the embedding model in the embedding manager."""
    model = MagicMock()
    embedding_manager.set_embed_model(model)
    assert embedding_manager.embed_model is model

def test_get_embedding(embedding_manager):
    """Test getting an embedding for a single input."""
    model = MagicMock()
    model.encode.return_value = [[0.1, 0.2]]
    embedding_manager.set_embed_model(model)
    result = embedding_manager.get_embedding("A")
    assert result == [0.1, 0.2]

def test_get_batch_embeddings(embedding_manager):
    """Test getting embeddings for a batch of inputs."""
    model = MagicMock()
    model.batch_encode.return_value = [[0.1, 0.2], [0.3, 0.4]]
    embedding_manager.set_embed_model(model)
    result = embedding_manager.get_batch_embeddings(["A", "B"])
    assert result == [[0.1, 0.2], [0.3, 0.4]]

def test_create_vector_index(embedding_manager, mock_connection_manager):
    """Test creating a vector index in the database."""
    session = MagicMock()
    session.execute_write = MagicMock()
    mock_connection_manager.get_session.return_value = session
    embedding_manager.create_vector_index(128)
    session.execute_write.assert_called()

def test_add_embeddings_to_entities(embedding_manager, mock_connection_manager):
    """Test adding embeddings to entities in the database."""
    session = MagicMock()
    session.execute_write = MagicMock()
    mock_connection_manager.get_session.return_value = session
    pairs = [("A", [0.1, 0.2])]
    count = embedding_manager.add_embeddings_to_entities(pairs)
    assert count == 1
    session.execute_write.assert_called() 