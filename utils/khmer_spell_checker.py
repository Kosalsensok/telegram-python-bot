import re
import html
import logging
from typing import Dict, List, Any, Tuple

# Common Khmer misspellings map (misspelled -> list of correct suggestions, explanation, auto_fixable, severity, confidence)
KHMER_DICTIONARY_RULES = {
    "សំរាប់": (["សម្រាប់"], "ពាក្យនេះជាទូទៅត្រូវសរសេរជា «សម្រាប់»។", True, "error", 0.96),
    "សំរេច": (["សម្រេច"], "ពាក្យនេះជាទូទៅត្រូវសរសេរជា «សម្រេច»។", True, "error", 0.95),
    "សំរួល": (["សម្រួល"], "ពាក្យនេះជាទូទៅត្រូវសរសេរជា «សម្រួល»។", True, "error", 0.95),
    "សំរេចចិត្ត": (["សម្រេចចិត្ត"], "ពាក្យនេះជាទូទៅត្រូវសរសេរជា «សម្រេចចិត្ត»។", True, "error", 0.96),
    "អោយ": (["ឱ្យ"], "ពាក្យនេះជាទូទៅត្រូវសរសេរជា «ឱ្យ»។", True, "error", 0.95),
    "រឺ": (["ឬ"], "សញ្ញាឈ្នាប់ «ឬ» ត្រូវសរសេរដោយប្រើតួអក្សរ ឬ មិនមែន រឺ ឡើយ។", True, "error", 0.96),
    "កំនត់": (["កំណត់"], "ពាក្យ «កំណត់» ប្រើប្រកប «ំណ» មិនមែន «ំន» ឡើយ។", True, "error", 0.95),
    "បំនង": (["បំណង"], "ពាក្យ «បំណង» ប្រើប្រកប «ំណ» មិនមែន «ំន» ឡើយ។", True, "error", 0.95),
    "តំលៃ": (["តម្លៃ"], "ពាក្យនេះត្រូវសរសេរជា «តម្លៃ»។", True, "error", 0.95),
    "តំឡើង": (["ដំឡើង", "តម្លើង"], "ពាក្យនេះជាទូទៅត្រូវសរសេរជា «ដំឡើង»។", True, "warning", 0.90),
    "ចំនុច": (["ចំណុច"], "ពាក្យនេះត្រូវសរសេរជា «ចំណុច»។", True, "error", 0.95),
    "ចំនែក": (["ចំណែក"], "ពាក្យនេះត្រូវសរសេរជា «ចំណែក»។", True, "error", 0.95),
    "ចំនាយ": (["ចំណាយ"], "ពាក្យនេះត្រូវសរសេរជា «ចំណាយ»។", True, "error", 0.95),
    "ចំនូល": (["ចំណូល"], "ពាក្យនេះត្រូវសរសេរជា «ចំណូល»។", True, "error", 0.95),
    "ប្រពន្ធ័": (["ប្រព័ន្ធ"], "ពាក្យ «ប្រព័ន្ធ» ប្រើទណ្ឌឃាតលើ ័ មិនមែន ័ ឡើយ។", True, "error", 0.96),
    "ពិេសស": (["ពិសេស"], "ស្រៈ «េ» ត្រូវស្ថិតនៅមុនព្យញ្ជនៈស។", True, "error", 0.95),
    "សម្ភារៈ": (["សម្ភារ"], "ពាក្យ «សម្ភារ» មិនត្រូវមាន ៈ នៅខាងចុងឡើយ។", True, "warning", 0.92),
    "អុីនធឺណិត": (["អ៊ីនធឺណិត"], "ពាក្យ «អ៊ីនធឺណិត» ត្រូវប្រើស្រៈ អ៊ី មិនមែន អុី ឡើយ។", True, "error", 0.95),
    "អុីនធឺណែត": (["អ៊ីនធឺណិត", "អ៊ីនធឺណែត"], "ពាក្យនេះគួរតែសរសេរជា «អ៊ីនធឺណិត»។", True, "warning", 0.90),
    "សន្តិភព": (["សន្តិភាព"], "ពាក្យ «សន្តិភាព» ត្រូវមានស្រៈ ា។", True, "error", 0.94),
    "បច្ចេកវិទ្យា": (["បច្ចេកវិទ្យា"], "ពាក្យ «បច្ចេកវិទ្យា» ត្រូវសរសេរឱ្យត្រឹមត្រូវ។", True, "error", 0.95),
    "អនាគត": (["អនាគត"], "ពាក្យ «អនាគត» ត្រូវសរសេរឱ្យត្រឹមត្រូវ។", True, "error", 0.95),
}

