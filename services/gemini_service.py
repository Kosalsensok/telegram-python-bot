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
        # Priority model list including verified working models
        self.models = list(dict.fromkeys([primary_model, "gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-flash-latest", "gemini-flash-lite-latest"]))
        self.client = genai.Client(api_key=api_key)

    def update_primary_model(self, new_model: str):
        self.primary_model = new_model
        self.models = list(dict.fromkeys([new_model, "gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-flash-latest", "gemini-flash-lite-latest"]))

    def _sync_generate_content(self, model: str, contents: list, mode: str = "general") -> str:
        """
        Synchronous internal API request call with mode system instruction.
        """
        prompt_instruction = get_prompt_for_mode(mode)
        config = genai_types.GenerateContentConfig(
            system_instruction=prompt_instruction
        )
        
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )
        except Exception as err:
            err_str = str(err)
            if ("429" in err_str or "503" in err_str or "404" in err_str or "RESOURCE_EXHAUSTED" in err_str or "UNAVAILABLE" in err_str or "NOT_FOUND" in err_str) and model != "gemini-flash-lite-latest":
                logging.warning(f"GeminiService: {model} issue ({err_str[:80]}), falling back to gemini-flash-lite-latest")
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

    async def generate_document_chat(
        self,
        file_bytes: bytes,
        mime_type: str,
        prompt: str,
        mode: str = "general"
    ) -> str:
        """
        Asynchronously processes binary document parts (e.g. PDF files or uncompressed images).
        """
        doc_part = genai_types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
        contents = [doc_part, prompt]

        last_exception = None
        for model in self.models:
            for attempt in range(3):
                try:
                    text = await asyncio.to_thread(self._sync_generate_content, model, contents, mode)
                    return text
                except Exception as e:
                    last_exception = e
                    err_str = str(e)
                    if "429" in err_str or "503" in err_str or "404" in err_str or "RESOURCE_EXHAUSTED" in err_str or "UNAVAILABLE" in err_str:
                        logging.warning(f"GeminiService: Document model {model} issue (attempt {attempt+1}/3). Waiting...")
                        await asyncio.sleep(2 * (attempt + 1))
                        continue
                    else:
                        logging.warning(f"GeminiService: Document model {model} failed: {e}. Trying fallback...")
                        break

        if last_exception:
            logging.error(f"GeminiService: All document models failed. Last error: {last_exception}")
            raise last_exception
        raise RuntimeError("Failed to generate document response from Gemini API.")

    async def generate_audio_chat(
        self,
        file_bytes: bytes,
        mime_type: str = "audio/ogg",
        prompt: str = "សូមស្តាប់សំឡេងនេះ ឆ្លើយតប និងពន្យល់ខ្លឹមសារជាភាសាខ្មែរ/អង់គ្លេសឱ្យបានច្បាស់លាស់។",
        mode: str = "general"
    ) -> str:
        """
        Asynchronously processes audio voice notes using GenAI Part.
        """
        audio_part = genai_types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
        contents = [audio_part, prompt]

        last_exception = None
        for model in self.models:
            for attempt in range(3):
                try:
                    text = await asyncio.to_thread(self._sync_generate_content, model, contents, mode)
                    return text
                except Exception as e:
                    last_exception = e
                    err_str = str(e)
                    if "429" in err_str or "503" in err_str or "404" in err_str or "RESOURCE_EXHAUSTED" in err_str or "UNAVAILABLE" in err_str:
                        logging.warning(f"GeminiService: Audio model {model} issue (attempt {attempt+1}/3). Waiting...")
                        await asyncio.sleep(2 * (attempt + 1))
                        continue
                    else:
                        logging.warning(f"GeminiService: Audio model {model} failed: {e}. Trying fallback...")
                        break

        if last_exception:
            logging.error(f"GeminiService: All audio models failed. Last error: {last_exception}")
            raise last_exception
        raise RuntimeError("Failed to generate audio response from Gemini API.")

