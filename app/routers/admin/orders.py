"""Admin order management — view all orders, update status."""
from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_superadmin
from app.models.order import Order, OrderStatus, OrderTracking

router = APIRouter(prefix="/admin/orders", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def order_list(
    request: Request,
    status: str = Query("all"),
    page: int = Query(1),
    db: Session = Depends(get_db),
    admin=Depends(require_superadmin),
):
    query = db.query(Order)
    if status != "all":
        query = query.filter(Order.status == status)
    total = query.count()
    size = 25
    orders = query.order_by(Order.created_at.desc()).offset((page - 1) * size).limit(size).all()
    return templates.TemplateResponse("admin/orders/list.html", {
        "request": request, "admin": admin,
        "orders": orders, "status_filter": status,
        "total": total, "page": page, "pages": (total + size - 1) // size,
        "statuses": [s.value for s in OrderStatus],
    })


@router.get("/{order_id}", response_class=HTMLResponse)
def order_detail(
    request: Request,
    order_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_superadmin),
):
    order = db.query(Order).filter_by(id=order_id).first()
    if not order:
        return RedirectResponse("/admin/orders")
    return templates.TemplateResponse("admin/orders/detail.html", {
        "request": request, "admin": admin, "order": order,
        "statuses": [s.value for s in OrderStatus],
    })


@router.post("/{order_id}/update-status")
def update_order_status(
    order_id: int,
    new_status: str = Form(...),
    note: str = Form(""),
    db: Session = Depends(get_db),
    admin=Depends(require_superadmin),
):
    from datetime import datetime, timezone
    order = db.query(Order).filter_by(id=order_id).first()
    if not order:
        return RedirectResponse("/admin/orders")

    order.status = new_status
    order.updated_at = datetime.now(timezone.utc)
    db.add(OrderTracking(
        order_id=order.id,
        status=new_status,
        description=note or f"Status updated to {new_status} by admin",
        source="system",
    ))
    db.commit()
    return RedirectResponse(f"/admin/orders/{order_id}", status_code=303)
