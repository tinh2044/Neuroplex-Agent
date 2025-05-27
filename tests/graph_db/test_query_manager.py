import pytest
from unittest.mock import MagicMock
from ai_engine.graph_database.managers.query_manager import QueryManager
from ai_engine.graph_database.managers.connection_manager import Neo4jConnectionManager

@pytest.fixture
def mock_connection_manager():
    mgr = Neo4jConnectionManager()
    mgr.get_session = MagicMock()
    return mgr

@pytest.fixture
def query_manager(mock_connection_manager):
    return QueryManager(mock_connection_manager)

def test_get_sample_nodes(query_manager, mock_connection_manager):
    """Test retrieving sample nodes from the query manager."""
    session = MagicMock()
    session.execute_read = MagicMock(return_value=[("A", "r", "B")])
    mock_connection_manager.get_session.return_value = session
    result = query_manager.get_sample_nodes(10)
    assert result == [("A", "r", "B")]
    session.execute_read.assert_called()

def test_query_by_similarity(query_manager, mock_connection_manager):
    """Test querying entities by similarity using the query manager."""
    session = MagicMock()
    session.execute_read = MagicMock(return_value=[["A", 0.99]])
    mock_connection_manager.get_session.return_value = session
    result = query_manager.query_by_similarity([0.1, 0.2], 5)
    assert result == [["A", 0.99]]
    session.execute_read.assert_called()

def test_query_specific_entity(query_manager, mock_connection_manager):
    """Test querying a specific entity using the query manager."""
    session = MagicMock()
    session.execute_read = MagicMock(return_value=[("A", "r", "B")])
    mock_connection_manager.get_session.return_value = session
    result = query_manager.query_specific_entity("A", 2, 10)
    assert result == [("A", "r", "B")]
    session.execute_read.assert_called() 