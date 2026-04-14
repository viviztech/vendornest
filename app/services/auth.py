"""
Auth service: OTP generation/verification, JWT tokens, password hashing.
Email OTP is the primary login method. Password login for admin/vendor.
"""
import random
import string
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt as _bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User, OTPLog, UserRole


# ── Password ───────────────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False

# ── OTP ────────────────────────────────────────────────────────────────────────
def generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))

def hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode()).hexdigest()

def create_otp_record(db: Session, email: str, purpose: str = "login") -> str:
    otp = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.otp_expire_minutes)

    # Invalidate previous OTPs for same email+purpose
    db.query(OTPLog).filter(
        OTPLog.email == email,
        OTPLog.purpose == purpose,
        OTPLog.verified == False,
    ).delete()

    record = OTPLog(
        email=email,
        otp_hash=hash_otp(otp),
        purpose=purpose,
        expires_at=expires_at,
    )
    db.add(record)
    db.commit()
    return otp

def verify_otp(db: Session, email: str, otp: str, purpose: str = "login") -> bool:
    record = db.query(OTPLog).filter(
        OTPLog.email == email,
        OTPLog.purpose == purpose,
        OTPLog.verified == False,
        OTPLog.expires_at > datetime.now(timezone.utc),
    ).order_by(OTPLog.created_at.desc()).first()

    if not record:
        return False
    if record.otp_hash != hash_otp(otp):
        return False

    record.verified = True
    record.verified_at = datetime.now(timezone.utc)
    db.commit()
    return True

# ── JWT ────────────────────────────────────────────────────────────────────────
def create_access_token(user_id: int, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    payload = {"sub": str(user_id), "role": role, "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def create_refresh_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.jwt_refresh_token_expire_days
    )
    payload = {"sub": str(user_id), "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None

# ── User helpers ───────────────────────────────────────────────────────────────
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email.lower().strip()).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user or not user.hashed_password:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user
