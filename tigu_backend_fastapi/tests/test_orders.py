import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "tigu_backend_fastapi"))

from app.models.order import Order, OrderItem
from app.models.product import Product, Category
from app.models.user import User, Company


@pytest.fixture
def test_order(db_session: Session, test_user: User, test_company: Company, test_product: Product) -> Order:
    """Create a test order"""
    from app.utils.id_generator import generate_id, generate_order_number
    
    order = Order(
        id=generate_id(),
        order_number=generate_order_number(),
        buyer_id=test_company.id,
        supplier_id=test_product.supplier_id,
        status="pending",
        total_amount=Decimal("199.98"),  # 2 * 99.99
        currency="CNY",
        created_by=test_user.id
    )
    db_session.add(order)
    db_session.flush()
    
    # Add order items
    order_item = OrderItem(
        id=generate_id(),
        order_id=order.id,
        product_id=test_product.id,
        quantity=2,
        unit_price=Decimal("99.99"),
        subtotal=Decimal("199.98")
    )
    db_session.add(order_item)
    db_session.commit()
    db_session.refresh(order)
    return order


class TestOrderCreation:
    """Test order creation endpoints"""
    
    def test_create_order_success(self, client: TestClient, auth_headers: dict, test_product: Product):
        """Test successful order creation"""
        order_data = {
            "items": [
                {
                    "product_id": test_product.id,
                    "quantity": 2
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
        
        response = client.post("/api/v1/orders/", json=order_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check order structure
        assert "id" in data
        assert "order_number" in data
        assert data["status"] == "pending"
        assert len(data["items"]) == 1
        assert data["items"][0]["product_id"] == test_product.id
        assert data["items"][0]["quantity"] == 2
        assert data["total_amount"] > 0

    def test_create_order_multiple_products(self, client: TestClient, auth_headers: dict, test_product: Product, test_category: Category, test_supplier_company: Company, db_session: Session):
        """Test creating order with multiple products"""
        from app.utils.id_generator import generate_id
        
        # Create another product
        product2 = Product(
            id=generate_id(),
            name={"zh-CN": "测试产品2", "en-US": "Test Product 2"},
            sku="TEST-PROD-002",
            description={"zh-CN": "测试产品描述2", "en-US": "Test product description 2"},
            category_id=test_category.id,
            supplier_id=test_supplier_company.id,
            price=149.99,
            stock=50,
            min_order_quantity=1,
            is_active=True
        )
        db_session.add(product2)
        db_session.commit()
        
        order_data = {
            "items": [
                {
                    "product_id": test_product.id,
                    "quantity": 1
                },
                {
                    "product_id": product2.id,
                    "quantity": 3
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
            }
        }
        
        response = client.post("/api/v1/orders/", json=order_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["items"]) == 2
        # Total should be 1 * 99.99 + 3 * 149.99 = 549.96
        assert float(data["total_amount"]) == pytest.approx(549.96, rel=1e-2)

    def test_create_order_insufficient_stock(self, client: TestClient, auth_headers: dict, test_product: Product):
        """Test creating order with insufficient stock"""
        order_data = {
            "items": [
                {
                    "product_id": test_product.id,
                    "quantity": 999  # More than available stock (100)
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
            }
        }
        
        response = client.post("/api/v1/orders/", json=order_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "insufficient stock" in response.json()["detail"].lower()

    def test_create_order_non_existent_product(self, client: TestClient, auth_headers: dict):
        """Test creating order with non-existent product"""
        order_data = {
            "items": [
                {
                    "product_id": 999999,  # Non-existent product
                    "quantity": 1
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
            }
        }
        
        response = client.post("/api/v1/orders/", json=order_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "product not found" in response.json()["detail"].lower()

    def test_create_order_unauthorized(self, client: TestClient, test_product: Product):
        """Test creating order without authentication"""
        order_data = {
            "items": [
                {
                    "product_id": test_product.id,
                    "quantity": 1
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
            }
        }
        
        response = client.post("/api/v1/orders/", json=order_data)
        
        assert response.status_code == 401

    def test_create_order_invalid_quantity(self, client: TestClient, auth_headers: dict, test_product: Product):
        """Test creating order with invalid quantity"""
        order_data = {
            "items": [
                {
                    "product_id": test_product.id,
                    "quantity": 0  # Invalid quantity
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
            }
        }
        
        response = client.post("/api/v1/orders/", json=order_data, headers=auth_headers)
        
        assert response.status_code == 422


class TestOrderRetrieval:
    """Test order retrieval endpoints"""
    
    def test_get_orders(self, client: TestClient, auth_headers: dict, test_order: Order):
        """Test getting user's orders"""
        response = client.get("/api/v1/orders/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check pagination structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        
        # Should find our test order
        assert data["total"] >= 1
        order_found = any(item["id"] == test_order.id for item in data["items"])
        assert order_found

    def test_get_orders_with_pagination(self, client: TestClient, auth_headers: dict, test_order: Order):
        """Test orders pagination"""
        response = client.get("/api/v1/orders/?page=1&per_page=5", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 1
        assert data["size"] <= 5

    def test_get_order_by_id(self, client: TestClient, auth_headers: dict, test_order: Order):
        """Test getting order by ID"""
        response = client.get(f"/api/v1/orders/{test_order.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == test_order.id
        assert data["order_number"] == test_order.order_number
        assert "items" in data
        assert len(data["items"]) >= 1

    def test_get_order_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting non-existent order"""
        response = client.get("/api/v1/orders/999999", headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_order_unauthorized(self, client: TestClient, test_order: Order):
        """Test getting order without authentication"""
        response = client.get(f"/api/v1/orders/{test_order.id}")
        
        assert response.status_code == 401

    def test_get_order_wrong_user(self, client: TestClient, supplier_auth_headers: dict, test_order: Order):
        """Test getting order that doesn't belong to user"""
        response = client.get(f"/api/v1/orders/{test_order.id}", headers=supplier_auth_headers)
        
        assert response.status_code == 403
        assert "access" in response.json()["detail"].lower()


class TestOrderStatusManagement:
    """Test order status management"""
    
    def test_update_order_status_supplier(self, client: TestClient, supplier_auth_headers: dict, test_order: Order):
        """Test supplier updating order status"""
        status_data = {
            "status": "confirmed",
            "status_note": "Order confirmed by supplier"
        }
        
        response = client.put(f"/api/v1/orders/{test_order.id}/status", json=status_data, headers=supplier_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "confirmed"
        assert "status_updated_at" in data

    def test_update_order_status_invalid_transition(self, client: TestClient, supplier_auth_headers: dict, test_order: Order, db_session: Session):
        """Test invalid status transition"""
        # First, set order to completed
        test_order.status = "completed"
        db_session.commit()
        
        # Try to change back to pending (invalid transition)
        status_data = {
            "status": "pending",
            "status_note": "Trying to revert status"
        }
        
        response = client.put(f"/api/v1/orders/{test_order.id}/status", json=status_data, headers=supplier_auth_headers)
        
        assert response.status_code == 400
        assert "invalid status transition" in response.json()["detail"].lower()

    def test_cancel_order_buyer(self, client: TestClient, auth_headers: dict, test_order: Order):
        """Test buyer canceling order"""
        cancel_data = {
            "reason": "Changed mind"
        }
        
        response = client.post(f"/api/v1/orders/{test_order.id}/cancel", json=cancel_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "cancelled"

    def test_cancel_order_invalid_status(self, client: TestClient, auth_headers: dict, test_order: Order, db_session: Session):
        """Test canceling order with invalid status"""
        # Set order to shipped (cannot be cancelled)
        test_order.status = "shipped"
        db_session.commit()
        
        cancel_data = {
            "reason": "Changed mind"
        }
        
        response = client.post(f"/api/v1/orders/{test_order.id}/cancel", json=cancel_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "cannot be cancelled" in response.json()["detail"].lower()


class TestOrderFiltering:
    """Test order filtering and search"""
    
    def test_filter_orders_by_status(self, client: TestClient, auth_headers: dict, test_order: Order):
        """Test filtering orders by status"""
        response = client.get(f"/api/v1/orders/?status={test_order.status}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find our test order
        order_found = any(item["id"] == test_order.id for item in data["items"])
        assert order_found
        
        # All orders should have the filtered status
        for item in data["items"]:
            assert item["status"] == test_order.status

    def test_filter_orders_by_date_range(self, client: TestClient, auth_headers: dict, test_order: Order):
        """Test filtering orders by date range"""
        from datetime import datetime, timedelta
        
        # Filter for orders from yesterday to tomorrow
        start_date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        response = client.get(f"/api/v1/orders/?start_date={start_date}&end_date={end_date}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find our test order (created today)
        order_found = any(item["id"] == test_order.id for item in data["items"])
        assert order_found

    def test_search_orders_by_order_number(self, client: TestClient, auth_headers: dict, test_order: Order):
        """Test searching orders by order number"""
        response = client.get(f"/api/v1/orders/?search={test_order.order_number}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find our test order
        order_found = any(item["id"] == test_order.id for item in data["items"])
        assert order_found

    def test_get_orders_by_supplier(self, client: TestClient, supplier_auth_headers: dict, test_order: Order):
        """Test supplier getting their orders"""
        response = client.get("/api/v1/orders/supplier", headers=supplier_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find orders for this supplier
        assert "items" in data
        assert "total" in data


class TestOrderPayment:
    """Test order payment endpoints"""
    
    def test_create_payment(self, client: TestClient, auth_headers: dict, test_order: Order):
        """Test creating payment for order"""
        payment_data = {
            "payment_method": "alipay",
            "amount": float(test_order.total_amount),
            "currency": "CNY"
        }
        
        response = client.post(f"/api/v1/orders/{test_order.id}/payment", json=payment_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "payment_id" in data
        assert "payment_url" in data or "qr_code" in data

    def test_payment_callback(self, client: TestClient, test_order: Order):
        """Test payment callback webhook"""
        callback_data = {
            "order_id": test_order.id,
            "payment_id": "test_payment_id",
            "status": "success",
            "amount": float(test_order.total_amount),
            "transaction_id": "test_transaction_id"
        }
        
        response = client.post("/api/v1/orders/payment/callback", json=callback_data)
        
        assert response.status_code == 200

    def test_get_payment_status(self, client: TestClient, auth_headers: dict, test_order: Order):
        """Test getting payment status"""
        response = client.get(f"/api/v1/orders/{test_order.id}/payment/status", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "payment_status" in data
        assert "order_id" in data
        assert data["order_id"] == test_order.id


class TestOrderValidation:
    """Test order validation and error handling"""
    
    def test_create_order_missing_delivery_address(self, client: TestClient, auth_headers: dict, test_product: Product):
        """Test creating order without delivery address"""
        order_data = {
            "items": [
                {
                    "product_id": test_product.id,
                    "quantity": 1
                }
            ]
            # Missing delivery_address
        }
        
        response = client.post("/api/v1/orders/", json=order_data, headers=auth_headers)
        
        assert response.status_code == 422

    def test_create_order_empty_items(self, client: TestClient, auth_headers: dict):
        """Test creating order with no items"""
        order_data = {
            "items": [],  # Empty items list
            "delivery_address": {
                "recipient_name": "Test Recipient",
                "phone": "1234567890",
                "address": "123 Test Street",
                "city": "Test City",
                "province": "Test Province",
                "postal_code": "12345",
                "country": "China"
            }
        }
        
        response = client.post("/api/v1/orders/", json=order_data, headers=auth_headers)
        
        assert response.status_code == 422

    def test_update_order_status_unauthorized(self, client: TestClient, auth_headers: dict, test_order: Order):
        """Test buyer trying to update order status (should be supplier only)"""
        status_data = {
            "status": "confirmed",
            "status_note": "Buyer trying to confirm order"
        }
        
        response = client.put(f"/api/v1/orders/{test_order.id}/status", json=status_data, headers=auth_headers)
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower() 