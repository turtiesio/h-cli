from h.utils.ai.base import AIInterface


class OpenAI(AIInterface):
    """
    Placeholder for OpenAI implementation.
    """

    def __init__(self, api_key: str):
        """
        Initializes the OpenAI model.
        """
        if not api_key:
            raise ValueError("OpenAI API key not set.")

    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generates text using the OpenAI model.

        Args:
            prompt (str): The input prompt.
            **kwargs: Additional keyword arguments for the model.

        Returns:
            str: The generated text.
        """
        raise NotImplementedError("OpenAI implementation not yet available.")
