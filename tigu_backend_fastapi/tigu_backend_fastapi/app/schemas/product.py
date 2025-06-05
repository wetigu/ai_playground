# Pydantic schema for Product (request/response)

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

# Category schemas
class CategoryBase(BaseModel):
    name: Dict[str, str]  # {"zh-CN": "分类名", "en-US": "Category Name"}
    slug: str
    description: Optional[Dict[str, str]] = None
    parent_id: Optional[int] = None
    sort_order: int = 0
    is_active: bool = True

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[Dict[str, str]] = None
    slug: Optional[str] = None
    description: Optional[Dict[str, str]] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime

# Product Image schemas
class ProductImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    image_url: str
    alt_text: Optional[str] = None
    is_primary: bool
    sort_order: int
    created_at: datetime

# Product Video schemas
class ProductVideoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: Dict[str, str]
    description: Optional[Dict[str, str]] = None
    video_url: str
    thumbnail_url: Optional[str] = None
    video_type: str
    duration: Optional[int] = None
    file_size: Optional[int] = None
    quality: Optional[str] = None
    format: Optional[str] = None
    is_active: bool
    sort_order: int
    view_count: int
    like_count: int
    created_at: datetime
    updated_at: datetime

# Product schemas
class ProductBase(BaseModel):
    sku: str
    name: Dict[str, str]  # {"zh-CN": "产品名", "en-US": "Product Name"}
    description: Optional[Dict[str, str]] = None
    short_description: Optional[Dict[str, str]] = None
    specifications: Optional[Dict[str, Any]] = None
    price: Decimal = Field(..., gt=0)
    cost_price: Optional[Decimal] = None
    stock: int = Field(..., ge=0)
    min_stock: int = Field(default=0, ge=0)
    unit: Dict[str, str]  # {"zh-CN": "单位", "en-US": "Unit"}
    weight: Optional[Decimal] = None
    dimensions: Optional[str] = None
    category_id: int
    supplier_id: int
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[Dict[str, str]] = None
    description: Optional[Dict[str, str]] = None
    short_description: Optional[Dict[str, str]] = None
    specifications: Optional[Dict[str, Any]] = None
    price: Optional[Decimal] = Field(None, gt=0)
    cost_price: Optional[Decimal] = None
    stock: Optional[int] = Field(None, ge=0)
    min_stock: Optional[int] = Field(None, ge=0)
    unit: Optional[Dict[str, str]] = None
    weight: Optional[Decimal] = None
    dimensions: Optional[str] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime
    category: CategoryResponse
    images: List[ProductImageResponse] = []
    videos: List[ProductVideoResponse] = []

class ProductListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    sku: str
    name: Dict[str, str]
    short_description: Optional[Dict[str, str]] = None
    price: Decimal
    stock: int
    unit: Dict[str, str]
    category: CategoryResponse
    primary_image: Optional[ProductImageResponse] = None
    is_active: bool
    created_at: datetime

# Stock update schema
class StockUpdateRequest(BaseModel):
    stock: int = Field(..., ge=0)
    min_stock: Optional[int] = Field(None, ge=0)
