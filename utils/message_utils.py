import html
import logging
import re
from aiogram import types


def clean_latex_to_unicode(text: str) -> str:
    """
    Converts LaTeX math expressions into clean, human-readable Unicode text for Telegram:
    - \\frac{a}{b} -> a/b
    - \\times -> ×
    - \\dots / \\ldots -> …
    - \\left( / \\right) -> ( / )
    - \\sqrt{x} -> √(x)
    - \\leq / \\geq / \\neq / \\pm -> ≤ / ≥ / ≠ / ±
    """
    if not text:
        return ""

    # Replace \\frac{numerator}{denominator} with numerator/denominator (handling nesting)
    for _ in range(3):
        text = re.sub(r'\\frac\{([^{}]+)\}\{([^{}]+)\}', r'\1/\2', text)

    # Replace \\sqrt{x} with √(x)
    text = re.sub(r'\\sqrt\{([^{}]+)\}', r'√(\1)', text)
    text = re.sub(r'\\not\{([^{}]+)\}', r'\1', text)

    replacements = [
        (r'\\times', '×'),
        (r'\\cdot', '·'),
        (r'\\dots|\\ldots|\\cdots', '…'),
        (r'\\left\(', '('),
        (r'\\right\)', ')'),
        (r'\\left\[', '['),
        (r'\\right\]', ']'),
        (r'\\left\\{', '{'),
        (r'\\right\\}', '}'),
        (r'\\left', ''),
        (r'\\right', ''),
        (r'\\leq', '≤'),
        (r'\\geq', '≥'),
        (r'\\neq', '≠'),
        (r'\\pm', '±'),
        (r'\\div', '÷'),
        (r'\\infty', '∞'),
        (r'\\pi', 'π'),
        (r'\\sum', '∑'),
        (r'\\int', '∫'),
    ]

    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)

    # Convert superscripts ^2 -> ², ^3 -> ³, ^n -> ⁿ, etc.
    superscripts = {'0':'⁰', '1':'¹', '2':'²', '3':'³', '4':'⁴', '5':'⁵', '6':'⁶', '7':'⁷', '8':'⁸', '9':'⁹', '+':'⁺', '-':'⁻', '=':'⁼', '(':'⁽', ')':'⁾', 'n':'ⁿ'}
    for char, sup in superscripts.items():
        text = text.replace(f'^{char}', sup)
        text = text.replace(f'^{{{char}}}', sup)

    # Convert subscripts _0 -> ₀, _1 -> ₁, _n -> ₙ, etc.
    subscripts = {'0':'₀', '1':'₁', '2':'₂', '3':'₃', '4':'₄', '5':'₅', '6':'₆', '7':'₇', '8':'₈', '9':'₉', '+':'₊', '-':'₋', '=':'₌', '(':'₍', ')':'₎', 'a':'ₐ', 'e':'ₑ', 'i':'ᵢ', 'o':'ₒ', 'r':'ᵣ', 'u':'ᵤ', 'v':'ᵥ', 'x':'ₓ', 'n':'ₙ', 'k':'ₖ', 'm':'ₘ'}
    for char, sub in subscripts.items():
        text = text.replace(f'_{char}', sub)
        text = text.replace(f'_{{{char}}}', sub)

    # Clean $$...$$, \[...\], \(...\) wrappers unless inside a code block
    text = re.sub(r'\$\$\s*\n?(.*?)\n?\s*\$\$', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'\\\[\s*\n?(.*?)\n?\s*\\\]', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'\\\((.*?)\\\)', r'\1', text, flags=re.DOTALL)

    return text



def escape_tg_html(text: str) -> str:
    """
    Escapes strictly '<', '>', and '&' for Telegram HTML parse mode.
    Does NOT escape quotes (") to &quot; or (') to &#x27; because Telegram HTML does not support them as entities.
    """
    if not text:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def sanitize_telegram_html(text: str) -> str:
    """
    Sanitizes HTML for Telegram parse_mode='HTML':
    - Keeps valid Telegram HTML tags (<b>, <i>, <code>, <pre>, <s>, <u>, <blockquote>, <a href="...">)
    - Escapes invalid or unclosed '<', '>', and '&' characters in plain text as &lt;, &gt;, and &amp;
    """
    if not text:
        return ""

    valid_tag_pattern = re.compile(
        r'</?(?:b|i|s|u|code|pre|blockquote|span)(?:\s+(?:class="[^"]*"|expandable))*\s*>|<a\s+href="[^"]*"\s*>|</a>',
        re.IGNORECASE
    )

    parts = []
    last_idx = 0
    for m in valid_tag_pattern.finditer(text):
        start, end = m.span()
        raw_segment = text[last_idx:start]
        if raw_segment:
            parts.append(escape_tg_html(raw_segment))
        parts.append(m.group(0))
        last_idx = end

    remaining = text[last_idx:]
    if remaining:
        parts.append(escape_tg_html(remaining))

    return "".join(parts)


