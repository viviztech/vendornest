"""Commission calculation engine."""
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.commission import CommissionConfig, CommissionScope
from app.config import settings


def get_commission_rate(db: Session, vendor_id: int, brand_id: int) -> Decimal:
    """
    Priority: vendor-specific > brand-specific > global default
    """
    # 1. Vendor override
    vendor_cfg = db.query(CommissionConfig).filter(
        CommissionConfig.scope == CommissionScope.vendor,
        CommissionConfig.ref_id == vendor_id,
        CommissionConfig.is_active == True,
    ).first()
    if vendor_cfg:
        return Decimal(str(vendor_cfg.percentage))

    # 2. Brand rate
    brand_cfg = db.query(CommissionConfig).filter(
        CommissionConfig.scope == CommissionScope.brand,
        CommissionConfig.ref_id == brand_id,
        CommissionConfig.is_active == True,
    ).first()
    if brand_cfg:
        return Decimal(str(brand_cfg.percentage))

    # 3. Global default
    global_cfg = db.query(CommissionConfig).filter(
        CommissionConfig.scope == CommissionScope.global_,
        CommissionConfig.is_active == True,
    ).first()
    if global_cfg:
        return Decimal(str(global_cfg.percentage))

    # 4. Hard fallback from settings
    return Decimal(str(settings.default_commission_percent))


def calculate_commission(total_amount: Decimal, rate: Decimal) -> dict:
    commission = (total_amount * rate / 100).quantize(Decimal("0.01"))
    vendor_payout = total_amount - commission
    return {
        "commission_percent": float(rate),
        "commission_amount": float(commission),
        "vendor_payout": float(vendor_payout),
    }
