import pytest
import os
import json
from ai_engine.graph_database.managers.metadata_manager import MetadataManager

@pytest.fixture
def metadata_manager(tmp_path):
    """Create a metadata manager with the given work directory."""
    work_dir = tmp_path / "kg" 
    mgr = MetadataManager(work_dir=str(work_dir))
    return mgr

def test_save_and_load_graph_info(metadata_manager):
    """Test saving and loading graph info using the metadata manager."""
    info = {"a": 1, "b": 2}
    assert metadata_manager.save_graph_info(info) is True
    loaded = metadata_manager.load_graph_info()
    assert loaded == info

def test_load_graph_info_file_not_exist(tmp_path):
    """Test loading graph info when the file does not exist."""
    mgr = MetadataManager(work_dir=str(tmp_path / "not_exist"))
    assert mgr.load_graph_info() is None

def test_save_graph_info_error(monkeypatch, metadata_manager):
    """Test that an error is raised when saving graph info fails."""
    monkeypatch.setattr("builtins.open", lambda *a, **k: (_ for _ in ()).throw(IOError("fail")))
    with pytest.raises(Exception):
        metadata_manager.save_graph_info({"x": 1}) 