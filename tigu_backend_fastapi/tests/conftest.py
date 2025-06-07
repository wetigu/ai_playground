# Pytest configuration and fixtures

import pytest
import asyncio
import sys
from pathlib import Path
from typing import Generator, Dict
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "tigu_backend_fastapi"))

from app.main import app
from app.db.base import get_db, Base
from app.core.security import get_password_hash
from app.models.user import User, Company, CompanyUser
from app.models.product import Category, Product
from app.utils.id_generator import generate_id, generate_company_code
from datetime import datetime

# Create test database
SQLITE_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLITE_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db_engine) -> Generator[Session, None, None]:
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session) -> TestClient:
    return TestClient(app)

# User fixtures
@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user"""
    user = User(
        id=generate_id(),
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        phone="+1-416-555-0001",
        is_active=True,
        email_verified_at=datetime.utcnow(),
        password_changed_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture  
def test_admin_user(db_session: Session) -> User:
    """Create a test admin user"""
    user = User(
        id=generate_id(),
        email="admin@example.com", 
        hashed_password=get_password_hash("adminpassword123"),
        full_name="Admin User",
        phone="+1-416-555-0002",
        is_active=True,
        is_superuser=True,
        email_verified_at=datetime.utcnow(),
        password_changed_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

# Company fixtures 
@pytest.fixture
def test_company(db_session: Session) -> Company:
    """Create a test company"""
    company = Company(
        id=generate_id(),
        company_code=generate_company_code(),
        company_name={"zh-CN": "测试公司", "en-US": "Test Company"},
        company_type="both",
        business_license="TEST-LICENSE-001",
        tax_number="TEST-TAX-001",
        legal_representative="Test Representative",
        registered_address="123 Test Street, Test City",
        business_scope={"zh-CN": "建材贸易", "en-US": "Building materials trading"},
        is_verified=True
    )
    db_session.add(company)
    db_session.commit() 
    db_session.refresh(company)
    return company

@pytest.fixture
def test_supplier_company(db_session: Session) -> Company:
    """Create a test supplier company"""
    company = Company(
        id=generate_id(),
        company_code=generate_company_code(),
        company_name={"zh-CN": "供应商公司", "en-US": "Supplier Company"}, 
        company_type="supplier",
        business_license="SUP-LICENSE-001",
        tax_number="SUP-TAX-001",
        legal_representative="Supplier Representative",
        registered_address="456 Supplier Ave, Supply City",
        business_scope={"zh-CN": "建材供应", "en-US": "Building materials supply"},
        is_verified=True
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company

# Category fixtures
@pytest.fixture
def test_category(db_session: Session) -> Category:
    """Create a test category"""
    category = Category(
        id=generate_id(),
        category_code="TEST-CAT-001",
        name={"zh-CN": "测试分类", "en-US": "Test Category"},
        description={"zh-CN": "测试用分类", "en-US": "Test category description"},
        is_active=True,
        sort_order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category

# Product fixtures
@pytest.fixture  
def test_product(db_session: Session, test_category: Category, test_supplier_company: Company) -> Product:
    """Create a test product"""
    product = Product(
        id=generate_id(),
        sku="TEST-PRODUCT-001",
        name={"zh-CN": "测试产品", "en-US": "Test Product"},
        description={"zh-CN": "测试产品描述", "en-US": "Test product description"},
        short_description={"zh-CN": "测试简述", "en-US": "Test short description"},
        specifications={"material": "Steel", "grade": "A36"},
        price=1000.00,
        cost_price=800.00,
        stock=100,
        min_stock=10,
        unit={"zh-CN": "件", "en-US": "Piece"},
        weight=10.50,
        dimensions="100mm×50mm×25mm", 
        category_id=test_category.id,
        supplier_id=test_supplier_company.id,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product

# Authentication fixtures
@pytest.fixture
def auth_headers(test_user: User) -> Dict[str, str]:
    """Get authentication headers for test user"""
    from app.core.security import create_access_token
    access_token = create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture  
def admin_auth_headers(test_admin_user: User) -> Dict[str, str]:
    """Get authentication headers for admin user"""
    from app.core.security import create_access_token
    access_token = create_access_token(subject=str(test_admin_user.id))
    return {"Authorization": f"Bearer {access_token}"}

# Configure pytest for async tests
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
