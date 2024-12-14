import google.generativeai as genai
from h.utils.ai.base import AIInterface
import os

class GeminiAI(AIInterface):
    """
    Implementation of AIInterface using Google Gemini.
    """

    def __init__(self):
        """
        Initializes the Gemini AI model.
        """
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generates text using the Gemini model.

        Args:
            prompt (str): The input prompt.
            **kwargs: Additional keyword arguments for the model.

        Returns:
            str: The generated text.
        """
        chat = self.model.start_chat()
        response = chat.send_message(prompt, **kwargs)
        return response.text