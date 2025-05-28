"""Handles embedding model interactions, supporting local, Ollama, and other remote services."""
import os
import json
import asyncio
import requests
from FlagEmbedding import FlagModel

from ai_engine.utils import hashstr, logger, get_docker_safe_url


class BaseEmbeddingModel:
    """
    Base class for embedding models, providing a common interface and utility methods.

    Attributes:
        status_tracker (dict): A dictionary to track the progress of batch embedding operations.
    """
    status_tracker = {}

    def get_dimension(self):
        """
        Retrieves the embedding dimension for the model.

        It first checks for a 'dimension' attribute on the instance,
        then in the model configuration based on 'embed_model_fullname',
        and finally based on 'model'.

        Returns:
            int or None: The embedding dimension if found, otherwise None.
        """
        if hasattr(self, "dimension"):
            return self.dimension

        if hasattr(self, "embed_model_fullname"):
            return self.config.embed_model_names[self.embed_model_fullname].get("dimension", None)
        if hasattr(self, "model"):
            return self.config.embed_model[self.model].get("dimension", None)
        return None

    def vectorize(self, input_data):
        """
        Generates embeddings for the given input data.
        This method should be implemented by subclasses.

        Args:
            input_data (str | list[str]): The input text or list of texts to embed.

        Returns:
            list: A list of embeddings.
        """
        return self.run_inference(input_data)

    def vectorize_queries(self, queries):
        """
        Generates embeddings specifically for query-like input data.
        By default, this calls the standard vectorize method.

        Args:
            queries (str | list[str]): The input query or list of queries to embed.

        Returns:
            list: A list of embeddings.
        """
        return self.run_inference(queries)

    async def avectorize(self, input_data):
        """
        Asynchronously generates embeddings for the given input data.

        Args:
            input_data (str | list[str]): The input text or list of texts to embed.

        Returns:
            list: A list of embeddings.
        """
        return await asyncio.to_thread(self.vectorize, input_data)

    async def avectorize_queries(self, queries):
        """
        Asynchronously generates embeddings specifically for query-like input data.

        Args:
            queries (str | list[str]): The input query or list of queries to embed.

        Returns:
            list: A list of embeddings.
        """
        return await asyncio.to_thread(self.vectorize_queries, queries)

    async def abatch_vectorize(self, items, batch_limit=20):
        """
        Asynchronously generates embeddings for a list of items in batches.

        Args:
            items (list[str]): A list of texts to embed.
            batch_limit (int, optional): The maximum number of items to process in a single batch.
                                         Defaults to 20.

        Returns:
            list: A list of embeddings for all items.
        """
        return await asyncio.to_thread(self.batch_vectorize, items, batch_limit)

    def batch_vectorize(self, items, batch_limit=20):
        """
        Generates embeddings for a list of items in batches.

        Logs progress if the number of items exceeds the batch_limit and updates
        the `status_tracker`.

        Args:
            items (list[str]): A list of texts to embed.
            batch_limit (int, optional): The maximum number of items to process in a single batch.
                                         Defaults to 20.

        Returns:
            list: A list of embeddings for all items.
        """
        logger.info("Processing vectorization in batches: total %d items", len(items))
        result = []

        if len(items) > batch_limit:
            task_tag = hashstr(items)
            self.status_tracker[task_tag] = {
                'status': 'in-progress',
                'total': len(items),
                'progress': 0
            }

        for idx in range(0, len(items), batch_limit):
            segment = items[idx:idx + batch_limit]
            logger.info("Encoding items %d to %d", idx, idx + batch_limit)
            vectors = self.vectorize(segment)
            logger.debug("Vector count: %d, Segment size: %d, Dim: %d", len(vectors), len(segment), len(vectors[0]))
            result.extend(vectors)

        if len(items) > batch_limit:
            self.status_tracker[task_tag]['progress'] = len(items)
            self.status_tracker[task_tag]['status'] = 'completed'

        return result
    
    def run_inference(self, input_data: list[str] | str):
        pass


class LocalEmbeddingModel(FlagModel, BaseEmbeddingModel):
    """Embedding model that loads and runs models locally using FlagEmbedding."""
    def __init__(self, config, **kwargs):
        """
        Initializes a local embedding model using FlagEmbedding.

        The model path is determined by looking up `config.embed_model` in
        `config.embed_model_names`, then checking `config.model_local_paths`
        and `local_path` within the model's metadata. If the `MODEL_DIR`
        environment variable is set, it also checks for the model in that directory.

        Args:
            config: The application configuration object.
            **kwargs: Additional keyword arguments passed to the FlagModel constructor.
        """
        model_meta = config.embed_model_names[config.embed_model]
        self.config = config

        self.model = config.model_local_paths.get(model_meta["name"], model_meta.get("local_path"))
        self.model = self.model or model_meta["name"]
        self.dimension = model_meta["dimension"]
        self.embed_model_fullname = config.embed_model

        if os.getenv("MODEL_DIR"):
            potential_path = os.path.join(os.getenv("MODEL_DIR"), self.model)
            if os.path.exists(potential_path):
                self.model = potential_path
            else:
                logger.warning("Model `%s` not found at `%s`, using fallback `%s`", model_meta['name'], self.model, model_meta['name'])

        logger.info("Initializing local embedding model `%s` from `%s` on `%s`", model_meta['name'], self.model, config.device)

        super().__init__(
            self.model,
            query_instruction_for_retrieval=model_meta.get("query_instruction", None),
            use_fp16=False,
            device=config.device,
            **kwargs
        )

        logger.info("Model `%s` loaded successfully.", model_meta['name'])

    def run_inference(self, input_data: list[str] | str):
        """Generates embeddings using the underlying FlagModel.

        Args:
            input_data (list[str] | str): The text or list of texts to embed.

        Returns:
            list: A list of embeddings.
        """
        return self.encode(input_data)


