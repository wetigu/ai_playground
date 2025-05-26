# 后端开发规范与数据库设计指南

## 目录
1. [项目结构规范](#1-项目结构规范)
2. [数据库设计规范](#2-数据库设计规范)
3. [后端代码规范](#3-后端代码规范)
4. [API设计规范](#4-api设计规范)
5. [安全规范](#5-安全规范)
6. [测试规范](#6-测试规范)
7. [部署规范](#7-部署规范)

## 1. 项目结构规范

### 1.1 推荐的项目目录结构

```
tigu_backend_fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI应用入口
│   ├── api/                    # API路由
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py          # 路由聚合器
│   │       └── routers/
│   │           ├── __init__.py
│   │           ├── products.py
│   │           ├── categories.py
│   │           ├── users.py
│   │           └── orders.py
│   ├── core/                   # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py           # 应用配置
│   │   ├── security.py         # 安全相关
│   │   └── deps.py             # 依赖注入
│   ├── crud/                   # 数据库操作
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── user.py
│   │   └── order.py
│   ├── db/                     # 数据库相关
│   │   ├── __init__.py
│   │   ├── base.py             # 数据库基类
│   │   ├── session.py          # 数据库会话
│   │   └── init_db.py          # 数据库初始化
│   ├── models/                 # SQLAlchemy模型
│   │   ├── __init__.py
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── user.py
│   │   └── order.py
│   ├── schemas/                # Pydantic模型
│   │   ├── __init__.py
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── user.py
│   │   └── order.py
│   ├── services/               # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── product_service.py
│   │   ├── user_service.py
│   │   └── order_service.py
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       ├── email.py
│       └── helpers.py
├── tests/                      # 测试文件
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   └── test_crud/
├── migrations/                 # 数据库迁移
├── scripts/                    # 脚本文件
├── requirements.txt            # 依赖列表
├── pyproject.toml             # 项目配置
├── Dockerfile                 # Docker配置
├── docker-compose.yml         # Docker Compose配置
├── alembic.ini               # Alembic配置
└── README.md                 # 项目说明
```

## 2. 数据库设计规范

### 2.1 命名规范

- **表名**: 使用小写字母，单词间用下划线分隔，使用复数形式
  - 正确: `users`, `product_categories`, `order_items`
  - 错误: `User`, `productCategory`, `orderitem`

- **字段名**: 使用小写字母，单词间用下划线分隔
  - 正确: `user_id`, `created_at`, `full_name`
  - 错误: `userId`, `createdAt`, `fullName`

- **主键**: 统一使用 `id`
- **外键**: 使用 `表名_id` 格式，如 `user_id`, `category_id`

### 2.2 必需字段规范

每个表必须包含以下字段：
```sql
id INT AUTO_INCREMENT PRIMARY KEY,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
```

### 2.3 完整数据库表设计示例

```sql
-- 创建数据库
CREATE DATABASE tigu_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE tigu_db;

-- 用户表
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(20),
    company_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 产品分类表
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_parent (parent_id),
    INDEX idx_active (is_active),
    INDEX idx_sort (sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 产品表
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    sku VARCHAR(100) NOT NULL UNIQUE,
    price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2),
    stock INT NOT NULL DEFAULT 0,
    min_stock INT DEFAULT 0,
    unit VARCHAR(20) DEFAULT '件',
    weight DECIMAL(8,2),
    dimensions VARCHAR(100),
    category_id INT,
    supplier_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (supplier_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_sku (sku),
    INDEX idx_name (name),
    INDEX idx_category (category_id),
    INDEX idx_supplier (supplier_id),
    INDEX idx_active (is_active),
    INDEX idx_price (price),
    INDEX idx_stock (stock)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 订单表
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    user_id INT,
    status ENUM('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
    total_amount DECIMAL(12,2) NOT NULL,
    shipping_address TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_order_number (order_number),
    INDEX idx_user (user_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 订单项表
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_order (order_id),
    INDEX idx_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 产品图片表
CREATE TABLE product_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    image_url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(255),
    is_primary BOOLEAN DEFAULT FALSE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_product (product_id),
    INDEX idx_primary (is_primary)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## 3. 后端代码规范

### 3.1 配置管理 (app/core/config.py)

```python
import os
from typing import List, Union, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # 项目信息
    PROJECT_NAME: str = "建材B2B平台API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "建材B2B平台后端API服务"
    API_V1_STR: str = "/api/v1"
    
    # 环境配置
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # MySQL数据库配置
    MYSQL_SERVER: str = os.getenv("MYSQL_SERVER", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "password")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "tigu_db")
    
    # Redis配置
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # 安全配置
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "your-secret-key-change-in-production"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS配置
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = os.getenv(
        "BACKEND_CORS_ORIGINS", 
        "http://localhost:3000,http://localhost:8080"
    )
    
    # 邮件配置
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DB}?charset=utf8mb4"

    def get_cors_origins(self) -> List[str]:
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
        return self.BACKEND_CORS_ORIGINS

settings = Settings()
```

### 3.2 数据库会话管理 (app/db/session.py)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings

# 创建MySQL数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,  # MySQL连接回收时间
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,  # 开发环境显示SQL
    connect_args={
        "charset": "utf8mb4",
        "autocommit": False
    }
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 3.3 SQLAlchemy模型示例 (app/models/product.py)

```python
from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, ForeignKey, DateTime, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    cost_price = Column(DECIMAL(10, 2))
    stock = Column(Integer, nullable=False, default=0)
    min_stock = Column(Integer, default=0)
    unit = Column(String(20), default="件")
    weight = Column(DECIMAL(8, 2))
    dimensions = Column(String(100))
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"))
    supplier_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    category = relationship("Category", back_populates="products")
    supplier = relationship("User", back_populates="supplied_products")
    order_items = relationship("OrderItem", back_populates="product")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', sku='{self.sku}')>"

class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    image_url = Column(String(500), nullable=False)
    alt_text = Column(String(255))
    is_primary = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    product = relationship("Product", back_populates="images")

    def __repr__(self):
        return f"<ProductImage(id={self.id}, product_id={self.product_id}, is_primary={self.is_primary})>"
```

### 3.4 用户模型示例 (app/models/user.py)

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    phone = Column(String(20))
    company_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    supplied_products = relationship("Product", back_populates="supplier")
    orders = relationship("Order", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', full_name='{self.full_name}')>"
```

### 3.5 Pydantic模型示例 (app/schemas/product.py)

```python
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from datetime import datetime
from typing import Optional, List

class ProductImageBase(BaseModel):
    image_url: str = Field(..., description="图片URL")
    alt_text: Optional[str] = Field(None, description="图片描述")
    is_primary: bool = Field(False, description="是否为主图")
    sort_order: int = Field(0, description="排序")

class ProductImageCreate(ProductImageBase):
    pass

class ProductImage(ProductImageBase):
    id: int
    product_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="产品名称")
    description: Optional[str] = Field(None, description="产品描述")
    sku: str = Field(..., min_length=1, max_length=100, description="产品SKU")
    price: Decimal = Field(..., gt=0, description="产品价格")
    cost_price: Optional[Decimal] = Field(None, ge=0, description="成本价格")
    stock: int = Field(..., ge=0, description="库存数量")
    min_stock: int = Field(0, ge=0, description="最小库存")
    unit: str = Field("件", max_length=20, description="计量单位")
    weight: Optional[Decimal] = Field(None, ge=0, description="重量(kg)")
    dimensions: Optional[str] = Field(None, max_length=100, description="尺寸")
    category_id: Optional[int] = Field(None, description="分类ID")
    supplier_id: Optional[int] = Field(None, description="供应商ID")
    is_active: bool = Field(True, description="是否激活")

    @validator('price', 'cost_price')
    def validate_price(cls, v):
        if v is not None and v < 0:
            raise ValueError('价格不能为负数')
        return v

class ProductCreate(ProductBase):
    images: Optional[List[ProductImageCreate]] = Field([], description="产品图片")

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    min_stock: Optional[int] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=20)
    weight: Optional[Decimal] = Field(None, ge=0)
    dimensions: Optional[str] = Field(None, max_length=100)
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    is_active: Optional[bool] = None

class ProductInDBBase(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class Product(ProductInDBBase):
    images: List[ProductImage] = []

class ProductInDB(ProductInDBBase):
    pass

# 产品列表响应
class ProductListResponse(BaseModel):
    items: List[Product]
    total: int
    page: int
    size: int
    pages: int
```

### 3.6 CRUD操作示例 (app/crud/product.py)

```python
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from app.crud.base import CRUDBase
from app.models.product import Product, ProductImage
from app.schemas.product import ProductCreate, ProductUpdate

class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def get_by_sku(self, db: Session, *, sku: str) -> Optional[Product]:
        """根据SKU获取产品"""
        return db.query(Product).filter(Product.sku == sku).first()

    def get_by_category(
        self, 
        db: Session, 
        *, 
        category_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        """根据分类获取产品列表"""
        return (
            db.query(Product)
            .filter(Product.category_id == category_id)
            .filter(Product.is_active == True)
            .order_by(desc(Product.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_products(
        self,
        db: Session,
        *,
        keyword: str,
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """搜索产品"""
        query = db.query(Product).filter(Product.is_active == True)
        
        # 关键词搜索 - MySQL使用LIKE
        if keyword:
            search_term = f"%{keyword}%"
            query = query.filter(
                or_(
                    Product.name.like(search_term),
                    Product.description.like(search_term),
                    Product.sku.like(search_term)
                )
            )
        
        # 分类筛选
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        # 价格范围筛选
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        
        return query.order_by(desc(Product.created_at)).offset(skip).limit(limit).all()

    def get_low_stock_products(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        """获取库存不足的产品"""
        return (
            db.query(Product)
            .filter(Product.stock <= Product.min_stock)
            .filter(Product.is_active == True)
            .order_by(Product.stock.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_stock(
        self, 
        db: Session, 
        *, 
        product_id: int, 
        quantity_change: int
    ) -> Optional[Product]:
        """更新库存"""
        product = self.get(db, id=product_id)
        if product:
            new_stock = product.stock + quantity_change
            product.stock = max(0, new_stock)  # 确保库存不为负数
            db.add(product)
            db.commit()
            db.refresh(product)
        return product

    def create_with_images(
        self, 
        db: Session, 
        *, 
        obj_in: ProductCreate
    ) -> Product:
        """创建产品并添加图片"""
        # 创建产品
        product_data = obj_in.dict(exclude={'images'})
        db_product = Product(**product_data)
        db.add(db_product)
        db.flush()  # 获取产品ID但不提交事务
        
        # 添加图片
        if obj_in.images:
            for image_data in obj_in.images:
                db_image = ProductImage(
                    product_id=db_product.id,
                    **image_data.dict()
                )
                db.add(db_image)
        
        db.commit()
        db.refresh(db_product)
        return db_product

product = CRUDProduct(Product)
```

### 3.7 API路由示例 (app/api/v1/routers/products.py)

```python
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings

router = APIRouter()

@router.get("/", response_model=schemas.ProductListResponse)
def read_products(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    category_id: Optional[int] = Query(None, description="分类ID"),
    min_price: Optional[float] = Query(None, ge=0, description="最低价格"),
    max_price: Optional[float] = Query(None, ge=0, description="最高价格"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取产品列表
    支持关键词搜索、分类筛选、价格范围筛选
    """
    if keyword or category_id or min_price or max_price:
        products = crud.product.search_products(
            db=db,
            keyword=keyword or "",
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            skip=skip,
            limit=limit
        )
    else:
        products = crud.product.get_multi(db, skip=skip, limit=limit)
    
    # 获取总数
    total = db.query(models.Product).filter(models.Product.is_active == True).count()
    
    return schemas.ProductListResponse(
        items=products,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.post("/", response_model=schemas.Product)
def create_product(
    *,
    db: Session = Depends(deps.get_db),
    product_in: schemas.ProductCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    创建新产品
    """
    # 检查SKU是否已存在
    existing_product = crud.product.get_by_sku(db, sku=product_in.sku)
    if existing_product:
        raise HTTPException(
            status_code=400,
            detail="SKU已存在"
        )
    
    # 检查分类是否存在
    if product_in.category_id:
        category = crud.category.get(db, id=product_in.category_id)
        if not category:
            raise HTTPException(
                status_code=404,
                detail="分类不存在"
            )
    
    # 创建产品（包含图片）
    product = crud.product.create_with_images(db=db, obj_in=product_in)
    return product

@router.get("/{id}", response_model=schemas.Product)
def read_product(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    根据ID获取产品详情
    """
    product = crud.product.get(db=db, id=id)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    return product

@router.put("/{id}", response_model=schemas.Product)
def update_product(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    product_in: schemas.ProductUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    更新产品信息
    """
    product = crud.product.get(db=db, id=id)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    # 如果更新SKU，检查是否重复
    if product_in.sku and product_in.sku != product.sku:
        existing_product = crud.product.get_by_sku(db, sku=product_in.sku)
        if existing_product:
            raise HTTPException(
                status_code=400,
                detail="SKU已存在"
            )
    
    product = crud.product.update(db=db, db_obj=product, obj_in=product_in)
    return product

@router.delete("/{id}")
def delete_product(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    删除产品（软删除）
    """
    product = crud.product.get(db=db, id=id)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    # 软删除：设置为不活跃
    product_update = schemas.ProductUpdate(is_active=False)
    crud.product.update(db=db, db_obj=product, obj_in=product_update)
    return {"message": "产品删除成功"}

@router.get("/low-stock/", response_model=List[schemas.Product])
def get_low_stock_products(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取库存不足的产品列表
    """
    products = crud.product.get_low_stock_products(
        db=db, skip=skip, limit=limit
    )
    return products

@router.patch("/{id}/stock", response_model=schemas.Product)
def update_product_stock(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    quantity_change: int = Query(..., description="库存变化量（正数增加，负数减少）"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    更新产品库存
    """
    product = crud.product.update_stock(
        db=db, product_id=id, quantity_change=quantity_change
    )
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    return product
```

## 4. API设计规范

### 4.1 RESTful API设计原则

- 使用HTTP动词表示操作：
  - GET: 获取资源
  - POST: 创建资源
  - PUT: 完整更新资源
  - PATCH: 部分更新资源
  - DELETE: 删除资源

- URL设计规范：
  ```
  GET    /api/v1/products          # 获取产品列表
  POST   /api/v1/products          # 创建产品
  GET    /api/v1/products/{id}     # 获取单个产品
  PUT    /api/v1/products/{id}     # 更新产品
  DELETE /api/v1/products/{id}     # 删除产品
  PATCH  /api/v1/products/{id}/stock  # 更新库存
  ```

### 4.2 统一响应格式

```python
from pydantic import BaseModel
from typing import Any, Optional, List

class APIResponse(BaseModel):
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None
    error_code: Optional[str] = None

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: str
    details: Optional[Any] = None
```

### 4.3 错误处理

```python
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": f"HTTP_{exc.status_code}",
            "data": None
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "请求参数验证失败",
            "error_code": "VALIDATION_ERROR",
            "data": exc.errors()
        }
    )

async def mysql_exception_handler(request: Request, exc: Exception):
    logger.error(f"MySQL Error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "数据库操作失败",
            "error_code": "DATABASE_ERROR",
            "data": None
        }
    )
```

## 5. 安全规范

### 5.1 JWT认证实现 (app/core/security.py)

```python
from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any]) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload.get("sub")
    except JWTError:
        return None

def verify_refresh_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "refresh":
            return None
        return payload.get("sub")
    except JWTError:
        return None
```

### 5.2 依赖注入 (app/api/deps.py)

```python
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app import crud, models
from app.core import security
from app.db.session import SessionLocal

security_scheme = HTTPBearer()

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> models.User:
    token = credentials.credentials
    user_id = security.verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user

def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="权限不足"
        )
    return current_user
```

## 6. 测试规范

### 6.1 测试配置 (tests/conftest.py)

```python
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import get_db
from app.db.base import Base
from app.core.config import settings

# 测试数据库URL - 使用内存SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db() -> Generator:
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db) -> Generator:
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session) -> Generator:
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def normal_user_token_headers(client: TestClient) -> dict:
    return get_user_token_headers(client, "test@example.com", "testpass123")

def get_user_token_headers(client: TestClient, email: str, password: str) -> dict:
    login_data = {
        "username": email,
        "password": password,
    }
    r = client.post("/api/v1/auth/login", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
```

### 6.2 API测试示例 (tests/test_api/test_products.py)

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_create_product(client: TestClient, db_session: Session, normal_user_token_headers: dict):
    data = {
        "name": "测试产品",
        "sku": "TEST001",
        "price": 99.99,
        "stock": 100,
        "category_id": 1,
        "images": [
            {
                "image_url": "https://example.com/image1.jpg",
                "alt_text": "产品图片1",
                "is_primary": True,
                "sort_order": 1
            }
        ]
    }
    response = client.post(
        "/api/v1/products/", 
        json=data, 
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["sku"] == data["sku"]
    assert len(content["images"]) == 1

def test_get_products(client: TestClient, normal_user_token_headers: dict):
    response = client.get("/api/v1/products/", headers=normal_user_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert "items" in content
    assert "total" in content
    assert "page" in content
    assert "size" in content
    assert "pages" in content

def test_search_products(client: TestClient, normal_user_token_headers: dict):
    # 先创建一个产品
    data = {
        "name": "搜索测试产品",
        "sku": "SEARCH001",
        "price": 199.99,
        "stock": 50
    }
    client.post("/api/v1/products/", json=data, headers=normal_user_token_headers)
    
    # 搜索产品
    response = client.get(
        "/api/v1/products/?keyword=搜索测试", 
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["items"]) > 0
    assert "搜索测试" in content["items"][0]["name"]

def test_update_product_stock(client: TestClient, normal_user_token_headers: dict):
    # 先创建一个产品
    data = {
        "name": "库存测试产品",
        "sku": "STOCK001",
        "price": 299.99,
        "stock": 100
    }
    response = client.post("/api/v1/products/", json=data, headers=normal_user_token_headers)
    product_id = response.json()["id"]
    
    # 更新库存
    response = client.patch(
        f"/api/v1/products/{product_id}/stock?quantity_change=-10",
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert content["stock"] == 90
```

## 7. 部署规范

### 7.1 Docker配置 (Dockerfile)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建上传目录
RUN mkdir -p uploads

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 7.2 Docker Compose配置 (docker-compose.yml)

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MYSQL_SERVER=db
      - MYSQL_PORT=3306
      - MYSQL_USER=tigu_user
      - MYSQL_PASSWORD=tigu_password
      - MYSQL_DB=tigu_db
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=your-production-secret-key
      - ENVIRONMENT=production
      - DEBUG=false
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped

  db:
    image: mysql:8.0
    environment:
      - MYSQL_DATABASE=tigu_db
      - MYSQL_USER=tigu_user
      - MYSQL_PASSWORD=tigu_password
      - MYSQL_ROOT_PASSWORD=root_password
    volumes:
      - mysql_data:/var/lib/mysql
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "3306:3306"
    command: --default-authentication-plugin=mysql_native_password
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      timeout: 20s
      retries: 10
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

volumes:
  mysql_data:
  redis_data:
```

### 7.3 环境变量配置 (.env.example)

```bash
# 项目配置
PROJECT_NAME=建材B2B平台API
ENVIRONMENT=production
DEBUG=false

# MySQL数据库配置
MYSQL_SERVER=localhost
MYSQL_PORT=3306
MYSQL_USER=tigu_user
MYSQL_PASSWORD=your_secure_password
MYSQL_DB=tigu_db

# Redis配置
REDIS_URL=redis://localhost:6379

# 安全配置
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS配置
BACKEND_CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# 邮件配置
SMTP_TLS=true
SMTP_PORT=587
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=your-email@gmail.com
EMAILS_FROM_NAME=建材B2B平台

# 文件上传配置
MAX_FILE_SIZE=10485760
UPLOAD_DIR=uploads
```

### 7.4 依赖管理 (requirements.txt)

```text
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pymysql==1.1.0
cryptography==41.0.7
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
alembic==1.13.0
python-dotenv==1.0.0
redis==5.0.1
celery==5.3.4
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
```

## 8. 开发最佳实践

### 8.1 代码质量

1. **使用类型注解**: 所有函数和方法都应该有完整的类型注解
2. **文档字符串**: 所有公共函数和类都应该有详细的文档字符串
3. **代码格式化**: 使用black和isort进行代码格式化
4. **静态分析**: 使用mypy进行类型检查

### 8.2 MySQL优化

1. **索引优化**: 为经常查询的字段创建合适的索引
2. **查询优化**: 避免SELECT *，使用具体字段名
3. **连接池**: 合理配置数据库连接池参数
4. **事务管理**: 合理使用事务，避免长事务

```python
# 数据库连接池配置示例
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,  # 1小时回收连接
    pool_size=10,       # 连接池大小
    max_overflow=20,    # 最大溢出连接数
    echo=settings.DEBUG,
    connect_args={
        "charset": "utf8mb4",
        "autocommit": False,
        "init_command": "SET sql_mode='STRICT_TRANS_TABLES'"
    }
)
```

### 8.3 性能优化

1. **分页查询**: 大数据量查询必须使用分页
2. **缓存策略**: 使用Redis缓存热点数据
3. **异步处理**: 使用Celery处理耗时任务
4. **数据库读写分离**: 生产环境考虑主从分离

### 8.4 监控和日志

```python
import logging
from app.core.config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 在关键操作中添加日志
@router.post("/products/")
def create_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating product: {product_in.name}")
    try:
        product = crud.product.create_with_images(db=db, obj_in=product_in)
        logger.info(f"Product created successfully: {product.id}")
        return product
    except Exception as e:
        logger.error(f"Failed to create product: {str(e)}")
        raise
```
