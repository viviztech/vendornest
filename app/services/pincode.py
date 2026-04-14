"""Pincode search service — find vendors by pincode."""
from typing import List
from sqlalchemy.orm import Session
from app.models.location import Pincode
from app.models.vendor import Vendor, VendorPincode, VendorStatus


def find_pincode(db: Session, pincode_str: str):
    return db.query(Pincode).filter(
        Pincode.pincode == pincode_str.strip(),
        Pincode.is_active == True,
    ).first()


def get_vendors_by_pincode(db: Session, pincode_str: str) -> List[Vendor]:
    """Return all approved vendors who service this pincode."""
    pincode = find_pincode(db, pincode_str)
    if not pincode:
        return []

    vendors = (
        db.query(Vendor)
        .join(VendorPincode, VendorPincode.vendor_id == Vendor.id)
        .filter(
            VendorPincode.pincode_id == pincode.id,
            VendorPincode.is_active == True,
            Vendor.status == VendorStatus.approved,
        )
        .order_by(Vendor.is_featured.desc(), Vendor.rating.desc())
        .all()
    )
    return vendors


def get_pincode_info(db: Session, pincode_str: str) -> dict:
    pc = find_pincode(db, pincode_str)
    if not pc:
        return {}
    return {
        "pincode": pc.pincode,
        "post_office": pc.post_office,
        "district": pc.district.name if pc.district else "",
        "state": pc.state.name if pc.state else "",
    }
