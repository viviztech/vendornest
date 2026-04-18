"""Admin dashboard."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.dependencies import require_superadmin
from app.models.user import User
from app.models.vendor import Vendor, VendorStatus
from app.models.order import Order, OrderStatus
from app.models.service import ServiceRequest
from app.models.enquiry import Enquiry, EnquiryStatus

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), admin=Depends(require_superadmin)):
    stats = {
        "total_vendors": db.query(Vendor).count(),
        "pending_vendors": db.query(Vendor).filter_by(status=VendorStatus.pending).count(),
        "total_customers": db.query(User).filter_by(role="customer").count(),
        "total_orders": db.query(Order).count(),
        "confirmed_orders": db.query(Order).filter(
            Order.status.notin_([OrderStatus.pending_payment, OrderStatus.payment_failed])
        ).count(),
        "pending_services": db.query(ServiceRequest).filter_by(status="pending").count(),
        "total_enquiries": db.query(Enquiry).count(),
        "open_enquiries": db.query(Enquiry).filter_by(status=EnquiryStatus.open).count(),
        "quoted_enquiries": db.query(Enquiry).filter_by(status=EnquiryStatus.quoted).count(),
        "closed_enquiries": db.query(Enquiry).filter_by(status=EnquiryStatus.closed).count(),
    }
    recent_vendors = db.query(Vendor).order_by(Vendor.created_at.desc()).limit(5).all()
    recent_orders = db.query(Order).order_by(Order.created_at.desc()).limit(5).all()
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request, "admin": admin,
        "stats": stats, "recent_vendors": recent_vendors, "recent_orders": recent_orders,
    })
