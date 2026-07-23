import io
import time
import aiohttp
import random
import urllib.parse
import logging
from typing import Optional, Tuple, Dict, Any
from PIL import Image
from services.gemini_service import GeminiService

# In-memory image cache to store generated images for instant JPG/PNG download & ratio change
IMAGE_CACHE: Dict[str, Dict[str, Any]] = {}
MAX_IMAGE_CACHE_SIZE = 100

ASPECT_RATIOS: Dict[str, Tuple[int, int, str]] = {
    "1:1": (1024, 1024, "📐 1:1 (Square - 1024x1024)"),
    "16:9": (1280, 720, "🖼 16:9 (Landscape - 1280x720)"),
    "9:16": (720, 1280, "📱 9:16 (Portrait - 720x1280)"),
    "4:3": (1024, 768, "🖥 4:3 (Desktop - 1024x768)"),
    "3:4": (768, 1024, "📸 3:4 (Photo - 768x1024)")
}


def convert_to_png(image_bytes: bytes) -> bytes:
    """
    Converts raw image bytes to lossless uncompressed PNG format using PIL.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        out = io.BytesIO()
        img.save(out, format="PNG", optimize=True)
        return out.getvalue()
    except Exception as e:
        logging.error(f"Error converting image to PNG: {e}")
        return image_bytes


def convert_to_jpg(image_bytes: bytes) -> bytes:
    """
    Converts raw image bytes to maximum quality JPEG format using PIL.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        out = io.BytesIO()
        img.save(out, format="JPEG", quality=95, optimize=True)
        return out.getvalue()
    except Exception as e:
        logging.error(f"Error converting image to JPG: {e}")
        return image_bytes


def enhance_image_hd(image_bytes: bytes, sharpness_factor: float = 2.2, contrast_factor: float = 1.15) -> bytes:
    """
    Enhances blurry or low-res images using Lanczos 2x super-resolution,
    Unsharp Masking, Detail Filter, and PIL ImageEnhance contrast & sharpness tuning.
    Returns crystal clear high-definition JPEG bytes.
    """
    try:
        from PIL import ImageEnhance, ImageFilter
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode != "RGB":
            img = img.convert("RGB")

        # 1. Lanczos 2x Super-Resolution Upscaling
        width, height = img.size
        new_width = max(width * 2, 1024)
        new_height = max(height * 2, 1024)
        
        # Cap max resolution to 4096 to prevent memory overflow
        if new_width > 4096 or new_height > 4096:
            scale = min(4096 / new_width, 4096 / new_height)
            new_width = int(new_width * scale)
            new_height = int(new_height * scale)

        upscaled = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 2. Unsharp Mask & Detail Filter Enhancement
        sharpened = upscaled.filter(ImageFilter.UnsharpMask(radius=2, percent=180, threshold=3))
        detailed = sharpened.filter(ImageFilter.DETAIL)

        # 3. Tune Sharpness, Contrast & Color Vibrance
        enhancer_sharp = ImageEnhance.Sharpness(detailed)
        img_sharp = enhancer_sharp.enhance(sharpness_factor)

        enhancer_contrast = ImageEnhance.Contrast(img_sharp)
        img_contrast = enhancer_contrast.enhance(contrast_factor)

        enhancer_color = ImageEnhance.Color(img_contrast)
        final_img = enhancer_color.enhance(1.08)

        output = io.BytesIO()
        final_img.save(output, format="JPEG", quality=95, optimize=True)
        return output.getvalue()
    except Exception as e:
        logging.error(f"Error in enhance_image_hd: {e}")
        return image_bytes


