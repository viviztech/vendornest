from sqlalchemy import (
    Column, Integer, String, Boolean, Enum, DateTime, ForeignKey, Numeric, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class CommissionScope(str, enum.Enum):
    global_ = "global"
    brand = "brand"
    vendor = "vendor"


class SettlementStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    settled = "settled"
    failed = "failed"


class CommissionConfig(Base):
    __tablename__ = "commission_configs"

    id = Column(Integer, primary_key=True, index=True)
    scope = Column(Enum(CommissionScope), nullable=False)
    ref_id = Column(Integer)  # brand_id or vendor_id depending on scope
    percentage = Column(Numeric(5, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(Integer, primary_key=True, index=True)
    settlement_number = Column(String(20), unique=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    order_count = Column(Integer, default=0)
    gross_amount = Column(Numeric(15, 2), nullable=False)
    commission_amount = Column(Numeric(15, 2), nullable=False)
    tds_amount = Column(Numeric(15, 2), default=0)
    net_amount = Column(Numeric(15, 2), nullable=False)
    status = Column(Enum(SettlementStatus), default=SettlementStatus.pending)
    bank_reference = Column(String(100))
    notes = Column(Text)
    initiated_by = Column(Integer, ForeignKey("users.id"))
    settled_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    vendor = relationship("Vendor")
