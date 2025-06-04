"""
Pytest configuration and fixtures for backend API testing
"""
import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch

# Add parent directory to Python path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from db_manager import DBManager
from models.token_model import Base

def get_db_override():
    """Override for database dependency"""
    pass


@pytest.fixture(scope="session")
def test_db():
    """Create a test database for the entire test session"""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    # Create test engine
    engine = create_engine(f"sqlite:///{db_path}")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    yield TestingSessionLocal, engine
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def db_session(test_db):
    """Create a database session for each test"""
    TestingSessionLocal, _ = test_db
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """Create a test client with dependency overrides"""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Mock AI engine components to avoid dependencies
    with patch('routers.base.agent_config') as mock_config, \
         patch('routers.base.retriever') as mock_retriever, \
         patch('routers.base.knowledge_base') as mock_kb, \
         patch('routers.base.graph_db') as mock_graph, \
         patch('routers.admin.get_db', override_get_db):
        
        # Configure mocks
        mock_config.get_safe_config.return_value = {"test": "config"}
        mock_config.save.return_value = None
        mock_config.__getitem__ = Mock()
        mock_config.__setitem__ = Mock()
        
        mock_retriever.restart.return_value = None
        mock_kb.restart.return_value = None
        
        client = TestClient(app)
        yield client


@pytest.fixture
def mock_ai_components():
    """Mock AI engine components for testing"""
    with patch('ai_engine.agent_config') as mock_config, \
         patch('ai_engine.retriever') as mock_retriever, \
         patch('ai_engine.knowledge_base') as mock_kb, \
         patch('ai_engine.graph_db') as mock_graph, \
         patch('ai_engine.executor') as mock_executor, \
         patch('ai_engine.models.select_model') as mock_model:
        
        # Configure mocks with realistic responses
        mock_config.get_safe_config.return_value = {"model": "test-model"}
        mock_retriever.return_value = ("modified_query", [])
        mock_kb.get_databases.return_value = {"databases": [], "message": "success"}
        
        # Mock model responses
        mock_model_instance = Mock()
        mock_model_instance.model_name = "test-model"
        mock_model_instance.generate_response.return_value = "Test response"
        mock_model.return_value = mock_model_instance
        
        yield {
            'config': mock_config,
            'retriever': mock_retriever,
            'knowledge_base': mock_kb,
            'graph_db': mock_graph,
            'executor': mock_executor,
            'model': mock_model
        }


@pytest.fixture
def sample_token_data():
    """Sample token data for testing"""
    return {
        "agent_id": "test-agent-123",
        "name": "Test Token"
    }


@pytest.fixture
def sample_chat_data():
    """Sample chat data for testing"""
    return {
        "query": "Hello, how are you?",
        "meta": {
            "use_web": False,
            "use_graph": False,
            "history_round": 5
        },
        "history": []
    }


@pytest.fixture
def sample_database_data():
    """Sample database data for testing"""
    return {
        "database_name": "test_db",
        "description": "Test database for unit testing",
        "dimension": 768
    } 