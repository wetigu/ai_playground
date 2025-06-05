# Pydantic schema for Order (request/response)

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum

# Enums
class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentStatusEnum(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class QuotationStatusEnum(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"

# Order Item schemas
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    product_name: Dict[str, str]
    product_sku: str
    product_specifications: Optional[Dict[str, Any]] = None
    created_at: datetime

# Order schemas
class OrderBase(BaseModel):
    buyer_company_id: int
    supplier_company_id: int
    delivery_address: Dict[str, Any]
    delivery_contact: Dict[str, Any]
    requested_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[OrderStatusEnum] = None
    payment_status: Optional[PaymentStatusEnum] = None
    delivery_address: Optional[Dict[str, Any]] = None
    delivery_contact: Optional[Dict[str, Any]] = None
    requested_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None

class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    order_number: str
    buyer_company_id: int
    buyer_user_id: int
    supplier_company_id: int
    status: OrderStatusEnum
    payment_status: PaymentStatusEnum
    subtotal: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    delivery_address: Dict[str, Any]
    delivery_contact: Dict[str, Any]
    requested_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []

# Quotation Item schemas
class QuotationItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)
    description: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    delivery_time: Optional[int] = None  # days

class QuotationItemCreate(QuotationItemBase):
    pass

class QuotationItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    description: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    delivery_time: Optional[int] = None
    created_at: datetime

# Quotation schemas
class QuotationBase(BaseModel):
    buyer_company_id: int
    buyer_user_id: int
    supplier_company_id: int
    valid_until: datetime
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    notes: Optional[str] = None

class QuotationCreate(QuotationBase):
    items: List[QuotationItemCreate]

class QuotationUpdate(BaseModel):
    status: Optional[QuotationStatusEnum] = None
    valid_until: Optional[datetime] = None
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    notes: Optional[str] = None

class QuotationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    quotation_number: str
    buyer_company_id: int
    buyer_user_id: int
    supplier_company_id: int
    supplier_user_id: int
    status: QuotationStatusEnum
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    valid_until: datetime
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    notes: Optional[str] = None
    order_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    sent_at: Optional[datetime] = None
    viewed_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None
    items: List[QuotationItemResponse] = []
