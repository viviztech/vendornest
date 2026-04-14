"""VendorNest — FastAPI application entry point."""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.database import check_db_connection, check_redis_connection

# ── Routers ───────────────────────────────────────────────────────────────────
from app.routers.auth.routes import router as auth_router
from app.routers.public.search import router as public_router
from app.routers.admin.dashboard import router as admin_dashboard_router
from app.routers.admin.vendors import router as admin_vendors_router
from app.routers.admin.brands import router as admin_brands_router
from app.routers.admin.commissions import router as admin_commissions_router
from app.routers.vendor.dashboard import router as vendor_dashboard_router
from app.routers.vendor.products import router as vendor_products_router
from app.routers.vendor.orders import router as vendor_orders_router
from app.routers.vendor.service import router as vendor_service_router
from app.routers.vendor.pincodes import router as vendor_pincodes_router
from app.routers.customer.orders import router as customer_orders_router
from app.routers.customer.service import router as customer_service_router
from app.routers.customer.b2b import router as customer_b2b_router

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    description="Hardware Vendor Connect Platform",
    version="1.0.0",
    docs_url="/api/docs" if not settings.is_production else None,
    redoc_url=None,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.app_secret_key,
    max_age=86400,
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="app/templates")

# ── Include routers ───────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(public_router)
app.include_router(admin_dashboard_router)
app.include_router(admin_vendors_router)
app.include_router(admin_brands_router)
app.include_router(admin_commissions_router)
app.include_router(vendor_dashboard_router)
app.include_router(vendor_products_router)
app.include_router(vendor_orders_router)
app.include_router(vendor_service_router)
app.include_router(vendor_pincodes_router)
app.include_router(customer_orders_router)
app.include_router(customer_service_router)
app.include_router(customer_b2b_router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "db": check_db_connection(),
        "redis": check_redis_connection(),
        "app": settings.app_name,
        "env": settings.app_env,
    }


# ── Razorpay webhook ──────────────────────────────────────────────────────────
@app.post("/webhooks/razorpay")
async def razorpay_webhook(request: Request):
    from app.services.payment import verify_webhook_signature
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")
    if not verify_webhook_signature(body, signature):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid signature")
    # Handle payment events here
    return {"status": "ok"}


# ── Delhivery webhook ─────────────────────────────────────────────────────────
@app.post("/webhooks/delhivery")
async def delhivery_webhook(request: Request):
    data = await request.json()
    # Process delivery status update
    # Update order tracking based on data
    return {"status": "ok"}
