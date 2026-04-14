"""Vendor product management."""
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_vendor
from app.models.vendor import Vendor
from app.models.product import Brand, Category, Product, VendorProduct, ProductImage
from app.services.storage import upload_product_image

router = APIRouter(prefix="/vendor/products", tags=["vendor"])
templates = Jinja2Templates(directory="app/templates")


def get_vendor(user, db):
    return db.query(Vendor).filter_by(user_id=user.id).first()


@router.get("", response_class=HTMLResponse)
def product_list(request: Request, page: int = Query(1), db: Session = Depends(get_db), user=Depends(require_vendor)):
    vendor = get_vendor(user, db)
    size = 20
    query = db.query(VendorProduct).filter_by(vendor_id=vendor.id)
    total = query.count()
    products = query.offset((page - 1) * size).limit(size).all()
    return templates.TemplateResponse("vendor/products/list.html", {
        "request": request, "user": user, "vendor": vendor,
        "products": products, "total": total, "page": page, "pages": (total + size - 1) // size,
    })


@router.get("/add", response_class=HTMLResponse)
def add_product_page(request: Request, db: Session = Depends(get_db), user=Depends(require_vendor)):
    vendor = get_vendor(user, db)
    brands = db.query(Brand).filter_by(is_active=True).order_by(Brand.name).all()
    categories = db.query(Category).filter_by(is_active=True).order_by(Category.name).all()
    return templates.TemplateResponse("vendor/products/add.html", {
        "request": request, "user": user, "vendor": vendor,
        "brands": brands, "categories": categories,
    })


@router.post("/add")
async def add_product(
    request: Request,
    product_id: int = Form(None),
    brand_id: int = Form(...),
    category_id: int = Form(...),
    product_name: str = Form(""),
    price: float = Form(...),
    stock: int = Form(0),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    user=Depends(require_vendor),
):
    vendor = get_vendor(user, db)

    # Create product if not existing
    if not product_id and product_name:
        from python_slugify import slugify
        import uuid
        prod = Product(
            brand_id=brand_id,
            category_id=category_id,
            name=product_name.strip(),
            slug=f"{slugify(product_name)}-{uuid.uuid4().hex[:6]}",
        )
        db.add(prod)
        db.flush()
        product_id = prod.id

        if image and image.filename:
            img_url = upload_product_image(image)
            if img_url:
                db.add(ProductImage(product_id=product_id, image_url=img_url, is_primary=True))

    listing = VendorProduct(
        vendor_id=vendor.id,
        product_id=product_id,
        price=price,
        stock=stock,
    )
    db.add(listing)
    db.commit()
    return RedirectResponse("/vendor/products", status_code=303)


@router.post("/{listing_id}/toggle")
def toggle_product(listing_id: int, db: Session = Depends(get_db), user=Depends(require_vendor)):
    vendor = get_vendor(user, db)
    listing = db.query(VendorProduct).filter_by(id=listing_id, vendor_id=vendor.id).first()
    if listing:
        listing.is_active = not listing.is_active
        db.commit()
    return RedirectResponse("/vendor/products", status_code=303)


@router.post("/{listing_id}/update-stock")
def update_stock(
    listing_id: int,
    stock: int = Form(...),
    db: Session = Depends(get_db),
    user=Depends(require_vendor),
):
    vendor = get_vendor(user, db)
    listing = db.query(VendorProduct).filter_by(id=listing_id, vendor_id=vendor.id).first()
    if listing:
        listing.stock = stock
        db.commit()
    return RedirectResponse("/vendor/products", status_code=303)
