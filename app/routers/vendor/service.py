"""Vendor service request management."""
from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_vendor
from app.models.vendor import Vendor
from app.models.service import ServiceRequest, ServiceTracking

router = APIRouter(prefix="/vendor/services", tags=["vendor"])
templates = Jinja2Templates(directory="app/templates")


def get_vendor(user, db):
    return db.query(Vendor).filter_by(user_id=user.id).first()


@router.get("", response_class=HTMLResponse)
def service_list(
    request: Request,
    status: str = Query("all"),
    page: int = Query(1),
    db: Session = Depends(get_db),
    user=Depends(require_vendor),
):
    vendor = get_vendor(user, db)
    query = db.query(ServiceRequest).filter_by(vendor_id=vendor.id)
    if status != "all":
        query = query.filter(ServiceRequest.status == status)
    total = query.count()
    size = 20
    requests = query.order_by(ServiceRequest.created_at.desc()).offset((page - 1) * size).limit(size).all()
    return templates.TemplateResponse("vendor/services/list.html", {
        "request": request, "user": user, "vendor": vendor,
        "service_requests": requests, "status_filter": status,
        "total": total, "page": page, "pages": (total + size - 1) // size,
    })


@router.get("/{sr_id}", response_class=HTMLResponse)
def service_detail(request: Request, sr_id: int, db: Session = Depends(get_db), user=Depends(require_vendor)):
    vendor = get_vendor(user, db)
    sr = db.query(ServiceRequest).filter_by(id=sr_id, vendor_id=vendor.id).first()
    if not sr:
        return RedirectResponse("/vendor/services")
    return templates.TemplateResponse("vendor/services/detail.html", {
        "request": request, "user": user, "vendor": vendor, "sr": sr,
    })


@router.post("/{sr_id}/update")
def update_service(
    sr_id: int,
    new_status: str = Form(...),
    technician_name: str = Form(""),
    technician_phone: str = Form(""),
    confirmed_date: str = Form(""),
    confirmed_time: str = Form(""),
    resolution_notes: str = Form(""),
    service_charge: float = Form(0),
    db: Session = Depends(get_db),
    user=Depends(require_vendor),
):
    from datetime import datetime, timezone, date
    vendor = get_vendor(user, db)
    sr = db.query(ServiceRequest).filter_by(id=sr_id, vendor_id=vendor.id).first()
    if not sr:
        return RedirectResponse("/vendor/services")

    sr.status = new_status
    if technician_name:
        sr.technician_name = technician_name
    if technician_phone:
        sr.technician_phone = technician_phone
    if confirmed_date:
        sr.confirmed_date = date.fromisoformat(confirmed_date)
    if confirmed_time:
        sr.confirmed_time = confirmed_time
    if resolution_notes:
        sr.resolution_notes = resolution_notes
    if service_charge:
        sr.service_charge = service_charge
        sr.total_amount = (sr.visiting_charge or 0) + service_charge + (sr.parts_charge or 0)
    if new_status == "completed":
        sr.completed_at = datetime.now(timezone.utc)

    db.add(ServiceTracking(
        service_request_id=sr.id, status=new_status,
        description=f"Status updated to {new_status}",
        updated_by=user.id,
    ))
    db.commit()
    return RedirectResponse(f"/vendor/services/{sr_id}", status_code=303)
