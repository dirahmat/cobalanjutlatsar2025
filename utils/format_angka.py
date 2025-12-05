import re

def sanitize_number(s):
    """Extract digits and convert to integer."""
    if not s:
        return 0
    digits = re.sub(r"[^\d]", "", str(s))
    return int(digits) if digits else 0


def format_with_dots(num):
    """Format integer with dot separators."""
    try:
        return f"{int(num):,}".replace(",", ".")
    except:
        return "-"
