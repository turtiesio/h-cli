from abc import ABC, abstractmethod
from typing import Any, Dict, List


class AIInterface(ABC):
    """
    Abstract base class for AI model interactions.
    """

    @abstractmethod
    def generate_text(self, prompt: str, **kwargs: Dict[str, Any]) -> str:
        """
        Generates text based on the given prompt.

        Args:
            prompt (str): The input prompt.
            **kwargs: Additional keyword arguments for the model.

        Returns:
            str: The generated text.
        """
        pass
