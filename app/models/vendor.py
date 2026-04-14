from sqlalchemy import (
    Column, Integer, String, Boolean, Enum, DateTime, Text,
    ForeignKey, Numeric, Time
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class VendorStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    suspended = "suspended"


class DayOfWeek(str, enum.Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    business_name = Column(String(300), nullable=False)
    business_slug = Column(String(300), unique=True, index=True)
    description = Column(Text)
    gst_number = Column(String(20), unique=True)
    pan_number = Column(String(20))
    address_line = Column(Text)
    state_id = Column(Integer, ForeignKey("states.id"))
    district_id = Column(Integer, ForeignKey("districts.id"))
    pincode_id = Column(Integer, ForeignKey("pincodes.id"))
    logo_url = Column(String(500))
    status = Column(Enum(VendorStatus), default=VendorStatus.pending, index=True)
    rejection_reason = Column(Text)
    commission_override = Column(Numeric(5, 2))  # NULL = use global default
    bank_account_number = Column(String(30))
    bank_ifsc = Column(String(15))
    bank_account_name = Column(String(200))
    rating = Column(Numeric(3, 2), default=0.0)
    total_orders = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    approved_at = Column(DateTime(timezone=True))
    approved_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="vendor", foreign_keys=[user_id])
    state = relationship("State")
    district = relationship("District")
    pincode = relationship("Pincode")
    brands = relationship("VendorBrand", back_populates="vendor")
    pincodes = relationship("VendorPincode", back_populates="vendor")
    documents = relationship("VendorDocument", back_populates="vendor")
    products = relationship("VendorProduct", back_populates="vendor")
    service_slots = relationship("VendorServiceSlot", back_populates="vendor")
    orders = relationship("Order", back_populates="vendor")
    service_requests = relationship("ServiceRequest", back_populates="vendor")
    reviews = relationship("VendorReview", back_populates="vendor")


class VendorBrand(Base):
    __tablename__ = "vendor_brands"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    auth_doc_url = Column(String(500))
    verified = Column(Boolean, default=False)
    verified_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    vendor = relationship("Vendor", back_populates="brands")
    brand = relationship("Brand")


class VendorPincode(Base):
    __tablename__ = "vendor_pincodes"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    pincode_id = Column(Integer, ForeignKey("pincodes.id"), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    vendor = relationship("Vendor", back_populates="pincodes")
    pincode = relationship("Pincode")


class VendorDocument(Base):
    __tablename__ = "vendor_documents"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    doc_type = Column(String(50))  # gst_cert | pan | brand_auth | other
    doc_url = Column(String(500), nullable=False)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    vendor = relationship("Vendor", back_populates="documents")


class VendorServiceSlot(Base):
    __tablename__ = "vendor_service_slots"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    day_of_week = Column(Enum(DayOfWeek), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    max_bookings = Column(Integer, default=5)
    is_active = Column(Boolean, default=True)

    vendor = relationship("Vendor", back_populates="service_slots")


class VendorReview(Base):
    __tablename__ = "vendor_reviews"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"))
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text)
    is_visible = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    vendor = relationship("Vendor", back_populates="reviews")
    customer = relationship("Customer")
