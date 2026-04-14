"""Admin commission management."""
from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_superadmin
from app.models.commission import CommissionConfig, CommissionScope
from app.models.product import Brand
from app.models.vendor import Vendor

router = APIRouter(prefix="/admin/commissions", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def commission_list(request: Request, db: Session = Depends(get_db), admin=Depends(require_superadmin)):
    configs = db.query(CommissionConfig).order_by(CommissionConfig.scope).all()
    brands = db.query(Brand).filter_by(is_active=True).all()
    vendors = db.query(Vendor).filter_by(status="approved").all()
    return templates.TemplateResponse("admin/commissions.html", {
        "request": request, "admin": admin,
        "configs": configs, "brands": brands, "vendors": vendors,
    })


@router.post("/add")
def add_commission(
    scope: str = Form(...),
    ref_id: int = Form(None),
    percentage: float = Form(...),
    db: Session = Depends(get_db),
    admin=Depends(require_superadmin),
):
    cfg = CommissionConfig(
        scope=scope, ref_id=ref_id, percentage=percentage, created_by=admin.id
    )
    db.add(cfg)
    db.commit()
    return RedirectResponse("/admin/commissions", status_code=303)


@router.post("/{config_id}/delete")
def delete_commission(config_id: int, db: Session = Depends(get_db), admin=Depends(require_superadmin)):
    cfg = db.query(CommissionConfig).filter_by(id=config_id).first()
    if cfg:
        db.delete(cfg)
        db.commit()
    return RedirectResponse("/admin/commissions", status_code=303)
