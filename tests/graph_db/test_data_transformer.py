import pytest
from unittest.mock import MagicMock
from ai_engine.graph_database.managers.data_transformer import DataTransformer

def test_clean_embeddings_from_triples():
    triples = [[MagicMock(_properties={"name": "A", "embedding": [1,2,3]}), MagicMock(), MagicMock(_properties={"name": "B", "embedding": [4,5,6]})]]
    cleaned = DataTransformer.clean_embeddings_from_triples(triples)
    assert cleaned[0][0]._properties["embedding"] is None
    assert cleaned[0][2]._properties["embedding"] is None

def test_format_query_results():
    n = MagicMock(element_id="1", _properties={"name": "A"})
    m = MagicMock(element_id="2", _properties={"name": "B"})
    r = MagicMock(element_id="r1", type="related")
    results = [[n, r, m]]
    formatted = DataTransformer.format_query_results(results)
    assert "nodes" in formatted and "edges" in formatted
    assert formatted["nodes"][0]["id"] == "1"
    assert formatted["edges"][0]["id"] == "r1" 