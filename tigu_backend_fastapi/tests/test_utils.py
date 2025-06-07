"""
Test utilities and helper functions for API testing
"""
import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from decimal import Decimal
import json

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "tigu_backend_fastapi"))


class APITestHelper:
    """Helper class for common API testing patterns"""
    
    def __init__(self, client: TestClient):
        self.client = client
    
    def assert_pagination_response(self, response_data: dict, expected_min_total: int = 0):
        """Assert that response has proper pagination structure"""
        assert "items" in response_data
        assert "total" in response_data
        assert "page" in response_data
        assert "size" in response_data
        assert "pages" in response_data
        
        assert isinstance(response_data["items"], list)
        assert isinstance(response_data["total"], int)
        assert isinstance(response_data["page"], int)
        assert isinstance(response_data["size"], int)
        assert isinstance(response_data["pages"], int)
        
        assert response_data["total"] >= expected_min_total
        assert response_data["page"] >= 1
        assert response_data["size"] >= 0
        assert response_data["pages"] >= 0
    
    def assert_error_response(self, response, expected_status: int, expected_message_contains: str = None):
        """Assert that response is an error with expected status and message"""
        assert response.status_code == expected_status
        
        error_data = response.json()
        assert "detail" in error_data
        
        if expected_message_contains:
            assert expected_message_contains.lower() in error_data["detail"].lower()
    
    def assert_success_response(self, response, expected_fields: List[str] = None):
        """Assert that response is successful and contains expected fields"""
        assert response.status_code == 200
        
        data = response.json()
        if expected_fields:
            for field in expected_fields:
                assert field in data
    
    def create_auth_headers(self, email: str, password: str) -> Dict[str, str]:
        """Create authentication headers for given user credentials"""
        login_data = {"email": email, "password": password}
        response = self.client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        token_data = response.json()
        
        return {"Authorization": f"Bearer {token_data['access_token']}"}
    
    def test_unauthorized_access(self, endpoint: str, method: str = "GET", data: dict = None):
        """Test that endpoint requires authentication"""
        if method.upper() == "GET":
            response = self.client.get(endpoint)
        elif method.upper() == "POST":
            response = self.client.post(endpoint, json=data or {})
        elif method.upper() == "PUT":
            response = self.client.put(endpoint, json=data or {})
        elif method.upper() == "DELETE":
            response = self.client.delete(endpoint)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        assert response.status_code == 401
    
    def test_pagination(self, endpoint: str, headers: dict, params: dict = None):
        """Test pagination functionality for an endpoint"""
        base_params = params or {}
        
        # Test default pagination
        response = self.client.get(endpoint, headers=headers, params=base_params)
        assert response.status_code == 200
        self.assert_pagination_response(response.json())
        
        # Test custom page size
        test_params = {**base_params, "per_page": 5}
        response = self.client.get(endpoint, headers=headers, params=test_params)
        assert response.status_code == 200
        data = response.json()
        assert data["size"] <= 5
        
        # Test specific page
        test_params = {**base_params, "page": 1, "per_page": 10}
        response = self.client.get(endpoint, headers=headers, params=test_params)
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1


class DataFactory:
    """Factory for creating test data"""
    
    @staticmethod
    def create_user_data(email: str = None, **overrides) -> Dict[str, Any]:
        """Create user registration data"""
        base_data = {
            "email": email or "test@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User",
            "phone": "1234567890",
            "company_name": "Test Company",
            "company_type": "buyer",
            "business_license": "TEST123",
            "tax_number": "TAX123"
        }
        base_data.update(overrides)
        return base_data
    
    @staticmethod
    def create_product_data(category_id: str, **overrides) -> Dict[str, Any]:
        """Create product data"""
        base_data = {
            "name": {"zh-CN": "测试产品", "en-US": "Test Product"},
            "sku": "TEST-PROD-001",
            "description": {"zh-CN": "测试产品描述", "en-US": "Test product description"},
            "category_id": category_id,
            "price": 99.99,
            "stock": 100,
            "min_order_quantity": 1,
            "specifications": {"color": "blue", "size": "large"},
            "is_active": True
        }
        base_data.update(overrides)
        return base_data
    
    @staticmethod
    def create_order_data(product_id: str, quantity: int = 1, **overrides) -> Dict[str, Any]:
        """Create order data"""
        base_data = {
            "items": [
                {
                    "product_id": product_id,
                    "quantity": quantity
                }
            ],
            "delivery_address": {
                "recipient_name": "Test Recipient",
                "phone": "1234567890",
                "address": "123 Test Street",
                "city": "Test City",
                "province": "Test Province",
                "postal_code": "12345",
                "country": "China"
            },
            "notes": "Test order notes"
        }
        base_data.update(overrides)
        return base_data
    
    @staticmethod
    def create_category_data(slug: str = None, **overrides) -> Dict[str, Any]:
        """Create category data"""
        base_data = {
            "name": {"zh-CN": "测试分类", "en-US": "Test Category"},
            "slug": slug or "test-category",
            "description": {"zh-CN": "测试分类描述", "en-US": "Test category description"},
            "is_active": True,
            "sort_order": 1
        }
        base_data.update(overrides)
        return base_data
    
    @staticmethod
    def create_company_data(company_type: str = "buyer", **overrides) -> Dict[str, Any]:
        """Create company data"""
        base_data = {
            "company_name": {"zh-CN": "测试公司", "en-US": "Test Company"},
            "company_type": company_type,
            "business_license": "TEST123",
            "tax_number": "TAX123",
            "description": {"zh-CN": "测试公司描述", "en-US": "Test company description"},
            "website": "https://example.com"
        }
        base_data.update(overrides)
        return base_data


