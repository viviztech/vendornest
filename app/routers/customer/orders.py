"""Customer order flow: cart, checkout, payment, tracking."""
from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import json

from app.database import get_db
from app.dependencies import get_current_user, require_customer
from app.models.vendor import Vendor
from app.models.customer import Customer, CustomerAddress
from app.models.product import VendorProduct
from app.models.order import Order, OrderItem, OrderTracking, OrderStatus, PaymentStatus
from app.models.location import Pincode, State
from app.services import payment as payment_svc
from app.services.commission import get_commission_rate, calculate_commission
from app.services.notification import send_order_confirmation_email
from app.utils.helpers import generate_order_number
from app.config import settings

router = APIRouter(prefix="/customer", tags=["customer"])
templates = Jinja2Templates(directory="app/templates")


def get_customer(user, db):
    return db.query(Customer).filter_by(user_id=user.id).first()


# ── Cart (session via cookie JSON) ────────────────────────────────────────────
@router.get("/cart", response_class=HTMLResponse)
def cart_page(request: Request, db: Session = Depends(get_db)):
    cart = _get_cart(request)
    items = []
    total = 0
    for item in cart:
        listing = db.query(VendorProduct).filter_by(id=item["listing_id"]).first()
        if listing and listing.is_active:
            subtotal = float(listing.price) * item["qty"]
            items.append({"listing": listing, "qty": item["qty"], "subtotal": subtotal})
            total += subtotal
    return templates.TemplateResponse("customer/cart.html", {
        "request": request, "cart_items": items, "total": total,
    })


@router.post("/cart/add")
def add_to_cart(
    request: Request,
    listing_id: int = Form(...),
    qty: int = Form(1),
):
    cart = _get_cart(request)
    for item in cart:
        if item["listing_id"] == listing_id:
            item["qty"] += qty
            break
    else:
        cart.append({"listing_id": listing_id, "qty": qty})
    resp = RedirectResponse("/customer/cart", status_code=303)
    resp.set_cookie("cart", json.dumps(cart), max_age=7 * 24 * 3600, httponly=True)
    return resp


@router.post("/cart/remove/{listing_id}")
def remove_from_cart(request: Request, listing_id: int):
    cart = [i for i in _get_cart(request) if i["listing_id"] != listing_id]
    resp = RedirectResponse("/customer/cart", status_code=303)
    resp.set_cookie("cart", json.dumps(cart), httponly=True)
    return resp


# ── Checkout ──────────────────────────────────────────────────────────────────
@router.get("/checkout", response_class=HTMLResponse)
def checkout_page(request: Request, db: Session = Depends(get_db), user=Depends(require_customer)):
    cart = _get_cart(request)
    if not cart:
        return RedirectResponse("/customer/cart")
    customer = get_customer(user, db)
    addresses = db.query(CustomerAddress).filter_by(customer_id=customer.id).all()
    states = db.query(State).filter_by(is_active=True).order_by(State.name).all()
    items, total = _resolve_cart(cart, db)
    return templates.TemplateResponse("customer/checkout.html", {
        "request": request, "user": user, "customer": customer,
        "cart_items": items, "total": total,
        "addresses": addresses, "states": states,
        "razorpay_key": settings.razorpay_key_id,
    })


