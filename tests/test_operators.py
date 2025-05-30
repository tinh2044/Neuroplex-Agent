import pytest
from unittest.mock import Mock
from ai_engine.core.operators import BaseOperator, HyDEOperator

def test_base_operator_requires_prompt_template():
    class TestOperator(BaseOperator):
        pass
    
    with pytest.raises(ValueError):
        TestOperator()

def mock_llm_handler(prompt):
    return Mock(content="Generated hypothesis")

def test_hyde_operator_initialization():
    hyde = HyDEOperator()
    assert hyde.prompt_template is not None

def test_hyde_operator_execution_success():
    result = HyDEOperator.execute(
        llm_handler=mock_llm_handler,
        user_question="What is AI?",
        related_context="AI is artificial intelligence"
    )
    assert result.content == "Generated hypothesis"

def test_hyde_operator_empty_question():
    with pytest.raises(ValueError):
        HyDEOperator.execute(
            llm_handler=mock_llm_handler,
            user_question="",
            related_context="Some context"
        )

def test_hyde_operator_invalid_handler():
    with pytest.raises(TypeError):
        HyDEOperator.execute(
            llm_handler="not_a_callable",
            user_question="What is AI?",
            related_context="Some context"
        )

def test_hyde_operator_callable():
    hyde = HyDEOperator()
    result = hyde(
        llm_handler=mock_llm_handler,
        user_question="What is AI?",
        related_context="Some context"
    )
    assert result.content == "Generated hypothesis" 