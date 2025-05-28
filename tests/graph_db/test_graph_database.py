import pytest
from unittest.mock import MagicMock, patch
from ai_engine.graph_database import (
    GraphDatabaseManager, GraphDatabase,
    Neo4jConnectionManager, EntityManager, EmbeddingManager, QueryManager, MetadataManager, DataTransformer
)
from ai_engine import agent_config
@pytest.fixture
def mock_connection_manager():
    mgr = Neo4jConnectionManager(agent_config)
    mgr.connect = MagicMock()
    mgr.disconnect = MagicMock()
    mgr.is_connected = MagicMock(return_value=True)
    mgr.get_session = MagicMock()
    mgr.create_database = MagicMock(return_value='neo4j')
    mgr.use_database = MagicMock()
    return mgr

@pytest.fixture
def graph_db(mock_connection_manager):
    # Patch managers to use the mock connection manager
    with patch('ai_engine.graph_database.managers.Neo4jConnectionManager', return_value=mock_connection_manager):
        db = GraphDatabaseManager(agent_config)
        db.connection_manager = mock_connection_manager
        db.entity_manager.connection_manager = mock_connection_manager
        db.embedding_manager.connection_manager = mock_connection_manager
        db.query_manager.connection_manager = mock_connection_manager
        return db

def test_add_and_delete_entities(graph_db):
    """Test adding and deleting entities using the graph database facade."""
    graph_db.entity_manager.add_entities = MagicMock()
    graph_db.entity_manager.delete_entity = MagicMock()
    triples = [{"h": "A", "t": "B", "r": "related"}]
    graph_db.add_entities(triples)
    graph_db.entity_manager.add_entities.assert_called_once_with(triples, None)
    graph_db.delete_entity("A")
    graph_db.entity_manager.delete_entity.assert_called_once_with("A", None)

def test_get_entities_without_embedding(graph_db):
    """Test retrieving entities without embeddings using the graph database facade."""
    graph_db.entity_manager.get_entities_without_embedding = MagicMock(return_value=["A", "B"])
    result = graph_db.get_entities_without_embedding()
    assert result == ["A", "B"]

def test_embedding_manager_methods(graph_db):
    """Test embedding manager methods via the graph database facade."""
    graph_db.embedding_manager.set_embed_model = MagicMock()
    graph_db.embedding_manager.get_embedding = MagicMock(return_value=[0.1, 0.2])
    graph_db.embedding_manager.get_batch_embeddings = MagicMock(return_value=[[0.1, 0.2], [0.3, 0.4]])
    graph_db.embedding_manager.create_vector_index = MagicMock()
    graph_db.embedding_manager.add_embeddings_to_entities = MagicMock(return_value=2)
    graph_db.set_embed_model("mock_model")
    graph_db.embedding_manager.set_embed_model.assert_called_once_with("mock_model")
    assert graph_db.get_embedding("A") == [0.1, 0.2]
    assert graph_db.get_batch_embeddings(["A", "B"]) == [[0.1, 0.2], [0.3, 0.4]]
    graph_db.create_vector_index(128)
    graph_db.embedding_manager.create_vector_index.assert_called_once_with(128, None)
    assert graph_db.add_embeddings_to_entities([("A", [0.1, 0.2])]) == 2

def test_query_manager_methods(graph_db):
    """Test query manager methods via the graph database facade."""
    graph_db.query_manager.get_sample_nodes = MagicMock(return_value=[("A", "r", "B")])
    graph_db.query_manager.query_by_similarity = MagicMock(return_value=[{"name": "A", "score": 0.99}])
    graph_db.query_manager.query_specific_entity = MagicMock(return_value=[("A", "r", "B")])
    assert graph_db.get_sample_nodes() == [("A", "r", "B")]
    assert graph_db.query_by_similarity([0.1, 0.2]) == [{"name": "A", "score": 0.99}]
    assert graph_db.query_specific_entity("A") == [("A", "r", "B")]

def test_metadata_manager_methods(graph_db):
    """Test metadata manager methods via the graph database facade."""
    graph_db.metadata_manager.save_graph_info = MagicMock(return_value=True)
    graph_db.metadata_manager.load_graph_info = MagicMock(return_value={"graph": "info"})
    assert graph_db.save_graph_info({"graph": "info"}) is True
    assert graph_db.load_graph_info() == {"graph": "info"}

def test_data_transformer_methods():
    """Test data transformer static methods for cleaning and formatting triples."""
    triples = [[MagicMock(_properties={"name": "A", "embedding": [1,2,3]}), MagicMock(), MagicMock(_properties={"name": "B", "embedding": [4,5,6]})]]
    cleaned = DataTransformer.clean_embeddings_from_triples(triples)
    assert cleaned[0][0]._properties["embedding"] is None
    assert cleaned[0][2]._properties["embedding"] is None
    # Test format_query_results
    n = MagicMock(element_id="1", _properties={"name": "A"})
    m = MagicMock(element_id="2", _properties={"name": "B"})
    r = MagicMock(element_id="r1", type="related")
    results = [[n, r, m]]
    formatted = DataTransformer.format_query_results(results)
    assert "nodes" in formatted and "edges" in formatted
    assert formatted["nodes"][0]["id"] == "1"
    assert formatted["edges"][0]["id"] == "r1"

def test_facade_backward_compatibility():
    """Test that GraphDatabase is an alias for GraphDatabaseManager (backward compatibility)."""
    # GraphDatabase alias should work
    from ai_engine.graph_database import GraphDatabaseManager, GraphDatabase
    assert GraphDatabase is GraphDatabaseManager 