# Regex Patterns for Protection/Exclusion Rules (DO NOT AUTO-CORRECT OR CHECK THESE)
EXCLUSION_PATTERNS = [
    r'https?://[^\s]+',                      # URLs
    r'www\.[^\s]+',                          # Web addresses
    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', # Emails
    r'\+?\d{8,15}',                           # Phone numbers
    r'@[a-zA-Z0-9_]{3,}',                    # Telegram usernames
    r'#[a-zA-Z0-9_\u1780-\u17FF]+',           # Hashtags
    r'/[a-zA-Z0-9_]+',                        # Telegram bot commands like /start
    r'```[\s\S]*?```',                       # Code blocks
    r'`[^`]+`',                               # Inline code
    r'\{[\s\S]*?\}',                          # JSON snippets
    r'<[^>]+>',                               # HTML tags
]

def _is_protected_range(start: int, end: int, protected_ranges: List[Tuple[int, int]]) -> bool:
    """Checks if character span intersects with any protected exclusion range."""
    for p_start, p_end in protected_ranges:
        if max(start, p_start) < min(end, p_end):
            return True
    return False

def count_khmer_words_and_chars(text: str) -> Tuple[int, int]:
    """
    Calculates accurate word count and character count for Khmer text.
    Handles space segmentation as well as zero-width spaces (\u200B).
    """
    if not text:
        return 0, 0
    char_count = len(text)
    # Split text by whitespace and zero-width spaces (\u200B)
    raw_tokens = re.split(r'[\s\u200B\u200C\u200D]+', text)
    tokens = [t for t in raw_tokens if t.strip()]
    word_count = len(tokens)
    return word_count, char_count


