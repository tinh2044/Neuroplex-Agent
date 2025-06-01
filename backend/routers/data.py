"""
This file is responsible for handling the data related requests.
It includes endpoints for creating, deleting, querying, and uploading databases, documents, and files.
"""
import os
import asyncio
import traceback
from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Body, Query

from ai_engine.utils import logger, hashstr
from ai_engine import executor, retriever, agent_config, knowledge_base, graph_database

data = APIRouter(prefix="/data")


@data.get("/")
async def get_databases():
    """Get all databases"""
    try:
        database = knowledge_base.get_databases()
    except Exception as e:
        logger.error("Failed to get database list, %s, %s", e, traceback.format_exc())
        return {"message": f"Failed to get database list {e}", "databases": []}
    return database

@data.post("/")
async def create_database(
    database_name: str = Body(...),
    description: str = Body(...),
    dimension: Optional[int] = Body(None)
):
    """Create a new database"""
    logger.debug("Create database %s", database_name)
    try:
        database_info = knowledge_base.create_database(
            database_name,
            description,
            dimension=dimension
        )
    except Exception as e:
        logger.error("Failed to create database %s, %s, %s", database_name, e, traceback.format_exc())
        return {"message": f"Failed to create database {database_name} {e}", "status": "failed"}
    return database_info

@data.delete("/")
async def delete_database(db_id):
    """Delete a database"""
    logger.debug("Delete database %s", db_id)
    knowledge_base.delete_database(db_id)
    return {"message": "Database deleted successfully"}

@data.post("/query-test")
async def query_test(query: str = Body(...), meta: dict = Body(...)):
    """Query test"""
    logger.debug("Query test in %s: %s", meta, query)
    result = retriever.query_knowledgebase(query, history=None, refs={"meta": meta})
    return result

@data.post("/file-to-chunk")
async def file_to_chunk(db_id: str = Body(...), files: list[str] = Body(...), params: dict = Body(...)):
    """File to chunk"""
    logger.debug("File to chunk for db_id %s: %s %s", db_id, files, params)
    try:
        processed_files = await knowledge_base.add_files(db_id, files, params)
        return {"message": "Files processed and pending indexing", "files": processed_files, "status": "success"}
    except Exception as e:
        logger.error("Failed to process files for pending indexing: %s, %s", e, traceback.format_exc())
        return {"message": f"Failed to process files for pending indexing: {e}", "status": "failed"}

@data.post("/add-by-file")
async def create_document_by_file(db_id: str = Body(...), files: List[str] = Body(...)):
    """Create document by file"""
    logger.debug("Add document in %s by file: %s", db_id, files)
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            executor,
            lambda: knowledge_base.add_files(db_id, files)
        )
        return {"message": "Files added successfully", "status": "success"}
    except Exception as e:
        logger.error("Failed to add files %s, %s, %s", files, e, traceback.format_exc())
        return {"message": f"Failed to add files {files} {e}", "status": "failed"}

@data.get("/info")
async def get_database_info(db_id: str):
    """Get database info"""
    database = knowledge_base.get_database_info(db_id)
    if database is None:
        raise HTTPException(status_code=404, detail="Database not found")
    return database

@data.delete("/document")
async def delete_document(db_id: str = Body(...), file_id: str = Body(...)):
    """Delete document"""
    logger.debug("DELETE document %s info in %s", file_id, db_id)
    knowledge_base.delete_file(db_id, file_id)
    return {"message": "Document deleted successfully"}

@data.get("/document")
async def get_document_info(db_id: str, file_id: str):
    """Get document info"""
    logger.debug("GET document %s info in %s", file_id, db_id)

    try:
        info = knowledge_base.get_file_info(db_id, file_id)
    except Exception as e:
        logger.error("Failed to get file info, %s, %s, %s", e, db_id, file_id)
        info = {"message": "Failed to get file info", "status": "failed"}

    return info

@data.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db_id: Optional[str] = Query(None)
):
    """Upload file"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No selected file")

    if db_id:
        upload_dir = knowledge_base.get_db_upload_path(db_id)
    else:
        upload_dir = os.path.join(agent_config.save_dir, "data", "uploads")

    basename, ext = os.path.splitext(file.filename)
    filename = f"{basename}_{hashstr(basename, 4, with_salt=True)}{ext}".lower()
    file_path = os.path.join(upload_dir, filename)
    os.makedirs(upload_dir, exist_ok=True)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return {"message": "File successfully uploaded", "file_path": file_path, "db_id": db_id}

@data.get("/graph")
async def get_graph_info():
    """Get graph info"""
    graph_info = graph_database.metadata_manager.load_graph_info()
    if graph_info is None:
        raise HTTPException(status_code=400, detail="Error in retrieving graph database")
    return graph_info

@data.post("/graph/index-nodes")
async def index_nodes(data: dict = Body(default={})):
    """Index nodes"""
    if not graph_database.is_connected():
        raise HTTPException(status_code=400, detail="Graph database not started")

    kgdb_name = data.get('kgdb_name', 'neo4j')
    count = graph_database.add_embeddings_to_entities([], kgdb_name) if graph_database.is_connected() else 0

    return {"status": "success", "message": f"Successfully indexed {count} nodes", "indexed_count": count}

@data.get("/graph/node")
async def get_graph_node(entity_name: str):
    """Get graph node"""
    result = graph_database.query_specific_entity(entity_name)
    return {"result": graph_database.data_transformer.format_query_results(result), "message": "success"}

@data.get("/graph/nodes")
async def get_graph_nodes(kgdb_name: str, num: int):
    """Get graph nodes"""
    if not agent_config.enable_knowledge_graph:
        raise HTTPException(status_code=400, detail="Knowledge graph is not enabled")

    logger.debug("Get graph nodes in %s with %s nodes", kgdb_name, num)
    result = graph_database.get_sample_nodes(num, kgdb_name)
    return {"result": graph_database.data_transformer.format_query_results(result), "message": "success"}

@data.post("/graph/add-by-jsonl")
async def add_graph_entity(file_path: str = Body(...), kgdb_name: Optional[str] = Body(None)):
    """Add graph entity"""
    if not agent_config.enable_graph:
        return {"message": "Knowledge graph is not enabled", "status": "failed"}

    if not file_path.endswith('.jsonl'):
        return {"message": "File format error, please upload jsonl file", "status": "failed"}

    try:
        import json
        with open(file_path, 'r') as f:
            triples = [json.loads(line) for line in f]
        graph_database.add_entities(triples, kgdb_name)
        return {"message": "Entities added successfully", "status": "success"}
    except Exception as e:
        logger.error("Failed to add entities %s, %s, %s", file_path, e, traceback.format_exc())
        return {"message": f"Failed to add entities {file_path} {e}", "status": "failed"}

