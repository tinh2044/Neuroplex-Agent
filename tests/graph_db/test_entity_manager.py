import pytest
from unittest.mock import MagicMock
from ai_engine.graph_database.managers.entity_manager import EntityManager
from ai_engine.graph_database.managers.connection_manager import Neo4jConnectionManager

@pytest.fixture
def mock_connection_manager():
    mgr = Neo4jConnectionManager()
    mgr.get_session = MagicMock()
    return mgr

@pytest.fixture
def entity_manager(mock_connection_manager):
    return EntityManager(mock_connection_manager)

def test_add_entities(entity_manager, mock_connection_manager):
    """Test adding entities to the database."""
    session = MagicMock()
    session.execute_write = MagicMock()
    mock_connection_manager.get_session.return_value = session
    triples = [{"h": "A", "t": "B", "r": "related"}]
    entity_manager.add_entities(triples)
    session.execute_write.assert_called()

def test_delete_entity(entity_manager, mock_connection_manager):
    """Test deleting an entity from the database."""
    session = MagicMock()
    session.execute_write = MagicMock()
    mock_connection_manager.get_session.return_value = session
    entity_manager.delete_entity("A")
    session.execute_write.assert_called()
    entity_manager.delete_entity()
    session.execute_write.assert_called()

def test_get_entities_without_embedding(entity_manager, mock_connection_manager):
    """Test retrieving entities that do not have embeddings."""
    session = MagicMock()
    session.execute_read = MagicMock(return_value=["A", "B"])
    mock_connection_manager.get_session.return_value = session
    result = entity_manager.get_entities_without_embedding()
    assert result == ["A", "B"]
    session.execute_read.assert_called() 