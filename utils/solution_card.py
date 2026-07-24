import io
import re
import os
import json
import secrets
import logging
import subprocess
import tempfile
import time
from typing import Dict, Any, Optional, List

from utils.response_router import (
    parse_ai_structured_response,
    clean_broken_characters,
    format_telegram_html
)

# Global Solution Cache with TTL (24 Hours)
SOLUTION_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 86400  # 24 hours


def generate_short_solution_id() -> str:
    """Generates a secure 8-character random hex string solution ID."""
    return secrets.token_hex(4)


def save_solution_cache(
    solution_id: str,
    raw_text: str,
    parsed_data: Dict[str, Any],
    telegram_user_id: Optional[int] = None,
    chat_id: Optional[int] = None,
    code_files: Optional[List[Dict[str, str]]] = None,
    card_bytes: Optional[bytes] = None
) -> str:
    """
    Saves structured solution response data in memory cache indexed by short solution_id.
    Prevents callback_data overflow (Telegram 64-byte limit).
    """
    now = time.time()
    SOLUTION_CACHE[solution_id] = {
        "solutionId": solution_id,
        "telegramUserId": telegram_user_id,
        "chatId": chat_id,
        "raw_text": raw_text,
        "data": parsed_data,
        "responseType": parsed_data.get("response_type", "general_answer"),
        "title": parsed_data.get("title", "Smart AI Solution"),
        "code_files": code_files or [],
        "card_bytes": card_bytes,
        "pdf_bytes": None,
        "createdAt": now,
        "expiresAt": now + CACHE_TTL_SECONDS
    }

    # Clean expired records
    cleanup_expired_solution_cache()
    return solution_id


def get_solution_cache(solution_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves cached solution record by short solution_id."""
    clean_id = str(solution_id).strip()
    record = SOLUTION_CACHE.get(clean_id)
    if not record:
        return None
    if time.time() > record.get("expiresAt", 0):
        SOLUTION_CACHE.pop(clean_id, None)
        return None
    return record


def cleanup_expired_solution_cache():
    """Removes expired solution records from cache memory."""
    now = time.time()
    expired_keys = [k for k, v in SOLUTION_CACHE.items() if v.get("expiresAt", 0) < now]
    for k in expired_keys:
        SOLUTION_CACHE.pop(k, None)


def render_solution_card(
    solution_text: str,
    bot_branding: str = "Smart AI Assistant",
    bot_username: str = "@mysmart_v2_2026_bot",
    parsed_data: Optional[Dict[str, Any]] = None
) -> Optional[bytes]:
    """
    Renders HD PNG Answer Card via Playwright HTML Renderer (dist/renderer/cli_render.js).
    Form A Vertical Stepper layout with local KaTeX & fonts.
    """
    data = parsed_data or parse_ai_structured_response(solution_text)

    temp_dir = tempfile.gettempdir()
    ts = int(time.time() * 1000)
    payload_file = os.path.join(temp_dir, f"sol_input_{ts}_{secrets.token_hex(2)}.json")
    output_png = os.path.join(temp_dir, f"sol_output_{ts}_{secrets.token_hex(2)}.png")

    try:
        with open(payload_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

        cli_js = os.path.join(os.path.dirname(__file__), "..", "dist", "renderer", "cli_render.js")
        if os.path.exists(cli_js):
            res = subprocess.run(
                ["node", cli_js, payload_file, output_png, "png"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if res.returncode == 0 and os.path.exists(output_png):
                with open(output_png, "rb") as f:
                    png_bytes = f.read()
                return png_bytes
            else:
                logging.warning(f"cli_render.js PNG render failed: {res.stderr}")
    except Exception as e:
        logging.error(f"Error rendering solution card via Playwright CLI: {e}")
    finally:
        for p in [payload_file, output_png]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

    return _fallback_pil_solution_card(data)


def render_solution_pdf(
    solution_text: str,
    bot_branding: str = "Smart AI Assistant",
    bot_username: str = "@mysmart_v2_2026_bot",
    parsed_data: Optional[Dict[str, Any]] = None
) -> Optional[bytes]:
    """
    Renders A4 Printable PDF Document via Playwright HTML Renderer.
    """
    data = parsed_data or parse_ai_structured_response(solution_text)

    temp_dir = tempfile.gettempdir()
    ts = int(time.time() * 1000)
    payload_file = os.path.join(temp_dir, f"sol_pdf_input_{ts}_{secrets.token_hex(2)}.json")
    output_pdf = os.path.join(temp_dir, f"sol_output_{ts}_{secrets.token_hex(2)}.pdf")

    try:
        with open(payload_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

        cli_js = os.path.join(os.path.dirname(__file__), "..", "dist", "renderer", "cli_render.js")
        if os.path.exists(cli_js):
            res = subprocess.run(
                ["node", cli_js, payload_file, output_pdf, "pdf"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if res.returncode == 0 and os.path.exists(output_pdf):
                with open(output_pdf, "rb") as f:
                    pdf_bytes = f.read()
                return pdf_bytes
            else:
                logging.warning(f"cli_render.js PDF render failed: {res.stderr}")
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
    if parsed_data.get("summary") or parsed_data.get("summary_km"):
        lines.append(clean_broken_characters(parsed_data.get("summary_km") or parsed_data.get("summary") or ""))

    for kv in parsed_data.get("key_values", []):
        lines.append(f"• {clean_broken_characters(kv.get('label',''))}: {clean_broken_characters(kv.get('value',''))}")

    for sec in parsed_data.get("sections", []):
        heading = sec.get("heading_km") or sec.get("heading") or "Section"
        content = sec.get("content_km") or sec.get("content") or ""
        lines.append(f"[{clean_broken_characters(heading)}]")
        for sub_line in clean_broken_characters(content).split("\n"):
            if sub_line.strip():
                lines.append(sub_line.strip())

    font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "KhmerFont.ttf")
    try:
        font = ImageFont.truetype(font_path, 24)
    except Exception:
        font = ImageFont.load_default()

    line_height = 42
    total_height = max(500, padding * 2 + len(lines) * line_height + 60)

    card = Image.new("RGB", (width, total_height), (15, 23, 42))
    draw = ImageDraw.Draw(card)

    draw.rectangle([10, 10, width - 10, total_height - 10], outline=(56, 189, 248), width=2)
    y = padding + 20
    for l in lines[:30]:
        draw.text((padding, y), l[:75], fill=(248, 250, 252), font=font)
        y += line_height

    out = io.BytesIO()
    card.save(out, format="PNG")
    return out.getvalue()
