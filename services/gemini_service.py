import asyncio
import logging
import time
import hashlib
from typing import List, Dict, Optional, Union
from google import genai
from google.genai import types as genai_types
from PIL import Image
from prompts.mode_prompts import get_prompt_for_mode

class GeminiService:
    """
    Service wrapper for Google GenAI SDK.
    Handles non-blocking asynchronous execution, concurrency rate-limiting,
    fast LRU response caching, and model fallback logic.
    """
    def __init__(self, api_key: str, primary_model: str = "gemini-flash-lite-latest", max_concurrency: int = 15):
        self.api_key = api_key
        self.primary_model = primary_model
        # Priority model list including verified working models
        self.models = list(dict.fromkeys([primary_model, "gemini-flash-lite-latest", "gemini-flash-latest", "gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-pro-latest"]))
        self.client = genai.Client(api_key=api_key)
        
        # High-concurrency semaphore to protect network sockets and prevent HTTP 429 rate limit spikes
        self._semaphore = asyncio.Semaphore(max_concurrency)
        
        # High-speed In-Memory TTL Cache (key -> (text_response, timestamp))
        self._cache: Dict[str, tuple] = {}
        self._cache_ttl = 3600  # 1 hour cache duration
        self._max_cache_size = 1000

    def update_primary_model(self, new_model: str):
        self.primary_model = new_model
        self.models = list(dict.fromkeys([new_model, "gemini-flash-lite-latest", "gemini-flash-latest", "gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-pro-latest"]))

    def _get_cache_key(self, prompt: str, mode: str = "general", history: Optional[List[Dict[str, str]]] = None) -> str:
        """Generates MD5 hash cache key for prompt, mode and last history item."""
        hist_sig = ""
        if history:
            # Include last 2 history items in signature if available
            hist_sig = "|".join([f"{h.get('role')}:{h.get('content')[:50]}" for h in history[-2:]])
        raw_str = f"{mode}:{hist_sig}:{prompt.strip()}"
        return hashlib.md5(raw_str.encode("utf-8")).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[str]:
        """Retrieves cached AI response if valid and not expired."""
        if cache_key in self._cache:
            text, ts = self._cache[cache_key]
            if time.time() - ts < self._cache_ttl:
                logging.debug(f"GeminiService: LRU Cache hit for key {cache_key[:8]}")
                return text
            else:
                del self._cache[cache_key]
        return None

    def _set_cache(self, cache_key: str, text: str):
        """Stores AI response in LRU cache with automatic pruning."""
        if len(self._cache) >= self._max_cache_size:
            # Prune oldest 20% of entries
            sorted_keys = sorted(self._cache.keys(), key=lambda k: self._cache[k][1])
            for k in sorted_keys[:self._max_cache_size // 5]:
                self._cache.pop(k, None)
        self._cache[cache_key] = (text, time.time())

    def _sync_generate_content(self, model: str, contents: list, mode: str = "general") -> str:
        """
        Synchronous internal API request call with mode system instruction.
        """
        prompt_instruction = get_prompt_for_mode(mode)
        config = genai_types.GenerateContentConfig(
            system_instruction=prompt_instruction
        ) if prompt_instruction else None
        
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
        Includes instant LRU cache lookup and concurrency rate limiting.

        :param user_prompt: Current user message string
        :param history: Prior user and model dialogue turns
        :param mode: Active operating mode key
        :return: AI response text
        """
        # 1. Fast Cache Check (<1ms response time even with zero cellular signal)
        cache_key = self._get_cache_key(user_prompt, mode, history)
        cached_response = self._get_from_cache(cache_key)
        if cached_response:
            return cached_response

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
        # 2. Acquire semaphore concurrency slot before network call
        async with self._semaphore:
            for model in self.models:
                for attempt in range(2):
                    try:
                        # Wrap synchronous SDK call in asyncio thread pool to avoid blocking event loop
                        text = await asyncio.to_thread(self._sync_generate_content, model, contents, mode)
                        if text:
                            self._set_cache(cache_key, text)
                        return text
                    except Exception as e:
                        last_exception = e
                        err_str = str(e)
                        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                            logging.warning(f"GeminiService: Model {model} rate limited. Instant failover to next model...")
                            break  # Immediately move to next fallback model
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

