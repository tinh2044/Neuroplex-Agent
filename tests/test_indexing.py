import pytest
import os
from pathlib import Path
from ai_engine.core.indexing import chunk, pdfreader, plainreader, read_text

@pytest.fixture
def sample_text():
    return "This is a test sentence. This is another test sentence. And here's a third one."

@pytest.fixture
def temp_text_file(tmp_path, sample_text):
    file_path = tmp_path / "test.txt"
    with open(file_path, "w") as f:
        f.write(sample_text)
    return file_path

def test_chunk_text():
    text = "This is a test sentence. This is another test sentence."
    params = {"chunk_size": 100, "chunk_overlap": 20}
    nodes = chunk(text, params)
    assert len(nodes) > 0
    assert any(text in node.text for node in nodes)

def test_chunk_file(temp_text_file):
    params = {"chunk_size": 20, "chunk_overlap": 5, "use_parser": True}
    nodes = chunk(str(temp_text_file), params)
    assert len(nodes) > 0

def test_plainreader(temp_text_file):
    text = plainreader(str(temp_text_file))
    assert isinstance(text, str)
    assert len(text) > 0

def test_read_text_txt(temp_text_file):
    text = read_text(str(temp_text_file))
    assert isinstance(text, str)
    assert len(text) > 0

def test_read_text_unsupported():
    with pytest.raises(Exception):
        read_text("test.unsupported")

def test_read_text_nonexistent():
    with pytest.raises(AssertionError):
        read_text("nonexistent.txt")

def test_chunk_invalid_file():
    # For non-existent files, the function treats them as text input
    result = chunk("nonexistent.txt", {"use_parser": True})
    assert len(result) > 0
    assert result[0].text == "nonexistent.txt"  # The file path is treated as text

def test_chunk_with_different_sizes():
    text = "This is a test. " * 10
    params1 = {"chunk_size": 20, "chunk_overlap": 5}
    params2 = {"chunk_size": 50, "chunk_overlap": 10}
    
    nodes1 = chunk(text, params1)
    nodes2 = chunk(text, params2)
    
    assert len(nodes1) >= len(nodes2)  # Smaller chunk size should result in more chunks 