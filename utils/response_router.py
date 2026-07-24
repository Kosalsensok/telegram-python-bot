import json
import re
import html
import logging
import unicodedata
from typing import Dict, Any, List, Optional, Tuple

RESPONSE_TYPES = [
    "greeting",
    "general_answer",
    "code_answer",
    "technical_explanation",
    "software_requirements",
    "project_prototype",
    "system_architecture",
    "database_design",
    "api_design",
    "mathematics",
    "physics",
    "chemistry",
    "email_analysis",
    "document_analysis",
    "table_analysis",
    "general_image_analysis",
    # Aliases
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
    Normalizes string to Unicode NFC.
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r'[\u25A1\u25A0\u25A2\u25A3\u25A4\u25A5]', '•', text)
    text = text.replace('\ufffd', '')
    text = re.sub(r'•\s*•+', '•', text)
    return text.strip()


def detect_response_type_from_text(text: str, user_prompt: str = "") -> str:
    """
    Intelligent classifier to assign query/response to one of the ResponseType categories.
    Prioritizes Greetings and Specific Technical Sub-domains before broad requirement types.
    """
    combined = (text + " " + user_prompt).lower().strip()
    clean_prompt = user_prompt.strip().lower()
    clean_text = text.strip().lower()

    # Priority 0: Greeting Detection
    greeting_exact = ["hi", "hello", "hey", "greetings", "សួស្តី", "សួស្ដី", "hi bot", "hello bot", "good morning", "good evening", "good afternoon"]
    if clean_prompt in greeting_exact or clean_text in greeting_exact or (len(combined) < 15 and any(combined.startswith(g) for g in ["hi", "hello", "hey", "សួស្តី", "សួស្ដី"])):
        return "greeting"

    # Specific Technical Sub-domain Detection (Priority 1)
    if any(k in combined for k in ["database", "schema", "tables", "primary key", "foreign key", "sql", "ដាតាបេស"]):
        return "database_design"
    if any(k in combined for k in ["api endpoint", "rest api", "json endpoint", "http route", "api design"]):
        return "api_design"
    if any(k in combined for k in ["architecture", "microservice", "system design", "component diagram"]):
        return "system_architecture"
    if any(k in combined for k in ["prototype", "build prototype", "បង្កើត prototype", "project zip"]):
        return "project_prototype"
    if any(k in combined for k in ["write code", "write a code", "code c++", "c++ loop", "python script", "code block", "#include", "def ", "function "]):
        return "code_answer"

    # General Requirements (Priority 2)
    if any(k in combined for k in ["requirements", "functional requirements", "system requirements", "mart system", "pos system", "feature list", "តម្រូវការ"]):
        return "software_requirements"

    # Science / Math
    if any(k in combined for k in ["h2o", "co2", "reaction", "chemical", "គីមី"]):
        return "chemistry"
    if any(k in combined for k in ["velocity", "force", "acceleration", "joule", "watt", "ល្បឿន", "កម្លាំង", "រូបវិទ្យា"]):
        return "physics"
    math_kw = ["\\frac", "\\sqrt", "equation", "solve", "proof", "∫", "∑", "lim", "លំហាត់", "សមីការ", "គណនា"]
    if any(k in combined for k in math_kw) or re.search(r'\\[a-zA-Z]+|\$\$?.*?\$\$?', text):
        return "mathematics"

    # Image / Analysis
    if any(k in combined for k in ["email", "e-mail", "stripe", "payment", "invoice", "visa ending", "card ending", "subscription", "sender"]):
        return "email_analysis"
    if "<table>" in combined or ("|" in text and text.count("|") > 4):
        return "table_analysis"
    if any(k in combined for k in ["document", "pdf", "page", "article", "សៀវភៅ", "ឯកសារ"]):
        return "document_analysis"

    return "general_answer"


