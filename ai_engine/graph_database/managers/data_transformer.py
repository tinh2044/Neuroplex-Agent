"""
DataTransformer - Handles data transformation and formatting

This module handles all data transformation and formatting for the graph database system.
"""
from typing import List, Any, Dict
from ai_engine.utils.logging import logger

class DataTransformer:
    """
    Provides static methods for transforming and formatting query results.

    Example:
        >>> DataTransformer.format_query_results([...])
    """
    @staticmethod
    def clean_embeddings_from_triples(triples: List[Any]) -> List[Any]:
        """
        Remove embedding data from triples for serialization or display.

        Args:
            triples (List[Any]): List of triples.
        Returns:
            List[Any]: Triples with embeddings removed.
        """
        for item in triples:
            n = item[0]
            m = item[2]
            if hasattr(n, '_properties') and isinstance(getattr(n, '_properties'), dict):
                getattr(n, '_properties')['embedding'] = None
            if hasattr(m, '_properties') and isinstance(getattr(m, '_properties'), dict):
                getattr(m, '_properties')['embedding'] = None
        logger.debug("Embeddings cleaned from triples.")
        return triples

    @staticmethod
    def format_query_results(results: List[Any]) -> Dict[str, Any]:
        """
        Format raw query results into a node/edge graph structure.

        Args:
            results (List[Any]): Raw query results.
        Returns:
            Dict[str, Any]: Formatted graph structure.
        """
        formatted_results = {"nodes": [], "edges": []}
        node_ids = set()
        edge_ids = set()
        for item in results:
            if len(item) < 3:
                continue
            n, r, m = item[0], item[1], item[2]
            n_id = getattr(n, 'element_id', None)
            m_id = getattr(m, 'element_id', None)
            n_name = getattr(n, '_properties', {}).get('name', 'unknown')
            m_name = getattr(m, '_properties', {}).get('name', 'unknown')
            r_id = getattr(r, 'element_id', None)
            r_type = getattr(r, 'type', 'unknown')
            if n_id and n_id not in node_ids:
                formatted_results["nodes"].append({"id": n_id, "name": n_name})
                node_ids.add(n_id)
            if m_id and m_id not in node_ids:
                formatted_results["nodes"].append({"id": m_id, "name": m_name})
                node_ids.add(m_id)
            if r_id and r_id not in edge_ids:
                formatted_results["edges"].append({
                    "id": r_id,
                    "type": r_type,
                    "source_id": n_id,
                    "target_id": m_id,
                    "source_name": n_name,
                    "target_name": m_name
                })
                edge_ids.add(r_id)
        logger.debug("Query results formatted to graph structure.")
        return formatted_results 