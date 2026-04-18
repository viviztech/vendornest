from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    email = Column(String(255))
    phone = Column(String(15))
    city = Column(String(200))
    pincode = Column(String(6))
    is_b2b = Column(Boolean, default=False)
    company_name = Column(String(300))
    gst_number = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="customer")
    addresses = relationship("CustomerAddress", back_populates="customer")
    orders = relationship("Order", back_populates="customer")
    service_requests = relationship("ServiceRequest", back_populates="customer")
    b2b_quotes = relationship("B2BQuote", back_populates="customer")
    enquiries = relationship("Enquiry", back_populates="customer")


class CustomerAddress(Base):
    __tablename__ = "customer_addresses"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    label = Column(String(50), default="Home")  # Home | Office | Other
    name = Column(String(200), nullable=False)
    phone = Column(String(15), nullable=False)
    address_line1 = Column(Text, nullable=False)
    address_line2 = Column(Text)
    city = Column(String(100), nullable=False)
    pincode_id = Column(Integer, ForeignKey("pincodes.id"), nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer", back_populates="addresses")
    pincode = relationship("Pincode")
    state = relationship("State")
