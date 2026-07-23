import json
import re
import html
import logging
from typing import Dict, Any, List, Optional, Tuple

RESPONSE_TYPES = [
    "mathematics",
    "chemistry",
    "physics",
    "email",
    "document",
    "table",
    "general_image"
]


def contains_broken_characters(text: str) -> bool:
    """
    Checks for broken square characters, replacement glyphs, or invalid unicode symbols.
    - U+25A1: □
    - U+FFFD: 
    - Other invalid box glyphs
    """
    if not text:
        return False
    broken_patterns = [
        "\u25a1",  # □
        "\ufffd",  # 
        "\u25a0",  # ■
        "\u25a2",  # ▢
        "\u25a3",  # ▣
        "\u25a4",  # ▤
        "\u25a5",  # ▥
    ]
    return any(p in text for p in broken_patterns)


def clean_broken_characters(text: str) -> str:
    """
    Sanitizes broken characters and replaces bullet boxes with clean bullet points or removes replacement glyphs.
    """
    if not text:
        return ""
    # Normalize unicode to NFC
    import unicodedata
    text = unicodedata.normalize("NFC", text)

    # Replace broken box symbols with clean bullet points or spaces
    text = re.sub(r'[\u25A1\u25A0\u25A2\u25A3\u25A4\u25A5]', '•', text)
    text = text.replace('\ufffd', '')

    # Fix repetitive bullet markers
    text = re.sub(r'•\s*•+', '•', text)
    return text.strip()


def detect_response_type_from_text(text: str, user_prompt: str = "") -> str:
    """
    Fall-back rule-based classifier if AI returns free-form text instead of JSON.
    """
    combined = (text + " " + user_prompt).lower()

    # Email / Payment detection
    email_keywords = [
        "email", "e-mail", "stripe", "payment", "invoice", "unsuccessful", "charged",
        "visa ending", "card ending", "subscription", "sender", "recipient", "subject",
        "អ៊ីមែល", "ការបង់ប្រាក់", "បង់ប្រាក់", "ប្រធានបទ", "អ្នកផ្ញើ"
    ]
    if any(k in combined for k in email_keywords):
        return "email"

    # Math / Scientific detection
    math_keywords = [
        "\\frac", "\\sqrt", "equation", "solve", "proof", "∫", "∑", "lim",
        "លំហាត់", "សមីការ", "គណនា", "ស្រាយបញ្ជាក់", "រកតម្លៃ", "តម្លៃនៃ", "អនុគមន៍", "ដេរីវេ"
    ]
    if any(k in combined for k in math_keywords) or re.search(r'\\[a-zA-Z]+|\$\$?.*?\$\$?', text):
        return "mathematics"

    # Chemistry detection
    chem_keywords = ["h2o", "co2", "reaction", "molecule", "chemical", "ប្រតិកម្ម", "គីមី"]
    if any(k in combined for k in chem_keywords):
        return "chemistry"

    # Physics detection
    physics_keywords = ["velocity", "force", "acceleration", "joule", "watt", "ល្បឿន", "កម្លាំង", "រូបវិទ្យា"]
    if any(k in combined for k in physics_keywords):
        return "physics"

    # Table detection
    if "<table>" in combined or ("|" in text and text.count("|") > 4):
        return "table"

    # Document / PDF text
    doc_keywords = ["document", "pdf", "page", "article", "សៀវភៅ", "ឯកសារ", "អត្ថបទ"]
    if any(k in combined for k in doc_keywords):
        return "document"

    return "general_image"


