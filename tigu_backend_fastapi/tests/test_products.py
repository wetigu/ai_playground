# Test cases for product-related functionality

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "tigu_backend_fastapi"))

from app.models.product import Product, Category
from app.models.user import User, Company


class TestProductCategories:
    """Test product category endpoints"""
    
    def test_get_categories(self, client: TestClient):
        """Test getting product categories"""
        response = client.get("/api/v1/products/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data

    def test_get_category_by_slug(self, client: TestClient, test_category: Category):
        """Test getting category by slug"""
        response = client.get(f"/api/v1/products/categories/{test_category.slug}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_category.id
        assert data["slug"] == test_category.slug

    def test_get_category_not_found(self, client: TestClient):
        """Test getting non-existent category"""
        response = client.get("/api/v1/products/categories/non-existent-slug")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_category_as_admin(self, client: TestClient, auth_headers: dict, test_user: User, db_session: Session):
        """Test creating category as admin"""
        # Make user superuser
        test_user.is_superuser = True
        db_session.commit()
        
        category_data = {
            "name": {"zh-CN": "新分类", "en-US": "New Category"},
            "slug": "new-category",
            "description": {"zh-CN": "新分类描述", "en-US": "New category description"},
            "is_active": True,
            "sort_order": 10
        }
        
        response = client.post("/api/v1/products/categories", json=category_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == category_data["slug"]

    def test_create_category_duplicate_slug(self, client: TestClient, auth_headers: dict, test_user: User, test_category: Category, db_session: Session):
        """Test creating category with duplicate slug"""
        # Make user superuser
        test_user.is_superuser = True
        db_session.commit()
        
        category_data = {
            "name": {"zh-CN": "重复分类", "en-US": "Duplicate Category"},
            "slug": test_category.slug,  # Same slug as existing category
            "description": {"zh-CN": "重复分类描述", "en-US": "Duplicate category description"},
            "is_active": True,
            "sort_order": 10
        }
        
        response = client.post("/api/v1/products/categories", json=category_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_create_category_forbidden(self, client: TestClient, auth_headers: dict):
        """Test creating category without admin privileges"""
        category_data = {
            "name": {"zh-CN": "新分类", "en-US": "New Category"},
            "slug": "new-category",
            "description": {"zh-CN": "新分类描述", "en-US": "New category description"},
            "is_active": True,
            "sort_order": 10
        }
        
        response = client.post("/api/v1/products/categories", json=category_data, headers=auth_headers)
        
        assert response.status_code == 403
        assert "permissions" in response.json()["detail"].lower()


class TestProductCRUD:
    """Test product CRUD operations"""
    
    def test_get_products(self, client: TestClient, test_product: Product):
        """Test getting products with pagination"""
        response = client.get("/api/v1/products/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check pagination structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        
        # Check that our test product is included
        assert data["total"] >= 1
        assert len(data["items"]) >= 1

    def test_get_products_with_pagination(self, client: TestClient, test_product: Product):
        """Test products pagination"""
        response = client.get("/api/v1/products/?page=1&per_page=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 1
        assert data["size"] <= 5

    def test_get_product_by_id(self, client: TestClient, test_product: Product):
        """Test getting product by ID"""
        response = client.get(f"/api/v1/products/{test_product.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == test_product.id
        assert data["sku"] == test_product.sku
        assert data["name"] == test_product.name
        assert data["price"] == test_product.price

    def test_get_product_not_found(self, client: TestClient):
        """Test getting non-existent product"""
        response = client.get("/api/v1/products/999999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_product(self, client: TestClient, supplier_auth_headers: dict, test_category: Category, test_supplier_company: Company):
        """Test creating a new product"""
        product_data = {
            "name": {"zh-CN": "新产品", "en-US": "New Product"},
            "sku": "NEW-PROD-001",
            "description": {"zh-CN": "新产品描述", "en-US": "New product description"},
            "category_id": test_category.id,
            "price": 199.99,
            "stock": 50,
            "min_order_quantity": 1,
            "specifications": {"color": "red", "size": "medium"},
            "is_active": True,
            "images": [
                {
                    "image_url": "https://example.com/image1.jpg",
                    "alt_text": "Product image 1",
                    "is_primary": True,
                    "sort_order": 1
                }
            ]
        }
        
        response = client.post("/api/v1/products/", json=product_data, headers=supplier_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["sku"] == product_data["sku"]
        assert data["name"] == product_data["name"]
        assert data["price"] == product_data["price"]
        assert data["category_id"] == test_category.id
        assert len(data["images"]) == 1

    def test_create_product_unauthorized(self, client: TestClient, test_category: Category):
        """Test creating product without authentication"""
        product_data = {
            "name": {"zh-CN": "新产品", "en-US": "New Product"},
            "sku": "NEW-PROD-001",
            "description": {"zh-CN": "新产品描述", "en-US": "New product description"},
            "category_id": test_category.id,
            "price": 199.99,
            "stock": 50
        }
        
        response = client.post("/api/v1/products/", json=product_data)
        
        assert response.status_code == 401

    def test_update_product(self, client: TestClient, supplier_auth_headers: dict, test_product: Product):
        """Test updating a product"""
        update_data = {
            "name": {"zh-CN": "更新产品", "en-US": "Updated Product"},
            "price": 299.99,
            "stock": 200
        }
        
        response = client.put(f"/api/v1/products/{test_product.id}", json=update_data, headers=supplier_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == update_data["name"]
        assert data["price"] == update_data["price"]
        assert data["stock"] == update_data["stock"]

    def test_delete_product(self, client: TestClient, supplier_auth_headers: dict, test_product: Product):
        """Test deleting a product (soft delete)"""
        response = client.delete(f"/api/v1/products/{test_product.id}", headers=supplier_auth_headers)
        
        assert response.status_code == 200
        
        # Verify product is no longer active
        get_response = client.get(f"/api/v1/products/{test_product.id}")
        assert get_response.status_code == 404


class TestProductFiltering:
    """Test product filtering and search"""
    
    def test_filter_by_category_slug(self, client: TestClient, test_product: Product, test_category: Category):
        """Test filtering products by category slug"""
        response = client.get(f"/api/v1/products/?category_slug={test_category.slug}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find our test product
        assert data["total"] >= 1
        product_found = any(item["id"] == test_product.id for item in data["items"])
        assert product_found

    def test_filter_by_category_id(self, client: TestClient, test_product: Product, test_category: Category):
        """Test filtering products by category ID"""
        response = client.get(f"/api/v1/products/?category_id={test_category.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find our test product
        assert data["total"] >= 1
        product_found = any(item["id"] == test_product.id for item in data["items"])
        assert product_found

    def test_filter_by_supplier(self, client: TestClient, test_product: Product, test_supplier_company: Company):
        """Test filtering products by supplier"""
        response = client.get(f"/api/v1/products/?supplier_id={test_supplier_company.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find our test product
        assert data["total"] >= 1
        product_found = any(item["id"] == test_product.id for item in data["items"])
        assert product_found

    def test_filter_by_price_range(self, client: TestClient, test_product: Product):
        """Test filtering products by price range"""
        # Test product has price 99.99
        response = client.get("/api/v1/products/?min_price=50&max_price=150")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find our test product
        product_found = any(item["id"] == test_product.id for item in data["items"])
        assert product_found
        
        # Test excluding our product
        response = client.get("/api/v1/products/?min_price=200&max_price=300")
        data = response.json()
        
        # Should not find our test product
        product_found = any(item["id"] == test_product.id for item in data["items"])
        assert not product_found

    def test_filter_by_stock_availability(self, client: TestClient, test_product: Product):
        """Test filtering products by stock availability"""
        response = client.get("/api/v1/products/?in_stock=true")
        
        assert response.status_code == 200
        data = response.json()
        
        # All products should have stock > 0
        for item in data["items"]:
            assert item["stock"] > 0

    def test_search_products(self, client: TestClient, test_product: Product):
        """Test searching products by keyword"""
        # Search by part of product name
        response = client.get("/api/v1/products/?search=Test")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find our test product
        product_found = any(item["id"] == test_product.id for item in data["items"])
        assert product_found

    def test_search_products_by_sku(self, client: TestClient, test_product: Product):
        """Test searching products by SKU"""
        response = client.get(f"/api/v1/products/?search={test_product.sku}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find our test product
        product_found = any(item["id"] == test_product.id for item in data["items"])
        assert product_found

    def test_search_no_results(self, client: TestClient):
        """Test search with no matching results"""
        response = client.get("/api/v1/products/?search=NonExistentProduct12345")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] == 0
        assert len(data["items"]) == 0

    def test_combined_filters(self, client: TestClient, test_product: Product, test_category: Category):
        """Test combining multiple filters"""
        response = client.get(
            f"/api/v1/products/?category_id={test_category.id}&min_price=50&max_price=150&in_stock=true"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find our test product as it matches all criteria
        product_found = any(item["id"] == test_product.id for item in data["items"])
        assert product_found


class TestProductValidation:
    """Test product validation and error handling"""
    
    def test_create_product_invalid_category(self, client: TestClient, supplier_auth_headers: dict):
        """Test creating product with invalid category"""
        product_data = {
            "name": {"zh-CN": "新产品", "en-US": "New Product"},
            "sku": "NEW-PROD-001",
            "description": {"zh-CN": "新产品描述", "en-US": "New product description"},
            "category_id": 999999,  # Non-existent category
            "price": 199.99,
            "stock": 50
        }
        
        response = client.post("/api/v1/products/", json=product_data, headers=supplier_auth_headers)
        
        assert response.status_code == 400
        assert "category" in response.json()["detail"].lower()

    def test_create_product_duplicate_sku(self, client: TestClient, supplier_auth_headers: dict, test_product: Product, test_category: Category):
        """Test creating product with duplicate SKU"""
        product_data = {
            "name": {"zh-CN": "重复SKU产品", "en-US": "Duplicate SKU Product"},
            "sku": test_product.sku,  # Same SKU as existing product
            "description": {"zh-CN": "重复SKU产品描述", "en-US": "Duplicate SKU product description"},
            "category_id": test_category.id,
            "price": 199.99,
            "stock": 50
        }
        
        response = client.post("/api/v1/products/", json=product_data, headers=supplier_auth_headers)
        
        assert response.status_code == 400
        assert "sku" in response.json()["detail"].lower()

    def test_create_product_invalid_price(self, client: TestClient, supplier_auth_headers: dict, test_category: Category):
        """Test creating product with invalid price"""
        product_data = {
            "name": {"zh-CN": "新产品", "en-US": "New Product"},
            "sku": "NEW-PROD-001",
            "description": {"zh-CN": "新产品描述", "en-US": "New product description"},
            "category_id": test_category.id,
            "price": -10.99,  # Negative price
            "stock": 50
        }
        
        response = client.post("/api/v1/products/", json=product_data, headers=supplier_auth_headers)
        
        assert response.status_code == 422

    def test_create_product_missing_required_fields(self, client: TestClient, supplier_auth_headers: dict):
        """Test creating product with missing required fields"""
        incomplete_data = {
            "name": {"zh-CN": "新产品", "en-US": "New Product"},
            # Missing required fields like sku, price, etc.
        }
        
        response = client.post("/api/v1/products/", json=incomplete_data, headers=supplier_auth_headers)
        
        assert response.status_code == 422
