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
from typing import Any

import yaml


from ai_engine.utils import logger

MOCK_AGENT_KEY = 'this_is_mock_agent_key_in_frontend'


class BaseConfig(dict):
    """
    Base configuration class for all configurations.
    """

    def __key(self, key):
        return "" if key is None else key  

    def __str__(self):
        return json.dumps(self)

    def __setattr__(self, key, value):
        if key.startswith('_'):
            # Allow direct attribute access for internal attributes
            super().__setattr__(key, value)
        else:
            self[self.__key(key)] = value

    def __getattr__(self, key):
        if key.startswith('_'):
            # Allow direct attribute access for internal attributes
            return super().__getattribute__(key)
        return self.get(self.__key(key))

    def __getitem__(self, key):
        return self.get(self.__key(key))

    def __setitem__(self, key, value):
        return super().__setitem__(self.__key(key), value)

    def __dict__(self):
        return {k: v for k, v in self.items()}

    def update(self, other):
        for key, value in other.items():
            self[key] = value

class AgentConfig(BaseConfig):
    """Configuration manager for AI agents, handling model settings, workspace, and feature flags."""
    def __init__(self, config_path=None, model_path=None, private_path=None):
        super().__init__()
        # Initialize internal attributes first using direct dict access
        super().__setattr__('_config_store', {})
        super().__setattr__('_config_items', {})
        
        self.workspace = "saves"
        self.config_path = str(Path(config_path)) if config_path else None
        self.model_path = str(Path(model_path)) if model_path else None
        self.private_path = str(Path(private_path)) if private_path else None
        self.models = {}
        self.embed_model = {}
        self.rankers = {}
        
        # Initialize critical attributes first
        self.provider = "siliconflow"
        self.model = "Qwen/Qwen2.5-7B-Instruct"
        
        # Then add all configuration items
        self.add_item("workspace", "workspace", des="Agent workspace directory")
        self.add_item("enable_rerank", False, des="Whether to use embed reranker")
        self.add_item("enable_kb", False, des="Whether to use knowledge base")
        self.add_item("enable_graph", True, des="Whether to use graph")
        self.add_item("enable_websearch", False, des="Whether to use web search")
        self.add_item("provider", "siliconflow", choices=["siliconflow", "openai", "anthropic", "google", "huggingface"])
        self.add_item("model", "Qwen/Qwen2.5-7B-Instruct", des="Model name")
        self.add_item("embed_model", "ollama/bge-m3", des="Embedding model")
        self.add_item("ranker", "huggingface/bge-reranker-v2-m3", des="Ranking model")
        self.add_item("local_paths", {}, des="Local model paths")
        self.add_item("query_mode", "off", des="Query enhancement mode", choices=["off", "on", "hyde"])
        self.add_item("device", "cuda", des="Compute device", choices=["cpu", "cuda"])

    def add_item(self, key, default, des=None, choices=None):
        """Add a configuration item."""
        # Store in _config_store directly
        self._config_store[key] = {"default": default}
        # Store metadata
        self._config_items[key] = {
            "default": default,
            "des": des,
            "choices": choices
        }
        # Set the actual value
        self[key] = default

    def get(self, key, default=None):
        """Get a configuration item."""
        # First try getting from dict
        try:
            return super().get(key, default)
        except Exception:
            # Fallback to config store
            config_item = self._config_store.get(key, {})
            return config_item.get("default", default)

    def set(self, key, value):
        """Set a configuration item."""
        # Update both the dict and config store
        self[key] = value
        if key in self._config_store:
            self._config_store[key]["default"] = value
        else:
            self._config_store[key] = {"default": value}
    
    def __dict__(self):
        blocklist = [
            "_config_items",
            "_config_store",
            "model_names",
            "model_provider_status",
            "embed_model_names",
            "reranker_names",
        ]
        return {k: v for k, v in super().items() if k not in blocklist}

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
            json.dump({k: v["default"] for k, v in self._config_store.items()}, f, indent=4, ensure_ascii=False)
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
    
    def _update_models_from_file(self):
        """
        
        """

        with open(Path("src/static/models.yaml"), encoding='utf-8') as f:
            _models = yaml.safe_load(f)

        try:
            with open(Path("src/static/models.private.yml"), encoding='utf-8') as f:
                _models_private = yaml.safe_load(f)
        except FileNotFoundError:
            _models_private = {}


        self.models = {**_models["MODEL_NAMES"], **_models_private.get("MODEL_NAMES", {})}
        self.embed_model = {**_models["EMBED_MODEL_INFO"], **_models_private.get("EMBED_MODEL_INFO", {})}
        self.reranker = {**_models["RERANKER_LIST"], **_models_private.get("RERANKER_LIST", {})}

    def _save_models_to_file(self):
        _models = {
            "MODEL_NAMES": self.models,
            "EMBED_MODEL_INFO": self.embed_model,
            "RERANKER_LIST": self.reranker,
        }
        with open(Path("src/static/models.private.yml"), 'w', encoding='utf-8') as f:
            yaml.dump(_models, f, indent=2, allow_unicode=True)

    def handle_self(self):
        """
        """
        provider_info = self.models.get(self.provider, {})
        self.model_dir = os.environ.get("MODEL_DIR", "")

        if self.model_dir:
            if os.path.exists(self.model_dir):
                logger.debug(f"MODEL_DIR （{self.model_dir}） folder below: {os.listdir(self.model_dir)}")
            else:
                logger.warning(f"Remind: MODEL_DIR （{self.model_dir}） not found, if not configured, please ignore, if configured, please check if it is configured correctly;"
                               "for example, the mapping in the docker-compose file")
        
        if self.provider != "custom":
            if self.model not in provider_info["models"]:
                logger.warning(f"Model name {self.model} not in {self.provider}, using default model name")
                self.model = provider_info["default"]

            default_model_name = provider_info["default"]
            self.model = self.get("model") or default_model_name
        else:
            self.model = self.get("model")
            if self.model not in [item["custom_id"] for item in self.get("custom_models", [])]:
                logger.warning(f"Model name {self.model} not in custom models, using default model name")
                if self.get("custom_models", []):
                    self.model = self.get("custom_models", [])[0]["custom_id"]
                else:
                    self.model = self._config_items["model"]["default"]
                    self.provider = self._config_items["provider"]["default"]
                    logger.error(f"No custom models found, using default model {self.model} from {self.provider}")

        conds = {}
        self.model_provider_status = {}
        for provider in self.model_names:
            conds[provider] = self.model_names[provider]["env"]
            conds_bool = [bool(os.getenv(_k)) for _k in conds[provider]]
            self.model_provider_status[provider] = all(conds_bool)
        
        if os.getenv("TAVILY_API_KEY"):
            self.enable_web_search = True

        self.valuable_model_provider = [k for k, v in self.model_provider_status.items() if v]
        assert len(self.valuable_model_provider) > 0, f"No model provider available, please check your `.env` file. API_KEY_LIST: {conds}"