"""
This file contains components related to RAG (Retrieval-Augmented Generation).
"""

from typing import Optional, Callable, Dict, Any, Union
from ai_engine.utils import prompts
from ai_engine.utils.logging import logger
import time


class BaseOperator:
    """
    Base class for RAG components that process queries and context.

    Attributes:
        prompt_template (Optional[str]): Template string used for generating prompts.
    """
    prompt_template: Optional[str] = None

    def __init__(self):
        """Initialize the operator."""
        if self.__class__ != BaseOperator and not self.prompt_template:
            raise ValueError(f"{self.__class__.__name__} requires a prompt template")

    @classmethod
    def execute(cls, 
                llm_handler: Callable,
                user_question: str, 
                related_context: str,
                **options: Dict[str, Any]) -> Any:
        """
        Execute the operator's logic.

        Args:
            llm_handler: Callable model interface that takes a prompt and returns a response
            user_question: The original user query
            related_context: Retrieved relevant context
            **options: Additional options for execution

        Returns:
            Any: The processed result from the operator

        Raises:
            NotImplementedError: If the subclass doesn't implement this method
        """
        raise NotImplementedError("Subclasses must implement execute method")

    def __call__(self, **params) -> Any:
        """
        Allows instance to be called like a function.

        Args:
            **params: Parameters to pass to execute()

        Returns:
            Any: Result from execute()
        """
        return self.execute(**params)


class HyDEOperator(BaseOperator):
    """
    HyDE (Hypothetical Document Embeddings) operator for query rewriting in RAG pipelines.
    
    This operator implements the HyDE technique which generates hypothetical documents
    that could answer a query, then uses these documents to enhance retrieval.
    
    The process:
    1. Takes a user query and optional context
    2. Generates a hypothetical passage that would answer the query
    3. Uses this passage to enhance the retrieval process
    
    Attributes:
        prompt_template (str): Template for generating hypothetical documents
    
    References:
        Paper: "HyDE: Using Hypothetical Documents to Improve Retrieval"
        Authors: Akari Asai, Sewon Min, Zexuan Zhong, Danqi Chen
        URL: https://arxiv.org/abs/2212.10496
    """
    prompt_template = prompts.HYDE_GENERATION_PROMPT

    def __init__(self):
        """Initialize the HyDE operator."""
        super().__init__()

    @classmethod
    def execute(cls,
                llm_handler: Callable,
                user_question: str,
                related_context: str,
                **options: Dict[str, Any]) -> Any:
        """
        Generate hypothesis using a prompt and an LLM handler.

        Args:
            llm_handler: Callable model interface that processes prompts
            user_question: The original user query
            related_context: Retrieved relevant context for prompt conditioning
            **options: Additional options for execution

        Returns:
            Any: The generated hypothetical document or enhanced query

        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If LLM generation fails
        """
        # Input validation
        if not user_question or not user_question.strip():
            raise ValueError("User question cannot be empty")
        
        if not callable(llm_handler):
            raise TypeError("llm_handler must be callable")

        # Log operation start
        logger.info(f"Executing HyDE for question: {user_question[:100]}...")
        start_time = time.time()

        try:
            # Generate the prompt
            generated_prompt = cls.prompt_template.format(
                query=user_question,
                context_str=related_context if related_context else ""
            )

            # Get response from LLM
            result = llm_handler(generated_prompt)

            # Log success
            duration = time.time() - start_time
            logger.info(f"HyDE execution completed in {duration:.2f}s")
            
            return result

        except (AttributeError, KeyError) as e:
            logger.error(f"Failed to generate HyDE prompt: {str(e)}")
            raise ValueError(f"Failed to generate HyDE prompt: {str(e)}")
        except Exception as e:
            logger.error(f"HyDE execution failed: {str(e)}")
            raise RuntimeError(f"HyDE execution failed: {str(e)}")
