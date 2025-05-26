"""Handles interactions with OpenAI-compatible chat models."""
import os
import requests
from openai import OpenAI
from langchain_openai import ChatOpenAI
from ai_engine.utils import logger, get_docker_safe_url


class OpenAIBase:
    """Base class for interacting with OpenAI-compatible chat models."""
    def __init__(self, api_key, base_url, model_name, **options):
        """
        Initializes the OpenAIBase model.

        Args:
            api_key (str): The API key for the model provider.
            base_url (str): The base URL for the API.
            model_name (str): The name of the model to use.
            **options: Additional keyword arguments for model configuration.
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.llm_client = OpenAI(api_key=api_key, base_url=base_url)
        self.model_config = options

        self.chat_open_ai = ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=base_url
        )

    def generate_response(self, prompt_payload, use_streaming=False):
        """
        Generates a response from the chat model.

        Args:
            prompt_payload (str | list[dict]): The prompt string or a list of message dictionaries.
            use_streaming (bool, optional): Whether to use streaming for the response. Defaults to False.

        Returns:
            A streaming iterator if use_streaming is True, otherwise the complete message object.
        """
        if isinstance(prompt_payload, str):
            prompt_payload = [{"role": "user", "content": prompt_payload}]

        return self._handle_stream(prompt_payload) if use_streaming else self._handle_sync(prompt_payload)

    def _handle_stream(self, prompt_payload):
        """
        Handles generating a response using streaming.

        Args:
            prompt_payload (list[dict]): The list of message dictionaries.

        Yields:
            The delta of each chunk in the streamed response.

        Raises:
            RuntimeError: If there is an error during streaming.
        """
        try:
            result = self.llm_client.chat.completions.create(
                model=self.model_name,
                messages=prompt_payload,
                stream=True,
            )
            for piece in result:
                if piece.choices:
                    yield piece.choices[0].delta
        except Exception as err:
            msg = "Streaming error: %s, URL: %s, API: %s***, Model: %s" % (err, self.base_url, self.api_key[:5], self.model_name)
            logger.error(msg)
            raise RuntimeError(msg)

    def _handle_sync(self, prompt_payload):
        """
        Handles generating a synchronous (non-streaming) response.

        Args:
            prompt_payload (list[dict]): The list of message dictionaries.

        Returns:
            The message object from the model's response.
        """
        result = self.llm_client.chat.completions.create(
            model=self.model_name,
            messages=prompt_payload,
            stream=False,
        )
        return result.choices[0].message

    def list_available_models(self):
        """
        Lists available text models from the provider.

        Returns:
            list: A list of available models, or an empty list if an error occurs.
        """
        try:
            return self.llm_client.models.list(extra_query={"type": "text"})
        except Exception as err:
            logger.error("Model listing error: %s", err)
            return []

    def fetch_model_info(self, model_url):
        """
        Fetches detailed information about a specific model from a given URL.

        Args:
            model_url (str): The URL to fetch model information from.

        Returns:
            dict: A dictionary containing the model information.
        """
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.api_key}"
        }
        response = requests.get(model_url, headers=headers, timeout=10)
        return response.json()


class OpenModel(OpenAIBase):
    """Chat model specifically for OpenAI services."""
    def __init__(self, model_name=None):
        """
        Initializes the OpenModel.

        Args:
            model_name (str, optional): The name of the OpenAI model to use.
                                      Defaults to "gpt-4o-mini".
                                      Reads OPENAI_API_KEY and OPENAI_API_BASE from environment variables.
        """
        model_name = model_name or "gpt-4o-mini"
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_API_BASE")
        super().__init__(api_key=api_key, base_url=base_url, model_name=model_name)


class CustomModel(OpenAIBase):
    """Chat model for custom, OpenAI-compatible API endpoints."""
    def __init__(self, model_info):
        """
        Initializes the CustomModel.

        Args:
            model_info (dict): A dictionary containing model configuration:
                               - "name" (str): The model name.
                               - "api_key" (str, optional): The API key. Defaults to "custom_model".
                               - "api_base" (str): The base URL for the custom API.
        """
        model_name = model_info["name"]
        api_key = model_info.get("api_key") or "custom_model"
        base_url = get_docker_safe_url(model_info["api_base"])
        logger.info("> Custom model loaded: %s, endpoint: %s", model_name, base_url)

        super().__init__(api_key=api_key, base_url=base_url, model_name=model_name)


class GeneralResponse:
    """A simple wrapper for holding response content."""
    def __init__(self, content):
        """
        Initializes the GeneralResponse.

        Args:
            content: The content of the response.
        """
        self.content = content
        self.is_full = False


if __name__ == "__main__":
    pass