class OllamaEmbedding(BaseEmbeddingModel):
    """Embedding model that interacts with an Ollama API."""
    def __init__(self, config) -> None:
        """
        Initializes an embedding model that interacts with an Ollama API.

        Args:
            config: The application configuration object. It uses `config.embed_model`
                    to find the model details in `config.embed_model_names`.
        """
        self.meta = config.embed_model_names[config.embed_model]
        self.model = self.meta["name"]
        self.url = self.meta.get("url", "http://localhost:11434/api/embed")
        self.url = get_docker_safe_url(self.url)
        self.dimension = self.meta.get("dimension", None)
        self.embed_model_fullname = config.embed_model

    def run_inference(self, input_data: list[str] | str):
        """
        Generates embeddings using the Ollama API.

        Args:
            input_data (list[str] | str): The text or list of texts to embed.

        Returns:
            list: A list of embeddings from the Ollama API.

        Raises:
            AssertionError: If the API response does not contain 'embeddings'.
        """
        if isinstance(input_data, str):
            input_data = [input_data]

        payload = {
            "model": self.model,
            "input": input_data,
        }
        resp = requests.post(self.url, json=payload, timeout=10)
        output = json.loads(resp.text)
        assert output.get("embeddings"), f"Ollama embedding failed: {output}"
        return output["embeddings"]


class OtherEmbedding(BaseEmbeddingModel):
    """Embedding model that interacts with a generic API."""
    def __init__(self, config) -> None:
        """
        Initializes a generic embedding model for other API-based services.

        Requires 'url', 'name', and 'api_key' (via environment variable)
        to be defined in the configuration for the specified `config.embed_model`.

        Args:
            config: The application configuration object.
        """
        self.meta = config.embed_model_names[config.embed_model]
        self.embed_model_fullname = config.embed_model
        self.dimension = self.meta.get("dimension", None)
        self.model = self.meta["name"]
        self.api_key = os.getenv(self.meta["api_key"], None)
        self.url = get_docker_safe_url(self.meta["url"])
        assert self.url and self.model, f"Missing URL or model in config: {config.embed_model}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def run_inference(self, input_data):
        """
        Generates embeddings using a configured third-party API.

        Args:
            input_data (str | list[str]): The text or list of texts to embed.

        Returns:
            list: A list of embeddings from the API.

        Raises:
            AssertionError: If the API response does not contain 'data'.
        """
        request_body = self.prepare_payload(input_data)
        resp = requests.post(self.url, json=request_body, headers=self.headers, timeout=10)
        output = json.loads(resp.text)
        assert output["data"], f"Embedding API failed: {output}"
        return [entry["embedding"] for entry in output["data"]]

    def prepare_payload(self, content):
        """
        Constructs the payload for the embedding API request.

        Args:
            content (str | list[str]): The input text or list of texts.

        Returns:
            dict: The payload dictionary for the API request.
        """
        return {
            "model": self.model,
            "input": content,
        }


def initialize_embedding(config):
    """
    Initializes and returns an embedding model based on the application configuration.

    Selects the appropriate embedding model class (Local, Ollama, or Other)
    based on the 'provider' part of `config.embed_model`.

    Args:
        config: The application configuration object.

    Returns:
        BaseEmbeddingModel or None: An instance of an embedding model, or None
                                     if `config.enable_knowledge_base` is False.
    Raises:
        AssertionError: If `config.embed_model` is not found in `config.embed_model_names`.
    """
    if not config.enable_kb:
        return None
    embed_model = str(config.embed_model)
    provider, _ = embed_model.split('/', 1)
    assert embed_model in config.embed_model, f"Unsupported model: {embed_model}"

    logger.debug("Initializing embedding model `%s`...", embed_model)

    if provider == "local":
        return LocalEmbeddingModel(config)
    elif provider == "ollama":
        return OllamaEmbedding(config)
    else:
        return OtherEmbedding(config)


def resolve_local_model_path(paths, name, fallback):
    """
    Resolves the local path for a model.

    Args:
        paths (dict): A dictionary of model names to paths.
        name (str): The name of the model.
        fallback (str): The fallback path to use if the name is not in paths.

    Returns:
        str: The resolved model path.
    """
    return paths.get(name, fallback)
