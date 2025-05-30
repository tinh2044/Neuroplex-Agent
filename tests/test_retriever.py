import pytest
from unittest.mock import Mock, patch
from ai_engine.core.retriever import Retriever

@pytest.fixture
def mock_model():
    model = Mock()
    model.generate_response = Mock(return_value=Mock(content="test response"))
    return model

@pytest.fixture
def mock_config():
    config = Mock()
    config.enable_reranker = True
    config.enable_websearch = True
    config.enable_kb = True
    config.provider = "test_provider"
    config.model = "test_model"
    config.query_mode = "off"
    # Mock the reranker configuration
    config.ranker = Mock()
    config.ranker.keys.return_value = ["test/reranker"]
    config.reranker = "test/reranker"
    config.ranker.split.return_value = ["test", "reranker"]
    return config

@pytest.fixture
def mock_graph_db():
    db = Mock()
    db.get_sample_nodes.return_value = []
    db.format_query_results.return_value = {"nodes": [], "edges": []}
    return db

@pytest.fixture
def mock_knowledge_base():
    kb = Mock()
    kb.query.return_value = {
        "results": [],
        "all_results": []
    }
    return kb

@pytest.fixture
def retriever(mock_config, mock_graph_db, mock_knowledge_base, mock_model):
    patches = [
        patch('ai_engine.core.retriever.initialize_reranker', return_value=Mock()),
        patch('ai_engine.core.retriever.WebSearcher', return_value=Mock()),
        patch('ai_engine.core.retriever.select_model', return_value=mock_model),
        patch('ai_engine.models.select_model', return_value=mock_model)
    ]
    
    for p in patches:
        p.start()
    
    yield Retriever(mock_config, mock_graph_db, mock_knowledge_base)
    
    for p in patches:
        p.stop()

def test_retriever_initialization(retriever):
    assert retriever.agent_config is not None
    assert retriever.graph_database is not None
    assert retriever.knowledge_base is not None

def test_query_graph(retriever):
    query = "test query"
    history = []
    refs = {
        "meta": {"use_graph": True},
        "entities": ["entity1", "entity2"]
    }
    
    result = retriever.query_graph(query, history, refs)
    assert "results" in result
    assert isinstance(result["results"], dict)

def test_query_knowledgebase(retriever):
    query = "test query"
    history = []
    refs = {
        "meta": {"db_id": "test_db"},
        "rewritten_query": query
    }
    
    result = retriever.query_knowledgebase(query, history, refs)
    assert "results" in result
    assert "all_results" in result
    assert "rw_query" in result

@patch('ai_engine.core.retriever.WebSearcher')
def test_query_web(mock_websearcher, retriever):
    query = "test query"
    history = []
    refs = {"meta": {"use_web": True}}
    
    mock_websearcher.return_value.search.return_value = []
    result = retriever.query_web(query, history, refs)
    assert "results" in result

@patch('ai_engine.core.retriever.KNOWBASE_QA_TEMPLATE', "{query}\n\nContext:\n{external}")
def test_construct_query(retriever):
    query = "original query"
    refs = {
        "knowledge_base": {
            "results": [{"id": "1", "entity": {"text": "test knowledge"}}]
        },
        "graph_base": {
            "results": {
                "nodes": ["node1"],
                "edges": [{"source_name": "A", "target_name": "B", "type": "relates"}]
            }
        },
        "web_search": {
            "results": [{"title": "Test", "content": "test content"}]
        }
    }
    meta = {}
    
    result = retriever.construct_query(query, refs, meta)
    assert isinstance(result, str)
    assert query in result

def test_retrieval_flow(retriever):
    query = "test query"
    history = []
    meta = {"use_graph": True, "db_id": "test_db", "use_web": True}
    
    refs = retriever.retrieval(query, history, meta)
    assert "query" in refs
    assert "history" in refs
    assert "meta" in refs
    assert "entities" in refs
    assert "knowledge_base" in refs
    assert "graph_base" in refs
    assert "web_search" in refs 