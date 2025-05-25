"""
Configuration management for the modular graph database system.
"""
import os
from typing import Optional

class GraphDatabaseConfig:
    """
    Centralized configuration for the graph database system.
    Reads from environment variables with default values.
    """
    NEO4J_URI: str = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME: str = os.environ.get("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD: str = os.environ.get("NEO4J_PASSWORD", "0123456789")
    NEO4J_DB_NAME: str = os.environ.get("NEO4J_DB_NAME", "neo4j")
    ENABLE_KNOWLEDGE_GRAPH: bool = os.environ.get("ENABLE_KNOWLEDGE_GRAPH", "1") == "1"
    ENABLE_KNOWLEDGE_BASE: bool = os.environ.get("ENABLE_KNOWLEDGE_BASE", "1") == "1"
    SAVE_DIR: str = os.environ.get("GRAPH_SAVE_DIR", os.path.join(os.getcwd(), "data"))
    EMBED_MODEL: Optional[str] = os.environ.get("EMBED_MODEL", None)
    # Add more config parameters as needed

    @classmethod
    def validate(cls):
        """
        Validate the configuration parameters.
        """
        if not cls.NEO4J_URI:
            raise ValueError("NEO4J_URI must be set.")
        if not cls.NEO4J_USERNAME:
            raise ValueError("NEO4J_USERNAME must be set.")
        if not cls.NEO4J_PASSWORD:
            raise ValueError("NEO4J_PASSWORD must be set.")

    def __init__(self):
        self.validate()

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