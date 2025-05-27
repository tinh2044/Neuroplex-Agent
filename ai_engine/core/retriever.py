import traceback

from ai_engine import agent_config, graph_database, knowledge_base
from ai_engine.utils.logging import logger
from ai_engine.models import select_model
from ai_engine.core.operators import HyDEOperator
from ai_engine.models.rerank_model import initialize_reranker
from ai_engine.utils.web_search import WebSearcher
from ai_engine.utils.prompts import KEYWORD_EXTRACTION_PROMPT, NER_PROMPT_TEMPLATE, KNOWBASE_QA_TEMPLATE, QUERY_REWRITE_PROMPT_FLEXIBLE

class Retriever:
    def __init__(self):
        self._load_models()

    def _load_models(self):
        if hasattr(agent_config, "enable_reranker") and agent_config.enable_reranker:
            self.reranker = initialize_reranker(agent_config)

        if hasattr(agent_config, "enable_websearch") and agent_config.enable_websearch:
            self.web_searcher = WebSearcher()

    def retrieval(self, query, history, meta):
        refs = {"query": query, "history": history, "meta": meta}
        refs["model_name"] = agent_config.model
        refs["entities"] = self.reco_entities(query, history, refs)
        refs["knowledge_base"] = self.query_knowledgebase(query, history, refs)
        refs["graph_base"] = self.query_graph(query, history, refs)
        refs["web_search"] = self.query_web(query, history, refs)

        return refs

    def restart(self):
        """Restart all models"""
        self._load_models()

    def construct_query(self, query, refs, meta):
        logger.debug(f"{refs=}")
        if not refs or len(refs) == 0:
            return query

        external_parts = []

        # Parse knowledge base results
        kb_res = refs.get("knowledge_base", {}).get("results", [])
        if kb_res:
            kb_text = "\n".join(f"{r['id']}: {r['entity']['text']}" for r in kb_res)
            external_parts.extend(["Knowledge base information:", kb_text])

        # Parse graph database results
        db_res = refs.get("graph_base", {}).get("results", {})
        if db_res.get("nodes") and len(db_res["nodes"]) > 0:
            db_text = "\n".join(
                [f"{edge['source_name']} and {edge['target_name']} are connected by {edge['type']}" for edge in db_res.get("edges", [])]
            )
            external_parts.extend(["Graph database information:", db_text])

        # Parse web search results
        web_res = refs.get("web_search", {}).get("results", [])
        if web_res:
            web_text = "\n".join(f"{r['title']}: {r['content']}" for r in web_res)
            external_parts.extend(["Web search information:", web_text])

        # Construct query
        if external_parts and len(external_parts) > 0:
            external = "\n\n".join(external_parts)
            query = KNOWBASE_QA_TEMPLATE.format(external=external, query=query)

        return query

    def query_classification(self, query):
        """Judge whether to query
        - For tasks that are completely based on user-provided information, it is called "sufficient";
        - Otherwise, it is called "insufficient" and may need to be retrieved.
        """
        raise NotImplementedError

    def query_graph(self, query, history, refs):
        results = []
        if refs["meta"].get("use_graph") and agent_config.enable_kb:
            for entity in refs["entities"]:
                if entity == "":
                    continue
                result = graph_database.get_sample_nodes(entity)
                if result != []:
                    results.extend(result)
        return {"results": graph_database.format_query_results(results)}


    def query_knowledgebase(self, query, history, refs):
        """Query knowledge base"""

        response = {
            "results": [],
            "all_results": [],
            "rw_query": query,
            "message": "",
        }

        meta = refs["meta"]

        db_id = meta.get("db_id")
        if not db_id or not agent_config.enable_kb:
            response["message"] = "The knowledge base is not enabled, or the knowledge base is not specified, or the knowledge base does not exist"
            return response

        rw_query = self.rewrite_query(query, history, refs)

        logger.debug(f"{meta=}")
        query_result = knowledge_base.query(query=rw_query,
                                            db_id=db_id,
                                            distance_threshold=meta.get("distanceThreshold", 0.5),
                                            rerank_threshold=meta.get("rerankThreshold", 0.1),
                                            max_query_count=meta.get("maxQueryCount", 20),
                                            top_k=meta.get("topK", 10))

        response["results"] = query_result["results"]
        response["all_results"] = query_result["all_results"]
        response["rw_query"] = rw_query

        return response

    def query_web(self, query, history, refs):
        """Query web"""

        if not (refs["meta"].get("use_web") or not agent_config.enable_websearch):
            return {"results": [], "message": "Web search is disabled"}

        try:
            search_results = self.web_searcher.search(query, max_results=5)
        except Exception as e:
            logger.error(f"Web search error: {str(e)}")
            return {"results": [], "message": "Web search error"}

        return {"results": search_results}

    def rewrite_query(self, query, history, refs):
        """Rewrite query"""
        model_provider = agent_config.provider
        model_name = agent_config.model
        model = select_model(model_provider=model_provider, model_name=model_name)
        if refs["meta"].get("mode") == "search":  # If it is a search mode, use the meta configuration, otherwise use the global configuration
            rewrite_query_span = refs["meta"].get("use_rewrite_query", "off")
        else:
            rewrite_query_span = agent_config.query_mode

        if rewrite_query_span == "off":
            rewritten_query = query
        else:

            history_query = [entry["content"] for entry in history if entry["role"] == "user"] if history else ""
            rewritten_query_prompt = QUERY_REWRITE_PROMPT_FLEXIBLE.format(history=history_query, query=query)
            rewritten_query = model.generate_response(rewritten_query_prompt).content

        if rewrite_query_span == "hyde":
            res = HyDEOperator.execute(model_callable=model.generate_response, query=query, context_str=history_query)
            rewritten_query = res.content

        return rewritten_query

    def reco_entities(self, query, history, refs):
        """Recognize entities in the sentence"""
        query = refs.get("rewritten_query", query)
        model_provider = agent_config.provider
        model_name = agent_config.model
        model = select_model(model_provider=model_provider, model_name=model_name)

        entities = []
        if refs["meta"].get("use_graph"):
            

            entity_extraction_prompt = NER_PROMPT_TEMPLATE.format(text=query)
            entities = model.generate_response(entity_extraction_prompt).content.split("<->")

        return entities

    def __call__(self, query, history, meta):
        refs = self.retrieval(query, history, meta)
        query = self.construct_query(query, refs, meta)
        return query, refs