def get_cached_image(cache_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve cached image metadata by cache ID.
    """
    return IMAGE_CACHE.get(cache_id)


def parse_aspect_ratio(prompt: str) -> Tuple[str, int, int, str]:
    """
    Parses user prompt for aspect ratio parameters like 16:9, 9:16, 1:1, 4:3.
    Returns: (ratio_key, width, height, clean_prompt)
    """
    prompt_lower = prompt.lower().strip()
    clean_prompt = prompt.strip()

    for ratio_key, (w, h, desc) in ASPECT_RATIOS.items():
        if f"--{ratio_key}" in prompt_lower or f"ratio {ratio_key}" in prompt_lower:
            clean = prompt_lower.replace(f"--{ratio_key}", "").replace(f"ratio {ratio_key}", "").strip()
            return ratio_key, w, h, clean if clean else prompt
        elif ratio_key in prompt_lower.split():
            words = prompt.split()
            words_clean = [w for w in words if w.lower() != ratio_key]
            clean = " ".join(words_clean).strip()
            return ratio_key, w, h, clean if clean else prompt

    return "1:1", 1024, 1024, clean_prompt


class ImageGenService:
    """
    High-definition, unlimited AI Image Generator using Pollinations AI (Flux HD models)
    with Gemini AI prompt optimization, aspect ratio control, and multi-format export.
    """
    def __init__(self, gemini_service: Optional[GeminiService] = None):
        self.gemini_service = gemini_service

    async def optimize_prompt(self, raw_prompt: str) -> str:
        """
        Translates Khmer prompts and enhances raw prompts into vivid, detailed English image generation prompts.
        """
        if not raw_prompt or not raw_prompt.strip():
            return "stunning ultra-sharp masterpiece, 8k resolution, cinematic studio lighting, photorealistic, 4k ultra-hd"

        if not self.gemini_service:
            return f"{raw_prompt.strip()}, 8k resolution, ultra-sharp focus, masterpiece, photorealistic, intricate detail"

        enhancement_instruction = (
            "You are an expert AI prompt engineer for ultra high quality image generation.\n"
            "Translate any Khmer or foreign text into vivid, detailed English.\n"
            "Enhance the description with high quality keywords (e.g. 8k resolution, ultra-sharp focus, cinematic lighting, masterpiece, hyper-realistic, 4k ultra-hd, professional photography, highly detailed texture).\n"
            "Output ONLY the final English prompt string, nothing else. No markdown, no quotes."
        )

        try:
            enhanced = await self.gemini_service.generate_text_chat(
                user_prompt=f"{enhancement_instruction}\n\nUser Prompt: {raw_prompt}",
                mode="general"
            )
            clean_prompt = enhanced.strip().strip('"\'`')
            return clean_prompt if clean_prompt else f"{raw_prompt.strip()}, 8k resolution, ultra-sharp focus, masterpiece"
        except Exception as e:
            logging.warning(f"Failed to optimize prompt with Gemini: {e}")
            return f"{raw_prompt.strip()}, 8k resolution, ultra-sharp focus, masterpiece"

    async def generate_image(
        self, 
        prompt: str, 
        width: int = 1024, 
        height: int = 1024, 
        model: str = "flux"
    ) -> Tuple[Optional[bytes], str, int, str]:
        """
        Fetches generated HD image bytes from Pollinations AI.
        Returns: (image_bytes, optimized_prompt, seed, cache_id)
        """
        optimized_prompt = await self.optimize_prompt(prompt)
        seed = random.randint(1, 2147483647)
        encoded_prompt = urllib.parse.quote(optimized_prompt)

        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&model={model}&nologo=true"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        image_bytes = None
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, timeout=45) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        if len(data) > 5000:
                            image_bytes = data
                    else:
                        logging.warning(f"Pollinations primary model '{model}' returned status {resp.status}. Trying fallback model...")

            if not image_bytes:
                fallback_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&model=turbo&nologo=true"
                async with aiohttp.ClientSession(headers=headers) as session:
                    async with session.get(fallback_url, timeout=30) as resp:
                        if resp.status == 200:
                            data = await resp.read()
                            if len(data) > 5000:
                                image_bytes = data
        except Exception as e:
            logging.error(f"Error fetching generated image from Pollinations AI: {e}")

        cache_id = f"img_{seed}_{int(time.time())}"
        if image_bytes:
            if len(IMAGE_CACHE) >= MAX_IMAGE_CACHE_SIZE:
                first_key = next(iter(IMAGE_CACHE))
                IMAGE_CACHE.pop(first_key, None)
            IMAGE_CACHE[cache_id] = {
                "bytes": image_bytes,
                "prompt": prompt,
                "optimized_prompt": optimized_prompt,
                "seed": seed,
                "width": width,
                "height": height,
                "model": model
            }

        return image_bytes, optimized_prompt, seed, cache_id