def parse_ai_structured_response(raw_text: str, default_prompt: str = "") -> Dict[str, Any]:
    """
    Parses raw AI response into structured JSON schema.
    If raw AI response is valid JSON, extracts fields.
    Otherwise, builds structured dictionary using intelligent extraction.
    """
    cleaned_raw = clean_broken_characters(raw_text)

    # Try JSON extraction
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned_raw, re.DOTALL)
    json_str = json_match.group(1) if json_match else cleaned_raw.strip()

    parsed = None
    if json_str.startswith("{") and json_str.endswith("}"):
        try:
            parsed = json.loads(json_str)
        except Exception:
            parsed = None

    if parsed and isinstance(parsed, dict) and "sections" in parsed:
        res_type = parsed.get("response_type", "general_image")
        if res_type not in RESPONSE_TYPES:
            res_type = detect_response_type_from_text(cleaned_raw, default_prompt)
        parsed["response_type"] = res_type
        return parsed

    # Fallback: Extract title, summary, sections manually
    res_type = detect_response_type_from_text(cleaned_raw, default_prompt)
    lines = [l.strip() for l in cleaned_raw.split("\n") if l.strip()]

    title = lines[0] if lines else "ការវិភាគរូបភាព (Image Analysis)"
    if len(title) > 80:
        title = title[:80] + "..."

    summary = ""
    sections = []
    key_values = []
    warnings = []
    recommendations = []
    current_heading = "ព័ត៌មានលម្អិត"
    current_content_lines = []

    for line in lines[1:]:
        # Key value detection (e.g. "Key: Value" or "• Key: Value")
        kv_match = re.match(r'^(?:[•\-*]\s*)?([^:\n]{2,35}):\s*(.+)$', line)
        if kv_match:
            lbl = kv_match.group(1).strip()
            val = kv_match.group(2).strip()
            if any(w in lbl.lower() for w in ["warning", "caution", "ប្រុងប្រយ័ត្ន"]):
                warnings.append(val)
            elif any(r in lbl.lower() for r in ["recommendation", "suggest", "អនុសាសន៍"]):
                recommendations.append(val)
            else:
                key_values.append({"label": lbl, "value": val})
            continue

        if line.startswith(("#", "==", "**", "1.", "2.", "3.", "---")):
            if current_content_lines:
                sections.append({
                    "heading": current_heading,
                    "content": "\n".join(current_content_lines)
                })
                current_content_lines = []
            current_heading = re.sub(r'[*_#=\-]', '', line).strip()
        else:
            if not summary and len(line) > 20:
                summary = line
            else:
                current_content_lines.append(line)

    if current_content_lines:
        sections.append({
            "heading": current_heading,
            "content": "\n".join(current_content_lines)
        })

    if not sections and not key_values:
        sections.append({
            "heading": "ខ្លឹមសារ",
            "content": cleaned_raw
        })

    return {
        "response_type": res_type,
        "language": "km",
        "title": title,
        "summary": summary or title,
        "sections": sections,
        "key_values": key_values,
        "warnings": warnings,
        "recommendations": recommendations,
        "math_expressions": []
    }


def format_telegram_html(data: Dict[str, Any]) -> str:
    """
    Formats structured solution response into clean, safe Telegram HTML text message.
    Escapes HTML entities to avoid parse errors.
    """
    res_type = data.get("response_type", "general_image")
    title = html.escape(clean_broken_characters(data.get("title", "")))
    summary = html.escape(clean_broken_characters(data.get("summary", "")))

    header_icons = {
        "email": "📧 <b>ការវិភាគអ៊ីមែល / Email Analysis</b>",
        "document": "📄 <b>ការវិភាគឯកសារ / Document Analysis</b>",
        "table": "📊 <b>ការវិភាគតារាង / Table Extraction</b>",
        "mathematics": "🎓 <b>ចម្លើយលំហាត់គណិតវិទ្យា / Math Solution</b>",
        "chemistry": "🧪 <b>ការវិភាគគីមីវិទ្យា / Chemistry Solution</b>",
        "physics": "⚡ <b>ការវិភាគរូបវិទ្យា / Physics Solution</b>",
        "general_image": "🖼 <b>ការវិភាគរូបភាព / Image Analysis</b>"
    }

    header_str = header_icons.get(res_type, "🖼 <b>ការវិភាគរូបភាព (Image Analysis)</b>")
    parts = [header_str]

    if title:
        parts.append(f"\n<b>📌 {title}</b>")

    if summary:
        parts.append(f"\n<b>សេចក្តីសង្ខេប</b>\n{summary}")

    key_values = data.get("key_values", [])
    if key_values:
        kv_lines = ["\n<b>ព័ត៌មានសំខាន់ (Key Info)</b>"]
        for kv in key_values:
            lbl = html.escape(clean_broken_characters(kv.get("label", "")))
            val = html.escape(clean_broken_characters(kv.get("value", "")))
            if lbl and val:
                kv_lines.append(f"• <b>{lbl}៖</b> {val}")
        parts.append("\n".join(kv_lines))

    sections = data.get("sections", [])
    for sec in sections:
        heading = html.escape(clean_broken_characters(sec.get("heading", "")))
        content = html.escape(clean_broken_characters(sec.get("content", "")))
        if content:
            if heading:
                parts.append(f"\n<b>{heading}</b>\n{content}")
            else:
                parts.append(f"\n{content}")

    warnings = data.get("warnings", [])
    if warnings:
        warn_lines = ["\n⚠️ <b>ការប្រុងប្រយ័ត្ន (Security Warning)</b>"]
        for w in warnings:
            warn_lines.append(f"• {html.escape(clean_broken_characters(w))}")
        parts.append("\n".join(warn_lines))

    recommendations = data.get("recommendations", [])
    if recommendations:
        rec_lines = ["\n💡 <b>អនុសាសន៍ (Recommendation)</b>"]
        for r in recommendations:
            rec_lines.append(f"• {html.escape(clean_broken_characters(r))}")
        parts.append("\n".join(rec_lines))

    full_text = "\n".join(parts)
    return clean_broken_characters(full_text)
