"""Utility helpers."""
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
