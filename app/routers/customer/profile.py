"""Customer dashboard and profile."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_customer
from app.models.customer import Customer
from app.models.order import Order

router = APIRouter(prefix="/customer", tags=["customer"])
templates = Jinja2Templates(directory="app/templates")


def get_customer(user, db):
    return db.query(Customer).filter_by(user_id=user.id).first()


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), user=Depends(require_customer)):
    customer = get_customer(user, db)
    recent_orders = db.query(Order).filter_by(customer_id=customer.id).order_by(Order.created_at.desc()).limit(5).all()
    return templates.TemplateResponse("customer/dashboard.html", {
        "request": request, "user": user, "customer": customer,
        "recent_orders": recent_orders,
    })
