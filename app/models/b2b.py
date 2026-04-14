from sqlalchemy import (
    Column, Integer, String, Boolean, Enum, DateTime, Text,
    ForeignKey, Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class B2BQuoteStatus(str, enum.Enum):
    submitted = "submitted"
    vendor_reviewing = "vendor_reviewing"
    quote_sent = "quote_sent"
    negotiating = "negotiating"
    accepted = "accepted"
    rejected = "rejected"
    converted_to_order = "converted_to_order"
    expired = "expired"


class B2BQuote(Base):
    __tablename__ = "b2b_quotes"

    id = Column(Integer, primary_key=True, index=True)
    quote_number = Column(String(20), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    business_name = Column(String(300), nullable=False)
    business_gst = Column(String(20))
    requirements = Column(Text, nullable=False)
    delivery_pincode = Column(String(6))
    delivery_address = Column(Text)
    expected_delivery_date = Column(DateTime(timezone=True))
    status = Column(Enum(B2BQuoteStatus), default=B2BQuoteStatus.submitted, index=True)
    vendor_note = Column(Text)
    quoted_total = Column(Numeric(15, 2))
    validity_days = Column(Integer, default=7)
    expires_at = Column(DateTime(timezone=True))
    converted_order_id = Column(Integer, ForeignKey("orders.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    customer = relationship("Customer", back_populates="b2b_quotes")
    vendor = relationship("Vendor")
    items = relationship("B2BQuoteItem", back_populates="quote")
    messages = relationship("B2BMessage", back_populates="quote")


class B2BQuoteItem(Base):
    __tablename__ = "b2b_quote_items"

    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Integer, ForeignKey("b2b_quotes.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))
    product_name = Column(String(300))  # for free-text items
    quantity = Column(Integer, nullable=False, default=1)
    vendor_price = Column(Numeric(12, 2))
    note = Column(Text)

    quote = relationship("B2BQuote", back_populates="items")
    product = relationship("Product")


class B2BMessage(Base):
    __tablename__ = "b2b_messages"

    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Integer, ForeignKey("b2b_quotes.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sender_role = Column(String(20))  # customer | vendor | admin
    message = Column(Text, nullable=False)
    attachment_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    quote = relationship("B2BQuote", back_populates="messages")
    sender = relationship("User")
