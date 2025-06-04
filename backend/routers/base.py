"""
Base router for the backend
"""
from fastapi import APIRouter, Body
from collections import deque
from ai_engine.utils.logging import LOG_FILE
from ai_engine import agent_config, retriever, knowledge_base

base = APIRouter()


@base.get("/")
async def route_index():
    """
    Route for the index page
    """
    return {"message": "Hello World!"}

@base.get("/health")
async def health_check():
    """
    Health check endpoint for Docker monitoring
    """
    return {"status": "healthy", "message": "Backend is running"}

@base.get("/config")
def get_config():
    """
    Route for the config page
    """
    return agent_config.get_safe_config()

@base.post("/config")
async def update_config(key = Body(...), value = Body(...)):
    """
    Route for the config page
    """
    if key == "custom_models":
        value = agent_config.compare_custom_models(value)

    agent_config[key] = value
    agent_config.save()
    return agent_config.get_safe_config()

@base.post("/restart")
async def restart():
    """
    Route for the restart page
    """
    knowledge_base.restart()
    retriever.restart()
    return {"message": "Restarted!"}

@base.get("/log")
def get_log():
    """
    Route for the log page
    """

    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        last_lines = deque(f, maxlen=1000)

    log = ''.join(last_lines)
    return {"log": log, "message": "success", "log_file": LOG_FILE}


