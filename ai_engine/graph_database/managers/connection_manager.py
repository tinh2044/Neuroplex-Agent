"""
Neo4jConnectionManager - Handles Neo4j connection management

This module handles all connection-related operations for the graph database system.
"""
from typing import Optional
from neo4j import GraphDatabase, Driver, Session
from ai_engine.utils.logging import logger
from ai_engine.configs.agent import AgentConfig
from ai_engine.graph_database.exceptions import Neo4jConnectionError
from ai_engine.graph_database.config import GraphDatabaseConfig


class Neo4jConnectionManager:
    """
    Manages Neo4j database connections, session lifecycle, and database switching.

    Example:
        >>> conn_mgr = Neo4jConnectionManager()
        >>> session = conn_mgr.get_session()
    """
    def __init__(self, agent_config: AgentConfig) -> None:
        """
        Initialize the connection manager.

        Args:
            config (Optional[GraphDatabaseConfig]): Configuration object. If None, uses default config.
        """
        self.config = GraphDatabaseConfig(agent_config)
        self._driver: Optional[Driver] = None
        self._status: str = "closed"
        self.db_name: str = self.config.NEO4J_DB_NAME
        self._connect_lazy: bool = True

    def connect(self) -> None:
        """
        Establish a connection to the Neo4j database.

        Raises:
            Neo4jConnectionError: If connection fails.
        """
        if self._driver is not None:
            logger.info("Neo4j driver already connected.")
            return
        try:
            logger.info("Connecting to Neo4j at %s/%s", self.config.NEO4J_URI, self.db_name)
            self._driver = GraphDatabase.driver(
                f"{self.config.NEO4J_URI}/{self.db_name}",
                auth=(self.config.NEO4J_USERNAME, self.config.NEO4J_PASSWORD)
            )
            self._status = "open"
            logger.info("Connected to Neo4j at %s/%s", self.config.NEO4J_URI, self.db_name)
        except Exception as e:
            logger.error("Failed to connect to Neo4j: %s", e)
            self._status = "closed"
            raise Neo4jConnectionError(f"Failed to connect to Neo4j: {e}") from e

    def disconnect(self) -> None:
        """
        Close the Neo4j database connection.
        """
        if self._driver:
            self._driver.close()
            self._driver = None
            self._status = "closed"
            logger.info("Neo4j connection closed.")

    def is_connected(self) -> bool:
        """
        Check if the connection to Neo4j is open.

        Returns:
            bool: True if connected, False otherwise.
        """
        return self._status == "open" and self._driver is not None

    def get_session(self) -> Session:
        """
        Get a new session for the current database.

        Returns:
            Session: Neo4j session object.
        Raises:
            Neo4jConnectionError: If not connected.
        """
        if not self.is_connected():
            self.connect()
        if not self._driver:
            raise Neo4jConnectionError("Neo4j driver is not connected.")
        return self._driver.session()

    def create_database(self, db_name: str) -> str:
        """
        Create a new database if it does not exist.

        Args:
            db_name (str): Name of the database to create.
        Returns:
            str: Name of the created or existing database.
        Raises:
            Neo4jConnectionError: If operation fails.
        """
        session = self.get_session()
        try:
            existing_databases = session.run("SHOW DATABASES")
            existing_db_names = [db['name'] for db in existing_databases]
            if db_name in existing_db_names:
                logger.info("Database '%s' already exists.", db_name)
                return db_name
            session.run(f"CREATE DATABASE {db_name}")
            logger.info("Database '%s' created successfully.", db_name)
            return db_name
        except Exception as e:
            logger.error("Failed to create database '%s': %s", db_name, e)
            raise Neo4jConnectionError(f"Failed to create database '{db_name}': {e}") from e 
        finally:
            session.close()

    def use_database(self, db_name: str) -> None:
        """
        Switch to the specified database.

        Args:
            db_name (str): Name of the database to use.
        Raises:
            Neo4jConnectionError: If switching fails.
        """
        if db_name != self.db_name:
            logger.info("Switching database from '%s' to '%s'", self.db_name, db_name)
            self.db_name = db_name
            self.disconnect()
            self.connect()
        elif not self.is_connected():
            self.connect() 