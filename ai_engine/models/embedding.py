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
            logger: Logger instance for logging messages
        """
        self.meta = config.embed_models[config.embed_model]
        
        logger.info(f"Initializing Ollama embedding with config: {self.meta}")
        
        self.model = self.meta["name"]
        self.url = self.meta.get("url", "http://localhost:11434/api/embed")
        self.url = get_docker_safe_url(self.url)
        self.dimension = self.meta.get("dimension", None)
        self.embed_model_fullname = config.embed_model
        
        # Base URL for other Ollama API endpoints
        self.base_url = self.url.replace("/api/embed", "")
        
        # Check if model exists, if not, try to pull it
        self._ensure_model_available()
    
    def _check_model_exists(self) -> bool:
        """
        Check if the model exists in Ollama.
        Returns:
            bool: True if model exists, False otherwise
        """
        try:
            list_url = f"{self.base_url}/api/tags"
            response = requests.get(list_url, timeout=10)
            
            if response.status_code == 200:
                models_data = response.json()
                existing_models = [model['name'] for model in models_data.get('models', [])]
                return self.model in existing_models
            else:
                logger.warning(f"Failed to check existing models: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking if model exists: {e}")
            return False
    
    def _pull_model(self) -> bool:
        """
        Pull the model from Ollama registry.
        Returns:
            bool: True if pull successful, False otherwise
        """
        try:
            logger.info(f"Model '{self.model}' not found. Attempting to pull from Ollama registry...")
            logger.info("Note: You are using Ollama in Docker. This may take a while for the first download.")
            
            pull_url = f"{self.base_url}/api/pull"
            payload = {"name": self.model}
            
            response = requests.post(pull_url, json=payload, timeout=300, stream=True)
            
            if response.status_code == 200:
                logger.info("Pulling model... Please wait.")
                
                # Process streaming response
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if 'status' in data:
                                logger.info(f"Pull status: {data['status']}")
                                
                                # Check if pull is complete
                                if data.get('status') == 'success' or 'successfully' in data.get('status', '').lower():
                                    logger.info(f"Successfully pulled model '{self.model}'")
                                    return True
                        except json.JSONDecodeError:
                            continue
                
                return True
            else:
                logger.error(f"Failed to pull model: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("Timeout while pulling model. The model might be large. Please try again or pull manually.")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error pulling model: {e}")
            return False
    
    def _ensure_model_available(self):
        """
        Ensure the model is available, pull if necessary.
        """
        if not self._check_model_exists():
            logger.warning(f"Model '{self.model}' not found in Ollama")
            
            if not self._pull_model():
                error_msg = (
                    f"Failed to pull model '{self.model}'. "
                    f"Please manually pull the model using: docker exec ollama ollama pull {self.model}"
                )
                raise RuntimeError(error_msg)
        else:
            logger.info(f"Model '{self.model}' is available in Ollama")
    
    def run_inference(self, input_data):
        """
        Generates embeddings using the Ollama API.
        Args:
            input_data (Union[List[str], str]): The text or list of texts to embed.
        Returns:
            List[List[float]]: A list of embeddings from the Ollama API.
        Raises:
            RuntimeError: If the API response indicates an error or missing model.
        """
        if isinstance(input_data, str):
            input_data = [input_data]
        
        payload = {
            "model": self.model,
            "input": input_data,
        }
        
        try:
            logger.debug(f"Sending embedding request for {len(input_data)} texts")
            
            resp = requests.post(self.url, json=payload, timeout=30)
            
            if resp.status_code != 200:
                error_msg = f"Ollama API returned HTTP {resp.status_code}: {resp.text}"
                raise RuntimeError(error_msg)
            
            output = resp.json()
            
            # Check for errors in response
            if 'error' in output:
                error_msg = f"Ollama embedding failed: {output['error']}"
                
                # Special handling for model not found error
                if 'not found' in output['error'].lower():
                    logger.warning("Model not found error occurred. Attempting to pull model...")
                    
                    if self._pull_model():
                        # Retry the inference after pulling
                        logger.info("Retrying embedding after model pull...")
                        return self.run_inference(input_data)
                    else:
                        error_msg += f"\nPlease manually pull the model using: docker exec ollama ollama pull {self.model}"
                
                raise RuntimeError(error_msg)
            
            # Check if embeddings are present
            if not output.get("embeddings"):
                error_msg = f"No embeddings returned from Ollama API. Response: {output}"
                raise RuntimeError(error_msg)
            
            logger.debug(f"Successfully generated {len(output['embeddings'])} embeddings")
            
            return output["embeddings"]
            
        except requests.exceptions.Timeout:
            error_msg = "Timeout waiting for Ollama embedding response"
            raise RuntimeError(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error while calling Ollama API: {e}"
            raise RuntimeError(error_msg)
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response from Ollama API: {e}"
            raise RuntimeError(error_msg)

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
    assert embed_model in config.embed_models, f"Unsupported model: {embed_model}"

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
