import json
import re
import os
from typing import Any, Callable, Optional, Type, Union, Annotated


from pydantic import BaseModel, Field
from langchain_core.tools import tool, BaseTool, StructuredTool
from langchain_community.tools.tavily_search import TavilySearchResults

from ai_engine import graph_database, knowledge_base, agent_config

# refs https://github.com/chatchat-space/LangGraph-Chatchat chatchat-server/chatchat/server/agent/tools_factory/tools_registry.py
def regist_tool(
    *args: Any,
    title: str = "",
    description: str = "",
    return_direct: bool = False,
    args_schema: Optional[Type[BaseModel]] = None,
    infer_schema: bool = True,
) -> Union[Callable, BaseTool]:
    """
    wrapper of langchain tool decorator
    add tool to registry automatically
    """

    def _parse_tool(t: BaseTool):
        nonlocal description, title

        _TOOLS_REGISTRY[t.name] = t

        # change default description
        if not description:
            if t.func is not None:
                description = t.func.__doc__
            elif t.coroutine is not None:
                description = t.coroutine.__doc__
        t.description = " ".join(re.split(r"\n+\s*", description))
        # set a default title for human
        if not title:
            title = "".join([x.capitalize() for x in t.name.split("_")])
        setattr(t, "_title", title)

    def wrapper(def_func: Callable) -> BaseTool:
        partial_ = tool(
            *args,
            return_direct=return_direct,
            args_schema=args_schema,
            infer_schema=infer_schema,
        )
        t = partial_(def_func)
        _parse_tool(t)
        return t

    if len(args) == 0:
        return wrapper
    else:
        t = tool(
            *args,
            return_direct=return_direct,
            args_schema=args_schema,
            infer_schema=infer_schema,
        )
        _parse_tool(t)
        return t


class KnowledgeRetrieverModel(BaseModel):
    query: str = Field(description="The keywords to query, when querying, try to use keywords that may help answer this question, do not directly use the user's original input to query.")



def get_all_tools():
    """Get all tools"""
    tools = _TOOLS_REGISTRY.copy()

    # Get all knowledge bases
    for _, retrieve_info in knowledge_base.get_retrievers().items():
        name = f"retrieve_{retrieve_info['name']}"
        description = (
            f"Use {retrieve_info['name']} knowledge base for retrieval.\n"
            f"Below is the description of this knowledge base: \n{retrieve_info['description']}"
        )
        tools[name] = StructuredTool.from_function(
            retrieve_info["retriever"],
            name=name,
            description=description,
            args_schema=KnowledgeRetrieverModel)

    return tools

class BaseToolOutput:
    """
    LLM requires Tool output to be str, but Tool is used elsewhere when it should normally return structured data.
    Only need to wrap the Tool return value with this class to meet the needs of both.
    The base class simply serializes the return value to a string, or specify format="json" to convert it to json.
    Users can also inherit this class to define their own conversion methods.
    """

    def __init__(
        self,
        data: Any,
        _format: str | Callable = None,
        data_alias: str = "",
        **extras: Any,
    ) -> None:
        self.data = data
        self.format = _format
        self.extras = extras
        if data_alias:
            setattr(self, data_alias, property(lambda obj: obj.data))

    def __str__(self) -> str:
        if self.format == "json":
            return json.dumps(self.data, ensure_ascii=False, indent=2)
        elif callable(self.format):
            return self.format(self)
        else:
            return str(self.data)

@tool
def calculator(a: float, b: float, operation: str) -> float:
    """Calculate two numbers."""
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        return a / b
    else:
        raise ValueError(f"Invalid operation: {operation}, only support add, subtract, multiply, divide")

@tool
def get_knowledge_graph(query: Annotated[str, "The query to get knowledge graph."]):
    """Use this to get knowledge graph."""
    return graph_database.query_specific_entity(query, hops=2)




_TOOLS_REGISTRY = {
    "calculator": calculator,
    "get_knowledge_graph": get_knowledge_graph,
}

if agent_config.enable_web_search:
    _TOOLS_REGISTRY["TavilySearchResults"] = TavilySearchResults(max_results=10)