class DatabaseTestHelper:
    """Helper for database operations in tests"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def create_test_user(self, email: str, company_id: str = None, **overrides) -> 'User':
        """Create a test user in the database"""
        from app.models.user import User
        from app.core.security import get_password_hash
        from app.utils.id_generator import generate_id
        from datetime import datetime
        
        user_data = {
            "id": generate_id(),
            "email": email,
            "hashed_password": get_password_hash("TestPassword123!"),
            "full_name": "Test User",
            "phone": "1234567890",
            "is_active": True,
            "default_company_id": company_id,
            "password_changed_at": datetime.utcnow()
        }
        user_data.update(overrides)
        
        user = User(**user_data)
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        return user
    
    def create_test_company(self, company_type: str = "buyer", **overrides) -> 'Company':
        """Create a test company in the database"""
        from app.models.user import Company
        from app.utils.id_generator import generate_id, generate_company_code
        
        company_data = {
            "id": generate_id(),
            "company_code": generate_company_code(),
            "company_name": {"zh-CN": "测试公司", "en-US": "Test Company"},
            "company_type": company_type,
            "business_license": "TEST123",
            "tax_number": "TAX123",
            "is_verified": True
        }
        company_data.update(overrides)
        
        company = Company(**company_data)
        self.db_session.add(company)
        self.db_session.commit()
        self.db_session.refresh(company)
        return company
    
    def create_test_product(self, category_id: str, supplier_id: str, **overrides) -> 'Product':
        """Create a test product in the database"""
        from app.models.product import Product
        from app.utils.id_generator import generate_id
        
        product_data = {
            "id": generate_id(),
            "name": {"zh-CN": "测试产品", "en-US": "Test Product"},
            "sku": f"TEST-PROD-{generate_id()[:8]}",
            "description": {"zh-CN": "测试产品描述", "en-US": "Test product description"},
            "category_id": category_id,
            "supplier_id": supplier_id,
            "price": Decimal("99.99"),
            "stock": 100,
            "min_order_quantity": 1,
            "specifications": {"color": "blue", "size": "large"},
            "is_active": True
        }
        product_data.update(overrides)
        
        product = Product(**product_data)
        self.db_session.add(product)
        self.db_session.commit()
        self.db_session.refresh(product)
        return product
    
    def create_test_category(self, **overrides) -> 'Category':
        """Create a test category in the database"""
        from app.models.product import Category
        from app.utils.id_generator import generate_id
        
        category_data = {
            "id": generate_id(),
            "name": {"zh-CN": "测试分类", "en-US": "Test Category"},
            "slug": f"test-category-{generate_id()[:8]}",
            "description": {"zh-CN": "测试分类描述", "en-US": "Test category description"},
            "is_active": True,
            "sort_order": 1
        }
        category_data.update(overrides)
        
        category = Category(**category_data)
        self.db_session.add(category)
        self.db_session.commit()
        self.db_session.refresh(category)
        return category


def assert_datetime_format(datetime_str: str):
    """Assert that a string is in valid ISO datetime format"""
    from datetime import datetime
    try:
        datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
    except ValueError:
        pytest.fail(f"Invalid datetime format: {datetime_str}")


def assert_uuid_format(uuid_str: str):
    """Assert that a string is in valid UUID format"""
    import uuid
    try:
        uuid.UUID(uuid_str)
    except ValueError:
        pytest.fail(f"Invalid UUID format: {uuid_str}")


def assert_decimal_equal(actual: Any, expected: float, precision: int = 2):
    """Assert that decimal/float values are equal within precision"""
    if isinstance(actual, str):
        actual = float(actual)
    elif isinstance(actual, Decimal):
        actual = float(actual)
    
    assert abs(actual - expected) < (10 ** -precision), f"Expected {expected}, got {actual}"


def assert_multilingual_field(field_data: dict, required_languages: List[str] = None):
    """Assert that a field contains proper multilingual data"""
    required_languages = required_languages or ["zh-CN", "en-US"]
    
    assert isinstance(field_data, dict)
    for lang in required_languages:
        assert lang in field_data
        assert isinstance(field_data[lang], str)
        assert len(field_data[lang].strip()) > 0


def load_test_data(filename: str) -> dict:
    """Load test data from JSON file"""
    import os
    test_data_dir = os.path.join(os.path.dirname(__file__), "data")
    filepath = os.path.join(test_data_dir, filename)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


class MockExternalService:
    """Mock external services for testing"""
    
    @staticmethod
    def mock_payment_gateway():
        """Mock payment gateway responses"""
        return {
            "create_payment": {
                "payment_id": "mock_payment_123",
                "payment_url": "https://mock-payment.com/pay/123",
                "qr_code": "data:image/png;base64,mock_qr_code_data",
                "expires_at": "2024-12-31T23:59:59Z"
            },
            "payment_callback": {
                "status": "success",
                "transaction_id": "mock_transaction_456",
                "paid_amount": 99.99,
                "paid_at": "2024-01-01T12:00:00Z"
            }
        }
    
    @staticmethod
    def mock_email_service():
        """Mock email service responses"""
        return {
            "send_verification": {"message_id": "mock_email_123", "status": "sent"},
            "send_password_reset": {"message_id": "mock_email_124", "status": "sent"},
            "send_invitation": {"message_id": "mock_email_125", "status": "sent"}
        }
    
    @staticmethod
    def mock_sms_service():
        """Mock SMS service responses"""
        return {
            "send_verification": {"message_id": "mock_sms_123", "status": "sent"},
            "send_notification": {"message_id": "mock_sms_124", "status": "sent"}
        }


# Pytest fixtures for utilities
@pytest.fixture
def api_helper(client: TestClient) -> APITestHelper:
    """Provide API test helper"""
    return APITestHelper(client)


@pytest.fixture
def db_helper(db_session: Session) -> DatabaseTestHelper:
    """Provide database test helper"""
    return DatabaseTestHelper(db_session)


@pytest.fixture
def data_factory() -> DataFactory:
    """Provide data factory"""
    return DataFactory()


@pytest.fixture
def mock_services() -> MockExternalService:
    """Provide mock external services"""
    return MockExternalService()


# Common test patterns
def test_crud_endpoints(
    client: TestClient,
    auth_headers: dict,
    base_url: str,
    create_data: dict,
    update_data: dict,
    api_helper: APITestHelper
):
    """Test standard CRUD endpoints pattern"""
    
    # Test CREATE
    response = client.post(base_url, json=create_data, headers=auth_headers)
    api_helper.assert_success_response(response, ["id"])
    created_item = response.json()
    item_id = created_item["id"]
    
    # Test READ (list)
    response = client.get(base_url, headers=auth_headers)
    api_helper.assert_success_response(response)
    api_helper.assert_pagination_response(response.json(), expected_min_total=1)
    
    # Test READ (single)
    response = client.get(f"{base_url}/{item_id}", headers=auth_headers)
    api_helper.assert_success_response(response, ["id"])
    
    # Test UPDATE
    response = client.put(f"{base_url}/{item_id}", json=update_data, headers=auth_headers)
    api_helper.assert_success_response(response, ["id"])
    
    # Test DELETE (if applicable)
    response = client.delete(f"{base_url}/{item_id}", headers=auth_headers)
    assert response.status_code in [200, 204]
    
    return created_item


def test_unauthorized_endpoints(
    client: TestClient,
    endpoints: List[dict],
    api_helper: APITestHelper
):
    """Test that endpoints require authentication"""
    for endpoint_config in endpoints:
        endpoint = endpoint_config["url"]
        method = endpoint_config.get("method", "GET")
        data = endpoint_config.get("data")
        
        api_helper.test_unauthorized_access(endpoint, method, data) 