@router.post("/checkout/create-order")
def create_order(
    request: Request,
    address_id: int = Form(None),
    new_name: str = Form(""),
    new_phone: str = Form(""),
    new_address: str = Form(""),
    new_city: str = Form(""),
    new_pincode: str = Form(""),
    new_state_id: int = Form(None),
    db: Session = Depends(get_db),
    user=Depends(require_customer),
):
    from decimal import Decimal
    cart = _get_cart(request)
    if not cart:
        return RedirectResponse("/customer/cart")

    customer = get_customer(user, db)
    items, total = _resolve_cart(cart, db)
    if not items:
        return RedirectResponse("/customer/cart")

    # Resolve delivery address
    if address_id:
        addr_obj = db.query(CustomerAddress).filter_by(id=address_id, customer_id=customer.id).first()
        delivery_address = {
            "name": addr_obj.name, "phone": addr_obj.phone,
            "address": addr_obj.address_line1, "city": addr_obj.city,
            "pincode": addr_obj.pincode.pincode, "state": addr_obj.state.name,
        }
        pincode_id = addr_obj.pincode_id
    else:
        pc = db.query(Pincode).filter_by(pincode=new_pincode.strip()).first()
        if not pc:
            return RedirectResponse("/customer/checkout?error=invalid_pincode")
        delivery_address = {
            "name": new_name, "phone": new_phone,
            "address": new_address, "city": new_city,
            "pincode": new_pincode, "state": pc.state.name if pc.state else "",
        }
        pincode_id = pc.id

    # Group by vendor (simple: use first item's vendor)
    vendor_id = items[0]["listing"].vendor_id
    vendor = db.query(Vendor).filter_by(id=vendor_id).first()
    first_product = items[0]["listing"].product

    commission_rate = get_commission_rate(db, vendor_id, first_product.brand_id)
    total_decimal = Decimal(str(total))
    comm = calculate_commission(total_decimal, commission_rate)

    order_number = generate_order_number()
    rz_order = payment_svc.create_order(total, order_number, user.email)
    if not rz_order:
        return RedirectResponse("/customer/checkout?error=payment_failed")

    order = Order(
        order_number=order_number,
        customer_id=customer.id,
        vendor_id=vendor_id,
        subtotal=total,
        gst_amount=0,
        delivery_charge=0,
        total_amount=total,
        commission_percent=comm["commission_percent"],
        commission_amount=comm["commission_amount"],
        vendor_payout=comm["vendor_payout"],
        delivery_address=delivery_address,
        razorpay_order_id=rz_order["id"],
    )
    db.add(order)
    db.flush()

    for item in items:
        db.add(OrderItem(
            order_id=order.id,
            vendor_product_id=item["listing"].id,
            product_snapshot={"name": item["listing"].product.name, "brand": item["listing"].product.brand.name},
            quantity=item["qty"],
            unit_price=float(item["listing"].price),
            total_price=item["subtotal"],
        ))

    db.add(OrderTracking(order_id=order.id, status="pending_payment", description="Order created, awaiting payment"))
    db.commit()

    return templates.TemplateResponse("customer/payment.html", {
        "request": request, "user": user,
        "order": order, "rz_order": rz_order,
        "razorpay_key": settings.razorpay_key_id,
        "delivery_address": delivery_address,
        "total": total,
    })


@router.post("/checkout/payment-success")
def payment_success(
    request: Request,
    order_id: int = Form(...),
    razorpay_payment_id: str = Form(...),
    razorpay_order_id: str = Form(...),
    razorpay_signature: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(require_customer),
):
    if not payment_svc.verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
        return RedirectResponse(f"/customer/orders/{order_id}?error=payment_verify_failed")

    order = db.query(Order).filter_by(id=order_id).first()
    if order:
        order.status = OrderStatus.confirmed
        order.payment_status = PaymentStatus.paid
        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_signature = razorpay_signature
        db.add(OrderTracking(order_id=order.id, status="confirmed", description="Payment successful. Order confirmed."))
        db.commit()

        customer = get_customer(user, db)
        send_order_confirmation_email(user.email, user.name, order.order_number, float(order.total_amount))

    resp = RedirectResponse(f"/customer/orders/{order.order_number}", status_code=303)
    resp.set_cookie("cart", "[]")
    return resp


@router.get("/orders", response_class=HTMLResponse)
def order_list(request: Request, db: Session = Depends(get_db), user=Depends(require_customer)):
    customer = get_customer(user, db)
    orders = db.query(Order).filter_by(customer_id=customer.id).order_by(Order.created_at.desc()).all()
    return templates.TemplateResponse("customer/orders/list.html", {
        "request": request, "user": user, "orders": orders,
    })


@router.get("/orders/{order_number}", response_class=HTMLResponse)
def order_detail(request: Request, order_number: str, db: Session = Depends(get_db), user=Depends(require_customer)):
    customer = get_customer(user, db)
    order = db.query(Order).filter_by(order_number=order_number, customer_id=customer.id).first()
    if not order:
        return RedirectResponse("/customer/orders")
    return templates.TemplateResponse("customer/orders/detail.html", {
        "request": request, "user": user, "order": order,
    })


# ── Cart helpers ───────────────────────────────────────────────────────────────
def _get_cart(request: Request) -> list:
    try:
        return json.loads(request.cookies.get("cart", "[]"))
    except Exception:
        return []


def _resolve_cart(cart: list, db) -> tuple:
    items = []
    total = 0
    for item in cart:
        listing = db.query(VendorProduct).filter_by(id=item["listing_id"]).first()
        if listing and listing.is_active and listing.stock >= item["qty"]:
            subtotal = float(listing.price) * item["qty"]
            items.append({"listing": listing, "qty": item["qty"], "subtotal": subtotal})
            total += subtotal
    return items, total
