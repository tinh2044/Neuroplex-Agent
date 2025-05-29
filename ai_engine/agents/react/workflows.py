import os

from langchain_openai import ChatOpenAI
from typing import Literal, Annotated
from langchain_core.tools import tool, StructuredTool
from langgraph.prebuilt import create_react_agent


model = ChatOpenAI(model="gpt-4o-mini",
                   api_key=os.getenv("OPENAI_API_KEY"),
                   base_url="https://api.openai.com/v1",
                   temperature=0)


tools = []



graph = create_react_agent(model, tools=tools)
