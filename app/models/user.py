from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    superadmin = "superadmin"
    vendor = "vendor"
    customer = "customer"


class LangPref(str, enum.Enum):
    en = "en"
    ta = "ta"
    hi = "hi"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(15), unique=True, index=True)
    name = Column(String(200), nullable=False)
    hashed_password = Column(String(255))
    role = Column(Enum(UserRole), nullable=False, default=UserRole.customer)
    lang_pref = Column(Enum(LangPref), default=LangPref.en)
    is_active = Column(Boolean, default=True)
    is_email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime(timezone=True))
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    vendor = relationship("Vendor", back_populates="user", uselist=False,
                          foreign_keys="Vendor.user_id")
    customer = relationship("Customer", back_populates="user", uselist=False)


class OTPLog(Base):
    __tablename__ = "otp_logs"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    otp_hash = Column(String(255), nullable=False)
    purpose = Column(String(50), default="login")  # login | register | reset
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified = Column(Boolean, default=False)
    verified_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_hash = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
