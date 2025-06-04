import os
from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from ai_engine.agents import agent_manager
from ai_engine.tools import OcrProcessor
from ai_engine.core.indexing import chunk


tool = APIRouter(prefix="/tool")
ocr_processor = OcrProcessor()


class Tool(BaseModel):
    """
    Tool model for tool list
    """
    name: str
    title: str
    description: str
    url: str
    method: Optional[str] = "POST"
    params: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@tool.get("/", response_model=List[Tool])
async def route_index():
    """
    Route for the tool list
    """
    tools = [
        Tool(
            name="text-chunking",
            title="Text Chunking",
            description="Chunk text for better understanding. Can input text or upload file.",
            url="/tools/text-chunking",
            method="POST",
        ),
        Tool(
            name="pdf2txt",
            title="PDF to Text",
            description="Convert PDF file to text file.",
            url="/tools/pdf2txt",
            method="POST",
        ),
        Tool(
            name="agent",
            title="Agent (Dev)",
            description="Agent playground, still in development preview, welcome to raise issues, but please do not use it in production.",
            url="/tools/agent",
        )
    ]

    for agent in agent_manager.agents.values():
        tools.append(
            Tool(
                name=agent.name,
                title=agent.name,
                description=agent.description,
                url=f"/agent/{agent.name}",
                method="POST",
                metadata=agent.config_schema.to_dict(),
            )
        )

    return tools

@tool.post("/text-chunking")
async def text_chunking(text: str = Body(...), params: Dict[str, Any] = Body(...)):
    """
    Chunk text for better understanding. Can input text or upload file.
    """
    nodes = chunk(text, params=params)
    return {"nodes": [node.to_dict() for node in nodes]}

@tool.post("/pdf2txt")
async def handle_pdf2txt(file: str = Body(...)):
    """
    Process a PDF file and return the extracted text
    """
    text = ocr_processor.extract_text_from_pdf(file)
    return {"text": text}

