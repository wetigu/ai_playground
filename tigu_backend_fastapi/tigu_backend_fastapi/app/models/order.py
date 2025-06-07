# SQLAlchemy model for Order

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, DECIMAL, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..db.base import Base

class OrderStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(255), unique=True, index=True, nullable=False)
    
    # Customer information
    buyer_company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    buyer_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Supplier information
    supplier_company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Order details
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Pricing
    subtotal = Column(DECIMAL(12, 2), nullable=False)
    tax_amount = Column(DECIMAL(12, 2), default=0)
    shipping_amount = Column(DECIMAL(12, 2), default=0)
    discount_amount = Column(DECIMAL(12, 2), default=0)
    total_amount = Column(DECIMAL(12, 2), nullable=False)
    
    # Delivery information
    delivery_address = Column(JSON, nullable=False)
    delivery_contact = Column(JSON, nullable=False)
    requested_delivery_date = Column(DateTime, nullable=True)
    actual_delivery_date = Column(DateTime, nullable=True)
    
    # Additional information
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Item details
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    total_price = Column(DECIMAL(12, 2), nullable=False)
    
    # Product snapshot (in case product details change)
    product_name = Column(JSON, nullable=False)
    product_sku = Column(String(255), nullable=False)
    product_specifications = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="items")

class QuotationStatus(enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"

class Quotation(Base):
    __tablename__ = "quotations"
    
    id = Column(Integer, primary_key=True, index=True)
    quotation_number = Column(String(255), unique=True, index=True, nullable=False)
    
    # Customer information
    buyer_company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    buyer_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Supplier information
    supplier_company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    supplier_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Quotation details
    status = Column(Enum(QuotationStatus), default=QuotationStatus.DRAFT)
    
    # Pricing
    subtotal = Column(DECIMAL(12, 2), nullable=False)
    tax_amount = Column(DECIMAL(12, 2), default=0)
    discount_amount = Column(DECIMAL(12, 2), default=0)
    total_amount = Column(DECIMAL(12, 2), nullable=False)
    
    # Validity
    valid_until = Column(DateTime, nullable=False)
    
    # Terms and conditions
    payment_terms = Column(Text, nullable=True)
    delivery_terms = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Related order (if quotation is accepted)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    sent_at = Column(DateTime, nullable=True)
    viewed_at = Column(DateTime, nullable=True)
    responded_at = Column(DateTime, nullable=True)
    
    # Relationships
    items = relationship("QuotationItem", back_populates="quotation", cascade="all, delete-orphan")

class QuotationItem(Base):
    __tablename__ = "quotation_items"
    
    id = Column(Integer, primary_key=True, index=True)
    quotation_id = Column(Integer, ForeignKey("quotations.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Item details
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    total_price = Column(DECIMAL(12, 2), nullable=False)
    
    # Additional item information
    description = Column(Text, nullable=True)
    specifications = Column(JSON, nullable=True)
    brand = Column(String(255), nullable=True)
    model = Column(String(255), nullable=True)
    delivery_time = Column(Integer, nullable=True)  # days
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    quotation = relationship("Quotation", back_populates="items")
