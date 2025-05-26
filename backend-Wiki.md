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
id SERIAL PRIMARY KEY,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
```

### 2.3 完整数据库表设计示例

```sql
-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(20),
    company_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 产品分类表
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES categories(id),
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 产品表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    sku VARCHAR(100) UNIQUE NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2),
    stock INTEGER NOT NULL DEFAULT 0,
    min_stock INTEGER DEFAULT 0,
    unit VARCHAR(20) DEFAULT '件',
    weight DECIMAL(8,2),
    dimensions VARCHAR(100),
    category_id INTEGER REFERENCES categories(id),
    supplier_id INTEGER REFERENCES users(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 订单表
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'pending',
    total_amount DECIMAL(12,2) NOT NULL,
    shipping_address TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 订单项表
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_items_order ON order_items(order_id);
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
    
    # 数据库配置
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:password@localhost:5432/tigu_db"
    )
    
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

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20
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
from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    cost_price = Column(Numeric(10, 2))
    stock = Column(Integer, nullable=False, default=0)
    min_stock = Column(Integer, default=0)
    unit = Column(String(20), default="件")
    weight = Column(Numeric(8, 2))
    dimensions = Column(String(100))
    category_id = Column(Integer, ForeignKey("categories.id"))
    supplier_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    category = relationship("Category", back_populates="products")
    supplier = relationship("User", back_populates="supplied_products")
    order_items = relationship("OrderItem", back_populates="product")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', sku='{self.sku}')>"
```

### 3.4 Pydantic模型示例 (app/schemas/product.py)

```python
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from datetime import datetime
from typing import Optional, List

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
    category_id: int = Field(..., description="分类ID")
    supplier_id: Optional[int] = Field(None, description="供应商ID")
    is_active: bool = Field(True, description="是否激活")

    @validator('price', 'cost_price')
    def validate_price(cls, v):
        if v is not None and v < 0:
            raise ValueError('价格不能为负数')
        return v

class ProductCreate(ProductBase):
    pass

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
    pass

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

### 3.5 CRUD操作示例 (app/crud/product.py)

```python
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.crud.base import CRUDBase
from app.models.product import Product
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
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{keyword}%"),
                    Product.description.ilike(f"%{keyword}%"),
                    Product.sku.ilike(f"%{keyword}%")
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
        
        return query.offset(skip).limit(limit).all()

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
            product.stock += quantity_change
            if product.stock < 0:
                product.stock = 0
            db.add(product)
            db.commit()
            db.refresh(product)
        return product

product = CRUDProduct(Product)
```

### 3.6 API路由示例 (app/api/v1/routers/products.py)

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
    
    total = crud.product.count(db)
    
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
    category = crud.category.get(db, id=product_in.category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="分类不存在"
        )
    
    product = crud.product.create(db=db, obj_in=product_in)
    return product

@router.get("/{id}", response_model=schemas.Product)
def read_product(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    根据ID获取产品
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
    更新产品
    """
    product = crud.product.get(db=db, id=id)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
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
    删除产品
    """
    product = crud.product.get(db=db, id=id)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    product = crud.product.remove(db=db, id=id)
    return {"message": "产品删除成功"}

@router.get("/low-stock/", response_model=List[schemas.Product])
def get_low_stock_products(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取库存不足的产品
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
    quantity_change: int,
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
  ```

### 4.2 统一响应格式

```python
from pydantic import BaseModel
from typing import Any, Optional

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
```

### 4.3 错误处理

```python
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
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
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "请求参数验证失败",
            "error_code": "VALIDATION_ERROR",
            "data": exc.errors()
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

# 测试数据库URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
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
```

### 6.2 API测试示例 (tests/test_api/test_products.py)

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_create_product(client: TestClient, db_session: Session):
    data = {
        "name": "测试产品",
        "sku": "TEST001",
        "price": 99.99,
        "stock": 100,
        "category_id": 1
    }
    response = client.post("/api/v1/products/", json=data)
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["sku"] == data["sku"]

def test_get_products(client: TestClient):
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    content = response.json()
    assert "items" in content
    assert "total" in content
```

## 7. 部署规范

### 7.1 Docker配置 (Dockerfile)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
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
      - DATABASE_URL=postgresql://postgres:password@db:5432/tigu_db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=tigu_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 7.3 环境变量配置 (.env.example)

```bash
# 项目配置
PROJECT_NAME=建材B2B平台API
ENVIRONMENT=production
DEBUG=false

# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/tigu_db

# Redis配置
REDIS_URL=redis://localhost:6379

# 安全配置
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

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
```

## 8. 开发最佳实践

### 8.1 代码质量

1. **使用类型注解**: 所有函数和方法都应该有完整的类型注解
2. **文档字符串**: 所有公共函数和类都应该有详细的文档字符串
3. **代码格式化**: 使用black和isort进行代码格式化
4. **静态分析**: 使用mypy进行类型检查

### 8.2 性能优化

1. **数据库查询优化**: 使用适当的索引，避免N+1查询
2. **缓存策略**: 对频繁访问的数据使用Redis缓存
3. **分页处理**: 大数据量查询必须使用分页
4. **异步处理**: 对于耗时操作使用异步任务队列

### 8.3 监控和日志

```python
import logging
from app.core.config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# 在关键操作中添加日志
@router.post("/products/")
def create_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating product: {product_in.name}")
    try:
        product = crud.product.create(db=db, obj_in=product_in)
        logger.info(f"Product created successfully: {product.id}")
        return product
    except Exception as e:
        logger.error(f"Failed to create product: {str(e)}")
        raise
```

这个文档提供了完整的后端开发规范和数据库设计指南，包含了实际可用的代码示例。开发团队可以参考这些规范来确保代码质量、一致性和可维护性。 