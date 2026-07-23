import io
import logging
from PIL import Image

def process_image_bytes(image_bytes: bytes, max_size_mb: int = 10) -> Image.Image:
    """
    Validates, opens, and converts raw image bytes to a PIL RGB Image.

    :param image_bytes: Raw bytes downloaded from Telegram
    :param max_size_mb: Maximum allowed image size in megabytes
    :return: PIL Image in RGB format
    :raises ValueError: If image size exceeds limit or format is invalid
    """
    size_mb = len(image_bytes) / (1024 * 1024)
    if size_mb > max_size_mb:
        raise ValueError(f"Image size ({size_mb:.2f} MB) exceeds maximum allowed limit ({max_size_mb} MB).")

    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()  # Validate image integrity
        
        # Re-open after verify() because verify() alters file offset/state
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert image modes like RGBA or P to RGB for Gemini AI compatibility
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        return image
    except Exception as e:
        logging.error(f"Image processing error: {e}")
        raise ValueError("Invalid or corrupted image file.")
