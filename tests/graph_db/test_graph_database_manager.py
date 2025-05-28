import pytest
from unittest.mock import MagicMock, patch
from ai_engine.graph_database import GraphDatabaseManager, GraphDatabase
from ai_engine import agent_config
@pytest.fixture
def graph_db():
    with patch('ai_engine.graph_database.managers.Neo4jConnectionManager') as MockConnMgr, \
         patch('ai_engine.graph_database.managers.EntityManager') as MockEntityMgr, \
         patch('ai_engine.graph_database.managers.EmbeddingManager') as MockEmbedMgr, \
         patch('ai_engine.graph_database.managers.QueryManager') as MockQueryMgr, \
         patch('ai_engine.graph_database.managers.MetadataManager') as MockMetaMgr, \
         patch('ai_engine.graph_database.managers.DataTransformer') as MockDataTrans:
        db = GraphDatabaseManager(agent_config)
        db.connection_manager = MockConnMgr()
        db.entity_manager = MockEntityMgr()
        db.embedding_manager = MockEmbedMgr()
        db.query_manager = MockQueryMgr()
        db.metadata_manager = MockMetaMgr()
        db.data_transformer = MockDataTrans()
        return db

def test_entity_api(graph_db):
    """Test the entity-related API methods of GraphDatabaseManager."""
    graph_db.entity_manager.add_entities = MagicMock()
    graph_db.entity_manager.delete_entity = MagicMock()
    graph_db.entity_manager.get_entities_without_embedding = MagicMock(return_value=["A"])
    graph_db.add_entities([{"h": "A", "t": "B", "r": "r"}])
    graph_db.entity_manager.add_entities.assert_called()
    graph_db.delete_entity("A")
    graph_db.entity_manager.delete_entity.assert_called()
    assert graph_db.get_entities_without_embedding() == ["A"]

def test_embedding_api(graph_db):
    """Test the embedding-related API methods of GraphDatabaseManager."""
    graph_db.embedding_manager.set_embed_model = MagicMock()
    graph_db.embedding_manager.get_embedding = MagicMock(return_value=[0.1, 0.2])
    graph_db.embedding_manager.get_batch_embeddings = MagicMock(return_value=[[0.1, 0.2]])
    graph_db.embedding_manager.create_vector_index = MagicMock()
    graph_db.embedding_manager.add_embeddings_to_entities = MagicMock(return_value=1)
    graph_db.set_embed_model("m")
    graph_db.embedding_manager.set_embed_model.assert_called()
    assert graph_db.get_embedding("A") == [0.1, 0.2]
    assert graph_db.get_batch_embeddings(["A"]) == [[0.1, 0.2]]
    graph_db.create_vector_index(128)
    graph_db.embedding_manager.create_vector_index.assert_called()
    assert graph_db.add_embeddings_to_entities([("A", [0.1, 0.2])]) == 1

def test_query_api(graph_db):
    """Test the query-related API methods of GraphDatabaseManager."""
    graph_db.query_manager.get_sample_nodes = MagicMock(return_value=[("A", "r", "B")])
    graph_db.query_manager.query_by_similarity = MagicMock(return_value=[{"name": "A"}])
    graph_db.query_manager.query_specific_entity = MagicMock(return_value=[("A", "r", "B")])
    assert graph_db.get_sample_nodes() == [("A", "r", "B")]
    assert graph_db.query_by_similarity([0.1, 0.2]) == [{"name": "A"}]
    assert graph_db.query_specific_entity("A") == [("A", "r", "B")]

def test_metadata_api(graph_db):
    """Test the metadata-related API methods of GraphDatabaseManager."""
    graph_db.metadata_manager.save_graph_info = MagicMock(return_value=True)
    graph_db.metadata_manager.load_graph_info = MagicMock(return_value={"x": 1})
    assert graph_db.save_graph_info({"x": 1}) is True
    assert graph_db.load_graph_info() == {"x": 1}

def test_data_transformer_api(graph_db):
    """Test the data transformer API methods of GraphDatabaseManager."""
    graph_db.data_transformer.clean_embeddings_from_triples = MagicMock(return_value=[1])
    graph_db.data_transformer.format_query_results = MagicMock(return_value={"nodes": [], "edges": []})
    assert graph_db.clean_embeddings_from_triples([1]) == [1]
    assert graph_db.format_query_results([1]) == {"nodes": [], "edges": []}

def test_connection_api(graph_db):
    """Test the connection-related API methods of GraphDatabaseManager."""
    graph_db.connection_manager.connect = MagicMock()
    graph_db.connection_manager.disconnect = MagicMock()
    graph_db.connection_manager.is_connected = MagicMock(return_value=True)
    graph_db.connection_manager.get_session = MagicMock(return_value="session")
    graph_db.connection_manager.create_database = MagicMock(return_value="neo4j")
    graph_db.connection_manager.use_database = MagicMock()
    graph_db.connect()
    graph_db.connection_manager.connect.assert_called()
    graph_db.disconnect()
    graph_db.connection_manager.disconnect.assert_called()
    assert graph_db.is_connected() is True
    assert graph_db.get_session() == "session"
    assert graph_db.create_database("neo4j") == "neo4j"
    graph_db.use_database("neo4j")
    graph_db.connection_manager.use_database.assert_called()

def test_backward_compatibility():
    """Test that GraphDatabase is an alias for GraphDatabaseManager (backward compatibility)."""
    from ai_engine.graph_database import GraphDatabaseManager, GraphDatabase
    assert GraphDatabase is GraphDatabaseManager 