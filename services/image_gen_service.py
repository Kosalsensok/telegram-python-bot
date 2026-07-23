import aiohttp
import random
import urllib.parse
import logging
from typing import Optional, Tuple
from services.gemini_service import GeminiService

class ImageGenService:
    """
    High-definition, unlimited AI Image Generator using Pollinations AI (Flux & Turbo models)
    with Gemini AI prompt optimization for Khmer & English inputs.
    """
    def __init__(self, gemini_service: Optional[GeminiService] = None):
        self.gemini_service = gemini_service

    async def optimize_prompt(self, raw_prompt: str) -> str:
        """
        Translates Khmer prompts and enhances raw prompts into detailed English image generation prompts.
        """
        if not raw_prompt or not raw_prompt.strip():
            return "stunning ultra-realistic masterpiece, 8k resolution, cinematic lighting"

        if not self.gemini_service:
            return raw_prompt.strip()

        enhancement_instruction = (
            "You are an expert AI prompt engineer for high quality image generation.\n"
            "Translate any Khmer or foreign text into vivid, detailed English.\n"
            "Enhance the description with high quality keywords (e.g. 8k resolution, cinematic lighting, masterpiece, hyper-realistic, detailed texture).\n"
            "Output ONLY the final English prompt string, nothing else. No markdown, no quotes."
        )

        try:
            enhanced = await self.gemini_service.generate_text(
                prompt=f"{enhancement_instruction}\n\nUser Prompt: {raw_prompt}",
                temperature=0.7
            )
            clean_prompt = enhanced.strip().strip('"\'`')
            return clean_prompt if clean_prompt else raw_prompt
        except Exception as e:
            logging.warning(f"Failed to optimize prompt with Gemini: {e}")
            return raw_prompt.strip()

    async def generate_image(self, prompt: str, width: int = 1024, height: int = 1024, model: str = "flux") -> Tuple[Optional[bytes], str, int]:
        """
        Fetches generated HD image bytes from Pollinations AI.
        Returns: (image_bytes, optimized_prompt, seed)
        """
        optimized_prompt = await self.optimize_prompt(prompt)
        seed = random.randint(1, 2147483647)
        encoded_prompt = urllib.parse.quote(optimized_prompt)

        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&model={model}&nologo=true"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, timeout=45) as resp:
                    if resp.status == 200:
                        image_bytes = await resp.read()
                        if len(image_bytes) > 5000:
                            return image_bytes, optimized_prompt, seed
                    logging.warning(f"Pollinations primary model '{model}' returned status {resp.status}. Trying fallback model...")

            fallback_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&model=turbo&nologo=true"
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(fallback_url, timeout=30) as resp:
                    if resp.status == 200:
                        image_bytes = await resp.read()
                        if len(image_bytes) > 5000:
                            return image_bytes, optimized_prompt, seed
        except Exception as e:
            logging.error(f"Error fetching generated image from Pollinations AI: {e}")

        return None, optimized_prompt, seed
