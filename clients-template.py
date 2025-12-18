from google import genai
"""
This is a template for the gemini clients.

Rename this file to clients.py and replace the api key with your own.
"""

gemini_clients = [
    genai.Client(
        api_key="your-gemini-ai-studio-api-key",
    ).aio,
]
