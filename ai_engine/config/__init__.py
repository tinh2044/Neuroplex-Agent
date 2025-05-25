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

class AgentRegistry(dict):
    """A dictionary-like registry for managing agent configurations.
    
    This class extends the built-in dict to provide additional functionality
    for managing agent configurations, including custom attribute access
    and string representation.
    """
    def __key(self, key):
        return "" if key not in self else key
    def __str__(self):
        return json.dumps(self, indent=4, ensure_ascii=False)
    def __setattr__(self, name, value):
        return super().__setattr__(name, value)
    def __getitem__(self, key):
        return super().__getitem__(key)
    def __getattr__(self, key):
        key = self.__key(key)
        if key in self:
            return super().__getitem__(key)
        
        logger.error("Key '%s' not found in AgentRegistry.", key)
        raise KeyError(f"Key '{key}' not found in AgentRegistry.")
    def __setitem__(self, key, value):
        return super().__setitem__(key, value)
    def __dict__(self):
        return {k: v for k, v in self.items() if not k.startswith('_')}
    

class AgentConfig(AgentRegistry):
    """Configuration manager for AI agents, handling model settings, workspace, and feature flags."""
    def __init__(self, config_path=None, model_path=None, private_path=None):
        super().__init__()
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
        self.add_item("embed_model", default="siliconflow/BAAI/bge-m3", des="Embedding model", choices=list(self.embed_models.keys()))
        self.add_item("ranker", default="siliconflow/BAAI/bge-reranker-v2-m3", des="Ranking model", choices=list(self.rankers.keys()))
        self.add_item("local_paths", default={}, des="Local model paths")
        self.add_item("query_mode", default="off", des="Query enhancement mode", choices=["off", "on", "hyde"])
        self.add_item("device", default="cuda", des="Compute device", choices=["cpu", "cuda"])
    
    def add_item(self, key, default, des=None, choices=None):
        """Add or update a configuration item.
        
        Args:
            key: Configuration key
            value: Configuration value
            des: Optional description
            choices: Optional list of valid choices
        """
        if key in self:
            logger.warning("Key '%s' already exists. Overwriting the value.", key)
        self[key] = {
            "default": default,
            "des": des,
            "choices": choices
        }
        
    def __dict__(self):
        blocked = ["_items", "models", "provider_status", "embed_model", "rankers", "workspace", "config_path"]
        return {k: v for k, v in super().items() if k not in blocked}
    def _load_model(self):
        self.models  = {
           "siliconflow": {
                "models": ["Qwen/Qwen2.5-7B-Instruct"],
                "default": "Qwen/Qwen2.5-7B-Instruct",
                "env": ["SILICONFLOW_API_KEY"]
            }
            
        }

        self.embed_model = {}
        self.rankers = {}

        try:
            with open(Path(self.model_path), "r", encoding="utf-8") as f:
                _models : dict = yaml.safe_load(f)

                self.models = _models.get("MODEL_NAMES", {})
                self.embed_model = _models.get("EMBED_MODEL_INFO", {})
                self.rankers = _models.get("RERANKER_LIST", {})
        except FileNotFoundError:
            logger.warning("Model file not found, use default models.")

        try:
            with open(Path(self.private_path), "r", encoding="utf-8") as f:
                _private : dict = yaml.safe_load(f)
                self.models.update(_private.get("MODEL_NAMES", {}))
                self.embed_model.update(_private.get("EMBED_MODEL_INFO", {}))
                self.rankers.update(_private.get("RERANKER_LIST", {}))
        except FileNotFoundError:
            logger.warning("No private config file found")


    def _save_models(self):
        _models = {
            "MODEL_NAMES": self.models,
            "EMBED_MODEL_INFO": self.embed_model,
            "RERANKER_LIST": self.rankers
        }
        with open(Path(self.private_path), "w", encoding="utf-8") as f:
            yaml.dump(_models, f, indent=2, allow_unicode=True)
    

    def load(self):
        """Load agent configuration from the specified config file path."""
        logger.info("Loading agent configuration from %s", self.config_path)
        if not (self.config_path.endswith(".json") or  os.path.exists(self.config_path)):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                if not isinstance(config, dict):
                    raise ValueError("Invalid configuration file: root element must be a dictionary")
                
                self.update(config)
        except Exception as e:
            logger.error("Error loading configuration from %s: %s", self.config_path, str(e))
            raise e
        
    def save(self):
        """Save agent configuration to the specified config file path."""
        logger.info("Saving agent configuration to %s", self.config_path)
        
        if self.config_path is None:
            self.config_path = os.path.join(self.workspace, "config.json")
        
        if self.config_path.endswith(".json"):
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self, f, indent=4, ensure_ascii=False)
        elif self.config_path.endswith(".yaml"):
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self, f, indent=2, allow_unicode=True)
        else:
            logger.warning("Unsupported configuration file format: %s", self.config_path)
            with open(self.config_path, "w", encoding="utf-8") as f:
                f.write(str(self))
        
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