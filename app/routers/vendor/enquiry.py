"""Vendor enquiry routes — view all open enquiries, submit quote, follow-up."""
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_vendor
from app.models.vendor import Vendor, VendorStatus
from app.models.enquiry import (
    Enquiry, EnquiryStatus, EnquiryVendorResponse, EnquiryResponseStatus, EnquiryMessage
)
from app.models.customer import Customer
from app.utils.helpers import sanitize_message
from app.services.notification import (
    send_customer_quote_received_email,
    send_followup_notification_email,
)

router = APIRouter(prefix="/vendor/enquiries", tags=["vendor-enquiry"])
templates = Jinja2Templates(directory="app/templates")


def _get_vendor(user, db: Session) -> Vendor:
    return db.query(Vendor).filter_by(user_id=user.id).first()


@router.get("", response_class=HTMLResponse)
def enquiry_list(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_vendor),
):
    vendor = _get_vendor(user, db)
    if not vendor or vendor.status != VendorStatus.approved:
        return RedirectResponse("/vendor/dashboard")

    # All open/quoted enquiries visible to all vendors
    enquiries = (
        db.query(Enquiry)
        .filter(Enquiry.status.in_([EnquiryStatus.open, EnquiryStatus.quoted]))
        .order_by(Enquiry.created_at.desc())
        .all()
    )

    # Map enquiry_id → this vendor's response (if any)
    my_response_ids = {
        r.enquiry_id: r
        for r in db.query(EnquiryVendorResponse).filter_by(vendor_id=vendor.id).all()
    }

    return templates.TemplateResponse("vendor/enquiry/list.html", {
        "request": request,
        "user": user,
        "vendor": vendor,
        "enquiries": enquiries,
        "my_responses": my_response_ids,
    })


@router.get("/{enquiry_number}", response_class=HTMLResponse)
def enquiry_detail(
    request: Request,
    enquiry_number: str,
    db: Session = Depends(get_db),
    user=Depends(require_vendor),
):
    vendor = _get_vendor(user, db)
    if not vendor or vendor.status != VendorStatus.approved:
        return RedirectResponse("/vendor/dashboard")

    enquiry = db.query(Enquiry).filter_by(enquiry_number=enquiry_number).first()
    if not enquiry:
        return RedirectResponse("/vendor/enquiries")

    my_response = db.query(EnquiryVendorResponse).filter_by(
        enquiry_id=enquiry.id, vendor_id=vendor.id
    ).first()

    return templates.TemplateResponse("vendor/enquiry/detail.html", {
        "request": request,
        "user": user,
        "vendor": vendor,
        "enquiry": enquiry,
        "my_response": my_response,
    })


@router.post("/{enquiry_number}/quote")
def submit_quote(
    enquiry_number: str,
    price: float = Form(...),
    eta: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(require_vendor),
):
    vendor = _get_vendor(user, db)
    if not vendor or vendor.status != VendorStatus.approved:
        return RedirectResponse("/vendor/dashboard")

    enquiry = db.query(Enquiry).filter_by(enquiry_number=enquiry_number).first()
    if not enquiry or enquiry.status == EnquiryStatus.closed:
        return RedirectResponse("/vendor/enquiries")

    # One quote per vendor per enquiry
    existing = db.query(EnquiryVendorResponse).filter_by(
        enquiry_id=enquiry.id, vendor_id=vendor.id
    ).first()
    if existing:
        return RedirectResponse(f"/vendor/enquiries/{enquiry_number}")

    clean_message = sanitize_message(message.strip())
    response = EnquiryVendorResponse(
        enquiry_id=enquiry.id,
        vendor_id=vendor.id,
        price=price,
        eta=eta.strip(),
        message=clean_message,
    )
    db.add(response)

    # Move enquiry to quoted state if still open
    if enquiry.status == EnquiryStatus.open:
        enquiry.status = EnquiryStatus.quoted

    db.commit()
    db.refresh(response)

    # Notify customer (no contact info shared)
    customer = enquiry.customer
    customer_user = customer.user if customer else None
    if customer_user and customer_user.email:
        send_customer_quote_received_email(
            customer_user.email,
            enquiry_number,
            enquiry.product_service_type,
        )

    return RedirectResponse(f"/vendor/enquiries/{enquiry_number}", status_code=303)


@router.post("/{enquiry_number}/message/{response_id}")
def send_followup(
    enquiry_number: str,
    response_id: int,
    message: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(require_vendor),
):
    vendor = _get_vendor(user, db)
    enquiry = db.query(Enquiry).filter_by(enquiry_number=enquiry_number).first()
    if not enquiry:
        return RedirectResponse("/vendor/enquiries")

    vendor_response = db.query(EnquiryVendorResponse).filter_by(
        id=response_id, vendor_id=vendor.id, enquiry_id=enquiry.id
    ).first()
    if not vendor_response:
        return RedirectResponse(f"/vendor/enquiries/{enquiry_number}")

    clean_message = sanitize_message(message.strip())
    db.add(EnquiryMessage(
        response_id=response_id,
        sender_id=user.id,
        sender_role="vendor",
        message=clean_message,
    ))
    db.commit()

    # Notify customer
    customer_user = enquiry.customer.user if enquiry.customer else None
    if customer_user and customer_user.email:
        send_followup_notification_email(customer_user.email, "vendor", enquiry_number)

    return RedirectResponse(f"/vendor/enquiries/{enquiry_number}", status_code=303)
