# Import all models so Alembic can detect them
from app.models.location import State, District, Taluk, Pincode
from app.models.user import User, OTPLog, PasswordResetToken
from app.models.product import Brand, BrandCategory, Category, Product, ProductImage, VendorProduct
from app.models.vendor import Vendor, VendorBrand, VendorPincode, VendorDocument, VendorServiceSlot, VendorReview
from app.models.order import Order, OrderItem, OrderTracking
from app.models.service import ServiceCategory, ServiceRequest, ServiceTracking
from app.models.b2b import B2BQuote, B2BQuoteItem, B2BMessage
from app.models.commission import CommissionConfig, Settlement
from app.models.notification import NotificationTemplate, NotificationLog, TranslationString
from app.models.customer import Customer, CustomerAddress

__all__ = [
    "State", "District", "Taluk", "Pincode",
    "User", "OTPLog", "PasswordResetToken",
    "Brand", "BrandCategory", "Category", "Product", "ProductImage", "VendorProduct",
    "Vendor", "VendorBrand", "VendorPincode", "VendorDocument", "VendorServiceSlot", "VendorReview",
    "Order", "OrderItem", "OrderTracking",
    "ServiceCategory", "ServiceRequest", "ServiceTracking",
    "B2BQuote", "B2BQuoteItem", "B2BMessage",
    "CommissionConfig", "Settlement",
    "NotificationTemplate", "NotificationLog", "TranslationString",
    "Customer", "CustomerAddress",
]
