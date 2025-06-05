# API Endpoints for orders

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from app.db.base import get_db
from app.api.deps import get_current_user, get_current_active_user
from app.models.order import Order, OrderItem, Quotation, QuotationItem, OrderStatus, PaymentStatus, QuotationStatus
from app.models.product import Product
from app.models.user import User
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse,
    QuotationCreate, QuotationUpdate, QuotationResponse,
    OrderStatusEnum, PaymentStatusEnum, QuotationStatusEnum
)
from app.schemas.user import PaginatedResponse
import math
import uuid

router = APIRouter()

# Helper function to generate order numbers
def generate_order_number() -> str:
    return f"ORD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

def generate_quotation_number() -> str:
    return f"QUO-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

# Order endpoints
@router.get("/", response_model=PaginatedResponse)
async def get_orders(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[OrderStatusEnum] = Query(None, description="Filter by order status"),
    payment_status: Optional[PaymentStatusEnum] = Query(None, description="Filter by payment status"),
    buyer_company_id: Optional[int] = Query(None, description="Filter by buyer company"),
    supplier_company_id: Optional[int] = Query(None, description="Filter by supplier company"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get orders with pagination and filters
    """
    query = db.query(Order).options(
        joinedload(Order.items)
    )
    
    # Apply filters based on user's company associations
    # In a real app, you'd filter based on user's company memberships
    
    if status:
        query = query.filter(Order.status == status)
    
    if payment_status:
        query = query.filter(Order.payment_status == payment_status)
    
    if buyer_company_id:
        query = query.filter(Order.buyer_company_id == buyer_company_id)
    
    if supplier_company_id:
        query = query.filter(Order.supplier_company_id == supplier_company_id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    orders = query.order_by(Order.created_at.desc()).offset(offset).limit(per_page).all()
    
    return PaginatedResponse(
        items=orders,
        total=total,
        page=page,
        per_page=per_page,
        pages=math.ceil(total / per_page)
    )

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get order by ID
    """
    order = db.query(Order).options(
        joinedload(Order.items)
    ).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if user has permission to view this order
    # In a real app, you'd check if user belongs to buyer or supplier company
    
    return order

@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new order
    """
    # Calculate totals
    subtotal = Decimal('0')
    order_items = []
    
    for item_data in order_data.items:
        # Get product
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {item_data.product_id} not found"
            )
        
        # Check stock
        if product.stock < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product {product.sku}"
            )
        
        # Calculate item total
        item_total = item_data.unit_price * item_data.quantity
        subtotal += item_total
        
        # Create order item
        order_item = OrderItem(
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            total_price=item_total,
            product_name=product.name,
            product_sku=product.sku,
            product_specifications=product.specifications
        )
        order_items.append(order_item)
    
    # Create order
    order = Order(
        order_number=generate_order_number(),
        buyer_company_id=order_data.buyer_company_id,
        buyer_user_id=current_user.id,
        supplier_company_id=order_data.supplier_company_id,
        subtotal=subtotal,
        tax_amount=Decimal('0'),  # Calculate based on business rules
        shipping_amount=Decimal('0'),  # Calculate based on business rules
        discount_amount=Decimal('0'),
        total_amount=subtotal,  # Add tax and shipping, subtract discount
        delivery_address=order_data.delivery_address,
        delivery_contact=order_data.delivery_contact,
        requested_delivery_date=order_data.requested_delivery_date,
        notes=order_data.notes,
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.PENDING
    )
    
    db.add(order)
    db.flush()  # Get order ID
    
    # Add order items
    for order_item in order_items:
        order_item.order_id = order.id
        db.add(order_item)
    
    db.commit()
    
    # Load relationships for response
    order = db.query(Order).options(
        joinedload(Order.items)
    ).filter(Order.id == order.id).first()
    
    return order

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update order
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check permissions
    # In a real app, you'd check if user belongs to buyer or supplier company
    
    # Update fields
    update_data = order_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    db.commit()
    db.refresh(order)
    
    # Load relationships for response
    order = db.query(Order).options(
        joinedload(Order.items)
    ).filter(Order.id == order.id).first()
    
    return order

# Quotation endpoints
@router.get("/quotations/", response_model=PaginatedResponse)
async def get_quotations(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[QuotationStatusEnum] = Query(None, description="Filter by quotation status"),
    buyer_company_id: Optional[int] = Query(None, description="Filter by buyer company"),
    supplier_company_id: Optional[int] = Query(None, description="Filter by supplier company"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get quotations with pagination and filters
    """
    query = db.query(Quotation).options(
        joinedload(Quotation.items)
    )
    
    if status:
        query = query.filter(Quotation.status == status)
    
    if buyer_company_id:
        query = query.filter(Quotation.buyer_company_id == buyer_company_id)
    
    if supplier_company_id:
        query = query.filter(Quotation.supplier_company_id == supplier_company_id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    quotations = query.order_by(Quotation.created_at.desc()).offset(offset).limit(per_page).all()
    
    return PaginatedResponse(
        items=quotations,
        total=total,
        page=page,
        per_page=per_page,
        pages=math.ceil(total / per_page)
    )

@router.get("/quotations/{quotation_id}", response_model=QuotationResponse)
async def get_quotation(
    quotation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get quotation by ID
    """
    quotation = db.query(Quotation).options(
        joinedload(Quotation.items)
    ).filter(Quotation.id == quotation_id).first()
    
    if not quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found"
        )
    
    # Mark as viewed if buyer is viewing
    if (quotation.buyer_user_id == current_user.id and 
        quotation.status == QuotationStatus.SENT and 
        quotation.viewed_at is None):
        quotation.status = QuotationStatus.VIEWED
        quotation.viewed_at = datetime.utcnow()
        db.commit()
    
    return quotation

@router.post("/quotations/", response_model=QuotationResponse)
async def create_quotation(
    quotation_data: QuotationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new quotation
    """
    # Calculate totals
    subtotal = Decimal('0')
    quotation_items = []
    
    for item_data in quotation_data.items:
        # Get product
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {item_data.product_id} not found"
            )
        
        # Calculate item total
        item_total = item_data.unit_price * item_data.quantity
        subtotal += item_total
        
        # Create quotation item
        quotation_item = QuotationItem(
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            total_price=item_total,
            description=item_data.description,
            specifications=item_data.specifications,
            brand=item_data.brand,
            model=item_data.model,
            delivery_time=item_data.delivery_time
        )
        quotation_items.append(quotation_item)
    
    # Create quotation
    quotation = Quotation(
        quotation_number=generate_quotation_number(),
        buyer_company_id=quotation_data.buyer_company_id,
        buyer_user_id=quotation_data.buyer_user_id,
        supplier_company_id=quotation_data.supplier_company_id,
        supplier_user_id=current_user.id,
        subtotal=subtotal,
        tax_amount=Decimal('0'),
        discount_amount=Decimal('0'),
        total_amount=subtotal,
        valid_until=quotation_data.valid_until,
        payment_terms=quotation_data.payment_terms,
        delivery_terms=quotation_data.delivery_terms,
        notes=quotation_data.notes,
        status=QuotationStatus.DRAFT
    )
    
    db.add(quotation)
    db.flush()  # Get quotation ID
    
    # Add quotation items
    for quotation_item in quotation_items:
        quotation_item.quotation_id = quotation.id
        db.add(quotation_item)
    
    db.commit()
    
    # Load relationships for response
    quotation = db.query(Quotation).options(
        joinedload(Quotation.items)
    ).filter(Quotation.id == quotation.id).first()
    
    return quotation

@router.put("/quotations/{quotation_id}", response_model=QuotationResponse)
async def update_quotation(
    quotation_id: int,
    quotation_data: QuotationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update quotation
    """
    quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found"
        )
    
    # Update fields
    update_data = quotation_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(quotation, field, value)
    
    db.commit()
    db.refresh(quotation)
    
    # Load relationships for response
    quotation = db.query(Quotation).options(
        joinedload(Quotation.items)
    ).filter(Quotation.id == quotation.id).first()
    
    return quotation

@router.post("/quotations/{quotation_id}/send")
async def send_quotation(
    quotation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Send quotation to buyer
    """
    quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found"
        )
    
    if quotation.status != QuotationStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft quotations can be sent"
        )
    
    quotation.status = QuotationStatus.SENT
    quotation.sent_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Quotation sent successfully"}

@router.post("/quotations/{quotation_id}/accept")
async def accept_quotation(
    quotation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Accept quotation and create order
    """
    quotation = db.query(Quotation).options(
        joinedload(Quotation.items)
    ).filter(Quotation.id == quotation_id).first()
    
    if not quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found"
        )
    
    if quotation.status not in [QuotationStatus.SENT, QuotationStatus.VIEWED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quotation cannot be accepted in current status"
        )
    
    # Check if quotation is still valid
    if quotation.valid_until < datetime.utcnow():
        quotation.status = QuotationStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quotation has expired"
        )
    
    # Create order from quotation
    order = Order(
        order_number=generate_order_number(),
        buyer_company_id=quotation.buyer_company_id,
        buyer_user_id=quotation.buyer_user_id,
        supplier_company_id=quotation.supplier_company_id,
        subtotal=quotation.subtotal,
        tax_amount=quotation.tax_amount,
        shipping_amount=Decimal('0'),
        discount_amount=quotation.discount_amount,
        total_amount=quotation.total_amount,
        delivery_address={},  # Would need to be provided
        delivery_contact={},  # Would need to be provided
        notes=quotation.notes,
        status=OrderStatus.CONFIRMED,
        payment_status=PaymentStatus.PENDING
    )
    
    db.add(order)
    db.flush()
    
    # Create order items from quotation items
    for q_item in quotation.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=q_item.product_id,
            quantity=q_item.quantity,
            unit_price=q_item.unit_price,
            total_price=q_item.total_price,
            product_name={},  # Would get from product
            product_sku="",   # Would get from product
            product_specifications=q_item.specifications
        )
        db.add(order_item)
    
    # Update quotation status
    quotation.status = QuotationStatus.ACCEPTED
    quotation.responded_at = datetime.utcnow()
    quotation.order_id = order.id
    
    db.commit()
    
    return {"message": "Quotation accepted and order created", "order_id": order.id}

@router.post("/quotations/{quotation_id}/reject")
async def reject_quotation(
    quotation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Reject quotation
    """
    quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found"
        )
    
    if quotation.status not in [QuotationStatus.SENT, QuotationStatus.VIEWED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quotation cannot be rejected in current status"
        )
    
    quotation.status = QuotationStatus.REJECTED
    quotation.responded_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Quotation rejected"}
