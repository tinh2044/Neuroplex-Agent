from __future__ import annotations

import os

from typing import Annotated, Optional, TypedDict
from abc import abstractmethod
from dataclasses import dataclass, fields

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import BaseMessage
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph.message import add_messages


class State(TypedDict):
    """
    Define a basic State for all graphs to inherit, where:
    1. messages is the core information queue of all graphs, and all chat workflows should add key information to this queue;
    2. history is used to obtain history_len messages when all workflows are started once (to save costs and prevent the length of tokens occupied by a single round of conversation from reaching the upper limit supported by llm),
    the information in history should be discarded.
    """
    messages: Annotated[list[BaseMessage], add_messages]
    history: Optional[list[BaseMessage]]


@dataclass(kw_only=True)
class Configuration(dict):
    """
    Define a basic Configuration for various graphs to inherit
    """

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> Configuration:
        """Create a Configuration instance from a RunnableConfig object."""
        configurable = (config.get("configurable") or {}) if config else {}
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable.items() if k in _fields})

    @classmethod
    def to_dict(cls):
        # Create an instance to handle default_factory
        instance = cls()
        confs = {}
        configurable_items = {}
        for f in fields(cls):
            if f.init and not f.metadata.get("hide", False):
                value = getattr(instance, f.name)
                if callable(value) and hasattr(value, "__call__"):
                    confs[f.name] = value()
                else:
                    confs[f.name] = value

                if f.metadata.get("configurable"):
                    configurable_items[f.name] = {
                        "type": f.type.__name__,
                        "name": f.metadata.get("name", f.name),
                        "options": f.metadata.get("options", []),
                        "default": f.default,
                        "description": f.metadata.get("description", ""),
                    }
        confs["configurable_items"] = configurable_items
        return confs



class BaseAgent():
    """
        Define a basic Agent for various graph to inherit
    """

    name: str = "base_agent"
    description: str = "base_agent"
    config_schema: Configuration = Configuration
    requirements: list[str]

    def __init__(self, **kwargs):
        self.check_requirements()

    @classmethod
    def get_info(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "config_schema": cls.config_schema.to_dict(),
            "requirements": cls.requirements if hasattr(cls, "requirements") else [],
            "all_tools": cls.all_tools if hasattr(cls, "all_tools") else [],
        }

    def check_requirements(self):
        if not hasattr(self, "requirements") or not self.requirements:
            return
        for requirement in self.requirements:
            if requirement not in os.environ:
                raise ValueError(f"No configuration {requirement} environment variables, please configure them in the src/.env file and restart the service")

    def stream_values(self, messages: list[str], config_schema: RunnableConfig = None, **kwargs):
        graph = self.get_graph(config_schema=config_schema, **kwargs)
        for event in graph.stream({"messages": messages}, stream_mode="values", config=config_schema):
            yield event["messages"]

    def stream_messages(self, messages: list[str], config_schema: RunnableConfig = None, **kwargs):
        graph = self.get_graph(config_schema=config_schema, **kwargs)

        for msg, metadata in graph.stream({"messages": messages}, stream_mode="messages", config=config_schema):
            yield msg, metadata

    @abstractmethod
    def get_graph(self, **kwargs) -> CompiledStateGraph:
        pass