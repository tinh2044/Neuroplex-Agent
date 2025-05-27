"""
Manages conversation history with support for different message roles (system, user, assistant).
"""
from ai_engine.utils.prompts import generate_time_prompt

class HistoryManager():
    """Manages conversation history with support for different message roles (system, user, assistant)."""
    def __init__(self, history=None, system_prompt=None):
        self.messages = history or []

        system_prompt = system_prompt or generate_time_prompt()
        self.add_system(system_prompt)

    def add(self, role, content):
        """Add a message to the history."""
        self.messages.append({"role": role, "content": content})
        return self.messages

    def add_user(self, content):
        """Add a user message to the history."""
        return self.add("user", content)

    def add_system(self, content):
        return self.add("system", content)

    def add_ai(self, content):
        """Add an AI message to the history."""
        return self.add("assistant", content)

    def update_ai(self, content):
        """Update the last AI message in the history."""
        if self.messages[-1]["role"] == "assistant":
            self.messages[-1]["content"] = content
            return self.messages
        else:
            self.add_ai(content)
            return self.messages

    def get_history_with_msg(self, msg, role="user", max_rounds=None):
        """Get history with new message, but not append it to history."""
        if max_rounds is None:
            history = self.messages[:]
        else:
            history = self.messages[-(2*max_rounds):]

        history.append({"role": role, "content": msg})
        return history

    def __str__(self):
        history_str = ""
        for message in self.messages:
            msg = message["content"].replace('\n', ' ')
            history_str += f"\n{message['role']}: {msg}"
        return history_str