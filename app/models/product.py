from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text,
    ForeignKey, Numeric, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), unique=True, index=True)
    logo_url = Column(String(500))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    categories = relationship("Category", secondary="brand_categories", back_populates="brands")
    products = relationship("Product", back_populates="brand")


class BrandCategory(Base):
    __tablename__ = "brand_categories"

    brand_id = Column(Integer, ForeignKey("brands.id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    name = Column(String(100), nullable=False)
    name_ta = Column(String(100))
    name_hi = Column(String(100))
    slug = Column(String(100), unique=True, index=True)
    icon = Column(String(200))
    image_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    parent = relationship("Category", remote_side="Category.id", back_populates="children")
    children = relationship("Category", back_populates="parent")
    brands = relationship("Brand", secondary="brand_categories", back_populates="categories")
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    name = Column(String(300), nullable=False)
    name_ta = Column(String(300))
    name_hi = Column(String(300))
    slug = Column(String(300), unique=True, index=True)
    description = Column(Text)
    description_ta = Column(Text)
    description_hi = Column(Text)
    specifications = Column(JSON)  # {"RAM": "8GB", "Storage": "512GB SSD", ...}
    base_price = Column(Numeric(12, 2))  # manufacturer suggested price
    hsn_code = Column(String(20))        # for GST invoice
    gst_rate = Column(Numeric(5, 2), default=18.0)
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=True)  # admin can disable
    model_number = Column(String(100))
    warranty_months = Column(Integer, default=12)
    weight_kg = Column(Numeric(8, 3))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    brand = relationship("Brand", back_populates="products")
    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product")
    vendor_listings = relationship("VendorProduct", back_populates="product")


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    is_primary = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)

    product = relationship("Product", back_populates="images")


class VendorProduct(Base):
    __tablename__ = "vendor_products"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    price = Column(Numeric(12, 2), nullable=False)
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    vendor = relationship("Vendor", back_populates="products")
    product = relationship("Product", back_populates="vendor_listings")
    order_items = relationship("OrderItem", back_populates="vendor_product")
