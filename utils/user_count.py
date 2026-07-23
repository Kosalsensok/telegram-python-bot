def format_user_count(count: int) -> str:
    """
    Format user count for Bot Profile and UI display.

    Formatting Rules:
    - 0 -> 0
    - 999 -> 999
    - 1000 -> 1K
    - 1250 -> 1.2K
    - 15000 -> 15K
    - 1000000 -> 1M
    - 1250000 -> 1.2M
    """
    if count < 0:
        return "0"

    if count < 1000:
        return str(count)
    elif count < 1_000_000:
        val = count / 1000.0
        formatted = f"{val:.1f}".rstrip('0').rstrip('.')
        return f"{formatted}K"
    else:
        val = count / 1_000_000.0
        formatted = f"{val:.1f}".rstrip('0').rstrip('.')
        return f"{formatted}M"
