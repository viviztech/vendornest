"""Admin enquiry management — full oversight of all enquiries, quotes, messages."""
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_superadmin
from app.models.enquiry import Enquiry, EnquiryStatus, EnquiryVendorResponse, EnquiryMessage
from app.models.user import User

router = APIRouter(prefix="/admin/enquiries", tags=["admin-enquiry"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def enquiry_list(
    request: Request,
    status: str = "",
    db: Session = Depends(get_db),
    admin=Depends(require_superadmin),
):
    q = db.query(Enquiry).order_by(Enquiry.created_at.desc())
    if status:
        q = q.filter(Enquiry.status == status)
    enquiries = q.all()
    return templates.TemplateResponse("admin/enquiry/list.html", {
        "request": request,
        "admin": admin,
        "enquiries": enquiries,
        "current_status": status,
        "statuses": [e.value for e in EnquiryStatus],
    })


@router.get("/{enquiry_number}", response_class=HTMLResponse)
def enquiry_detail(
    request: Request,
    enquiry_number: str,
    db: Session = Depends(get_db),
    admin=Depends(require_superadmin),
):
    enquiry = db.query(Enquiry).filter_by(enquiry_number=enquiry_number).first()
    if not enquiry:
        return RedirectResponse("/admin/enquiries")
    return templates.TemplateResponse("admin/enquiry/detail.html", {
        "request": request,
        "admin": admin,
        "enquiry": enquiry,
    })


@router.post("/{enquiry_number}/close")
def close_enquiry(
    enquiry_number: str,
    db: Session = Depends(get_db),
    admin=Depends(require_superadmin),
):
    enquiry = db.query(Enquiry).filter_by(enquiry_number=enquiry_number).first()
    if enquiry:
        enquiry.status = EnquiryStatus.closed
        db.commit()
    return RedirectResponse(f"/admin/enquiries/{enquiry_number}", status_code=303)


@router.post("/{enquiry_number}/message/{response_id}")
def admin_send_message(
    enquiry_number: str,
    response_id: int,
    message: str = Form(...),
    db: Session = Depends(get_db),
    admin=Depends(require_superadmin),
):
    """Admin can post messages into any thread for oversight/intervention."""
    from app.utils.helpers import sanitize_message
    enquiry = db.query(Enquiry).filter_by(enquiry_number=enquiry_number).first()
    if not enquiry:
        return RedirectResponse("/admin/enquiries")

    vendor_response = db.query(EnquiryVendorResponse).filter_by(
        id=response_id, enquiry_id=enquiry.id
    ).first()
    if not vendor_response:
        return RedirectResponse(f"/admin/enquiries/{enquiry_number}")

    clean = sanitize_message(message.strip())
    db.add(EnquiryMessage(
        response_id=response_id,
        sender_id=admin.id,
        sender_role="admin",
        message=clean,
    ))
    db.commit()
    return RedirectResponse(f"/admin/enquiries/{enquiry_number}", status_code=303)
