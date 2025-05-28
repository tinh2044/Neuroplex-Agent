"""
Configuration management for the modular graph database system.
"""
import os
from ai_engine.configs.agent import BaseConfig, AgentConfig

class GraphDatabaseConfig(BaseConfig):
    """
    Centralized configuration for the graph database system.
    Reads from environment variables with default values.
    """
    def __init__(self, agent_config: AgentConfig):
        """Initialize configuration by reading from environment variables."""
        super().__init__()
        # Copy configuration from agent_config
        self.update(agent_config)
        
        # Set database specific configurations
        self.NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        self.NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
        self.NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "0123456789")
        self.NEO4J_DB_NAME = os.environ.get("NEO4J_DB_NAME", "neo4j")
        
        # Set derived configurations
        self.ENABLE_KNOWLEDGE_GRAPH = self.enable_graph
        self.ENABLE_KNOWLEDGE_BASE = self.enable_kb
        self.SAVE_DIR = os.path.join(self.workspace, "graph_database")
        self.EMBED_MODEL = self.embed_model
        
        self.validate()

    def validate(self):
        """
        Validate the configuration parameters.
        """
        if not self.NEO4J_URI:
            raise ValueError("NEO4J_URI must be set.")
        if not self.NEO4J_USERNAME:
            raise ValueError("NEO4J_USERNAME must be set.")
        if not self.NEO4J_PASSWORD:
            raise ValueError("NEO4J_PASSWORD must be set.")

    def get_config(self):
        """
        Get the configuration as a dictionary.
        """
        return {
            "NEO4J_URI": self.NEO4J_URI,
            "NEO4J_USERNAME": self.NEO4J_USERNAME,
            "NEO4J_PASSWORD": self.NEO4J_PASSWORD,
            "NEO4J_DB_NAME": self.NEO4J_DB_NAME,
            "ENABLE_KNOWLEDGE_GRAPH": self.ENABLE_KNOWLEDGE_GRAPH,
            "ENABLE_KNOWLEDGE_BASE": self.ENABLE_KNOWLEDGE_BASE,
            "SAVE_DIR": self.SAVE_DIR,
            "EMBED_MODEL": self.EMBED_MODEL
        } 