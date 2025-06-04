"""
Simple test to verify test setup
"""
import os
import sys
import pytest

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Test that basic imports work"""
    try:
        import main
        import db_manager
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_basic_math():
    """Test basic math to verify pytest is working"""
    assert 1 + 1 == 2
    assert 2 * 3 == 6


def test_directory_structure():
    """Test that required files exist"""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Check for main files
    assert os.path.exists(os.path.join(backend_dir, "main.py"))
    assert os.path.exists(os.path.join(backend_dir, "db_manager.py"))
    
    # Check for models directory
    models_dir = os.path.join(backend_dir, "models")
    assert os.path.exists(models_dir) 