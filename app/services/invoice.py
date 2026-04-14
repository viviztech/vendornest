"""GST invoice PDF generation using WeasyPrint."""
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from app.config import settings

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "invoice")


def generate_order_invoice(order) -> bytes:
    """Generate GST-compliant invoice PDF for an order."""
    try:
        from weasyprint import HTML, CSS
    except ImportError:
        raise RuntimeError("weasyprint not installed")

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("order_invoice.html")

    html_content = template.render(
        order=order,
        invoice_date=datetime.now().strftime("%d %b %Y"),
        platform_name=settings.app_name,
        platform_address="VendorNest, India",
        platform_gst="PENDING",
    )

    return HTML(string=html_content, base_url=TEMPLATE_DIR).write_pdf()


def generate_service_invoice(service_request) -> bytes:
    """Generate service invoice PDF."""
    try:
        from weasyprint import HTML
    except ImportError:
        raise RuntimeError("weasyprint not installed")

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("service_invoice.html")

    html_content = template.render(
        sr=service_request,
        invoice_date=datetime.now().strftime("%d %b %Y"),
        platform_name=settings.app_name,
    )

    return HTML(string=html_content, base_url=TEMPLATE_DIR).write_pdf()
