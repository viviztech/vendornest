"""Customer B2B bulk quote requests."""
from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_customer
from app.models.customer import Customer
from app.models.b2b import B2BQuote, B2BQuoteItem, B2BMessage
from app.utils.helpers import generate_quote_number

router = APIRouter(prefix="/customer/b2b", tags=["customer"])
templates = Jinja2Templates(directory="app/templates")


def get_customer(user, db):
    return db.query(Customer).filter_by(user_id=user.id).first()


@router.get("/request", response_class=HTMLResponse)
def b2b_request_page(
    request: Request,
    vendor_id: int = Query(...),
    db: Session = Depends(get_db),
    user=Depends(require_customer),
):
    from app.models.vendor import Vendor
    vendor = db.query(Vendor).filter_by(id=vendor_id).first()
    return templates.TemplateResponse("customer/b2b/request.html", {
        "request": request, "user": user, "vendor": vendor,
    })


@router.post("/request")
def submit_b2b_request(
    vendor_id: int = Form(...),
    business_name: str = Form(...),
    business_gst: str = Form(""),
    requirements: str = Form(...),
    delivery_pincode: str = Form(""),
    delivery_address: str = Form(""),
    db: Session = Depends(get_db),
    user=Depends(require_customer),
):
    customer = get_customer(user, db)
    quote = B2BQuote(
        quote_number=generate_quote_number(),
        customer_id=customer.id,
        vendor_id=vendor_id,
        business_name=business_name,
        business_gst=business_gst or None,
        requirements=requirements,
        delivery_pincode=delivery_pincode,
        delivery_address=delivery_address,
    )
    db.add(quote)
    db.commit()
    return RedirectResponse(f"/customer/b2b/{quote.quote_number}", status_code=303)


@router.get("", response_class=HTMLResponse)
def b2b_list(request: Request, db: Session = Depends(get_db), user=Depends(require_customer)):
    customer = get_customer(user, db)
    quotes = db.query(B2BQuote).filter_by(customer_id=customer.id).order_by(B2BQuote.created_at.desc()).all()
    return templates.TemplateResponse("customer/b2b/list.html", {
        "request": request, "user": user, "quotes": quotes,
    })


@router.get("/{quote_number}", response_class=HTMLResponse)
def b2b_detail(request: Request, quote_number: str, db: Session = Depends(get_db), user=Depends(require_customer)):
    customer = get_customer(user, db)
    quote = db.query(B2BQuote).filter_by(quote_number=quote_number, customer_id=customer.id).first()
    if not quote:
        return RedirectResponse("/customer/b2b")
    return templates.TemplateResponse("customer/b2b/detail.html", {
        "request": request, "user": user, "quote": quote,
    })


@router.post("/{quote_number}/message")
def send_message(
    quote_number: str,
    message: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(require_customer),
):
    customer = get_customer(user, db)
    quote = db.query(B2BQuote).filter_by(quote_number=quote_number, customer_id=customer.id).first()
    if quote:
        db.add(B2BMessage(quote_id=quote.id, sender_id=user.id, sender_role="customer", message=message))
        db.commit()
    return RedirectResponse(f"/customer/b2b/{quote_number}", status_code=303)
