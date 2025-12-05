import re

def format_with_dots(num):
    return f"{num:,}".replace(",", ".")

def sanitize_number(s):
    if not s:
        return 0
    digits = re.sub(r"[^\d]", "", str(s))
    return int(digits) if digits else 0
