"""
    Agents for the AI engine.
"""
from ai_engine.agents.chatbot import ChatbotAgent
from ai_engine.agents.react import ReActAgent

class AgentManager:
    """
        Agent manager for managing all agents.
    """
    def __init__(self):
        self.agents = {}

    def add_agent(self, agent_id, agent_class):
        """
            Add an agent to the manager.
        """
        self.agents[agent_id] = agent_class

    def get_runnable_agent(self, agent_id, **kwargs):
        """
            Get a runnable agent.
        """
        agent_class = self.get_agent(agent_id)
        return agent_class()

    def get_agent(self, agent_id):
        """
            Get an agent by id.
        """
        return self.agents[agent_id]


agent_manager = AgentManager()
agent_manager.add_agent("chatbot", ChatbotAgent)
agent_manager.add_agent("react", ReActAgent)

__all__ = ["agent_manager"]


if __name__ == "__main__":
    agent = agent_manager.get_agent("chatbot")
