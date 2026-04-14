"""Customer service booking."""
from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.dependencies import require_customer
from app.models.customer import Customer, CustomerAddress
from app.models.service import ServiceRequest, ServiceTracking, ServiceCategory
from app.models.vendor import Vendor
from app.models.product import Brand
from app.services.notification import send_service_booking_email
from app.utils.helpers import generate_request_number

router = APIRouter(prefix="/customer/services", tags=["customer"])
templates = Jinja2Templates(directory="app/templates")


def get_customer(user, db):
    return db.query(Customer).filter_by(user_id=user.id).first()


@router.get("/book", response_class=HTMLResponse)
def book_service_page(
    request: Request,
    vendor_id: int = Query(...),
    db: Session = Depends(get_db),
    user=Depends(require_customer),
):
    vendor = db.query(Vendor).filter_by(id=vendor_id).first()
    categories = db.query(ServiceCategory).filter_by(is_active=True).all()
    brands = db.query(Brand).filter_by(is_active=True).order_by(Brand.name).all()
    customer = get_customer(user, db)
    addresses = db.query(CustomerAddress).filter_by(customer_id=customer.id).all()
    return templates.TemplateResponse("customer/services/book.html", {
        "request": request, "user": user, "vendor": vendor,
        "categories": categories, "brands": brands, "addresses": addresses,
    })


@router.post("/book")
def book_service(
    request: Request,
    vendor_id: int = Form(...),
    service_category_id: int = Form(...),
    brand_id: int = Form(None),
    device_description: str = Form(...),
    issue_description: str = Form(...),
    service_address: str = Form(...),
    preferred_date: str = Form(...),
    preferred_time: str = Form(""),
    db: Session = Depends(get_db),
    user=Depends(require_customer),
):
    customer = get_customer(user, db)
    request_number = generate_request_number("SR")

    sr = ServiceRequest(
        request_number=request_number,
        customer_id=customer.id,
        vendor_id=vendor_id,
        service_category_id=service_category_id,
        brand_id=brand_id,
        device_description=device_description,
        issue_description=issue_description,
        service_address=service_address,
        preferred_date=date.fromisoformat(preferred_date),
        preferred_time=preferred_time,
    )
    db.add(sr)
    db.flush()
    db.add(ServiceTracking(
        service_request_id=sr.id, status="pending",
        description="Service request submitted"
    ))
    db.commit()

    send_service_booking_email(
        user.email, user.name, request_number,
        preferred_date, preferred_time or "As per availability"
    )
    return RedirectResponse(f"/customer/services/{request_number}", status_code=303)


@router.get("", response_class=HTMLResponse)
def service_list(request: Request, db: Session = Depends(get_db), user=Depends(require_customer)):
    customer = get_customer(user, db)
    requests = db.query(ServiceRequest).filter_by(customer_id=customer.id).order_by(
        ServiceRequest.created_at.desc()
    ).all()
    return templates.TemplateResponse("customer/services/list.html", {
        "request": request, "user": user, "service_requests": requests,
    })


@router.get("/{request_number}", response_class=HTMLResponse)
def service_detail(
    request: Request,
    request_number: str,
    db: Session = Depends(get_db),
    user=Depends(require_customer),
):
    customer = get_customer(user, db)
    sr = db.query(ServiceRequest).filter_by(
        request_number=request_number, customer_id=customer.id
    ).first()
    if not sr:
        return RedirectResponse("/customer/services")
    return templates.TemplateResponse("customer/services/detail.html", {
        "request": request, "user": user, "sr": sr,
    })
