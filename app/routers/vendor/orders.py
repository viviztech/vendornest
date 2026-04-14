"""Vendor order management."""
from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_vendor
from app.models.vendor import Vendor
from app.models.order import Order, OrderStatus, OrderTracking
from app.services.delivery import create_shipment

router = APIRouter(prefix="/vendor/orders", tags=["vendor"])
templates = Jinja2Templates(directory="app/templates")


def get_vendor(user, db):
    return db.query(Vendor).filter_by(user_id=user.id).first()


@router.get("", response_class=HTMLResponse)
def order_list(
    request: Request,
    status: str = Query("all"),
    page: int = Query(1),
    db: Session = Depends(get_db),
    user=Depends(require_vendor),
):
    vendor = get_vendor(user, db)
    query = db.query(Order).filter_by(vendor_id=vendor.id)
    if status != "all":
        query = query.filter(Order.status == status)
    total = query.count()
    size = 20
    orders = query.order_by(Order.created_at.desc()).offset((page - 1) * size).limit(size).all()
    return templates.TemplateResponse("vendor/orders/list.html", {
        "request": request, "user": user, "vendor": vendor,
        "orders": orders, "status_filter": status,
        "total": total, "page": page, "pages": (total + size - 1) // size,
        "statuses": [s.value for s in OrderStatus],
    })


@router.get("/{order_id}", response_class=HTMLResponse)
def order_detail(request: Request, order_id: int, db: Session = Depends(get_db), user=Depends(require_vendor)):
    vendor = get_vendor(user, db)
    order = db.query(Order).filter_by(id=order_id, vendor_id=vendor.id).first()
    if not order:
        return RedirectResponse("/vendor/orders")
    return templates.TemplateResponse("vendor/orders/detail.html", {
        "request": request, "user": user, "vendor": vendor, "order": order,
    })


@router.post("/{order_id}/update-status")
def update_order_status(
    order_id: int,
    new_status: str = Form(...),
    note: str = Form(""),
    waybill: str = Form(""),
    db: Session = Depends(get_db),
    user=Depends(require_vendor),
):
    from datetime import datetime, timezone
    vendor = get_vendor(user, db)
    order = db.query(Order).filter_by(id=order_id, vendor_id=vendor.id).first()
    if not order:
        return RedirectResponse("/vendor/orders")

    order.status = new_status
    if waybill:
        order.delhivery_awb = waybill
    order.updated_at = datetime.now(timezone.utc)

    tracking = OrderTracking(
        order_id=order.id,
        status=new_status,
        description=note or f"Status updated to {new_status}",
        source="vendor",
    )
    db.add(tracking)
    db.commit()
    return RedirectResponse(f"/vendor/orders/{order_id}", status_code=303)
