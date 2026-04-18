"""Utility helpers."""
import re
import random
import string
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")


def generate_order_number() -> str:
    ts = datetime.now(IST).strftime("%Y%m%d")
    rand = "".join(random.choices(string.digits, k=6))
    return f"VN{ts}{rand}"


def generate_request_number(prefix: str = "SR") -> str:
    ts = datetime.now(IST).strftime("%Y%m%d")
    rand = "".join(random.choices(string.digits, k=6))
    return f"{prefix}{ts}{rand}"


def generate_quote_number() -> str:
    return generate_request_number("QT")


def generate_settlement_number() -> str:
    return generate_request_number("ST")


def generate_enquiry_number() -> str:
    return generate_request_number("ENQ")


# Patterns that could reveal phone or email — blocked in portal messages
_PHONE_RE = re.compile(
    r"(\+?91[\s\-]?)?[6-9]\d{9}"          # Indian mobile
    r"|(\+?1[\s\-]?)?\(?\d{3}\)?[\s\-]\d{3}[\s\-]\d{4}",  # International
    re.IGNORECASE,
)
_EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+\-]+@[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}", re.IGNORECASE)


def contains_contact_info(text: str) -> bool:
    """Return True if text contains a phone number or email address."""
    return bool(_PHONE_RE.search(text) or _EMAIL_RE.search(text))


def sanitize_message(text: str) -> str:
    """Replace detected contact info with [BLOCKED] to prevent direct contact sharing."""
    text = _PHONE_RE.sub("[BLOCKED]", text)
    text = _EMAIL_RE.sub("[BLOCKED]", text)
    return text


def format_currency(amount: float) -> str:
    return f"₹{amount:,.2f}"


def paginate(query, page: int, size: int):
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size,
    }
