# SQLAlchemy model for Product

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Numeric, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.base import Base

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(JSON, nullable=False)  # {"zh-CN": "分类名", "en-US": "Category Name"}
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(JSON, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    parent = relationship("Category", remote_side=[id])
    children = relationship("Category")
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(JSON, nullable=False)  # {"zh-CN": "产品名", "en-US": "Product Name"}
    description = Column(JSON, nullable=True)
    short_description = Column(JSON, nullable=True)
    specifications = Column(JSON, nullable=True)
    
    # Pricing
    price = Column(DECIMAL(10, 2), nullable=False)
    cost_price = Column(DECIMAL(10, 2), nullable=True)
    
    # Inventory
    stock = Column(Integer, default=0)
    min_stock = Column(Integer, default=0)
    unit = Column(JSON, nullable=False)  # {"zh-CN": "单位", "en-US": "Unit"}
    
    # Physical properties
    weight = Column(DECIMAL(8, 2), nullable=True)
    dimensions = Column(String(255), nullable=True)
    
    # Relationships
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    videos = relationship("ProductVideo", back_populates="product", cascade="all, delete-orphan")

class ProductImage(Base):
    __tablename__ = "product_images"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    alt_text = Column(String(255), nullable=True)
    is_primary = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="images")

class ProductVideo(Base):
    __tablename__ = "product_videos"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    title = Column(JSON, nullable=False)
    description = Column(JSON, nullable=True)
    video_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    video_type = Column(String(50), nullable=False)  # product_demo, installation, usage, etc.
    duration = Column(Integer, nullable=True)  # in seconds
    file_size = Column(Integer, nullable=True)  # in bytes
    quality = Column(String(20), nullable=True)  # 720p, 1080p, 4K
    format = Column(String(20), nullable=True)  # mp4, webm, etc.
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    
    # Analytics
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="videos")
