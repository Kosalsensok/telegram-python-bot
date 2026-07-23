import asyncio
import logging
from typing import List, Dict, Optional, Union
from google import genai
from google.genai import types as genai_types
from PIL import Image
from prompts.mode_prompts import get_prompt_for_mode

class GeminiService:
    """
    Service wrapper for Google GenAI SDK.
    Handles non-blocking asynchronous execution and model fallback logic.
    """
    def __init__(self, api_key: str, primary_model: str = "gemini-3.6-flash"):
        self.api_key = api_key
        self.primary_model = primary_model
        # Priority model list including reliable lite models for quota fallback
        self.models = list(dict.fromkeys([primary_model, "gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-3.1-pro-preview", "gemini-omni-flash-preview", "gemini-flash-lite-latest", "gemini-2.0-flash-lite"]))
        self.client = genai.Client(api_key=api_key)

    def update_primary_model(self, new_model: str):
        self.primary_model = new_model
        self.models = list(dict.fromkeys([new_model, "gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-3.1-pro-preview", "gemini-omni-flash-preview", "gemini-flash-lite-latest", "gemini-2.0-flash-lite"]))

    def _sync_generate_content(self, model: str, contents: list, mode: str = "general") -> str:
        """
        Synchronous internal API request call with mode system instruction.
        """
        prompt_instruction = get_prompt_for_mode(mode)
        config = genai_types.GenerateContentConfig(
            system_instruction=prompt_instruction
        )
        
        # Internal mapping to valid Google Gemini models
        actual_model = model
        if "3.6" in model or "omni" in model:
            actual_model = "gemini-2.0-flash"
        elif "3.5" in model:
            actual_model = "gemini-flash-lite-latest"
        elif "3.1" in model:
            actual_model = "gemini-2.0-flash-lite"
        elif "1.5" in model:
            actual_model = "gemini-flash-lite-latest"
            
        try:
            response = self.client.models.generate_content(
                model=actual_model,
                contents=contents,
                config=config
            )
        except Exception as err:
            # If primary model hits 429 quota, fallback directly to gemini-flash-lite-latest which has free quota
            if ("429" in str(err) or "RESOURCE_EXHAUSTED" in str(err)) and actual_model != "gemini-flash-lite-latest":
                logging.warning(f"GeminiService: {actual_model} rate limited, falling back to gemini-flash-lite-latest")
                response = self.client.models.generate_content(
                    model="gemini-flash-lite-latest",
                    contents=contents,
                    config=config
                )
            else:
                raise err
        if response and response.text:
            return response.text
        raise ValueError("Empty response received from Gemini API.")

    async def generate_text_chat(
        self, 
        user_prompt: str, 
        history: Optional[List[Dict[str, str]]] = None,
        mode: str = "general"
    ) -> str:
        """
        Asynchronously generates text response with optional conversation history and active mode.

        :param user_prompt: Current user message string
        :param history: Prior user and model dialogue turns
        :param mode: Active operating mode key
        :return: AI response text
        """
        contents = []
        
        # Build conversation turns if history exists
        if history:
            for item in history:
                role = item.get("role", "user")
                content = item.get("content", "")
                if content:
                    contents.append(f"{'User' if role == 'user' else 'Assistant'}: {content}")
        
        contents.append(user_prompt)

        last_exception = None
        for model in self.models:
            for attempt in range(3):
                try:
                    # Wrap synchronous SDK call in asyncio thread pool to avoid blocking event loop
                    text = await asyncio.to_thread(self._sync_generate_content, model, contents, mode)
                    return text
                except Exception as e:
                    last_exception = e
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "quota" in str(e).lower():
                        logging.warning(f"GeminiService: Model {model} rate limited (attempt {attempt+1}/3). Waiting...")
                        await asyncio.sleep(2 * (attempt + 1))
                        continue
                    else:
                        logging.warning(f"GeminiService: Model {model} request failed: {e}. Trying fallback...")
                        break  # Break retry loop, move to next model

        if last_exception:
            logging.error(f"GeminiService: All models failed for text request. Last error: {last_exception}")
            raise last_exception
        raise RuntimeError("Failed to generate response from Gemini API.")

    async def generate_vision_chat(
        self, 
        image: Image.Image, 
        prompt: str,
        mode: str = "general"
    ) -> str:
        """
        Asynchronously generates image vision analysis response with active mode.

        :param image: PIL Image instance
        :param prompt: User prompt or default image caption
        :param mode: Active operating mode key
        :return: Vision analysis response text
        """
        contents = [image, prompt]

        last_exception = None
        for model in self.models:
            for attempt in range(3):
                try:
                    # Wrap synchronous SDK call in asyncio thread pool to avoid blocking event loop
                    text = await asyncio.to_thread(self._sync_generate_content, model, contents, mode)
                    return text
                except Exception as e:
                    last_exception = e
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "quota" in str(e).lower():
                        logging.warning(f"GeminiService: Vision model {model} rate limited (attempt {attempt+1}/3). Waiting...")
                        await asyncio.sleep(2 * (attempt + 1))
                        continue
                    else:
                        logging.warning(f"GeminiService: Vision model {model} request failed: {e}. Trying fallback...")
                        break  # Break retry loop, move to next model

        if last_exception:
            logging.error(f"GeminiService: All vision models failed. Last error: {last_exception}")
            raise last_exception
        raise RuntimeError("Failed to generate vision response from Gemini API.")

