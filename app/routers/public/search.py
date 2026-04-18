"""Public pincode search and vendor listing."""
from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.pincode import get_vendors_by_pincode, get_pincode_info
from app.models.product import Brand, Category, VendorProduct
from app.models.vendor import Vendor, VendorStatus
from app.utils.i18n import get_lang

router = APIRouter(tags=["public"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def homepage(request: Request, db: Session = Depends(get_db)):
    brands = db.query(Brand).filter_by(is_active=True).order_by(Brand.sort_order).limit(12).all()
    categories = db.query(Category).filter(
        Category.parent_id == None, Category.is_active == True
    ).order_by(Category.sort_order).all()
    lang = get_lang(request)
    return templates.TemplateResponse("public/home.html", {
        "request": request, "brands": brands,
        "categories": categories, "lang": lang,
    })


@router.get("/search", response_class=HTMLResponse)
def search_vendors(
    request: Request,
    pincode: str = Query(..., min_length=6, max_length=6),
    brand_id: int = Query(None),
    category_id: int = Query(None),
    db: Session = Depends(get_db),
):
    lang = get_lang(request)
    pincode_info = get_pincode_info(db, pincode)
    vendors = get_vendors_by_pincode(db, pincode)

    # Filter by brand if requested
    if brand_id:
        from app.models.vendor import VendorBrand
        vendor_ids = [
            vb.vendor_id for vb in db.query(VendorBrand).filter_by(brand_id=brand_id, verified=True).all()
        ]
        vendors = [v for v in vendors if v.id in vendor_ids]

    brands = db.query(Brand).filter_by(is_active=True).order_by(Brand.name).all()
    categories = db.query(Category).filter(
        Category.parent_id == None, Category.is_active == True
    ).all()

    return templates.TemplateResponse("public/search_results.html", {
        "request": request,
        "vendors": vendors,
        "pincode": pincode,
        "pincode_info": pincode_info,
        "brands": brands,
        "categories": categories,
        "selected_brand_id": brand_id,
        "lang": lang,
    })


@router.get("/vendor/{slug}", response_class=HTMLResponse)
def vendor_profile(
    request: Request,
    slug: str,
    db: Session = Depends(get_db),
):
    vendor = db.query(Vendor).filter(
        Vendor.business_slug == slug,
        Vendor.status == VendorStatus.approved,
    ).first()
    if not vendor:
        return templates.TemplateResponse("public/404.html", {"request": request}, status_code=404)

    lang = get_lang(request)
    products = db.query(VendorProduct).filter_by(
        vendor_id=vendor.id, is_active=True
    ).all()
    from app.models.vendor import VendorBrand
    vendor_brands = db.query(VendorBrand).filter_by(vendor_id=vendor.id, verified=True).all()

    return templates.TemplateResponse("public/vendor_profile.html", {
        "request": request,
        "vendor": vendor,
        "products": products,
        "vendor_brands": vendor_brands,
        "lang": lang,
    })


@router.get("/products", response_class=HTMLResponse)
def browse_products(
    request: Request,
    brand_id: int = Query(None),
    category_id: int = Query(None),
    q: str = Query(None),
    page: int = Query(1),
    db: Session = Depends(get_db),
):
    from app.models.product import Product
    query = db.query(Product).filter_by(is_active=True, is_approved=True)
    if brand_id:
        query = query.filter_by(brand_id=brand_id)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))

    size = 24
    total = query.count()
    products = query.order_by(Product.name).offset((page - 1) * size).limit(size).all()

    brands = db.query(Brand).filter_by(is_active=True).order_by(Brand.name).all()
    categories = db.query(Category).filter(
        Category.parent_id == None, Category.is_active == True
    ).all()

    return templates.TemplateResponse("public/products.html", {
        "request": request,
        "products": products,
        "brands": brands,
        "categories": categories,
        "total": total,
        "page": page,
        "pages": (total + size - 1) // size,
        "selected_brand_id": brand_id,
        "selected_category_id": category_id,
        "query": q,
        "lang": get_lang(request),
    })


@router.get("/product/{vendor_product_id}", response_class=HTMLResponse)
def product_detail(
    request: Request,
    vendor_product_id: int,
    db: Session = Depends(get_db),
):
    listing = db.query(VendorProduct).filter_by(
        id=vendor_product_id, is_active=True
    ).first()
    if not listing:
        return templates.TemplateResponse("public/404.html", {"request": request}, status_code=404)

    related = db.query(VendorProduct).filter(
        VendorProduct.product_id == listing.product_id,
        VendorProduct.id != listing.id,
        VendorProduct.is_active == True,
    ).limit(4).all()

    return templates.TemplateResponse("public/product_detail.html", {
        "request": request,
        "listing": listing,
        "related": related,
        "lang": get_lang(request),
    })


@router.get("/api/districts")
def get_districts(state_id: int = Query(...), db: Session = Depends(get_db)):
    from app.models.location import District
    from fastapi.responses import JSONResponse
    districts = db.query(District).filter_by(state_id=state_id).order_by(District.name).all()
    return JSONResponse([{"id": d.id, "name": d.name} for d in districts])


@router.get("/api/pincodes")
def get_pincodes(district_id: int = Query(...), db: Session = Depends(get_db)):
    from app.models.location import Pincode
    from fastapi.responses import JSONResponse
    pincodes = db.query(Pincode).filter_by(district_id=district_id, is_active=True).order_by(Pincode.pincode).all()
    return JSONResponse([{"id": p.id, "pincode": p.pincode, "office": p.post_office} for p in pincodes])


@router.get("/set-lang/{lang}")
def set_language(lang: str, request: Request):
    from fastapi.responses import RedirectResponse
    referer = request.headers.get("referer", "/")
    resp = RedirectResponse(url=referer, status_code=303)
    if lang in ["en", "ta", "hi"]:
        resp.set_cookie("lang", lang, max_age=365 * 24 * 3600)
    return resp
