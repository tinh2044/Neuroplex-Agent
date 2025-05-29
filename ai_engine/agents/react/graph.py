import uuid

from ai_engine.agents.registry import BaseAgent
from ai_engine.agents.react.configuration import ReActConfiguration

class ReActAgent(BaseAgent):
    name = "react"
    description = "A react agent that can answer questions and help with tasks."

    def get_graph(self, **kwargs):
        """Build graph"""
        from .workflows import graph
        return graph

def main():
    agent = ReActAgent(ReActConfiguration())

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    from ai_engine.agents.utils import agent_cli
    agent_cli(agent, config)


if __name__ == "__main__":
    main()
