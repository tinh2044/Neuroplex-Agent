"""Configuration module for the AI Engine.

This module provides configuration management for the AI Engine, including:
- Agent configuration handling
- Agent registry for managing agent instances
- Configuration file management

Example:
    # Create a new agent configuration
    config = AgentConfig()
    config.add_item('agent_name', 'default_agent', 'Name of the agent')
"""
import json
import os
from pathlib import Path

import yaml

from ai_engine.utils import logger

MOCK_AGENT_KEY = 'this_is_mock_agent_key_in_frontend'

class AgentConfig:
    """Configuration manager for AI agents, handling model settings, workspace, and feature flags."""
    def __init__(self, config_path=None, model_path=None, private_path=None):
        self.items = {}
        self.workspace = "saves"
        self.config_path = str(Path(config_path)) if config_path else None
        self.model_path = str(Path(model_path)) if model_path else None
        self.private_path = str(Path(private_path)) if private_path else None
        self.models = {}
        self.embed_model = {}
        self.rankers = {}

        self.add_item("workspace", default="workspace", des="Agent workspace directory")
        self.add_item("enable_rerank", default=False, des="Whether to use embed reranker")
        self.add_item("enable_kb", default=False, des="Whether to use knowledge base")
        self.add_item("enable_graph", default=False, des="Whether to use graph")
        self.add_item("enable_websearch", default=False, des="Whether to use web search")
        self.add_item("provider", default="siliconflow", choices=["siliconflow", "openai", "anthropic", "google", "huggingface"])
        self.add_item("model", default="Qwen/Qwen2.5-7B-Instruct", des="Model name")
        self.add_item("embed_model", default="ollama/bge-m3", des="Embedding model")
        self.add_item("ranker", default="huggingface/bge-reranker-v2-m3", des="Ranking model")
        self.add_item("local_paths", default={}, des="Local model paths")
        self.add_item("query_mode", default="off", des="Query enhancement mode", choices=["off", "on", "hyde"])
        self.add_item("device", default="cuda", des="Compute device", choices=["cpu", "cuda"])

    def add_item(self, key, default, des=None, choices=None):
        """Add or update a configuration item."""
        self.items[key] = {
            "default": default,
            "des": des,
            "choices": choices
        }

    def get(self, key, default=None):
        """Get a configuration item."""
        return self.items.get(key, {}).get("default", default)

    def set(self, key, value):
        """Set a configuration item."""
        if key in self.items:
            self.items[key]["default"] = value
        else:
            self.items[key] = {"default": value}

    def load(self):
        """Load agent configuration from the specified config file path."""
        logger.info("Loading agent configuration from %s", self.config_path)
        if not (self.config_path and (self.config_path.endswith(".json") or os.path.exists(self.config_path))):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                if not isinstance(config, dict):
                    raise ValueError("Invalid configuration file: root element must be a dictionary")
                for k, v in config.items():
                    self.set(k, v)
        except Exception as e:
            logger.error("Error loading configuration from %s: %s", self.config_path, str(e))
            raise e

    def save(self):
        """Save agent configuration to the specified config file path."""
        logger.info("Saving agent configuration to %s", self.config_path)
        if self.config_path is None:
            self.config_path = os.path.join(self.workspace, "config.json")
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump({k: v["default"] for k, v in self.items.items()}, f, indent=4, ensure_ascii=False)
        logger.info("Agent configuration saved to %s", self.config_path)

    def compare_custom_models(self, value):
        """Compare and preserve existing API keys"""
        current_keys = {model["custom_id"]: model.get("api_key") for model in self.get("custom_models", [])}
        for i, model in enumerate(value):
            custom_id = model.get("custom_id")
            api_key = model.get("api_key")
            if custom_id in current_keys:
                if api_key == MOCK_AGENT_KEY:
                    value[i]["api_key"] = current_keys[custom_id]
        return value
    