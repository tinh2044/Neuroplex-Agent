import pytest
from ai_engine.core.history import HistoryManager

@pytest.fixture
def history_manager():
    return HistoryManager(system_prompt="Test System")

def test_initialization():
    manager = HistoryManager()
    assert len(manager.messages) == 1
    assert manager.messages[0]["role"] == "system"

def test_initialization_with_system_prompt():
    system_prompt = "Custom System Prompt"
    manager = HistoryManager(system_prompt=system_prompt)
    assert manager.messages[0]["content"] == system_prompt

def test_add_user_message(history_manager):
    message = "User message"
    history_manager.add_user(message)
    assert history_manager.messages[-1]["role"] == "user"
    assert history_manager.messages[-1]["content"] == message

def test_add_ai_message(history_manager):
    message = "AI message"
    history_manager.add_ai(message)
    assert history_manager.messages[-1]["role"] == "assistant"
    assert history_manager.messages[-1]["content"] == message

def test_update_ai_message(history_manager):
    original = "Original AI message"
    updated = "Updated AI message"
    
    history_manager.add_ai(original)
    history_manager.update_ai(updated)
    
    assert history_manager.messages[-1]["role"] == "assistant"
    assert history_manager.messages[-1]["content"] == updated

def test_update_ai_message_when_last_not_ai(history_manager):
    user_msg = "User message"
    ai_msg = "AI message"
    
    history_manager.add_user(user_msg)
    history_manager.update_ai(ai_msg)
    
    assert len(history_manager.messages) == 3  # system + user + ai
    assert history_manager.messages[-1]["role"] == "assistant"
    assert history_manager.messages[-1]["content"] == ai_msg

def test_get_history_with_msg(history_manager):
    history_manager.add_user("User 1")
    history_manager.add_ai("AI 1")
    history_manager.add_user("User 2")
    
    new_msg = "New message"
    history = history_manager.get_history_with_msg(new_msg)
    
    assert len(history) == len(history_manager.messages) + 1
    assert history[-1]["content"] == new_msg
    assert history[-1]["role"] == "user"

def test_get_history_with_msg_max_rounds(history_manager):
    history_manager.add_user("User 1")
    history_manager.add_ai("AI 1")
    history_manager.add_user("User 2")
    history_manager.add_ai("AI 2")
    
    max_rounds = 1
    new_msg = "New message"
    history = history_manager.get_history_with_msg(new_msg, max_rounds=max_rounds)
    
    assert len(history) == 3  # Last round (2 messages) + new message
    assert history[-1]["content"] == new_msg

def test_string_representation(history_manager):
    history_manager.add_user("User message")
    history_manager.add_ai("AI message")
    
    string_rep = str(history_manager)
    assert "system:" in string_rep
    assert "user:" in string_rep
    assert "assistant:" in string_rep 