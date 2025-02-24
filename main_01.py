import openai
import logging
from typing import Optional
from config import API_CONFIG
from openai import OpenAI

logger = logging.getLogger('website_translator')


class OpenAITranslationClient:
    def __init__(self, api_key: str):
        """Initialize API client with provided OpenAI API key."""
        self.client = OpenAI(api_key=api_key)  # ✅ Corrected OpenAI Client Initialization

    def translate_text(self, content: str, target_language: str, max_tokens: int = 4096,
                       temperature: float = 0.3) -> str:
        """
        Sends a request to OpenAI API to translate text while preserving HTML structure.
        """
        if not isinstance(content, str):  # ✅ Ensure content is always a string
            content = str(content)

        prompt = f"""
        You are a professional translator. Translate the following Turkish HTML content into {target_language}.
        - Preserve all HTML tags and formatting.
        - Only translate readable text within the tags.
        - Do NOT alter or remove any tags.
        - Output should be in HTML format, identical in structure to the input but translated.

        Content:
        """

        messages = [
            {"role": "system",
             "content": "You are an AI trained for preserving HTML structures while translating content."},
            {"role": "user", "content": prompt + content}
        ]

        try:
            response = self.client.chat.completions.create(  # ✅ Corrected API Call
                model=API_CONFIG['model'],
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            translated_text = response.choices[0].message.content
            return translated_text.strip()

        except openai.OpenAIError as e:  # ✅ Corrected Exception Handling
            logger.error(f"OpenAI API Error: {str(e)}")
            raise RuntimeError("Translation failed due to API error.") from e

        except Exception as e:
            logger.error(f"Unexpected Error: {str(e)}")
            raise
