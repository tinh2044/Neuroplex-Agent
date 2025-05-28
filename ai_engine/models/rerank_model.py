"""
This module provides reranker model loading and scoring utilities for the AI engine.
It supports local reranker models using FlagEmbedding and exposes a unified initialize_reranker interface.
"""
import numpy as np
from FlagEmbedding import FlagReranker

from ai_engine.utils.logging import logger


class LocalReranker(FlagReranker):
    """
    LocalReranker loads a reranker model from a local path using FlagEmbedding.
    It is initialized with a config object and supports scoring via the parent FlagReranker interface.
    """
    def __init__(self, cfg, **options):
        reranker_entry = cfg.reranker_names[cfg.reranker]
        load_path = cfg.model_local_paths.get(reranker_entry["name"], reranker_entry.get("local_path"))
        load_path = load_path or reranker_entry["name"]

        logger.info("Initializing reranker model '%s' from path: %s", cfg.reranker, load_path)

        super().__init__(load_path, use_fp16=True, device=cfg.device, **options)
        logger.info("Reranker model '%s' successfully initialized", cfg.reranker)


def score_to_prob(values):
    """
    Converts raw scores to probability using sigmoid function.
    """
    return 1 / (1 + np.exp(-values))


def initialize_reranker(cfg):
    """
    Constructs and returns a reranker instance using the given configuration.
    """
    supported_keys = cfg.ranker.keys()
    if cfg.reranker not in supported_keys:
        raise ValueError(f"Unsupported Reranker: {cfg.ranker}, supported options: {supported_keys}")

    provider_type, _ = cfg.ranker.split('/', 1)
    if provider_type in {"local", "FlagEmbedding", "huggingface"}:
        return LocalReranker(cfg)
    else:
        raise ValueError(f"Unsupported provider: {cfg.ranker}, allowed: {supported_keys}")