def check_khmer_spelling(
    text: str,
    language: str = "km",
    mode: str = "standard",
    custom_dictionary: List[str] = None
) -> Dict[str, Any]:
    """
    Core Khmer Spell Checking Engine.
    Detects spelling mistakes, double spaces, invalid punctuation, and unicode sequence issues.
    Enforces strict protection rules for URLs, Code, Emails, Telegram commands, and Custom Dictionary words.
    """
    if custom_dictionary is None:
        custom_dictionary = []
    
    custom_dict_set = set(w.strip() for w in custom_dictionary if w.strip())

    if not text or not isinstance(text, str):
        return {
            "success": True,
            "originalText": text or "",
            "correctedText": text or "",
            "summary": {"totalIssues": 0, "errors": 0, "warnings": 0, "suggestions": 0, "autoFixable": 0},
            "issues": []
        }

    # Limit to 5,000 characters for safety
    text = text[:5000]

    # Find protected ranges to ignore (URLs, code, emails, commands, hashtags)
    protected_ranges: List[Tuple[int, int]] = []
    for pattern in EXCLUSION_PATTERNS:
        for m in re.finditer(pattern, text):
            protected_ranges.append((m.start(), m.end()))

    issues = []
    issue_id_counter = 1

    # 1. Check Misspelled Khmer Words
    for word_key, (suggestions, explanation, auto_fixable, severity, confidence) in KHMER_DICTIONARY_RULES.items():
        if word_key in custom_dict_set:
            continue
        
        pattern = re.compile(re.escape(word_key))
        for m in pattern.finditer(text):
            start_pos, end_pos = m.span()
            if _is_protected_range(start_pos, end_pos, protected_ranges):
                continue
            
            replacement = suggestions[0] if suggestions else word_key
            issues.append({
                "id": f"issue_{issue_id_counter}",
                "original": word_key,
                "suggestions": suggestions,
                "replacement": replacement,
                "type": "spelling",
                "severity": severity,
                "confidence": confidence,
                "start": start_pos,
                "end": end_pos,
                "explanation": explanation,
                "autoFixable": auto_fixable and confidence >= 0.90
            })
            issue_id_counter += 1

    # 2. Check Double Spaces (Spacing Error)
    space_pattern = re.compile(r' {2,}')
    for m in space_pattern.finditer(text):
        start_pos, end_pos = m.span()
        if _is_protected_range(start_pos, end_pos, protected_ranges):
            continue
        issues.append({
            "id": f"issue_{issue_id_counter}",
            "original": m.group(0),
            "suggestions": [" "],
            "replacement": " ",
            "type": "spacing",
            "severity": "warning",
            "confidence": 0.98,
            "start": start_pos,
            "end": end_pos,
            "explanation": "មានចន្លោះច្រើនជាប់គ្នា។ គួរប្រើចន្លោះតែមួយ។",
            "autoFixable": True
        })
        issue_id_counter += 1

    # 3. Check Space Before Punctuation (e.g., " ។" -> "។")
    punct_pattern = re.compile(r'\s+([។៖ៗ៕])')
    for m in punct_pattern.finditer(text):
        start_pos, end_pos = m.span()
        if _is_protected_range(start_pos, end_pos, protected_ranges):
            continue
        punct_char = m.group(1)
        issues.append({
            "id": f"issue_{issue_id_counter}",
            "original": m.group(0),
            "suggestions": [punct_char],
            "replacement": punct_char,
            "type": "punctuation",
            "severity": "warning",
            "confidence": 0.95,
            "start": start_pos,
            "end": end_pos,
            "explanation": f"មិនគួរមានចន្លោះនៅខាងមុខសញ្ញា «{punct_char}» ឡើយ។",
            "autoFixable": True
        })
        issue_id_counter += 1

    # 4. Check Repeated Words (e.g. "ពាក្យ ពាក្យ")
    repeat_pattern = re.compile(r'(\b[\u1780-\u17FF]+\b)\s+\1\b')
    for m in repeat_pattern.finditer(text):
        start_pos, end_pos = m.span()
        if _is_protected_range(start_pos, end_pos, protected_ranges):
            continue
        single_word = m.group(1)
        if single_word in custom_dict_set:
            continue
        issues.append({
            "id": f"issue_{issue_id_counter}",
            "original": m.group(0),
            "suggestions": [single_word],
            "replacement": single_word,
            "type": "repeated_word",
            "severity": "warning",
            "confidence": 0.92,
            "start": start_pos,
            "end": end_pos,
            "explanation": f"ពាក្យ «{single_word}» ត្រូវបានសរសេរស្ទួនពីរដងជាប់គ្នា។",
            "autoFixable": True
        })
        issue_id_counter += 1

    # Sort issues by start position ascending
    issues.sort(key=lambda x: x["start"])

    # Calculate Corrected Text (applying autoFixable high confidence issues)
    corrected_text = text
    # Apply in reverse order to preserve index positions
    for issue in sorted(issues, key=lambda x: x["start"], reverse=True):
        if issue["autoFixable"] and issue.get("replacement"):
            s_idx = issue["start"]
            e_idx = issue["end"]
            corrected_text = corrected_text[:s_idx] + issue["replacement"] + corrected_text[e_idx:]

    summary = {
        "totalIssues": len(issues),
        "errors": sum(1 for i in issues if i["severity"] == "error"),
        "warnings": sum(1 for i in issues if i["severity"] == "warning"),
        "suggestions": sum(1 for i in issues if i["severity"] == "suggestion"),
        "autoFixable": sum(1 for i in issues if i["autoFixable"])
    }

    return {
        "success": True,
        "originalText": text,
        "correctedText": corrected_text,
        "summary": summary,
        "issues": issues,
        "aiAssisted": False
    }


