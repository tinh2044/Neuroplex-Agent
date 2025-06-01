from fastapi import APIRouter, Body

base = APIRouter()

from ai_engine import config, retriever, knowledge_base, graph_base

@base.get("/")
async def route_index():
    return {"message": "Hello World!"}

@base.get("/config")
def get_config():
    return config.get_safe_config()

@base.post("/config")
async def update_config(key = Body(...), value = Body(...)):
    if key == "custom_models":
        value = config.compare_custom_models(value)

    config[key] = value
    config.save()
    return config.get_safe_config()

@base.post("/restart")
async def restart():
    knowledge_base.restart()
    graph_base.start()
    retriever.restart()
    return {"message": "Restarted!"}

@base.get("/log")
def get_log():
    from ai_engine.utils.logging import LOG_FILE
    from collections import deque

    with open(LOG_FILE, 'r') as f:
        last_lines = deque(f, maxlen=1000)

    log = ''.join(last_lines)
    return {"log": log, "message": "success", "log_file": LOG_FILE}