def parse_ai_structured_response(raw_text: str, user_prompt: str = "", default_prompt: str = "") -> Dict[str, Any]:
    """
    Parses raw AI response into structured JSON schema matching Zod requirements.
    If raw AI response is valid JSON, extracts fields.
    Otherwise, builds structured dictionary using intelligent extraction.
    """
    prompt = user_prompt or default_prompt
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

    if parsed and isinstance(parsed, dict) and ("sections" in parsed or "title" in parsed):
        res_type = parsed.get("response_type", "general_answer")
        if res_type not in RESPONSE_TYPES:
            res_type = detect_response_type_from_text(cleaned_raw, prompt)
        parsed["response_type"] = res_type
        if "title" not in parsed or not parsed["title"]:
            parsed["title"] = "ចម្លើយ Smart AI"
        if "sections" not in parsed:
            parsed["sections"] = []
        return parsed

    # Fallback: Rule-based extraction from unstructured text
    res_type = detect_response_type_from_text(cleaned_raw, prompt)
    lines = [l.strip() for l in cleaned_raw.split("\n") if l.strip()]

    title = lines[0] if lines else "Smart AI Assistant Response"
    if len(title) > 90:
        title = title[:90] + "..."

    summary = ""
    sections = []
    key_values = []
    warnings = []
    recommendations = []
    current_heading = "ទិដ្ឋភាពទូទៅ (Overview)"
    current_content_lines = []
    step_num = 1

    for line in lines[1:]:
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

        if line.startswith(("#", "==", "**", "1.", "2.", "3.", "---", "4.", "5.", "6.")):
            if current_content_lines:
                sections.append({
                    "id": f"sec_{step_num}",
                    "step_number": step_num,
                    "heading": current_heading,
                    "heading_km": current_heading,
                    "content": "\n".join(current_content_lines),
                    "content_km": "\n".join(current_content_lines)
                })
                step_num += 1
                current_content_lines = []
            current_heading = re.sub(r'[*_#=\-]', '', line).strip()
        else:
            if not summary and len(line) > 20:
                summary = line
            else:
                current_content_lines.append(line)

    if current_content_lines:
        sections.append({
            "id": f"sec_{step_num}",
            "step_number": step_num,
            "heading": current_heading,
            "heading_km": current_heading,
            "content": "\n".join(current_content_lines),
            "content_km": "\n".join(current_content_lines)
        })

    if not sections and not key_values:
        sections.append({
            "id": "sec_1",
            "step_number": 1,
            "heading": "ខ្លឹមសារ (Content)",
            "heading_km": "ខ្លឹមសារ",
            "content": cleaned_raw,
            "content_km": cleaned_raw
        })

    return {
        "response_type": res_type,
        "language": "km",
        "title": title,
        "subtitle": "Smart AI Response",
        "summary": summary or title,
        "summary_km": summary or title,
        "tags": ["AI", "SmartAssistant"],
        "sections": sections,
        "key_values": key_values,
        "warnings": warnings,
        "recommendations": recommendations,
        "math_expressions": [],
        "suggested_actions": ["view_overview", "view_details"]
    }


def format_greeting_telegram(data: Dict[str, Any]) -> str:
    """
    Format standard greeting response for Telegram output (Phase 7 A).
    """
    return (
        "👋 <b>សួស្តី!</b>\n"
        "ខ្ញុំជា <b>Smart AI Assistant</b>។\n\n"
        "ខ្ញុំអាចជួយអ្នកបានលើ៖\n"
        "• 💻 ការសរសេរកូដ (Code Generation)\n"
        "• 📐 គណិតវិទ្យា & វិទ្យាសាស្ត្រ (LaTeX Solver)\n"
        "• 🖼 វិភាគរូបភាព (Vision OCR & Inspection)\n"
        "• 🛒 Functional Requirements & Business Systems\n"
        "• 📦 Project Prototype & Architecture\n"
        "• 🧠 Technical Deep-Dive Explanations\n\n"
        "👉 សូមផ្ញើសំណួររបស់អ្នក ឬចុច Menu ខាងក្រោម។"
    )


def format_code_answer_telegram(data: Dict[str, Any]) -> str:
    """
    Format code answer response for Telegram output (Phase 7 B).
    """
    title = clean_broken_characters(data.get("title", "C++ Code Solution"))
    subtitle = clean_broken_characters(data.get("subtitle", ""))
    summary = clean_broken_characters(data.get("summary_km") or data.get("summary") or "")
    tags = data.get("tags", ["Code", "Implementation"])
    sections = data.get("sections", [])

    parts = [
        "💻 <b>CODE SOLUTION</b>",
        f"<b>{title}</b>"
    ]
    if subtitle:
        parts.append(f"<i>{subtitle}</i>")

    if summary:
        parts.append(f"\n<b>សង្ខេប៖</b> {summary}")

    if tags:
        parts.append(f"🏷 <b>Tags:</b> {' · '.join(tags)}")

    if sections:
        parts.append("")
        for sec in sections[:4]:
            step_num = sec.get("step_number", 1)
            heading = clean_broken_characters(sec.get("heading_km") or sec.get("heading") or "")
            content = clean_broken_characters(sec.get("content_km") or sec.get("content") or "")
            parts.append(f"<b>{step_num}️⃣ {heading}</b>\n{content}")

    return "\n".join(parts)


def format_software_requirements_telegram(data: Dict[str, Any]) -> str:
    """
    Format software requirements response for Telegram output (Phase 7 C).
    """
    title = clean_broken_characters(data.get("title", "SMART SYSTEM REQUIREMENTS"))
    subtitle = clean_broken_characters(data.get("subtitle", "Advanced Functional Requirements"))
    summary = clean_broken_characters(data.get("summary_km") or data.get("summary") or "")
    tags = data.get("tags", ["POS", "Inventory", "Analytics"])
    sections = data.get("sections", [])

    parts = [
        "━━━━━━━━━━━━━━━━━━",
        f"🛒 <b>{title.upper()}</b>\n{subtitle}",
        "━━━━━━━━━━━━━━━━━━",
        f"\n<b>សេចក្តីសង្ខេប៖</b> {summary}"
    ]

    if tags:
        parts.append(f"🏷 <b>Tags:</b> {' · '.join(tags)}")

    if sections:
        parts.append("")
        for sec in sections[:5]:
            step_num = sec.get("step_number", 1)
            num_emoji = f"{step_num}️⃣" if step_num <= 10 else f"[{step_num}]"
            heading = clean_broken_characters(sec.get("heading_km") or sec.get("heading") or "")
            content_snippet = clean_broken_characters(sec.get("content_km") or sec.get("content") or "")
            if content_snippet:
                snippet = content_snippet.split("\n")[0]
                if len(snippet) > 80:
                    snippet = snippet[:80] + "..."
                parts.append(f"{num_emoji} <b>{heading}</b>\n{snippet}")
            else:
                parts.append(f"{num_emoji} <b>{heading}</b>")

    parts.append("\n━━━━━━━━━━━━━━━━━━")
    parts.append("👇 <b>សូមជ្រើសរើសផ្នែកខាងក្រោម ដើម្បីមើលព័ត៌មានលម្អិត</b>")

    return "\n".join(parts)


