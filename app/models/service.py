from sqlalchemy import (
    Column, Integer, String, Boolean, Enum, DateTime, Text,
    ForeignKey, Numeric, Date, Time
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ServiceStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    technician_assigned = "technician_assigned"
    technician_on_the_way = "technician_on_the_way"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"
    no_show = "no_show"


class ServiceCategory(Base):
    __tablename__ = "service_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    name_ta = Column(String(100))
    name_hi = Column(String(100))
    brand_id = Column(Integer, ForeignKey("brands.id"))  # NULL = applies to all brands
    description = Column(Text)
    base_charge = Column(Numeric(10, 2), default=0)  # visiting charge
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

    brand = relationship("Brand")
    requests = relationship("ServiceRequest", back_populates="service_category")


class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_number = Column(String(20), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    service_category_id = Column(Integer, ForeignKey("service_categories.id"), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    device_description = Column(Text, nullable=False)
    issue_description = Column(Text, nullable=False)
    service_address = Column(Text, nullable=False)  # JSON serialized address
    preferred_date = Column(Date, nullable=False)
    preferred_time = Column(String(20))  # "10:00 AM - 12:00 PM"
    status = Column(Enum(ServiceStatus), default=ServiceStatus.pending, index=True)
    technician_name = Column(String(200))
    technician_phone = Column(String(15))
    confirmed_date = Column(Date)
    confirmed_time = Column(String(20))
    visited_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    resolution_notes = Column(Text)
    parts_used = Column(Text)
    visiting_charge = Column(Numeric(10, 2), default=0)
    service_charge = Column(Numeric(10, 2), default=0)
    parts_charge = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(12, 2), default=0)
    payment_status = Column(String(20), default="pending")
    invoice_url = Column(String(500))
    cancelled_at = Column(DateTime(timezone=True))
    cancel_reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    customer = relationship("Customer", back_populates="service_requests")
    vendor = relationship("Vendor", back_populates="service_requests")
    service_category = relationship("ServiceCategory", back_populates="requests")
    brand = relationship("Brand")
    tracking = relationship("ServiceTracking", back_populates="service_request",
                           order_by="ServiceTracking.created_at")


class ServiceTracking(Base):
    __tablename__ = "service_tracking"

    id = Column(Integer, primary_key=True, index=True)
    service_request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False)
    note = Column(Text)
    updated_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    service_request = relationship("ServiceRequest", back_populates="tracking")
