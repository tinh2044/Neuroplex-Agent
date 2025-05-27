import os
import pytest
from ai_engine.graph_database.config import GraphDatabaseConfig

def test_default_values(monkeypatch):
    """Test that default config values are set when environment variables are not present."""
    monkeypatch.delenv("NEO4J_URI", raising=False)
    monkeypatch.delenv("NEO4J_USERNAME", raising=False)
    monkeypatch.delenv("NEO4J_PASSWORD", raising=False)
    cfg = GraphDatabaseConfig()
    assert cfg.NEO4J_URI == "bolt://localhost:7687"
    assert cfg.NEO4J_USERNAME == "neo4j"
    assert cfg.NEO4J_PASSWORD == "0123456789"

def test_env_override(monkeypatch):
    """Test that config values are overridden by environment variables."""
    monkeypatch.setenv("NEO4J_URI", "bolt://test:7687")
    monkeypatch.setenv("NEO4J_USERNAME", "testuser")
    monkeypatch.setenv("NEO4J_PASSWORD", "testpass")
    cfg = GraphDatabaseConfig()
    assert cfg.NEO4J_URI == "bolt://test:7687"
    assert cfg.NEO4J_USERNAME == "testuser"
    assert cfg.NEO4J_PASSWORD == "testpass"

def test_validation(monkeypatch):
    """Test that validation raises ValueError when NEO4J_URI is empty."""
    monkeypatch.setenv("NEO4J_URI", "")
    with pytest.raises(ValueError):
        GraphDatabaseConfig().validate() 