def format_math_telegram(data: Dict[str, Any]) -> str:
    """
    Format mathematics / science response for Telegram output (Phase 7 D).
    """
    title = clean_broken_characters(data.get("title", "Mathematics Solution"))
    summary = clean_broken_characters(data.get("summary_km") or data.get("summary") or "")
    sections = data.get("sections", [])

    parts = [
        "🎓 <b>MATHEMATICS SOLUTION</b>",
        f"<b>{title}</b>"
    ]
    if summary:
        parts.append(f"\n{summary}")

    if sections:
        parts.append("")
        for sec in sections[:5]:
            step_num = sec.get("step_number", 1)
            heading = clean_broken_characters(sec.get("heading_km") or sec.get("heading") or "")
            content = clean_broken_characters(sec.get("content_km") or sec.get("content") or "")
            parts.append(f"<b>{step_num}️⃣ {heading}</b>\n{content}")

    return "\n".join(parts)


def format_email_telegram(data: Dict[str, Any]) -> str:
    """
    Format email analysis response for Telegram output.
    """
    title = clean_broken_characters(data.get("title", "Email Verification"))
    summary = clean_broken_characters(data.get("summary_km") or data.get("summary") or "")
    sections = data.get("sections", [])

    parts = [
        "📧 <b>EMAIL ANALYSIS</b>",
        f"<b>{title}</b>",
        f"\n{summary}"
    ]
    if sections:
        parts.append("")
        for sec in sections[:4]:
            heading = clean_broken_characters(sec.get("heading_km") or sec.get("heading") or "")
            content = clean_broken_characters(sec.get("content_km") or sec.get("content") or "")
            parts.append(f"<b>• {heading}:</b> {content}")

    return "\n".join(parts)


def format_document_telegram(data: Dict[str, Any]) -> str:
    """
    Format document extraction response for Telegram output.
    """
    title = clean_broken_characters(data.get("title", "Document Summary"))
    summary = clean_broken_characters(data.get("summary_km") or data.get("summary") or "")
    sections = data.get("sections", [])

    parts = [
        "📄 <b>DOCUMENT ANALYSIS</b>",
        f"<b>{title}</b>",
        f"\n{summary}"
    ]
    if sections:
        parts.append("")
        for sec in sections[:5]:
            heading = clean_broken_characters(sec.get("heading_km") or sec.get("heading") or "")
            content = clean_broken_characters(sec.get("content_km") or sec.get("content") or "")
            parts.append(f"<b>• {heading}:</b>\n{content}")

    return "\n".join(parts)


def format_general_answer_telegram(data: Dict[str, Any]) -> str:
    """
    Format general answer response for Telegram output.
    """
    title = clean_broken_characters(data.get("title", "Smart AI Response"))
    summary = clean_broken_characters(data.get("summary_km") or data.get("summary") or "")
    sections = data.get("sections", [])

    parts = [
        f"🤖 <b>{title}</b>"
    ]
    if summary and summary != title:
        parts.append(f"\n{summary}")

    if sections:
        parts.append("")
        for sec in sections[:5]:
            heading = clean_broken_characters(sec.get("heading_km") or sec.get("heading") or "")
            content = clean_broken_characters(sec.get("content_km") or sec.get("content") or "")
            parts.append(f"<b>• {heading}</b>\n{content}")

    return "\n".join(parts)


def format_telegram_html(data: Dict[str, Any]) -> str:
    """
    Formats structured response into Telegram-Native Premium HTML message (Layer 1).
    Dispatches to dedicated formatters according to response_type.
    """
    res_type = data.get("response_type", "general_answer")

    if res_type == "greeting":
        return format_greeting_telegram(data)
    elif res_type == "code_answer":
        return format_code_answer_telegram(data)
    elif res_type in ["software_requirements", "project_prototype", "system_architecture", "database_design", "api_design"]:
        return format_software_requirements_telegram(data)
    elif res_type in ["mathematics", "physics", "chemistry"]:
        return format_math_telegram(data)
    elif res_type in ["email_analysis", "email"]:
        return format_email_telegram(data)
    elif res_type in ["document_analysis", "document"]:
        return format_document_telegram(data)
    else:
        return format_general_answer_telegram(data)

