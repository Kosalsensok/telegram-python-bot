import io
import re
import os
import logging
from PIL import Image, ImageDraw, ImageFont

import time
from typing import Dict, Any, Optional

SOLUTION_CACHE: Dict[int, Dict[str, Any]] = {}

def save_solution_cache(user_id: int, text: str, card_bytes: bytes):
    """
    Save generated solution text and card bytes in memory for inline callback actions.
    """
    SOLUTION_CACHE[user_id] = {
        "text": text,
        "card_bytes": card_bytes,
        "timestamp": time.time()
    }

def get_solution_cache(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get cached solution data for a user ID.
    """
    return SOLUTION_CACHE.get(user_id)


FONT_PATHS = [
    os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "KhmerFontBold.ttf"),
    os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "KhmerFont.ttf"),
    "C:/Windows/Fonts/LEELAWAD.TTF",
    "C:/Windows/Fonts/LEELAWDB.TTF",
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
]


def _get_font(size: int):
    """
    Tries loading available TrueType fonts with proper fallback.
    """
    for font_path in FONT_PATHS:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def clean_text_for_card(text: str) -> str:
    """
    Strips raw HTML tags, Markdown symbols, and decorative lines to clean up text for rendering.
    """
    if not text:
        return ""

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove markdown headers and emphasis
    text = re.sub(r'[*_`#~]', '', text)
    # Remove long divider lines
    text = re.sub(r'^[=\-─_]{3,}$', '', text, flags=re.MULTILINE)
    # Replace unescaped &amp; / &lt; / &gt;
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")

    return text.strip()


def extract_core_solution_lines(text: str, max_lines: int = 18) -> list:
    """
    Extracts the most relevant solution lines (Given, Steps, Proof, Final Answer)
    filtering out long verbose intro/outro fluff.
    """
    cleaned = clean_text_for_card(text)
    raw_lines = [l.strip() for l in cleaned.split("\n") if l.strip()]

    filtered_lines = []
    skip_keywords = ["វិភាគប្រធានលំហាត់", "Problem Analysis", "Technical Explanation", "ទស្សនៈបន្ថែម", "កំណត់ចំណាំ"]

    for line in raw_lines:
        if any(kw.lower() in line.lower() for kw in skip_keywords):
            continue
        filtered_lines.append(line)

    if len(filtered_lines) > max_lines:
        # Keep head (Given / Steps) and tail (Conclusion / Final answer)
        head = filtered_lines[:12]
        tail = [l for l in filtered_lines[12:] if "ដូចនេះ" in l or "=" in l or "final" in l.lower() or "answer" in l.lower() or "≅" in l]
        filtered_lines = head + (tail if tail else filtered_lines[12:max_lines])

    return filtered_lines[:max_lines]


def render_solution_card(
    solution_text: str,
    title: str = "ចម្លើយលំហាត់ (Math Solution)",
    bot_branding: str = "AI : imsela.com",
    footer_tag: str = "🎓 លំហាត់រួចរាល់ !"
) -> bytes:
    """
    Renders a pristine, high-resolution solution card PNG image (imsela.com layout style).
    Optimized with large crisp Khmer typography, soft card container, and highlighted answer box.
    """
    try:
        lines = extract_core_solution_lines(solution_text)
        if not lines:
            lines = ["1.", "គេមាន:", "MA = MD, AB = DB", "ដូចនេះ ΔABC ≅ ΔDBC (លក្ខខណ្ឌ ជ-ជ-ជ)"]

        width = 1100
        padding = 45

        # Fonts
        branding_font = _get_font(34)
        body_font = _get_font(28)
        bold_font = _get_font(30)
        footer_font = _get_font(22)

        line_height = 48
        header_height = 110
        footer_height = 70

        # Calculate exact card height
        content_lines_count = len(lines)
        total_height = header_height + (content_lines_count * line_height) + footer_height + (padding * 2) + 40
        total_height = max(total_height, 450)

        # Create White Image Canvas
        card = Image.new("RGBA", (width, total_height), (255, 255, 255, 255))
        draw = ImageDraw.Draw(card)

        # 1. Subtle Outer Border (2px)
        draw.rectangle(
            [15, 15, width - 15, total_height - 15],
            outline=(225, 230, 238),
            width=2
        )

        # 2. Header Branding Bar: "🤖 AI : imsela.com"
        draw.text((padding, padding), f"🤖  {bot_branding}", fill=(60, 64, 72), font=branding_font)
        draw.line([padding, padding + 55, width - padding, padding + 55], fill=(230, 235, 242), width=2)

        # 3. Render Solution Text Lines
        y_cursor = padding + 80

        for line in lines:
            line_str = line.strip()
            if not line_str:
                y_cursor += 15
                continue

            # Identify if this is a conclusion / final answer line
            is_conclusion = any(k in line_str for k in ["ដូចនេះ", "Final Answer", "≅", "ចម្លើយ"])
            is_section_header = line_str.startswith(("1.", "2.", "3.", "4.", "គេមាន:", "ប្រៀបធៀប", "គណនា", "ស្រាយបញ្ជាក់"))

            if is_conclusion:
                # Draw Highlighted Box for Conclusion Line
                box_top = y_cursor - 6
                box_bottom = y_cursor + line_height - 6
                draw.rectangle(
                    [padding - 10, box_top, width - padding + 10, box_bottom],
                    fill=(240, 246, 255), # Soft blue background
                    outline=(180, 210, 255), # Accent border
                    width=1
                )
                draw.text((padding + 10, y_cursor), line_str, fill=(15, 85, 195), font=bold_font)
            elif is_section_header:
                draw.text((padding, y_cursor), line_str, fill=(20, 25, 35), font=bold_font)
            else:
                draw.text((padding, y_cursor), line_str, fill=(45, 50, 60), font=body_font)

            y_cursor += line_height

        # 4. Footer Accent Bar
        footer_y = total_height - padding - 35
        draw.line([padding, footer_y - 15, width - padding, footer_y - 15], fill=(230, 235, 242), width=2)
        draw.text((padding, footer_y), footer_tag, fill=(110, 115, 125), font=footer_font)

        out = io.BytesIO()
        card.convert("RGB").save(out, format="PNG", quality=95)
        return out.getvalue()

    except Exception as e:
        logging.error(f"Error rendering solution card PNG: {e}")
        return b""
