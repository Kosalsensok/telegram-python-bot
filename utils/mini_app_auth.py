# utils/mini_app_auth.py
"""
Telegram Web App / Mini App InitData Authentication helper.
Validates HMAC-SHA256 signature using Telegram Bot Token.
"""
import hmac
import hashlib
from urllib.parse import parse_qs, unquote

def validate_telegram_init_data(init_data: str, bot_token: str) -> bool:
    """
    Validates Telegram WebApp initData query string.
    Returns True if valid signature, False otherwise.
    """
    if not init_data or not bot_token:
        return False

    try:
        parsed_data = parse_qs(init_data, keep_blank_values=True)
        hash_val = parsed_data.get("hash", [None])[0]
        if not hash_val:
            return False

        # Filter out hash key and sort remaining data_check_string
        data_pairs = []
        for key, vals in parsed_data.items():
            if key != "hash":
                data_pairs.append(f"{key}={vals[0]}")
        data_pairs.sort()
        data_check_string = "\n".join(data_pairs)

        # Secret key = HMAC_SHA256("WebAppData", bot_token)
        secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()

        return hmac.compare_digest(calculated_hash, hash_val)
    except Exception:
        return False
