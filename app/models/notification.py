from sqlalchemy import (
    Column, Integer, String, Boolean, Enum, DateTime, Text, ForeignKey
)
from sqlalchemy.sql import func
from app.database import Base
import enum


class NotificationType(str, enum.Enum):
    email = "email"
    sms = "sms"
    whatsapp = "whatsapp"


class NotificationStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"


class NotificationTemplate(Base):
    __tablename__ = "notification_templates"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(NotificationType), nullable=False)
    event = Column(String(100), nullable=False)  # order_confirmed, service_booked, etc.
    lang = Column(String(5), default="en")
    subject = Column(String(300))
    body_template = Column(Text, nullable=False)  # Jinja2 template string
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(Enum(NotificationType), nullable=False)
    event = Column(String(100))
    recipient = Column(String(255))  # email or phone
    subject = Column(String(300))
    body = Column(Text)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.pending)
    error_message = Column(Text)
    sent_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TranslationString(Base):
    __tablename__ = "translation_strings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(200), nullable=False, index=True)
    lang = Column(String(5), nullable=False)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        __import__("sqlalchemy").UniqueConstraint("key", "lang", name="uq_translation_key_lang"),
    )
