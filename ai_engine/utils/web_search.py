import os
from typing import List, Dict, Optional
from tavily import TavilyClient
from ai_engine.utils.logging import logger


class WebSearcher:
    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY environment variable is not set")
        self.client = TavilyClient(api_key)
        logger.info("WebSearcher initialized with Tavily client")

    def search(
        self,
        query: str,
        max_results: int = 1,
        search_depth: str = "basic",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        include_raw_content: bool = False,
    ) -> List[Dict]:
        """
        Tavily Search for related content

        Args:
            query: search query
            max_results: maximum number of results
            search_depth: 'basic' or 'advanced'
            include_domains: domains to prioritize
            exclude_domains: domains to exclude
            include_raw_content: include full HTML if needed

        Returns:
            List of search result dictionaries
        """
        try:
            search_results = self.client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_domains=include_domains,
                exclude_domains=exclude_domains,
                include_raw_content=include_raw_content,
            )

            results = search_results.get("results", [])
            return [
                {
                    "title": r.get("title", ""),
                    "content": r.get("content", ""),
                    "url": r.get("url", ""),
                    "score": r.get("score", 0),
                }
                for r in results[:max_results]
            ]

        except Exception as e:
            logger.error("Error during web search", exc_info=True)
            return []

    def format_search_results(self, results: List[Dict]) -> str:
        """
        Format search results as human-readable text

        Args:
            results: List of result dictionaries

        Returns:
            A string representation of the search results
        """
        if not results:
            return "No related web search results found."

        lines = ["Here are the related web search results:\n"]
        for i, result in enumerate(results, 1):
            lines.append(f"{i}. {result['title']}")
            lines.append(f"   {result['content']}")
            lines.append(f"   Source: {result['url']}\n")

        return "\n".join(lines)
