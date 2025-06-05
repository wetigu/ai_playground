# API Endpoints for products

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional
from app.db.base import get_db
from app.api.deps import get_current_user, get_current_active_user, get_optional_current_user
from app.models.product import Product, Category, ProductImage, ProductVideo
from app.models.user import User
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    CategoryCreate, CategoryUpdate, CategoryResponse,
    StockUpdateRequest
)
from app.schemas.user import PaginatedResponse
import math

router = APIRouter()

# Category endpoints
@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    parent_id: Optional[int] = Query(None, description="Filter by parent category ID"),
    is_active: bool = Query(True, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    Get all categories
    """
    query = db.query(Category).filter(Category.is_active == is_active)
    
    if parent_id is not None:
        query = query.filter(Category.parent_id == parent_id)
    
    categories = query.order_by(Category.sort_order, Category.name).all()
    return categories

@router.get("/categories/{slug}", response_model=CategoryResponse)
async def get_category_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Get category by slug
    """
    category = db.query(Category).filter(
        Category.slug == slug,
        Category.is_active == True
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return category

@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new category (admin only)
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if slug already exists
    existing = db.query(Category).filter(Category.slug == category_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category slug already exists"
        )
    
    category = Category(**category_data.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

# Product endpoints
@router.get("/", response_model=PaginatedResponse)
async def get_products(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    category_slug: Optional[str] = Query(None, description="Filter by category slug"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    supplier_id: Optional[int] = Query(None, description="Filter by supplier ID"),
    search: Optional[str] = Query(None, description="Search in product name and description"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock availability"),
    is_active: bool = Query(True, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    Get products with pagination and filters
    """
    query = db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.images)
    ).filter(Product.is_active == is_active)
    
    # Apply filters
    if category_slug:
        category = db.query(Category).filter(Category.slug == category_slug).first()
        if category:
            query = query.filter(Product.category_id == category.id)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if supplier_id:
        query = query.filter(Product.supplier_id == supplier_id)
    
    if search:
        # Search in JSON fields (simplified - in production you'd use full-text search)
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.contains(search_term),
                Product.description.contains(search_term),
                Product.sku.contains(search_term)
            )
        )
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    if in_stock is not None:
        if in_stock:
            query = query.filter(Product.stock > 0)
        else:
            query = query.filter(Product.stock == 0)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    products = query.offset(offset).limit(per_page).all()
    
    # Convert to list response format
    items = []
    for product in products:
        primary_image = None
        if product.images:
            primary_image = next((img for img in product.images if img.is_primary), product.images[0])
        
        items.append(ProductListResponse(
            id=product.id,
            sku=product.sku,
            name=product.name,
            short_description=product.short_description,
            price=product.price,
            stock=product.stock,
            unit=product.unit,
            category=product.category,
            primary_image=primary_image,
            is_active=product.is_active,
            created_at=product.created_at
        ))
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=math.ceil(total / per_page)
    )

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Get product by ID
    """
    product = db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.images),
        joinedload(Product.videos)
    ).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product

@router.post("/", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new product
    """
    # Check if SKU already exists
    existing = db.query(Product).filter(Product.sku == product_data.sku).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product SKU already exists"
        )
    
    # Verify category exists
    category = db.query(Category).filter(Category.id == product_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found"
        )
    
    product = Product(**product_data.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    
    # Load relationships for response
    product = db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.images),
        joinedload(Product.videos)
    ).filter(Product.id == product.id).first()
    
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update product
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if user has permission to update this product
    # In a real app, you'd check if user belongs to the supplier company
    
    # Update fields
    update_data = product_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    # Load relationships for response
    product = db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.images),
        joinedload(Product.videos)
    ).filter(Product.id == product.id).first()
    
    return product

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete product (soft delete by setting is_active to False)
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Soft delete
    product.is_active = False
    db.commit()
    
    return {"message": "Product deleted successfully"}

@router.get("/low-stock/", response_model=List[ProductListResponse])
async def get_low_stock_products(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get products with low stock
    """
    products = db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.images)
    ).filter(
        Product.is_active == True,
        Product.stock <= Product.min_stock
    ).all()
    
    items = []
    for product in products:
        primary_image = None
        if product.images:
            primary_image = next((img for img in product.images if img.is_primary), product.images[0])
        
        items.append(ProductListResponse(
            id=product.id,
            sku=product.sku,
            name=product.name,
            short_description=product.short_description,
            price=product.price,
            stock=product.stock,
            unit=product.unit,
            category=product.category,
            primary_image=primary_image,
            is_active=product.is_active,
            created_at=product.created_at
        ))
    
    return items

@router.patch("/{product_id}/stock", response_model=ProductResponse)
async def update_product_stock(
    product_id: int,
    stock_data: StockUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update product stock
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update stock
    product.stock = stock_data.stock
    if stock_data.min_stock is not None:
        product.min_stock = stock_data.min_stock
    
    db.commit()
    db.refresh(product)
    
    # Load relationships for response
    product = db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.images),
        joinedload(Product.videos)
    ).filter(Product.id == product.id).first()
    
    return product
