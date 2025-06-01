"""
Module-level documentation for the AI Engine initialization module.

This module sets up the core configuration and dependencies for the AI Engine,
including environment loading, agent configuration, and potential future
knowledge base and graph database integrations.
"""
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from ai_engine.knowledge_database.kb_db_manager import KBDBManager
from ai_engine.knowledge_database import KnowledgeBase
from ai_engine.graph_database import GraphDatabase
from ai_engine.core.retriever import Retriever
from .configs.agent import AgentConfig

load_dotenv("ai_engine/.env")



executor = ThreadPoolExecutor()
agent_config = AgentConfig()
kb_db_manager = KBDBManager(agent_config)
knowledge_base = KnowledgeBase(agent_config, kb_db_manager)

graph_database = GraphDatabase(agent_config)

retriever = Retriever(agent_config=agent_config, knowledge_base=knowledge_base, graph_database=graph_database)