"""Handles model selection and initialization."""
import os
import traceback
from ai_engine.config import AgentConfig
from ai_engine.utils.logging import logger
from ai_engine.models.chat_model import OpenAIBase, OpenModel, CustomModel


def select_model(model_provider=None, model_name=None):
    """Select model based on model provider"""
    config = AgentConfig()
    if hasattr(config, "model_names"):
        model_provider = model_provider or config.model_provider
        model_info = config.model_names.get(model_provider, {})
        model_name = model_name or config.model_name or model_info.get("default", "")

    logger.info("Selecting model from `%s` with `%s`", model_provider, model_name)

    if model_provider is None:
        raise ValueError("Model provider not specified, please modify `model_provider` in `src/config/base.yaml`")

    if model_provider == "openai":
        return OpenModel(model_name)

    if model_provider == "custom":
        if hasattr(config, "custom_models"):
            model_info = next((x for x in config.custom_models if x["custom_id"] == model_name), None)
            if model_info is None:
                raise ValueError("Model %s not found in custom models" % model_name)

        return CustomModel(model_info)

    # Other models, use OpenAIBase by default
    try:
        model = OpenAIBase(
            api_key=os.getenv(model_info["env"][0]),
            base_url=model_info["base_url"],
            model_name=model_name,
        )
        return model
    except Exception as e:
        raise ValueError("Model provider %s load failed, %s \n %s" % (model_provider, e, traceback.format_exc()))
