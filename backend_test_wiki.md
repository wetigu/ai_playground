# Tigu B2B 后端测试指南

## 目录
1. [测试概述](#测试概述)
2. [单元测试 (Unit Testing)](#单元测试-unit-testing)
3. [API 测试](#api-测试)
4. [数据库测试](#数据库测试)
5. [认证测试](#认证测试)
6. [GitHub Actions 工作流](#github-actions-工作流)
7. [测试最佳实践](#测试最佳实践)
8. [故障排除](#故障排除)

---

## 测试概述

### 测试金字塔架构
```
    /\
   /  \     E2E API Tests (少量) - Postman/Newman
  /____\    
 /      \   API Tests (中等) - FastAPI TestClient
/________\  Unit Tests (大量) - Pytest
```

### 技术栈
- **单元测试**: Pytest + FastAPI TestClient
- **API测试**: Pytest + HTTPX + FastAPI TestClient
- **数据库测试**: Pytest + MySQL (测试) / SQLite (内存)
- **Mock工具**: pytest-mock + responses
- **代码覆盖率**: pytest-cov
- **CI/CD**: GitHub Actions

### 实际项目结构
```
tigu_backend_fastapi/
├── tigu_backend_fastapi/
│   └── app/
│       ├── api/v1/routers/
│       │   ├── auth.py
│       │   ├── products.py
│       │   └── orders.py
│       ├── models/
│       │   ├── user.py
│       │   ├── product.py
│       │   └── order.py
│       ├── schemas/
│       ├── crud/
│       ├── services/
│       ├── core/
│       ├── utils/
│       │   └── id_generator.py
│       └── main.py
├── tests/
│   ├── test_example.py
│   ├── test_products.py
│   └── conftest.py
├── requirements.txt
├── pyproject.toml
└── pytest.ini
```

### ID 生成策略
项目使用雪花算法生成 BigInt ID：
- **用户 ID**: BigInt (非字符串)
- **公司 ID**: BigInt (非字符串)  
- **产品 ID**: Integer (自增)
- **订单 ID**: Integer (自增)
- **ID 生成**: `utils.id_generator.generate_id()` 使用时间戳+随机数

---

## 单元测试 (Unit Testing)

### 1. 环境配置

#### 安装测试依赖
```bash
# 进入后端项目目录
cd tigu_backend_fastapi

# 核心测试依赖
pip install pytest pytest-asyncio pytest-cov pytest-mock
pip install httpx  # FastAPI 测试客户端
pip install factory-boy  # 测试数据工厂
pip install faker  # 生成假数据

# 数据库测试
pip install pytest-postgresql  # PostgreSQL 测试
pip install sqlalchemy-utils  # 数据库工具

# 或者使用 Poetry
poetry add --group dev pytest pytest-asyncio pytest-cov pytest-mock
poetry add --group dev httpx factory-boy faker
poetry add --group dev pytest-postgresql sqlalchemy-utils
```

#### Pytest 配置文件 (`pytest.ini`)
```ini
[tool:pytest]
minversion = 6.0
addopts = 
    -ra
    --cov=tigu_backend_fastapi
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=80
    --strict-markers
    --strict-config
    --disable-warnings
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    unit: unit tests
    integration: integration tests
    api: API tests
    auth: authentication tests
    database: database tests
asyncio_mode = auto
```

#### 测试配置 (`tests/conftest.py`)
```python
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base, get_db
from app.core.config import settings
from app.models.user import User, Company, CompanyUser
from app.core.security import get_password_hash

# 测试数据库配置 - 使用 MySQL 测试数据库或 SQLite 内存数据库
import os

# 优先使用环境变量中的测试数据库URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    "sqlite:///:memory:"  # 内存数据库用于快速测试
)

# 如果使用 MySQL 测试数据库
# TEST_DATABASE_URL = "mysql+pymysql://test_user:test_password@localhost:3306/tigu_test_db"

if "sqlite" in TEST_DATABASE_URL:
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环用于测试"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    """创建测试用户"""
    from app.utils.id_generator import generate_id
    
    user_id = generate_id()  # 生成 BigInt ID
    user = User(
        id=user_id,
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User",
        phone="1234567890",
        is_active=True,
        auth_provider="email"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_company(db_session):
    """创建测试公司"""
    from app.utils.id_generator import generate_id, generate_company_code
    
    company_id = generate_id()  # 生成 BigInt ID
    company = Company(
        id=company_id,
        company_code=generate_company_code(),
        company_name={"zh-CN": "测试公司", "en-US": "Test Company"},
        company_type="buyer",  # 使用实际的类型值
        business_license="123456789",
        tax_number="987654321",
        is_verified=True
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company

@pytest.fixture
def authenticated_user_token(client, test_user):
    """获取认证用户的访问令牌"""
    login_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(authenticated_user_token):
    """认证请求头"""
    return {"Authorization": f"Bearer {authenticated_user_token}"}
```

### 2. 单元测试示例

#### 用户模型测试 (`tests/unit/test_models.py`)
```python
import pytest
from datetime import datetime
from app.models.user import User, Company
from app.core.security import get_password_hash, verify_password

class TestUserModel:
    """用户模型测试"""
    
    def test_create_user(self, db_session):
        """测试创建用户"""
        from app.utils.id_generator import generate_id
        
        user_id = generate_id()
        user = User(
            id=user_id,
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Test User",
            phone="1234567890",
            auth_provider="email"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id == user_id
        assert isinstance(user.id, int)  # BigInt 是整数类型
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.created_at is not None

    def test_password_hashing(self):
        """测试密码哈希"""
        password = "mysecretpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_user_relationships(self, db_session, test_company):
        """测试用户关系"""
        from app.utils.id_generator import generate_id
        
        user_id = generate_id()
        user = User(
            id=user_id,
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Test User",
            auth_provider="email",
            default_company_id=test_company.id
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.default_company_id == test_company.id
        assert isinstance(user.default_company_id, int)  # BigInt 类型

class TestCompanyModel:
    """公司模型测试"""
    
    def test_create_company(self, db_session):
        """测试创建公司"""
        from app.utils.id_generator import generate_id, generate_company_code
        
        company_id = generate_id()
        company_code = generate_company_code()
        company = Company(
            id=company_id,
            company_code=company_code,
            company_name={"zh-CN": "测试公司", "en-US": "Test Company"},
            company_type="supplier",  # 使用实际的枚举值
            business_license="BL123456789",
            tax_number="TN987654321"
        )
        db_session.add(company)
        db_session.commit()
        
        assert company.id == company_id
        assert isinstance(company.id, int)  # BigInt 类型
        assert company.company_code == company_code
        assert company.company_name["zh-CN"] == "测试公司"
        assert company.company_type == "supplier"
        assert company.is_verified is False
```

#### 认证服务测试 (`tests/unit/test_auth.py`)
```python
import pytest
from datetime import datetime, timedelta
from app.core.security import (
    create_access_token, create_refresh_token, verify_token,
    get_password_hash, verify_password
)
from app.core.config import settings

class TestAuthentication:
    """认证功能测试"""
    
    def test_create_access_token(self):
        """测试创建访问令牌"""
        data = {"sub": "user123"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        
        # 验证令牌
        payload = verify_token(token)
        assert payload["sub"] == "user123"
        assert payload["type"] == "access"

    def test_create_refresh_token(self):
        """测试创建刷新令牌"""
        data = {"sub": "user123"}
        token = create_refresh_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        
        # 验证令牌
        payload = verify_token(token)
        assert payload["sub"] == "user123"
        assert payload["type"] == "refresh"

    def test_token_expiration(self):
        """测试令牌过期"""
        data = {"sub": "user123"}
        # 创建已过期的令牌
        expired_token = create_access_token(
            data, expires_delta=timedelta(seconds=-1)
        )
        
        with pytest.raises(Exception):  # JWT expired
            verify_token(expired_token)

    def test_password_operations(self):
        """测试密码操作"""
        password = "supersecret123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False
        assert hashed != password  # 确保密码被哈希

---

## API 测试

### 1. 认证 API 测试 (`tests/api/test_auth_api.py`)

```python
import pytest
from fastapi import status

class TestAuthAPI:
    """认证 API 测试"""
    
    def test_register_success(self, client, db_session):
        """测试用户注册成功"""
        user_data = {
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User",
            "phone": "1234567890",
            "company_name": "Test Company",
            "company_type": "manufacturer",
            "business_license": "BL123456",
            "tax_number": "TN123456"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["full_name"] == user_data["full_name"]

    def test_register_duplicate_email(self, client, test_user):
        """测试重复邮箱注册"""
        user_data = {
            "email": test_user.email,  # 使用已存在的邮箱
            "password": "password123",
            "full_name": "Another User",
            "phone": "1234567890",
            "company_name": "Another Company",
            "company_type": "distributor",
            "business_license": "BL654321",
            "tax_number": "TN654321"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"]

    def test_login_success(self, client, test_user):
        """测试登录成功"""
        login_data = {
            "email": test_user.email,
            "password": "testpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == test_user.email

    def test_login_invalid_credentials(self, client, test_user):
        """测试无效凭据登录"""
        login_data = {
            "email": test_user.email,
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect email or password" in response.json()["detail"]

    def test_refresh_token(self, client, test_user):
        """测试刷新令牌"""
        # 先登录获取刷新令牌
        login_data = {
            "email": test_user.email,
            "password": "testpassword"
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        refresh_token = login_response.json()["refresh_token"]
        
        # 使用刷新令牌获取新的访问令牌
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/api/v1/auth/refresh-token", json=refresh_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_get_profile(self, client, auth_headers):
        """测试获取用户资料"""
        response = client.get("/api/v1/auth/profile", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "full_name" in data
```

### 2. 产品 API 测试 (`tests/api/test_products_api.py`)

```python
import pytest
from fastapi import status

class TestProductsAPI:
    """产品 API 测试"""
    
    def test_get_products_list(self, client, auth_headers):
        """测试获取产品列表"""
        response = client.get("/api/v1/products/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data

    def test_create_product(self, client, auth_headers):
        """测试创建产品"""
        product_data = {
            "name": {"zh-CN": "测试产品", "en-US": "Test Product"},
            "description": {"zh-CN": "产品描述", "en-US": "Product description"},
            "category": "cement",
            "price": 299.99,
            "unit": "bag",
            "stock_quantity": 100,
            "min_order_quantity": 10,
            "specifications": {"weight": "50kg", "grade": "P.O 42.5"}
        }
        
        response = client.post(
            "/api/v1/products/", 
            json=product_data, 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"]["zh-CN"] == "测试产品"
        assert data["price"] == 299.99
```



---

## 数据库测试

### 1. 测试数据工厂 (`tests/factories.py`)

```python
import factory
from factory.alchemy import SQLAlchemyModelFactory
from factory import Sequence, SubFactory, LazyAttribute
from faker import Faker
from decimal import Decimal
from app.models.user import User, Company, CompanyUser
from app.models.product import Product, Category
from app.models.order import Order, OrderItem
from app.core.security import get_password_hash
from app.utils.id_generator import generate_id, generate_company_code

fake = Faker('zh_CN')

class CompanyFactory(SQLAlchemyModelFactory):
    """公司工厂"""
    class Meta:
        model = Company
        sqlalchemy_session_persistence = "commit"
    
    id = LazyAttribute(lambda obj: generate_id())  # 使用雪花算法生成 BigInt ID
    company_code = LazyAttribute(lambda obj: generate_company_code())
    company_name = LazyAttribute(lambda obj: {
        "zh-CN": fake.company(),
        "en-US": fake.company()
    })
    company_type = factory.Iterator(["supplier", "buyer", "both"])  # 实际的枚举值
    business_license = Sequence(lambda n: f"BL{n:09d}")
    tax_number = Sequence(lambda n: f"TN{n:09d}")
    is_verified = True
    credit_rating = "A"

class UserFactory(SQLAlchemyModelFactory):
    """用户工厂"""
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"
    
    id = LazyAttribute(lambda obj: generate_id())  # 使用雪花算法生成 BigInt ID
    email = factory.LazyAttribute(lambda obj: fake.email())
    hashed_password = LazyAttribute(lambda obj: get_password_hash("password123"))
    full_name = factory.LazyAttribute(lambda obj: fake.name())
    phone = factory.LazyAttribute(lambda obj: fake.phone_number())
    is_active = True
    auth_provider = "email"
    default_company = SubFactory(CompanyFactory)

class CategoryFactory(SQLAlchemyModelFactory):
    """产品分类工厂"""
    class Meta:
        model = Category
        sqlalchemy_session_persistence = "commit"
    
    name = LazyAttribute(lambda obj: {
        "zh-CN": fake.word(),
        "en-US": fake.word()
    })
    slug = factory.LazyAttribute(lambda obj: fake.slug())
    is_active = True

class ProductFactory(SQLAlchemyModelFactory):
    """产品工厂"""
    class Meta:
        model = Product
        sqlalchemy_session_persistence = "commit"
    
    # 产品使用 Integer 自增 ID (不是 BigInt)
    sku = factory.LazyAttribute(lambda obj: fake.ean8())
    name = LazyAttribute(lambda obj: {
        "zh-CN": fake.word(),
        "en-US": fake.word()
    })
    price = factory.LazyAttribute(lambda obj: Decimal(fake.pydecimal(left_digits=3, right_digits=2, positive=True)))
    unit = LazyAttribute(lambda obj: {
        "zh-CN": fake.word(),
        "en-US": fake.word()
    })
    stock = factory.LazyAttribute(lambda obj: fake.random_int(min=0, max=1000))
    category = SubFactory(CategoryFactory)
    supplier_id = LazyAttribute(lambda obj: generate_id())  # 指向公司的 BigInt ID
    is_active = True
```

### 2. 数据库测试用例 (`tests/database/test_crud.py`)

```python
import pytest
from app.crud.user import create_user, get_user_by_email
from app.crud.product import create_product, get_products
from app.schemas.user import UserCreate
from app.schemas.product import ProductCreate

class TestCRUDOperations:
    """CRUD 操作测试"""
    
    def test_create_user(self, db_session):
        """测试创建用户"""
        user_data = UserCreate(
            email="test@example.com",
            password="password123",
            full_name="Test User",
            phone="1234567890"
        )
        
        created_user = create_user(db_session, user_data)
        
        assert created_user.email == user_data.email
        assert created_user.full_name == user_data.full_name
        assert created_user.id is not None

    def test_get_user_by_email(self, db_session, test_user):
        """测试根据邮箱获取用户"""
        user = get_user_by_email(db_session, test_user.email)
        
        assert user is not None
        assert user.email == test_user.email
        assert user.id == test_user.id

    def test_create_product(self, db_session, test_company):
        """测试创建产品"""
        product_data = ProductCreate(
            name={"zh-CN": "测试产品", "en-US": "Test Product"},
            category="cement",
            price=299.99,
            unit="bag",
            company_id=test_company.id
        )
        
        created_product = create_product(db_session, product_data)
        
        assert created_product.name["zh-CN"] == "测试产品"
        assert created_product.price == 299.99
        assert created_product.company_id == test_company.id

    def test_get_products_with_filters(self, db_session, test_company):
        """测试筛选产品"""
        # 创建测试产品
        products_data = [
            {"name": {"zh-CN": "水泥A", "en-US": "Cement A"}, "category": "cement", "price": 200.0},
            {"name": {"zh-CN": "水泥B", "en-US": "Cement B"}, "category": "cement", "price": 300.0},
            {"name": {"zh-CN": "钢材", "en-US": "Steel"}, "category": "steel", "price": 400.0}
        ]
        
        for product_data in products_data:
            product_data.update({"unit": "bag", "company_id": test_company.id})
            create_product(db_session, ProductCreate(**product_data))
        
        # 测试分类筛选
        cement_products = get_products(db_session, category="cement")
        assert len(cement_products) == 2
        
        # 测试价格范围筛选
        filtered_products = get_products(db_session, min_price=250.0, max_price=350.0)
        assert len(filtered_products) == 1
        assert filtered_products[0].name["zh-CN"] == "水泥B"
```

---

## 认证测试

### 1. JWT 令牌测试 (`tests/auth/test_jwt.py`)

```python
import pytest
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.core.security import (
    create_access_token, create_refresh_token, verify_token,
    SECRET_KEY, ALGORITHM
)
from app.core.config import settings

class TestJWTAuthentication:
    """JWT 认证测试"""
    
    def test_create_and_verify_access_token(self):
        """测试创建和验证访问令牌"""
        user_id = "user123"
        token = create_access_token(data={"sub": user_id})
        
        # 解码令牌
        payload = verify_token(token)
        
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_create_and_verify_refresh_token(self):
        """测试创建和验证刷新令牌"""
        user_id = "user123"
        token = create_refresh_token(data={"sub": user_id})
        
        # 解码令牌
        payload = verify_token(token)
        
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
        assert "exp" in payload

    def test_expired_token(self):
        """测试过期令牌"""
        user_id = "user123"
        # 创建已过期的令牌
        expired_time = datetime.utcnow() - timedelta(minutes=1)
        token = jwt.encode(
            {"sub": user_id, "exp": expired_time, "type": "access"}, 
            SECRET_KEY, 
            algorithm=ALGORITHM
        )
        
        with pytest.raises(JWTError):
            verify_token(token)

    def test_invalid_token(self):
        """测试无效令牌"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(JWTError):
            verify_token(invalid_token)

    def test_token_without_subject(self):
        """测试没有主题的令牌"""
        token = jwt.encode(
            {"exp": datetime.utcnow() + timedelta(minutes=30), "type": "access"}, 
            SECRET_KEY, 
            algorithm=ALGORITHM
        )
        
        with pytest.raises(JWTError):
            verify_token(token)
```

### 2. 权限测试 (`tests/auth/test_permissions.py`)

```python
import pytest
from fastapi import HTTPException
from app.api.deps import get_current_user, get_current_active_user
from app.models.user import User

class TestPermissions:
    """权限测试"""
    
    @pytest.mark.asyncio
    async def test_get_current_user_with_valid_token(self, db_session, test_user):
        """测试有效令牌获取当前用户"""
        token = create_access_token(data={"sub": test_user.id})
        
        # 模拟依赖注入
        current_user = await get_current_user(token=token, db=db_session)
        
        assert current_user.id == test_user.id
        assert current_user.email == test_user.email

    @pytest.mark.asyncio
    async def test_get_current_user_with_invalid_token(self, db_session):
        """测试无效令牌获取当前用户"""
        invalid_token = "invalid.token"
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=invalid_token, db=db_session)
        
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_active_user_inactive(self, db_session):
        """测试获取非活跃用户"""
        # 创建非活跃用户
        inactive_user = User(
            id="inactive_user",
            email="inactive@example.com",
            hashed_password="hashed_password",
            full_name="Inactive User",
            is_active=False
        )
        db_session.add(inactive_user)
        db_session.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(current_user=inactive_user)
        
        assert exc_info.value.status_code == 400
        assert "Inactive user" in str(exc_info.value.detail)
```
``` 