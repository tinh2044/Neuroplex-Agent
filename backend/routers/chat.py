import os
import json
import asyncio
import traceback
import uuid
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessageChunk

from ai_engine import executor, agent_config, retriever
from ai_engine.core.history import HistoryManager
from ai_engine.agents import agent_manager
from ai_engine.models import select_model
from ai_engine.utils.logging import logger
from ai_engine.agents.tools_factory import get_all_tools

chat = APIRouter(prefix="/chat")

@chat.get("/")
async def chat_get():
    return "Hello World, you are using chat router!"

@chat.post("/")
async def chat_post(
        query: str = Body(...),
        meta: dict = Body(None),
        history: list[dict] | None = Body(None),
        thread_id: str | None = Body(None)):
    """The main endpoint for handling chat requests.
    Args:
        query: the user's input query text
        meta: a dictionary containing request metadata, which can contain the following fields:
            - use_web: whether to use web search
            - use_graph: whether to use knowledge graph
            - db_id: database ID
            - history_round: historical conversation round limit
            - system_prompt: system prompt word (str, without variables)
        history: conversation history list
        thread_id: conversation thread ID
    Returns:
        StreamingResponse: returns a streaming response with the following status:
            - searching: searching the knowledge base
            - generating: generating answers
            - reasoning: reasoning
            - loading: loading answers
            - finished: answers completed
            - error: an error occurred
    Raises:
        HTTPException: thrown when an error occurs in the retriever or model
    """
    model = select_model()
    meta["server_model_name"] = model.model_name
    history_manager = HistoryManager(history, system_prompt=meta.get("system_prompt"))
    logger.debug(f"Received query: {query} with meta: {meta}")

    def make_chunk(content=None, **kwargs):
        return json.dumps({
            "response": content,
            "meta": meta,
            **kwargs
        }, ensure_ascii=False).encode('utf-8') + b"\n"

    def need_retrieve(meta):
        return meta.get("use_web") or meta.get("use_graph") or meta.get("db_id")

    def generate_response():
        modified_query = query
        refs = None

        # Processing knowledge base retrieval
        if meta and need_retrieve(meta):
            chunk = make_chunk(status="searching")
            yield chunk

            try:
                modified_query, refs = retriever(modified_query, history_manager.messages, meta)
            except Exception as e:
                logger.error(f"Retriever error: {e}, {traceback.format_exc()}")
                yield make_chunk(message=f"Retriever error: {e}", status="error")
                return

            yield make_chunk(status="generating")

        messages = history_manager.get_history_with_msg(modified_query, max_rounds=meta.get('history_round'))
        history_manager.add_user(query)  # Note that we use the original query here

        content = ""
        reasoning_content = ""
        try:
            for delta in model.generate_response(messages, stream=True):
                if not delta.content and hasattr(delta, 'reasoning_content'):
                    reasoning_content += delta.reasoning_content or ""
                    chunk = make_chunk(reasoning_content=reasoning_content, status="reasoning")
                    yield chunk
                    continue

                # Baidu
                if hasattr(delta, 'is_full') and delta.is_full:
                    content = delta.content
                else:
                    content += delta.content or ""

                chunk = make_chunk(content=delta.content, status="loading")
                yield chunk

            logger.debug(f"Final response: {content}")
            logger.debug(f"Final reasoning response: {reasoning_content}")
            yield make_chunk(status="finished",
                            history=history_manager.update_ai(content),
                            refs=refs)
        except Exception as e:
            logger.error(f"Model error: {e}, {traceback.format_exc()}")
            yield make_chunk(message=f"Model error: {e}", status="error")
            return

    return StreamingResponse(generate_response(), media_type='application/json')

@chat.post("/call")
async def call(query: str = Body(...), meta: dict = Body(None)):
    meta = meta or {}
    model = select_model(model_provider=meta.get("model_provider"), model_name=meta.get("model_name"))
    async def predict_async(query):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, model.generate_response, query)

    response = await predict_async(query)
    logger.debug({"query": query, "response": response.content})

    return {"response": response.content}

@chat.get("/agent")
async def get_agent():
    agents = [agent.get_info() for agent in agent_manager.agents.values()]
    return {"agents": agents}

@chat.post("/agent/{agent_name}")
def chat_agent(agent_name: str,
               query: str = Body(...),
               history: list = Body(...),
               config: dict = Body({}),
               meta: dict = Body({})):

    meta.update({
        "query": query,
        "agent_name": agent_name,
        "server_model_name": config.get("model", agent_name) ,
        "thread_id": config.get("thread_id"),
    })

    def make_chunk(content=None, **kwargs):

        return json.dumps({
            "request_id": meta.get("request_id"),
            "response": content,
            **kwargs
        }, ensure_ascii=False).encode('utf-8') + b"\n"



    def stream_messages():

        # Represent that the server has received the request
        yield make_chunk(status="init", meta=meta)

        try:
            agent = agent_manager.get_runnable_agent(agent_name)
        except Exception as e:
            logger.error(f"Error getting agent {agent_name}: {e}, {traceback.format_exc()}")
            yield make_chunk(message=f"Error getting agent {agent_name}: {e}", status="error")
            return

        # Get history_round from config
        history_round = config.get("history_round")
        history_manager = HistoryManager(history)
        messages = history_manager.get_history_with_msg(query, max_rounds=history_round)
        history_manager.add_user(query)

        # Construct runtime configuration, if there is no thread_id, generate one
        if "thread_id" not in config or not config["thread_id"]:
            config["thread_id"] = str(uuid.uuid4())

        runnable_config = {"configurable": {**config}}

        content = ""

        try:
            for msg, metadata in agent.stream_messages(messages, config_schema=runnable_config):
                if isinstance(msg, AIMessageChunk) and msg.content != "<tool_call>":
                    content += msg.content
                    yield make_chunk(content=msg.content,
                                    msg=msg.model_dump(),
                                    metadata=metadata,
                                    status="loading")
                else:
                    yield make_chunk(msg=msg.model_dump(),
                                    metadata=metadata,
                                    status="loading")

            yield make_chunk(status="finished",
                            history=history_manager.update_ai(content),
                            meta=meta)
        except Exception as e:
            logger.error(f"Error streaming messages: {e}, {traceback.format_exc()}")
            yield make_chunk(message=f"Error streaming messages: {e}", status="error")

    return StreamingResponse(stream_messages(), media_type='application/json')

@chat.get("/models")
async def get_chat_models(model_provider: str):
    """Get the model list of the specified model provider"""
    model = select_model(model_provider=model_provider)
    return {"models": model.list_available_models()}

@chat.post("/models/update")
async def update_chat_models(model_provider: str, model_names: list[str]):
    """Update the model list of the specified model provider"""
    agent_config.model_names[model_provider]["models"] = model_names
    agent_config.save_models_to_file()
    return {"models": agent_config.model_names[model_provider]["models"]}

@chat.get("/tools")
async def get_tools():
    """Get all tools"""
    return {"tools": list(get_all_tools().keys())}
