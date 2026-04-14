from sqlalchemy import (
    Column, Integer, String, Boolean, Enum, DateTime, Text,
    ForeignKey, Numeric, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class OrderStatus(str, enum.Enum):
    pending_payment = "pending_payment"
    payment_failed = "payment_failed"
    confirmed = "confirmed"
    processing = "processing"
    packed = "packed"
    dispatched = "dispatched"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    cancelled = "cancelled"
    refund_initiated = "refund_initiated"
    refunded = "refunded"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"
    partially_refunded = "partially_refunded"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(20), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending_payment, index=True)
    subtotal = Column(Numeric(12, 2), nullable=False)
    gst_amount = Column(Numeric(12, 2), default=0)
    delivery_charge = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(12, 2), nullable=False)
    commission_percent = Column(Numeric(5, 2), nullable=False)
    commission_amount = Column(Numeric(12, 2), nullable=False)
    vendor_payout = Column(Numeric(12, 2), nullable=False)
    delivery_address = Column(JSON, nullable=False)  # snapshot at order time
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    razorpay_order_id = Column(String(100), unique=True)
    razorpay_payment_id = Column(String(100))
    razorpay_signature = Column(String(300))
    delhivery_awb = Column(String(100))
    delhivery_waybill = Column(String(100))
    invoice_url = Column(String(500))
    notes = Column(Text)
    cancelled_at = Column(DateTime(timezone=True))
    cancel_reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    customer = relationship("Customer", back_populates="orders")
    vendor = relationship("Vendor", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    tracking = relationship("OrderTracking", back_populates="order", order_by="OrderTracking.created_at")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    vendor_product_id = Column(Integer, ForeignKey("vendor_products.id"), nullable=False)
    product_snapshot = Column(JSON)  # product name/details at order time
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    gst_rate = Column(Numeric(5, 2), default=18.0)
    gst_amount = Column(Numeric(12, 2), default=0)
    total_price = Column(Numeric(12, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    vendor_product = relationship("VendorProduct", back_populates="order_items")


class OrderTracking(Base):
    __tablename__ = "order_tracking"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False)
    description = Column(Text)
    location = Column(String(200))
    source = Column(String(20), default="system")  # system | delhivery | vendor
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order", back_populates="tracking")
