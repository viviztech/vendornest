"""Auth routes: register, login (password + OTP), logout."""
from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database import get_db
from app.models.user import User, UserRole
from app.models.vendor import Vendor
from app.models.customer import Customer
from app.services import auth as auth_svc
from app.services.notification import send_otp_email
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

# ── Customer Register ──────────────────────────────────────────────────────────
@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    email = email.lower().strip()
    if auth_svc.get_user_by_email(db, email):
        return templates.TemplateResponse("auth/register.html", {
            "request": request, "error": "Email already registered. Please login."
        })
    user = User(
        email=email,
        name=name.strip(),
        phone=phone.strip(),
        hashed_password=auth_svc.hash_password(password),
        role=UserRole.customer,
    )
    db.add(user)
    db.flush()
    customer = Customer(user_id=user.id, name=name.strip(), email=email, phone=phone.strip())
    db.add(customer)
    db.commit()

    otp = auth_svc.create_otp_record(db, email, purpose="verify")
    send_otp_email(to=email, otp=otp, name=name)

    resp = RedirectResponse(url=f"/auth/verify-email?email={email}", status_code=303)
    return resp


# ── Email Verification ─────────────────────────────────────────────────────────
@router.get("/verify-email", response_class=HTMLResponse)
def verify_email_page(request: Request, email: str = ""):
    return templates.TemplateResponse("auth/verify_email.html", {"request": request, "email": email})


@router.post("/verify-email")
def verify_email(
    request: Request,
    email: str = Form(...),
    otp: str = Form(...),
    db: Session = Depends(get_db),
):
    if not auth_svc.verify_otp(db, email, otp, purpose="verify"):
        return templates.TemplateResponse("auth/verify_email.html", {
            "request": request, "email": email,
            "error": "Invalid or expired OTP. Please try again."
        })
    user = auth_svc.get_user_by_email(db, email)
    if user:
        user.is_email_verified = True
        user.email_verified_at = datetime.now(timezone.utc)
        db.commit()

    resp = RedirectResponse(url="/auth/login?verified=1", status_code=303)
    return resp


# ── Login (password) ──────────────────────────────────────────────────────────
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, verified: str = ""):
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "success": "Email verified! You can now login." if verified else "",
    })


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = auth_svc.authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse("auth/login.html", {
            "request": request,
            "error": "Invalid email or password."
        })

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    access_token = auth_svc.create_access_token(user.id, user.role)

    # Redirect by role
    redirect_map = {
        UserRole.superadmin: "/admin/dashboard",
        UserRole.vendor: "/vendor/dashboard",
        UserRole.customer: "/customer/dashboard",
    }
    resp = RedirectResponse(url=redirect_map.get(user.role, "/"), status_code=303)
    resp.set_cookie(
        "access_token", access_token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=settings.jwt_access_token_expire_minutes * 60,
    )
    return resp


# ── OTP Login (email OTP for customers) ───────────────────────────────────────
@router.get("/otp-login", response_class=HTMLResponse)
def otp_login_page(request: Request):
    return templates.TemplateResponse("auth/otp_login.html", {"request": request})


@router.post("/otp-login/send")
def send_otp(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    email = email.lower().strip()
    user = auth_svc.get_user_by_email(db, email)
    if not user:
        # Auto-register placeholder
        return templates.TemplateResponse("auth/otp_login.html", {
            "request": request,
            "error": "No account found. Please register first."
        })
    otp = auth_svc.create_otp_record(db, email, purpose="login")
    send_otp_email(to=email, otp=otp, name=user.name)
    return templates.TemplateResponse("auth/otp_verify.html", {
        "request": request, "email": email
    })


@router.post("/otp-login/verify")
def verify_otp_login(
    request: Request,
    email: str = Form(...),
    otp: str = Form(...),
    db: Session = Depends(get_db),
):
    if not auth_svc.verify_otp(db, email, otp, purpose="login"):
        return templates.TemplateResponse("auth/otp_verify.html", {
            "request": request, "email": email,
            "error": "Invalid or expired OTP."
        })
    user = auth_svc.get_user_by_email(db, email)
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    access_token = auth_svc.create_access_token(user.id, user.role)
    resp = RedirectResponse(url="/customer/dashboard", status_code=303)
    resp.set_cookie(
        "access_token", access_token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=settings.jwt_access_token_expire_minutes * 60,
    )
    return resp


# ── Logout ────────────────────────────────────────────────────────────────────
@router.get("/logout")
def logout():
    resp = RedirectResponse(url="/", status_code=303)
    resp.delete_cookie("access_token")
    return resp


# ── Vendor Register ───────────────────────────────────────────────────────────
@router.get("/vendor/register", response_class=HTMLResponse)
def vendor_register_page(request: Request, db: Session = Depends(get_db)):
    from app.models.location import State
    states = db.query(State).filter_by(is_active=True).order_by(State.name).all()
    return templates.TemplateResponse("auth/vendor_register.html", {
        "request": request, "states": states
    })


@router.post("/vendor/register")
def vendor_register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    business_name: str = Form(...),
    gst_number: str = Form(""),
    state_id: int = Form(...),
    district_id: int = Form(...),
    pincode_id: int = Form(...),
    address_line: str = Form(""),
    db: Session = Depends(get_db),
):
    from app.models.location import State
    email = email.lower().strip()

    if auth_svc.get_user_by_email(db, email):
        states = db.query(State).filter_by(is_active=True).order_by(State.name).all()
        return templates.TemplateResponse("auth/vendor_register.html", {
            "request": request, "states": states,
            "error": "Email already registered."
        })

    from python_slugify import slugify
    user = User(
        email=email, name=name.strip(), phone=phone.strip(),
        hashed_password=auth_svc.hash_password(password),
        role=UserRole.vendor,
    )
    db.add(user)
    db.flush()

    vendor = Vendor(
        user_id=user.id,
        business_name=business_name.strip(),
        business_slug=slugify(business_name),
        gst_number=gst_number.strip() or None,
        state_id=state_id,
        district_id=district_id,
        pincode_id=pincode_id,
        address_line=address_line.strip(),
    )
    db.add(vendor)
    db.commit()

    otp = auth_svc.create_otp_record(db, email, purpose="verify")
    send_otp_email(to=email, otp=otp, name=name)

    return RedirectResponse(url=f"/auth/verify-email?email={email}", status_code=303)