def markdown_to_telegram_html(text: str) -> str:
    """
    Converts standard Gemini Markdown & LaTeX into clean, valid Telegram HTML.
    Processes code blocks separately, converts LaTeX formulas to Unicode, and applies
    bold, italic, headers, links, and list formatting without breaking Telegram HTML parsing.
    """
    if not text:
        return ""

    # Ensure unclosed code blocks are properly closed
    if text.count("```") % 2 != 0:
        text += "\n```"

    # Match both standard Markdown ```...``` and HTML <pre>...</pre>
    code_block_pattern = re.compile(
        r'(```([\w#+-]+)?\n?(.*?)```)|(<pre(?: [^>]*)?>.*?</pre>)',
        re.DOTALL | re.IGNORECASE
    )
    
    parts = []
    last_idx = 0

    for match in code_block_pattern.finditer(text):
        start, end = match.span()
        
        # Process text before code block
        text_before = text[last_idx:start]
        if text_before:
            parts.append(_format_text_block(text_before))

        if match.group(1):
            # It's a markdown ``` block
            lang = match.group(2) or ""
            code_content = match.group(3)
            escaped_code = escape_tg_html(code_content.strip())
            if lang:
                clean_lang = lang.lower().replace("+", "p").replace("#", "sharp")
                parts.append(f'<pre><code class="language-{clean_lang}">{escaped_code}</code></pre>')
            else:
                parts.append(f'<pre>{escaped_code}</pre>')
        else:
            # It's an HTML <pre> block
            html_pre_block = match.group(4)
            parts.append(html_pre_block)

        last_idx = end

    # Process remaining text after the last code block
    text_after = text[last_idx:]
    if text_after:
        parts.append(_format_text_block(text_after))

    final_html = "".join(parts)
    return sanitize_telegram_html(final_html)


def _format_text_block(text: str) -> str:
    """
    Formats standard text block for Telegram HTML:
    - Converts LaTeX math to clean Unicode text (fractions, multiplication, dots, etc.)
    - Converts markdown bold, italic, code, headers, strikethrough, and links to valid Telegram HTML.
    """
    if not text:
        return ""

    # Convert any raw LaTeX math expressions outside code blocks to Unicode text
    text = clean_latex_to_unicode(text)

    # Auto-detect naked code blocks when triple backticks are missing (C++, C, Java, Python, JS, SQL)
    code_kw_pattern = re.compile(
        r'(?:\n|^)((?:(?:#include\s*<|int\s+main\s*\(|std::|using\s+namespace|for\s*\(\s*int|while\s*\([^)]*\)|do\s*\{|def\s+\w+|class\s+\w+|import\s+\w+|from\s+\w+|print\(|return\s+|if\s+__name__|function\s+\w+|const\s+\w+|let\s+\w+|public\s+static\s+void|System\.out\.print|SELECT\s+.*FROM|CREATE\s+TABLE).*\n?){2,})',
        re.MULTILINE | re.IGNORECASE
    )

    def _wrap_naked_code(m):
        raw_code = m.group(1).strip()
        lang = "python"
        if "#include" in raw_code or "std::" in raw_code or "int main" in raw_code or "cout" in raw_code:
            lang = "cpp"
        elif "public static void" in raw_code or "System.out" in raw_code:
            lang = "java"
        elif "function" in raw_code or "console.log" in raw_code or "const " in raw_code or "let " in raw_code:
            lang = "javascript"
        elif "SELECT" in raw_code.upper() or "CREATE TABLE" in raw_code.upper():
            lang = "sql"

        escaped_c = escape_tg_html(raw_code)
        return f'\n<pre><code class="language-{lang}">{escaped_c}</code></pre>\n'

    if "```" not in text and code_kw_pattern.search(text):
        text = code_kw_pattern.sub(_wrap_naked_code, text)

    # Step 1: Inline code `code`
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

    # Step 2: Markdown Headers (# Header, ## Header, ### Header) -> <b>Header</b>
    text = re.sub(r'^(#{1,6})\s+(.+)$', r'<b>\2</b>', text, flags=re.MULTILINE)

    # Step 3: Bold **text** or __text__ -> <b>text</b>
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)

    # Step 4: Italic *text* or _text_ -> <i>text</i>
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'<i>\1</i>', text)

    # Step 5: Strikethrough ~~text~~ -> <s>text</s>
    text = re.sub(r'~~(.+?)~~', r'<s>\1</s>', text)

    # Step 6: Links [title](url) -> <a href="url">title</a>
    text = re.sub(r'\[([^\]]+)\]\((https?://[^\s\)]+)\)', r'<a href="\2">\1</a>', text)

    return text


