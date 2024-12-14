import os
import sys
from dotenv import load_dotenv
from h.utils.ai import GeminiAI, OpenAI

def main():
    """
    Example usage of the AI interface.
    """
    load_dotenv()

    try:
        gemini_ai = GeminiAI()
    except ValueError as e:
        print(f"Error initializing Gemini: {e}")
        return

    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "Write a short poem about the moon."

    try:
        response = gemini_ai.generate_text(prompt)
        print("Gemini Response:")
        print(response)
    except Exception as e:
        print(f"Error generating text: {e}")

    try:
        openai_ai = OpenAI()
        prompt = "Write a short story about a cat."
        response = openai_ai.generate_text(prompt)
        print("OpenAI Response:")
        print(response)
    except NotImplementedError as e:
        print(f"Error initializing OpenAI: {e}")


if __name__ == "__main__":
    main()