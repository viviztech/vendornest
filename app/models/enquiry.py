from sqlalchemy import (
    Column, Integer, String, Boolean, Enum, DateTime, Text,
    ForeignKey, Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class EnquiryStatus(str, enum.Enum):
    open = "open"           # just submitted, awaiting vendor quotes
    quoted = "quoted"       # at least one vendor has responded
    closed = "closed"       # customer accepted a quote / admin closed
    expired = "expired"


class EnquiryResponseStatus(str, enum.Enum):
    submitted = "submitted"     # vendor sent quote
    followup = "followup"       # follow-up conversation active
    accepted = "accepted"       # customer accepted this vendor's quote
    rejected = "rejected"       # customer rejected this vendor's quote


class Enquiry(Base):
    """A user enquiry broadcast to ALL approved vendors."""
    __tablename__ = "enquiries"

    id = Column(Integer, primary_key=True, index=True)
    enquiry_number = Column(String(20), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)

    # Requirement details (safe to share)
    product_service_type = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(200), nullable=False)
    pincode = Column(String(6), nullable=False)

    status = Column(Enum(EnquiryStatus), default=EnquiryStatus.open, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    customer = relationship("Customer", back_populates="enquiries")
    responses = relationship("EnquiryVendorResponse", back_populates="enquiry", cascade="all, delete-orphan")


class EnquiryVendorResponse(Base):
    """A vendor's quote for a specific enquiry — no attachments allowed."""
    __tablename__ = "enquiry_vendor_responses"

    id = Column(Integer, primary_key=True, index=True)
    enquiry_id = Column(Integer, ForeignKey("enquiries.id"), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)

    # Quote fields
    price = Column(Numeric(12, 2), nullable=False)
    eta = Column(String(200), nullable=False)       # free-text ETA e.g. "3–5 working days"
    message = Column(Text, nullable=False)

    status = Column(Enum(EnquiryResponseStatus), default=EnquiryResponseStatus.submitted, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    enquiry = relationship("Enquiry", back_populates="responses")
    vendor = relationship("Vendor")
    messages = relationship("EnquiryMessage", back_populates="response", cascade="all, delete-orphan")


class EnquiryMessage(Base):
    """Follow-up messages on a specific vendor response thread — portal only."""
    __tablename__ = "enquiry_messages"

    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("enquiry_vendor_responses.id"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sender_role = Column(String(20), nullable=False)   # customer | vendor | admin
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    response = relationship("EnquiryVendorResponse", back_populates="messages")
    sender = relationship("User")
