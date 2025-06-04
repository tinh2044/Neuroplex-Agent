from dataclasses import dataclass, field

from ai_engine.agents.registry import Configuration

@dataclass(kw_only=True)
class ChatbotConfiguration(Configuration):
    """Chatbot configuration

    Configuration description:

    Configuration items with configurable set to True in metadata can be configured by users,
    Configuration items with configurable set to False cannot be configured by users, only preset by developers.
    """

    system_prompt: str = field(
        default="You are a helpful assistant.",
        metadata={
            "name": "System prompt",
            "configurable": True,
            "description": "Used to describe the role and behavior of the agent"
        },
    )

    model: str = field(
        default="ollama/llama3.1:8b",
        metadata={
            "name": "Agent model",
            "configurable": True,
            "options": [
                "ollama/llama3.1:8b",
                "ollama/llama3.1:13b",
                "ollama/llama3.1:70b",
            ],
            "description": "The driving model of the agent"
        },
    )

    tools: list[str] = field(
        default_factory=list,
        metadata={
            "name": "Tools",
            "configurable": False,
            "description": "List of tools"
        },
    )
