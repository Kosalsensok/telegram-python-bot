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
    "speech_to_text",
    # Aliases
    "email",
    "document",
    "table",
    "general_image",
    "stt"
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

    # Detect code block & language
    extracted_code = ""
    detected_lang = "cpp" if ("c++" in prompt.lower() or "cpp" in prompt.lower()) else "python"
    
    if any(k in prompt.lower() or k in cleaned_raw.lower() for k in ["#include", "std::", "cout", "c++", "cpp", "int main"]):
        detected_lang = "cpp"
    elif any(k in prompt.lower() or k in cleaned_raw.lower() for k in ["python", "def ", "import ", "print("]):
        detected_lang = "python"
    elif any(k in prompt.lower() or k in cleaned_raw.lower() for k in ["javascript", "console.log", "function ", "const ", "let "]):
        detected_lang = "javascript"
    elif any(k in prompt.lower() or k in cleaned_raw.lower() for k in ["java", "public static void", "System.out"]):
        detected_lang = "java"
    elif any(k in prompt.lower() or k in cleaned_raw.lower() for k in ["sql", "select ", "create table"]):
        detected_lang = "sql"

    code_match = re.search(r'```(?:([\w#+-]+))?\s*\n?(.*?)```', cleaned_raw, re.DOTALL)
    if code_match:
        lang_hint = code_match.group(1)
        if lang_hint:
            clean_hint = lang_hint.lower().strip()
            if clean_hint in ["cpp", "c++"]:
                detected_lang = "cpp"
            elif clean_hint in ["py", "python"]:
                detected_lang = "python"
            elif clean_hint in ["js", "javascript"]:
                detected_lang = "javascript"
            elif clean_hint in ["ts", "typescript"]:
                detected_lang = "typescript"
            elif clean_hint in ["java"]:
                detected_lang = "java"
            elif clean_hint in ["c"]:
                detected_lang = "c"
            elif clean_hint in ["sql"]:
                detected_lang = "sql"
        extracted_code = code_match.group(2).strip()

    if not extracted_code:
        html_code_match = re.search(r'<pre(?: [^>]*)?>(?:<code(?: [^>]*)?>)?(.*?)(?:</code>)?</pre>', cleaned_raw, re.DOTALL | re.IGNORECASE)
        if html_code_match:
            extracted_code = html.unescape(html_code_match.group(1).strip())

    LANG_TO_EXT = {
        "cpp": ".cpp", "c": ".c", "python": ".py", "javascript": ".js",
        "typescript": ".ts", "java": ".java", "php": ".php", "html": ".html",
        "css": ".css", "sql": ".sql", "json": ".json", "go": ".go", "rust": ".rs"
    }
    ext = LANG_TO_EXT.get(detected_lang, ".txt")
    filename = f"main{ext}"

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
        parsed["programming_language"] = detected_lang
        if extracted_code and "code" not in parsed:
            parsed["code"] = {"language": detected_lang, "filename": filename, "content": extracted_code}
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
                sec_dict = {
                    "id": f"sec_{step_num}",
                    "step_number": step_num,
                    "heading": current_heading,
                    "heading_km": current_heading,
                    "content": "\n".join(current_content_lines),
                    "content_km": "\n".join(current_content_lines)
                }
                if extracted_code and step_num == 1:
                    sec_dict["code"] = extracted_code
                sections.append(sec_dict)
                step_num += 1
                current_content_lines = []
            current_heading = re.sub(r'[*_#=\-]', '', line).strip()
        else:
            if not summary and len(line) > 20:
                summary = line
            else:
                current_content_lines.append(line)

    if current_content_lines:
        sec_dict = {
            "id": f"sec_{step_num}",
            "step_number": step_num,
            "heading": current_heading,
            "heading_km": current_heading,
            "content": "\n".join(current_content_lines),
            "content_km": "\n".join(current_content_lines)
        }
        if extracted_code and step_num == 1:
            sec_dict["code"] = extracted_code
        sections.append(sec_dict)

    if not sections and not key_values:
        sec_dict = {
            "id": "sec_1",
            "step_number": 1,
            "heading": "ខ្លឹមសារ (Content)",
            "heading_km": "ខ្លឹមសារ",
            "content": cleaned_raw,
            "content_km": cleaned_raw
        }
        if extracted_code:
            sec_dict["code"] = extracted_code
        sections.append(sec_dict)

    result_dict = {
        "response_type": res_type,
        "programming_language": detected_lang,
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
    if extracted_code:
        result_dict["code"] = {
            "language": detected_lang,
            "filename": filename,
            "content": extracted_code
        }
    return result_dict


def format_greeting_telegram(data: Dict[str, Any]) -> str:
    """
    Format standard greeting response for Telegram output (Phase 7 A).
    """
    return (
        "👋 <b>សួស្ដី!</b>\n"
        "ខ្ញុំជា <b>Smart AI Assistant</b> 🤖\n\n"
        "ខ្ញុំអាចជួយអ្នកលើ៖\n"
        "• 💻 <b>សរសេរកូដ៖</b> កូដ និងដោះស្រាយ Error\n"
        "• 📐 <b>លំហាត់៖</b> គណិត, រូប, គីមី (LaTeX Solver)\n"
        "• 🖼️ <b>រូបភាព៖</b> វិភាគ និងស្កែនរូបភាព (Vision OCR)\n"
        "• 🏗️ <b>ប្រព័ន្ធ AI៖</b> រៀបចំ Architecture & Requirements\n"
        "• 💡 <b>ប្រឹក្សាយោបល់៖</b> ពន្យល់បច្ចេកវិទ្យា និងដំណោះស្រាយ\n\n"
        "👉 <b>សូមផ្ញើសំណួរ ឬជ្រើសរើសមុខងារខាងក្រោម៖</b>"
    )


def format_code_answer_telegram(data: Dict[str, Any]) -> str:
    """
    Format code answer response for Telegram output without header overhead.
    """
    summary = clean_broken_characters(data.get("summary_km") or data.get("summary") or "")
    sections = data.get("sections", [])
    code_info = data.get("code", {})
    code_content = code_info.get("content", "") if isinstance(code_info, dict) else ""
    code_lang = code_info.get("language", "cpp") if isinstance(code_info, dict) else "cpp"

    parts = []
    if summary:
        parts.append(f"📌 <b>សង្ខេប៖</b> {summary}")

    if code_content:
        parts.append(f"\n💻 <b>ឧទាហរណ៍កូដ {code_lang.upper()}៖</b>\n<pre><code class=\"language-{code_lang}\">{code_content}</code></pre>")

    if sections:
        parts.append("\n─────────────────\n💡 <b>ចំណុចសំខាន់ៗ៖</b>")
        for sec in sections[:5]:
            heading = clean_broken_characters(sec.get("heading_km") or sec.get("heading") or "")
            content = clean_broken_characters(sec.get("content_km") or sec.get("content") or "")
            content_clean = re.sub(r'(?<=\S)\s*(•|\-|\*)\s+', r'\n• ', content)
            if heading and heading.lower() not in ["code", "solution", "overview", "សង្ខេប"]:
                parts.append(f"• <b>{heading}៖</b> {content_clean}")
            elif content_clean:
                parts.append(f"• {content_clean}")

    return "\n".join(parts)


def format_software_requirements_telegram(data: Dict[str, Any]) -> str:
    """
    Format software requirements response for Telegram output.
    Uses clean Khmer header '📄 លទ្ធផលវិភាគឯកសារ' per user spec.
    """
    title = clean_broken_characters(data.get("title", ""))
    summary = clean_broken_characters(data.get("summary_km") or data.get("summary") or "")
    tags = data.get("tags") or []
    sections = data.get("sections", [])

    parts = [
        "📄 <b>លទ្ធផលវិភាគឯកសារ</b>\n"
    ]
    if summary:
        clean_sum = re.sub(r'(?<=\S)\s*(\-|\•|\*)\s+', r'\n• ', summary)
        parts.append(f"📌 <b>ទិដ្ឋភាពទូទៅ (Overview)៖</b>\n{clean_sum}")

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
    Uses clean Khmer header '📄 លទ្ធផលវិភាគឯកសារ' per user spec.
    """
    title = clean_broken_characters(data.get("title", ""))
    summary = clean_broken_characters(data.get("summary_km") or data.get("summary") or "")
    sections = data.get("sections", [])

    parts = [
        "📄 <b>លទ្ធផលវិភាគឯកសារ</b>\n"
    ]
    if summary:
        clean_sum = re.sub(r'(?<=\S)\s*(\-|\•|\*)\s+', r'\n• ', summary)
        parts.append(f"📌 <b>ទិដ្ឋភាពទូទៅ (Overview)៖</b>\n{clean_sum}")

    if sections:
        parts.append("")
        for sec in sections[:5]:
            heading = clean_broken_characters(sec.get("heading_km") or sec.get("heading") or "")
            content = clean_broken_characters(sec.get("content_km") or sec.get("content") or "")
            clean_content = re.sub(r'(?<=\S)\s*(\-|\•|\*)\s+', r'\n• ', content)
            if heading:
                parts.append(f"• <b>{heading}៖</b>\n{clean_content}")
            else:
                parts.append(clean_content)

    return "\n".join(parts)


def format_general_answer_telegram(data: Dict[str, Any]) -> str:
    """
    Format general answer response for Telegram output.
    """
    title = clean_broken_characters(data.get("title", ""))
    summary = clean_broken_characters(data.get("summary_km") or data.get("summary") or "")
    sections = data.get("sections", [])

    parts = []
    if title and not any(t in title.lower() for t in ["smart ai", "assistant response", "general answer"]):
        parts.append(f"📌 <b>{title}</b>")
    elif summary:
        parts.append(f"📌 <b>សង្ខេប៖</b> {summary}")

    if summary and summary != title and not parts:
        parts.append(f"📌 <b>សង្ខេប៖</b> {summary}")

    if sections:
        parts.append("\n─────────────────\n💡 <b>ចំណុចសំខាន់ៗ៖</b>")
        for sec in sections[:5]:
            heading = clean_broken_characters(sec.get("heading_km") or sec.get("heading") or "")
            content = clean_broken_characters(sec.get("content_km") or sec.get("content") or "")
            content_clean = re.sub(r'(?<=\S)\s*(•|\-|\*)\s+', r'\n• ', content)
            if heading and not heading.lower().startswith("sec_"):
                parts.append(f"• <b>{heading}៖</b> {content_clean}")
            elif content_clean:
                parts.append(f"• {content_clean}")

    return "\n".join(parts)


def format_speech_to_text_telegram(data: Dict[str, Any]) -> str:
    """
    Format Speech-to-Text audio transcription response for Telegram output.
    - Converts **bold** to <b>bold</b> so Telegram HTML renders cleanly without raw **.
    - Strips top headers like '🧠 SMART AI ASSISTANT', '📌 សង្ខេប', '🏷 Tags', and duplicate '📝 លទ្ធផលបំប្លែងសំឡេង'.
    - Standardizes sections:
        📝 <b>លទ្ធផលបំប្លែងសំឡេង៖</b>
        💬 <b>អត្ថបទដែលបាននិយាយ៖</b>
        🤖 <b>ចម្លើយ AI៖</b>
        💡 <b>ចំណុចសំខាន់ៗដែលត្រូវដឹង៖</b>
        🔗 <b>ប្រភព និងឯកសារយោង៖</b>
    """
    raw_text = clean_broken_characters(data.get("raw_text") or data.get("summary_km") or data.get("summary") or "")

    # Clean stray headers, quote markers, duplicate headers and tags
    formatted = re.sub(r'🧠\s*\**SMART AI ASSISTANT\**\n?', '', raw_text, flags=re.IGNORECASE)
    formatted = re.sub(r'📌\s*\**សង្ខេប\**.*?\n', '', formatted, flags=re.IGNORECASE)
    formatted = re.sub(r'🏷\s*\**Tags\**.*?\n', '', formatted, flags=re.IGNORECASE)
    formatted = re.sub(r'•\s*(?:AI|CPlusPlus|Programming|SpeechToText|KhmerTranscription|Greeting)\b.*?\n', '', formatted, flags=re.IGNORECASE)
    formatted = re.sub(r'1️⃣\s*\**លទ្ធផលបំប្លែងសំឡេង.*?\n', '', formatted, flags=re.IGNORECASE)
    formatted = re.sub(r'2️⃣\s*\**ចម្លើយ.*?\n', '', formatted, flags=re.IGNORECASE)
    formatted = re.sub(r'📝\s*\**លទ្ធផលបំប្លែងសំឡេង\**.*?\n?', '', formatted, flags=re.IGNORECASE)
    formatted = re.sub(r'─{3,}', '', formatted)

    # Auto-wrap naked C++ code blocks if not already in triple backticks
    if "```" not in formatted and "#include" in formatted:
        def _wrap_naked_cpp(m):
            raw_c = m.group(0).strip()
            # Remove any raw C++ title line
            raw_c = re.sub(r'^(?:C\+\+|cpp)\s*\n?', '', raw_c, flags=re.IGNORECASE)
            return f'\n```cpp\n{raw_c}\n```\n'
        formatted = re.sub(r'(?:C\+\+|cpp)?\s*\n?(#include\s*<[\s\S]+?return\s+0;\s*\})', _wrap_naked_cpp, formatted, flags=re.IGNORECASE)

    # Convert **bold** to <b>bold</b> cleanly
    formatted = re.sub(r'\*\*([\s\S]+?)\*\*', r'<b>\1</b>', formatted)
    formatted = re.sub(r'(?<!\*)\*(?!\*)([\s\S]+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', formatted)

    # Ensure proper line breaks (\n) before bullet points (•) and sub-bullets
    formatted = re.sub(r'(?<=\S)\s*(•|\-)\s+', r'\n• ', formatted)
    # Ensure proper line breaks (\n) before numbered lists
    formatted = re.sub(r'(?<=\S)\s+(\d+\.\s+)', r'\n\1', formatted)

    # Clean orphan asterisks
    formatted = re.sub(r'\*+', '', formatted)
    formatted = formatted.strip()

    # Standardize section headers if present or missing
    formatted = re.sub(r'📜\s*<b>អត្ថបទដែលបានបំប្លែង\**', '💬 <b>អត្ថបទដែលបាននិយាយ៖</b>', formatted)
    formatted = re.sub(r'💡\s*<b>ចម្លើយ និងការបកស្រាយ\**', '🤖 <b>ចម្លើយ AI៖</b>', formatted)
    formatted = re.sub(r'🔗\s*<b>ប្រភព និងឯកសារយោង.*?\**', '🔗 <b>ប្រភព និងឯកសារយោង៖</b>', formatted)
    formatted = re.sub(r'🔗\s*<b>ប្រភពឯកសារយោង.*?\**', '🔗 <b>ប្រភព និងឯកសារយោង៖</b>', formatted)

    # Prepend header ONCE at the top
    formatted = f"📝 <b>លទ្ធផលបំប្លែងសំឡេង៖</b>\n\n{formatted}"

    return formatted


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
    elif res_type in ["speech_to_text", "stt"]:
        return format_speech_to_text_telegram(data)
    elif res_type in ["email_analysis", "email"]:
        return format_email_telegram(data)
    elif res_type in ["document_analysis", "document"]:
        return format_document_telegram(data)
    else:
        return format_general_answer_telegram(data)

