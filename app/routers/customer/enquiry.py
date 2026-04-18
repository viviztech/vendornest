"""Customer enquiry routes — submit, list, detail, follow-up."""
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_customer
from app.models.customer import Customer
from app.models.enquiry import Enquiry, EnquiryMessage, EnquiryStatus, EnquiryVendorResponse, EnquiryResponseStatus
from app.models.vendor import Vendor, VendorStatus
from app.utils.helpers import generate_enquiry_number, sanitize_message, contains_contact_info
from app.services.notification import (
    send_vendor_new_enquiry_email,
    send_enquiry_submitted_email,
    send_followup_notification_email,
)
from app.config import settings

router = APIRouter(prefix="/customer/enquiries", tags=["customer-enquiry"])
templates = Jinja2Templates(directory="app/templates")


def _get_customer(user, db: Session) -> Customer:
    return db.query(Customer).filter_by(user_id=user.id).first()


@router.get("", response_class=HTMLResponse)
def enquiry_list(request: Request, db: Session = Depends(get_db), user=Depends(require_customer)):
    customer = _get_customer(user, db)
    enquiries = (
        db.query(Enquiry)
        .filter_by(customer_id=customer.id)
        .order_by(Enquiry.created_at.desc())
        .all()
    )
    return templates.TemplateResponse("customer/enquiry/list.html", {
        "request": request, "user": user, "enquiries": enquiries,
    })


@router.get("/new", response_class=HTMLResponse)
def enquiry_form(request: Request, db: Session = Depends(get_db), user=Depends(require_customer)):
    customer = _get_customer(user, db)
    return templates.TemplateResponse("customer/enquiry/form.html", {
        "request": request, "user": user, "customer": customer,
    })


@router.post("/new")
def submit_enquiry(
    request: Request,
    product_service_type: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    pincode: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(require_customer),
):
    customer = _get_customer(user, db)

    enquiry = Enquiry(
        enquiry_number=generate_enquiry_number(),
        customer_id=customer.id,
        product_service_type=product_service_type.strip(),
        description=description.strip(),
        location=location.strip(),
        pincode=pincode.strip(),
    )
    db.add(enquiry)
    db.commit()
    db.refresh(enquiry)

    # Broadcast to ALL approved vendors
    vendors = db.query(Vendor).filter_by(status=VendorStatus.approved).all()
    for vendor in vendors:
        vendor_user = vendor.user
        if vendor_user and vendor_user.email:
            send_vendor_new_enquiry_email(
                to=vendor_user.email,
                vendor_name=vendor.business_name,
                enquiry_number=enquiry.enquiry_number,
                product_type=product_service_type,
            )

    # Notify admin
    if settings.smtp_from_email:
        send_enquiry_submitted_email(settings.smtp_from_email, enquiry.enquiry_number)

    return RedirectResponse(f"/customer/enquiries/{enquiry.enquiry_number}", status_code=303)


@router.get("/{enquiry_number}", response_class=HTMLResponse)
def enquiry_detail(
    request: Request,
    enquiry_number: str,
    db: Session = Depends(get_db),
    user=Depends(require_customer),
):
    customer = _get_customer(user, db)
    enquiry = db.query(Enquiry).filter_by(
        enquiry_number=enquiry_number, customer_id=customer.id
    ).first()
    if not enquiry:
        return RedirectResponse("/customer/enquiries")

    return templates.TemplateResponse("customer/enquiry/detail.html", {
        "request": request, "user": user, "enquiry": enquiry,
    })


@router.post("/{enquiry_number}/message/{response_id}")
def send_followup(
    enquiry_number: str,
    response_id: int,
    message: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(require_customer),
):
    customer = _get_customer(user, db)
    enquiry = db.query(Enquiry).filter_by(
        enquiry_number=enquiry_number, customer_id=customer.id
    ).first()
    if not enquiry:
        return RedirectResponse("/customer/enquiries")

    # Find the matching response
    vendor_response = next((r for r in enquiry.responses if r.id == response_id), None)
    if not vendor_response:
        return RedirectResponse(f"/customer/enquiries/{enquiry_number}")

    clean_message = sanitize_message(message.strip())
    db.add(EnquiryMessage(
        response_id=response_id,
        sender_id=user.id,
        sender_role="customer",
        message=clean_message,
    ))
    db.commit()

    # Notify vendor
    vendor_user = vendor_response.vendor.user
    if vendor_user and vendor_user.email:
        send_followup_notification_email(vendor_user.email, "customer", enquiry_number)

    return RedirectResponse(f"/customer/enquiries/{enquiry_number}", status_code=303)


@router.post("/{enquiry_number}/accept/{response_id}")
def accept_quote(
    enquiry_number: str,
    response_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_customer),
):
    customer = _get_customer(user, db)
    enquiry = db.query(Enquiry).filter_by(
        enquiry_number=enquiry_number, customer_id=customer.id
    ).first()
    if not enquiry or enquiry.status == EnquiryStatus.closed:
        return RedirectResponse("/customer/enquiries")

    accepted_response = db.query(EnquiryVendorResponse).filter_by(
        id=response_id, enquiry_id=enquiry.id
    ).first()
    if not accepted_response:
        return RedirectResponse(f"/customer/enquiries/{enquiry_number}")

    # Mark accepted response, reject all others
    for resp in enquiry.responses:
        if resp.id == response_id:
            resp.status = EnquiryResponseStatus.accepted
        else:
            resp.status = EnquiryResponseStatus.rejected

    enquiry.status = EnquiryStatus.closed
    db.commit()

    return RedirectResponse(f"/customer/enquiries/{enquiry_number}", status_code=303)
