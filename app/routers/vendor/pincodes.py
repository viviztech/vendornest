"""Vendor pincode coverage management."""
from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_vendor
from app.models.vendor import Vendor, VendorPincode
from app.models.location import Pincode, State, District

router = APIRouter(prefix="/vendor/pincodes", tags=["vendor"])
templates = Jinja2Templates(directory="app/templates")


def get_vendor(user, db):
    return db.query(Vendor).filter_by(user_id=user.id).first()


@router.get("", response_class=HTMLResponse)
def pincode_list(request: Request, db: Session = Depends(get_db), user=Depends(require_vendor)):
    vendor = get_vendor(user, db)
    covered = db.query(VendorPincode).filter_by(vendor_id=vendor.id, is_active=True).all()
    states = db.query(State).filter_by(is_active=True).order_by(State.name).all()
    return templates.TemplateResponse("vendor/pincodes.html", {
        "request": request, "user": user, "vendor": vendor,
        "covered_pincodes": covered, "states": states,
    })


@router.post("/add")
def add_pincode(
    pincode_str: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(require_vendor),
):
    vendor = get_vendor(user, db)
    pc = db.query(Pincode).filter_by(pincode=pincode_str.strip()).first()
    if pc:
        existing = db.query(VendorPincode).filter_by(vendor_id=vendor.id, pincode_id=pc.id).first()
        if not existing:
            db.add(VendorPincode(vendor_id=vendor.id, pincode_id=pc.id))
            db.commit()
    return RedirectResponse("/vendor/pincodes", status_code=303)


@router.post("/{vp_id}/remove")
def remove_pincode(vp_id: int, db: Session = Depends(get_db), user=Depends(require_vendor)):
    vendor = get_vendor(user, db)
    vp = db.query(VendorPincode).filter_by(id=vp_id, vendor_id=vendor.id).first()
    if vp:
        vp.is_active = False
        db.commit()
    return RedirectResponse("/vendor/pincodes", status_code=303)
