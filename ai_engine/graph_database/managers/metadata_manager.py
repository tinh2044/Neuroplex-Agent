"""
MetadataManager - Handles metadata and file I/O operations

This module handles all metadata and graph info operations for the graph database system.
"""
from typing import Optional, Dict, Any
import os
import json
import logging

from ai_engine.graph_database.exceptions import GraphDatabaseError
from ai_engine.graph_database.config import GraphDatabaseConfig

logger = logging.getLogger(__name__)

class MetadataManager:
    """
    Manages metadata and graph info, including file I/O for the graph database.

    Example:
        >>> meta_mgr = MetadataManager()
        >>> meta_mgr.save_graph_info({...})
    """
    def __init__(self, work_dir: Optional[str] = None) -> None:
        """
        Initialize the metadata manager.

        Args:
            work_dir (Optional[str]): Working directory for metadata files.
        """
        self.work_dir = work_dir or os.path.join(GraphDatabaseConfig.SAVE_DIR, "knowledge_graph", GraphDatabaseConfig.NEO4J_DB_NAME)
        os.makedirs(self.work_dir, exist_ok=True)
        self.info_file_path = os.path.join(self.work_dir, "graph_info.json")

    def save_graph_info(self, graph_info: Dict[str, Any]) -> bool:
        """
        Save the graph database information to a JSON file.

        Args:
            graph_info (Dict[str, Any]): Graph info to save.
        Returns:
            bool: True if saved successfully, False otherwise.
        Raises:
            GraphDatabaseError: If saving fails.
        """
        try:
            with open(self.info_file_path, 'w', encoding='utf-8') as f:
                json.dump(graph_info, f, ensure_ascii=False, indent=2)
            logger.info("Graph info saved to %s.", self.info_file_path)
            return True
        except Exception as e:
            logger.error("Failed to save graph info: %s", e)
            raise GraphDatabaseError(f"Failed to save graph info: {e}") from e

    def load_graph_info(self) -> Optional[Dict[str, Any]]:
        """
        Load the graph database information from a JSON file.

        Returns:
            Optional[Dict[str, Any]]: Loaded graph info, or None if not found.
        Raises:
            GraphDatabaseError: If loading fails.
        """
        if not os.path.exists(self.info_file_path):
            logger.warning("Graph info file does not exist: %s", self.info_file_path)
            return None
        try:
            with open(self.info_file_path, 'r', encoding='utf-8') as f:
                graph_info = json.load(f)
            logger.info("Graph info loaded from %s.", self.info_file_path)
            return graph_info
        except Exception as e:
            logger.error("Failed to load graph info: %s", e)
            raise GraphDatabaseError(f"Failed to load graph info: {e}") from e