async def check_khmer_spelling_ai(
    text: str,
    gemini_service=None,
    language: str = "km",
    mode: str = "standard",
    custom_dictionary: List[str] = None
) -> Dict[str, Any]:
    """
    AI-Enhanced Khmer Spell Checking & Writing Assistant.
    Combines rule-based checks with Google Gemini AI for contextual grammar,
    subscript misalignments, and phrasing improvements.
    """
    if custom_dictionary is None:
        custom_dictionary = []

    # Baseline rule-based results
    base_result = check_khmer_spelling(text, language=language, mode=mode, custom_dictionary=custom_dictionary)
    
    if not text or not text.strip():
        return base_result

    # Try Gemini AI Integration
    try:
        if not gemini_service:
            from config import GEMINI_API_KEY
            if GEMINI_API_KEY:
                from services import GeminiService
                gemini_service = GeminiService(api_key=GEMINI_API_KEY)

        if gemini_service:
            import json
            ai_prompt = f"""
You are an expert Khmer Proofreader, Lexicographer, and AI Writing Assistant powered by Google Gemini AI.
Analyze the following Khmer text for spelling errors, subscript misalignments, spacing mistakes, and phrasing improvements.
Custom dictionary words to ignore: {custom_dictionary or []}

Text to analyze:
"{text}"

Output STRICTLY a JSON object matching this schema with NO extra text or markdown formatting:
{{
  "correctedText": "full corrected text here",
  "issues": [
    {{
      "original": "misspelled word",
      "replacement": "correct word",
      "explanation": "Explanation in natural Khmer",
      "severity": "error",
      "autoFixable": true
    }}
  ]
}}
"""
            # Use mode="raw" so general chatbot prompt doesn't pollute the JSON output format
            raw_ai_response = await gemini_service.generate_text_chat(ai_prompt, mode="raw")
            
            clean_json = raw_ai_response.strip()
            # Extract JSON object block { ... } using regex if present
            json_match = re.search(r'\{[\s\S]*\}', clean_json)
            if json_match:
                clean_json = json_match.group(0)

            ai_data = json.loads(clean_json)
            
            if isinstance(ai_data, dict):
                ai_issues = ai_data.get("issues", [])
                
                # Protected ranges to prevent modifying code/URLs
                protected_ranges: List[Tuple[int, int]] = []
                for pattern in EXCLUSION_PATTERNS:
                    for m in re.finditer(pattern, text):
                        protected_ranges.append((m.start(), m.end()))

                custom_dict_set = set(w.strip() for w in custom_dictionary if w.strip())
                merged_issues = list(base_result["issues"])
                occupied_spans = [(i["start"], i["end"]) for i in merged_issues]

                def _overlaps(s: int, e: int) -> bool:
                    for os, oe in occupied_spans:
                        if max(s, os) < min(e, oe):
                            return True
                    return False

                issue_counter = len(merged_issues) + 1

                for ai_issue in ai_issues:
                    orig = ai_issue.get("original", "").strip()
                    repl = ai_issue.get("replacement", "").strip()
                    exp = ai_issue.get("explanation", "ការណែនាំពី Gemini AI").strip()
                    sev = ai_issue.get("severity", "suggestion").strip().lower()
                    if sev not in ("error", "warning", "suggestion"):
                        sev = "suggestion"
                    auto_fix = bool(ai_issue.get("autoFixable", True))

                    if orig and orig not in custom_dict_set and orig in text:
                        # Find non-overlapping occurrences of original text
                        for match in re.finditer(re.escape(orig), text):
                            s_pos, e_pos = match.span()
                            if not _overlaps(s_pos, e_pos) and not _is_protected_range(s_pos, e_pos, protected_ranges):
                                merged_issues.append({
                                    "id": f"issue_ai_{issue_counter}",
                                    "original": orig,
                                    "suggestions": [repl] if repl else [],
                                    "replacement": repl,
                                    "type": "ai_grammar" if sev != "error" else "spelling",
                                    "severity": sev,
                                    "confidence": 0.95,
                                    "start": s_pos,
                                    "end": e_pos,
                                    "explanation": exp,
                                    "autoFixable": auto_fix
                                })
                                occupied_spans.append((s_pos, e_pos))
                                issue_counter += 1
                                break  # Process first matching span

                merged_issues.sort(key=lambda x: x["start"])

                # Recompute correctedText cleanly from merged issues
                corrected_text = text
                for issue in sorted(merged_issues, key=lambda x: x["start"], reverse=True):
                    if issue.get("autoFixable") and issue.get("replacement") is not None:
                        s_idx = issue["start"]
                        e_idx = issue["end"]
                        corrected_text = corrected_text[:s_idx] + issue["replacement"] + corrected_text[e_idx:]

                base_result["correctedText"] = corrected_text
                base_result["issues"] = merged_issues
                base_result["summary"] = {
                    "totalIssues": len(merged_issues),
                    "errors": sum(1 for i in merged_issues if i["severity"] == "error"),
                    "warnings": sum(1 for i in merged_issues if i["severity"] == "warning"),
                    "suggestions": sum(1 for i in merged_issues if i["severity"] == "suggestion"),
                    "autoFixable": sum(1 for i in merged_issues if i.get("autoFixable", False))
                }
                base_result["aiAssisted"] = True

    except Exception as err:
        logging.warning(f"AI Spell Check Fallback to Rule-Based: {err}")

    return base_result
