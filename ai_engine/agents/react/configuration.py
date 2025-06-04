from dataclasses import dataclass, field
from datetime import datetime, timezone

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from ai_engine.agents.registry import Configuration

def get_default_requirements():
    return ["TAVILY_API_KEY"]

@tool
def multiply(first_int: int, second_int: int) -> int:
    """Multiply two integers together."""
    return first_int * second_int

@dataclass(kw_only=True)
class ReActConfiguration(Configuration):
    """ReAct agent configuration"""

    system_prompt: str = field(
        default=f"You are a helpful assistant. Now is {datetime.now(tz=timezone.utc).isoformat()}",
        metadata={
            "description": "The system prompt to use for the agent's interactions. "
            "This prompt sets the context and behavior for the agent."
        },
    )

    model: str = field(
        default="ollama/llama3.1:8b",
        metadata={
            "description": "The name of the language model to use for the agent's main interactions. "
            "Should be in the form: provider/model-name."
        },
    )

