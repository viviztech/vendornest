"""Multilingual support: EN, TA, HI."""
from fastapi import Request
from sqlalchemy.orm import Session
from app.models.notification import TranslationString

SUPPORTED_LANGS = ["en", "ta", "hi"]
DEFAULT_LANG = "en"


def get_lang(request: Request) -> str:
    """Extract language from cookie or Accept-Language header."""
    lang = request.cookies.get("lang")
    if lang in SUPPORTED_LANGS:
        return lang
    header = request.headers.get("Accept-Language", "")
    for part in header.split(","):
        code = part.strip().split(";")[0][:2].lower()
        if code in SUPPORTED_LANGS:
            return code
    return DEFAULT_LANG


def t(db: Session, key: str, lang: str = "en", **kwargs) -> str:
    """Fetch translated string from DB. Falls back to key."""
    record = db.query(TranslationString).filter_by(key=key, lang=lang).first()
    if not record and lang != DEFAULT_LANG:
        record = db.query(TranslationString).filter_by(key=key, lang=DEFAULT_LANG).first()
    if record:
        try:
            return record.value.format(**kwargs)
        except Exception:
            return record.value
    return key


def get_localized_name(obj, lang: str) -> str:
    """Get translated name field from model if available."""
    field = f"name_{lang}"
    val = getattr(obj, field, None)
    return val if val else getattr(obj, "name", "")
