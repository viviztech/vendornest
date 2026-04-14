"""Admin brand management."""
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from python_slugify import slugify

from app.database import get_db
from app.dependencies import require_superadmin
from app.models.product import Brand
from app.services.storage import upload_brand_logo

router = APIRouter(prefix="/admin/brands", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def brand_list(request: Request, db: Session = Depends(get_db), admin=Depends(require_superadmin)):
    brands = db.query(Brand).order_by(Brand.sort_order, Brand.name).all()
    return templates.TemplateResponse("admin/brands/list.html", {
        "request": request, "admin": admin, "brands": brands
    })


@router.get("/add", response_class=HTMLResponse)
def add_brand_page(request: Request, admin=Depends(require_superadmin)):
    return templates.TemplateResponse("admin/brands/form.html", {"request": request, "admin": admin, "brand": None})


@router.post("/add")
async def add_brand(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    sort_order: int = Form(0),
    logo: UploadFile = File(None),
    db: Session = Depends(get_db),
    admin=Depends(require_superadmin),
):
    logo_url = None
    if logo and logo.filename:
        logo_url = upload_brand_logo(logo)

    brand = Brand(name=name.strip(), slug=slugify(name), description=description, sort_order=sort_order, logo_url=logo_url)
    db.add(brand)
    db.commit()
    return RedirectResponse("/admin/brands", status_code=303)


@router.post("/{brand_id}/toggle")
def toggle_brand(brand_id: int, db: Session = Depends(get_db), admin=Depends(require_superadmin)):
    brand = db.query(Brand).filter_by(id=brand_id).first()
    if brand:
        brand.is_active = not brand.is_active
        db.commit()
    return RedirectResponse("/admin/brands", status_code=303)
