"""Admin vendor management."""
from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_superadmin
from app.models.vendor import Vendor, VendorStatus
from app.models.user import User
from app.services.notification import send_vendor_approval_email

router = APIRouter(prefix="/admin/vendors", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def vendor_list(
    request: Request,
    status: str = Query("all"),
    page: int = Query(1),
    db: Session = Depends(get_db),
    admin=Depends(require_superadmin),
):
    query = db.query(Vendor)
    if status != "all":
        query = query.filter(Vendor.status == status)
    total = query.count()
    size = 20
    vendors = query.order_by(Vendor.created_at.desc()).offset((page - 1) * size).limit(size).all()
    return templates.TemplateResponse("admin/vendors/list.html", {
        "request": request, "admin": admin,
        "vendors": vendors, "status_filter": status,
        "total": total, "page": page, "pages": (total + size - 1) // size,
    })


@router.get("/{vendor_id}", response_class=HTMLResponse)
def vendor_detail(request: Request, vendor_id: int, db: Session = Depends(get_db), admin=Depends(require_superadmin)):
    vendor = db.query(Vendor).filter_by(id=vendor_id).first()
    if not vendor:
        return RedirectResponse("/admin/vendors")
    return templates.TemplateResponse("admin/vendors/detail.html", {
        "request": request, "admin": admin, "vendor": vendor
    })


@router.post("/{vendor_id}/approve")
def approve_vendor(vendor_id: int, db: Session = Depends(get_db), admin=Depends(require_superadmin)):
    from datetime import datetime, timezone
    vendor = db.query(Vendor).filter_by(id=vendor_id).first()
    if vendor:
        vendor.status = VendorStatus.approved
        vendor.approved_at = datetime.now(timezone.utc)
        vendor.approved_by = admin.id
        db.commit()
        send_vendor_approval_email(vendor.user.email, vendor.user.name, approved=True)
    return RedirectResponse(f"/admin/vendors/{vendor_id}", status_code=303)


@router.post("/{vendor_id}/reject")
def reject_vendor(
    vendor_id: int,
    reason: str = Form(""),
    db: Session = Depends(get_db),
    admin=Depends(require_superadmin),
):
    vendor = db.query(Vendor).filter_by(id=vendor_id).first()
    if vendor:
        vendor.status = VendorStatus.rejected
        vendor.rejection_reason = reason
        db.commit()
        send_vendor_approval_email(vendor.user.email, vendor.user.name, approved=False, reason=reason)
    return RedirectResponse(f"/admin/vendors/{vendor_id}", status_code=303)


@router.post("/{vendor_id}/suspend")
def suspend_vendor(vendor_id: int, db: Session = Depends(get_db), admin=Depends(require_superadmin)):
    vendor = db.query(Vendor).filter_by(id=vendor_id).first()
    if vendor:
        vendor.status = VendorStatus.suspended
        db.commit()
    return RedirectResponse(f"/admin/vendors/{vendor_id}", status_code=303)
