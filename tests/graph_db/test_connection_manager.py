import pytest
from unittest.mock import MagicMock, patch
from ai_engine.graph_database.managers.connection_manager import Neo4jConnectionManager
from ai_engine.graph_database.config import GraphDatabaseConfig
from ai_engine import agent_config

@pytest.fixture
def config():
    """Create a config object."""
    return GraphDatabaseConfig(agent_config)

@pytest.fixture
def connection_manager(config):
    """Create a connection manager with the given config."""
    return Neo4jConnectionManager(config)

def test_connect_and_disconnect(connection_manager):
    """Test connecting and disconnecting the Neo4j connection manager."""
    with patch('neo4j.GraphDatabase.driver') as mock_driver:
        connection_manager.connect()
        assert connection_manager.is_connected()
        connection_manager.disconnect()
        assert not connection_manager.is_connected()

def test_get_session(connection_manager):
    """Test getting a session from the connection manager."""
    with patch('neo4j.GraphDatabase.driver') as mock_driver:
        mock_driver.return_value.session = MagicMock(return_value=MagicMock())
        connection_manager.connect()
        session = connection_manager.get_session()
        assert session is not None

def test_create_database(connection_manager):
    """Test creating a database using the connection manager."""
    with patch('neo4j.GraphDatabase.driver') as mock_driver:
        mock_session = MagicMock()
        mock_session.run.return_value = [{"name": "neo4j"}]
        mock_driver.return_value.session.return_value = mock_session
        connection_manager.connect()
        db_name = connection_manager.create_database("neo4j")
        assert db_name == "neo4j"

def test_use_database(connection_manager):
    """Test switching to a specific database using the connection manager."""
    with patch('neo4j.GraphDatabase.driver') as mock_driver:
        connection_manager.connect()
        connection_manager.use_database("neo4j")
        assert connection_manager.is_connected() 