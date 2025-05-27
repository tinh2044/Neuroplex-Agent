"""
This file contains some components related to RAG.
"""

from ai_engine.utils import prompts


class BaseOperator:
    """
    Base class for RAG components
    """
    prompt_template = None

    def __init__(self):
        pass

    @classmethod
    def execute(cls, llm_handler, user_question, related_context, **options):
        """
        Override this method in subclasses to define execution logic.

        Args:
            llm_handler: Callable model interface
            user_question: The original user query
            related_context: Retrieved relevant context
            **options: Additional options
        """
        pass

    def __call__(self, **params):
        """
        Allows instance to be called like a function.
        """
        return self.execute(**params)


class HyDEOperator(BaseOperator):
    """
    HyDE operator for query rewriting in RAG pipelines.
    """
    prompt_template = prompts.HYDE_GENERATION_PROMPT

    def __init__(self):
        # super().__init__()
        pass

    @classmethod
    def execute(cls, llm_handler, user_question, related_context, **options):
        """
        Generate hypothesis using a prompt and an LLM handler.

        Args:
            llm_handler: Callable model interface
            user_question: The original user query
            related_context: Retrieved relevant context for prompt conditioning
        """
        generated_prompt = cls.prompt_template.format(
            query=user_question,
            context_str=related_context
        )
        result = llm_handler(generated_prompt)
        return result
