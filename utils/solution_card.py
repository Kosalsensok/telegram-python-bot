import io
import re
import os
import json
import logging
import subprocess
import tempfile
import time
from typing import Dict, Any, Optional

from utils.response_router import (
    parse_ai_structured_response,
    clean_broken_characters,
    format_telegram_html
)

SOLUTION_CACHE: Dict[str, Dict[str, Any]] = {}


def save_solution_cache(solution_id: str, raw_text: str, parsed_data: Dict[str, Any], card_bytes: Optional[bytes] = None):
    """
    Saves solution text, parsed data structure, and card bytes in memory.
    """
    SOLUTION_CACHE[solution_id] = {
        "raw_text": raw_text,
        "data": parsed_data,
        "card_bytes": card_bytes,
        "timestamp": time.time()
    }


def get_solution_cache(solution_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves cached solution data by solution_id or user_id string.
    """
    return SOLUTION_CACHE.get(str(solution_id))


def render_solution_card(
    solution_text: str,
    bot_branding: str = "Smart AI Assistant",
    bot_username: str = "@mysmart_v2_2026_bot"
) -> Optional[bytes]:
    """
    Renders dynamic-height Solution Card PNG via Playwright HTML Renderer (dist/renderer/cli_render.js).
    """
    parsed_data = parse_ai_structured_response(solution_text)

    # Prepare temporary payload JSON file
    temp_dir = tempfile.gettempdir()
    payload_file = os.path.join(temp_dir, f"sol_input_{int(time.time()*1000)}.json")
    output_png = os.path.join(temp_dir, f"sol_output_{int(time.time()*1000)}.png")

    try:
        with open(payload_file, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, ensure_ascii=False)

        cli_js = os.path.join(os.path.dirname(__file__), "..", "dist", "renderer", "cli_render.js")
        if os.path.exists(cli_js):
            res = subprocess.run(
                ["node", cli_js, payload_file, output_png, "png"],
                capture_output=True,
                text=True,
                timeout=25
            )
            if res.returncode == 0 and os.path.exists(output_png):
                with open(output_png, "rb") as f:
                    png_bytes = f.read()
                return png_bytes
            else:
                logging.warning(f"cli_render.js failed: {res.stderr}")
    except Exception as e:
        logging.error(f"Error rendering solution card via Playwright CLI: {e}")
    finally:
        for p in [payload_file, output_png]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

    return _fallback_pil_solution_card(parsed_data)


def render_solution_pdf(
    solution_text: str,
    bot_branding: str = "Smart AI Assistant",
    bot_username: str = "@mysmart_v2_2026_bot"
) -> Optional[bytes]:
    """
    Renders printable Solution Card PDF via Playwright HTML Renderer.
    """
    parsed_data = parse_ai_structured_response(solution_text)

    temp_dir = tempfile.gettempdir()
    payload_file = os.path.join(temp_dir, f"sol_pdf_input_{int(time.time()*1000)}.json")
    output_pdf = os.path.join(temp_dir, f"sol_output_{int(time.time()*1000)}.pdf")

    try:
        with open(payload_file, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, ensure_ascii=False)

        cli_js = os.path.join(os.path.dirname(__file__), "..", "dist", "renderer", "cli_render.js")
        if os.path.exists(cli_js):
            res = subprocess.run(
                ["node", cli_js, payload_file, output_pdf, "pdf"],
                capture_output=True,
                text=True,
                timeout=25
            )
            if res.returncode == 0 and os.path.exists(output_pdf):
                with open(output_pdf, "rb") as f:
                    pdf_bytes = f.read()
                return pdf_bytes
    except Exception as e:
        logging.error(f"Error rendering PDF via Playwright CLI: {e}")
    finally:
        for p in [payload_file, output_pdf]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

    return None


def _fallback_pil_solution_card(parsed_data: Dict[str, Any]) -> bytes:
    """
    Emergency PIL fallback generator.
    """
    from PIL import Image, ImageDraw, ImageFont

    width = 960
    padding = 40
    lines = [clean_broken_characters(parsed_data.get("title", "Solution Card"))]
    if parsed_data.get("summary"):
        lines.append(clean_broken_characters(parsed_data["summary"]))

    for kv in parsed_data.get("key_values", []):
        lines.append(f"• {clean_broken_characters(kv.get('label',''))}: {clean_broken_characters(kv.get('value',''))}")

    for sec in parsed_data.get("sections", []):
        lines.append(f"[{clean_broken_characters(sec.get('heading',''))}]")
        for sub_line in clean_broken_characters(sec.get("content","")).split("\n"):
            if sub_line.strip():
                lines.append(sub_line.strip())

    font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "KhmerFont.ttf")
    try:
        font = ImageFont.truetype(font_path, 24)
    except Exception:
        font = ImageFont.load_default()

    line_height = 42
    total_height = max(500, padding * 2 + len(lines) * line_height + 60)

    card = Image.new("RGB", (width, total_height), (255, 255, 255))
    draw = ImageDraw.Draw(card)

    draw.rectangle([10, 10, width - 10, total_height - 10], outline=(220, 225, 235), width=2)
    y = padding + 20
    for l in lines[:25]:
        draw.text((padding, y), l[:75], fill=(23, 32, 51), font=font)
        y += line_height

    out = io.BytesIO()
    card.save(out, format="PNG")
    return out.getvalue()
