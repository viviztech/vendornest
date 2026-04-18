"""Vendor dashboard."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_vendor
from app.models.vendor import Vendor
from app.models.order import Order, OrderStatus
from app.models.service import ServiceRequest
from app.models.enquiry import Enquiry, EnquiryStatus, EnquiryVendorResponse, EnquiryResponseStatus

router = APIRouter(prefix="/vendor", tags=["vendor"])
templates = Jinja2Templates(directory="app/templates")


def get_vendor(user, db):
    return db.query(Vendor).filter_by(user_id=user.id).first()


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), user=Depends(require_vendor)):
    vendor = get_vendor(user, db)
    if not vendor:
        return templates.TemplateResponse("vendor/not_approved.html", {"request": request})

    open_enquiry_count = db.query(Enquiry).filter(
        Enquiry.status.in_([EnquiryStatus.open, EnquiryStatus.quoted])
    ).count()
    my_quotes_count = db.query(EnquiryVendorResponse).filter_by(vendor_id=vendor.id).count()
    accepted_quotes_count = db.query(EnquiryVendorResponse).filter_by(
        vendor_id=vendor.id, status=EnquiryResponseStatus.accepted
    ).count()

    stats = {
        "open_enquiries": open_enquiry_count,
        "my_quotes": my_quotes_count,
        "accepted_quotes": accepted_quotes_count,
        "total_orders": db.query(Order).filter_by(vendor_id=vendor.id).count(),
        "pending_orders": db.query(Order).filter_by(vendor_id=vendor.id, status=OrderStatus.confirmed).count(),
        "total_services": db.query(ServiceRequest).filter_by(vendor_id=vendor.id).count(),
        "total_products": len(vendor.products),
    }
    recent_orders = db.query(Order).filter_by(vendor_id=vendor.id).order_by(Order.created_at.desc()).limit(5).all()
    return templates.TemplateResponse("vendor/dashboard.html", {
        "request": request, "user": user, "vendor": vendor,
        "stats": stats, "recent_orders": recent_orders,
    })