def split_html_message(html_text: str, max_length: int = 3800) -> list[str]:
    """
    Splits long HTML text safely for Telegram while maintaining balanced HTML tags.
    """
    if not html_text:
        return []

    if len(html_text) <= max_length:
        return [html_text]

    chunks = []
    remaining = html_text

    while len(remaining) > max_length:
        cut_index = -1

        # Priority 1: Double newline (Paragraph break)
        para_index = remaining.rfind("\n\n", 0, max_length)
        if para_index > max_length // 2:
            cut_index = para_index + 2

        # Priority 2: Single newline
        if cut_index == -1:
            line_index = remaining.rfind("\n", 0, max_length)
            if line_index > max_length // 2:
                cut_index = line_index + 1

        # Priority 3: Sentence end
        if cut_index == -1:
            sentence_index = remaining.rfind(". ", 0, max_length)
            if sentence_index > max_length // 2:
                cut_index = sentence_index + 2

        # Priority 4: Space
        if cut_index == -1:
            space_index = remaining.rfind(" ", 0, max_length)
            if space_index > max_length // 4:
                cut_index = space_index + 1

        # Priority 5: Hard cut fallback
        if cut_index == -1:
            cut_index = max_length

        chunk = remaining[:cut_index]
        remaining = remaining[cut_index:]

        # Check tag balance for <pre> code blocks
        open_pres = re.findall(r'<pre(?: [^>]*)?>', chunk)
        close_pres = re.findall(r'</pre>', chunk)

        if len(open_pres) > len(close_pres):
            last_open_match = list(re.finditer(r'<pre(?: [^>]*)?>', chunk))[-1]
            last_open = last_open_match.group(0)
            
            has_code_tag = "<code" in chunk[last_open_match.start():]
            if has_code_tag:
                chunk += "</code></pre>"
                code_match = re.search(r'<code(?: class="[^"]*")?>', chunk[last_open_match.start():])
                if code_match:
                    reopen_tag = last_open + code_match.group(0)
                else:
                    reopen_tag = last_open + "<code>"
                remaining = reopen_tag + remaining
            else:
                chunk += "</pre>"
                remaining = last_open + remaining

        chunks.append(chunk)

    if remaining:
        chunks.append(remaining)

    return chunks


def split_message(text: str, max_length: int = 4000) -> list[str]:
    """
    Legacy plain text splitter fallback.
    """
    if not text:
        return []
    if len(text) <= max_length:
        return [text]
    return split_html_message(text, max_length)


async def send_safe_response(message: types.Message, text: str):
    """
    Converts AI response to Telegram HTML, splits long messages safely,
    and sends each chunk with parse_mode='HTML'.
    Falls back to sanitized plain text if HTML parsing fails.
    """
    if not text or not text.strip():
        return

    # 1. Convert Markdown & LaTeX from Gemini to Telegram HTML
    formatted_html = markdown_to_telegram_html(text)

    # 2. Split long formatted text into safe chunks
    chunks = split_html_message(formatted_html, max_length=3800)

    for chunk in chunks:
        try:
            await message.reply(chunk, parse_mode="HTML")
        except Exception as e:
            logging.warning(f"Failed to send HTML formatted message chunk, attempting plain text fallback: {e}")
            # Fallback: Strip HTML tags, unescape, and send as pure plain text without parse_mode
            plain_text = re.sub(r'<[^>]+>', '', chunk)
            plain_text = html.unescape(plain_text)
            try:
                await message.reply(plain_text, parse_mode=None)
            except Exception as fallback_err:
                logging.error(f"Fallback plain text message send failed: {fallback_err}")
