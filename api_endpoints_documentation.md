# Tigu B2B API Endpoints Documentation

## Overview
This document provides comprehensive documentation for all API endpoints implemented in the Tigu B2B Building Materials Marketplace platform.

**Base URL**: `http://localhost:8000`  
**API Version**: `v1`  
**API Prefix**: `/api/v1`

## Authentication
Most endpoints require authentication using JWT Bearer tokens. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 🔐 Authentication Endpoints

### POST `/api/v1/auth/register`
Register a new user and company.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "phone": "+1-416-555-0123",
  "company_name": "ABC Construction Ltd",
  "company_type": "buyer",
  "business_license": "ON-123456789",
  "tax_number": "BN123456789RT0001"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "default_company_id": 1
  }
}
```

### POST `/api/v1/auth/login`
User login with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** Same as register response.

### POST `/api/v1/auth/refresh-token`
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### POST `/api/v1/auth/logout`
Logout current user (requires authentication).

### POST `/api/v1/auth/logout-all`
Logout from all sessions (requires authentication).

### GET `/api/v1/auth/profile`
Get current user profile (requires authentication).

### PUT `/api/v1/auth/profile`
Update current user profile (requires authentication).

### POST `/api/v1/auth/change-password`
Change user password (requires authentication).

**Request Body:**
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword123"
}
```

### POST `/api/v1/auth/forgot-password`
Request password reset.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

### POST `/api/v1/auth/reset-password`
Reset password using token.

**Request Body:**
```json
{
  "token": "reset_token_here",
  "new_password": "newpassword123"
}
```

---

## 📦 Product Endpoints

### GET `/api/v1/products/categories`
Get all categories.

**Query Parameters:**
- `parent_id` (optional): Filter by parent category ID
- `is_active` (default: true): Filter by active status

**Response:**
```json
[
  {
    "id": 1,
    "name": {"zh-CN": "钢材", "en-US": "Steel"},
    "slug": "steel",
    "description": {"zh-CN": "各种钢材产品", "en-US": "Various steel products"},
    "parent_id": null,
    "sort_order": 0,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### GET `/api/v1/products/categories/{slug}`
Get category by slug.

**Response:** Single category object.

### POST `/api/v1/products/categories`
Create a new category (admin only, requires authentication).

**Request Body:**
```json
{
  "name": {"zh-CN": "新分类", "en-US": "New Category"},
  "slug": "new-category",
  "description": {"zh-CN": "描述", "en-US": "Description"},
  "parent_id": null,
  "sort_order": 0,
  "is_active": true
}
```

### GET `/api/v1/products/`
Get products with pagination and filters.

**Query Parameters:**
- `page` (default: 1): Page number
- `per_page` (default: 20, max: 100): Items per page
- `category_slug`: Filter by category slug
- `category_id`: Filter by category ID
- `supplier_id`: Filter by supplier ID
- `search`: Search in product name and description
- `min_price`: Minimum price filter
- `max_price`: Maximum price filter
- `in_stock`: Filter by stock availability
- `is_active` (default: true): Filter by active status

**Response:**
```json
{
  "items": [
    {
      "id": 100001,
      "sku": "REBAR-GRADE400-12",
      "name": {"zh-CN": "Grade 400 螺纹钢筋 #4", "en-US": "Grade 400 Rebar #4"},
      "short_description": {"zh-CN": "#4 Grade 400螺纹钢", "en-US": "#4 Grade 400 Rebar"},
      "price": 4200.00,
      "stock": 5000,
      "unit": {"zh-CN": "吨", "en-US": "Tonne"},
      "category": {
        "id": 4,
        "name": {"zh-CN": "钢筋", "en-US": "Rebar"},
        "slug": "rebar"
      },
      "primary_image": {
        "id": 1,
        "image_url": "https://cdn.tigu.com/products/rebar-grade400-12-main.jpg",
        "alt_text": "Grade 400 Rebar #4 Main Image",
        "is_primary": true,
        "sort_order": 1
      },
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 20,
  "pages": 8
}
```

### GET `/api/v1/products/{product_id}`
Get product by ID.

**Response:**
```json
{
  "id": 100001,
  "sku": "REBAR-GRADE400-12",
  "name": {"zh-CN": "Grade 400 螺纹钢筋 #4", "en-US": "Grade 400 Rebar #4"},
  "description": {"zh-CN": "Grade 400等级螺纹钢筋，#4规格，广泛用于建筑结构", "en-US": "Grade 400 rebar, #4 size, widely used in building structures"},
  "short_description": {"zh-CN": "#4 Grade 400螺纹钢", "en-US": "#4 Grade 400 Rebar"},
  "specifications": {
    "material": "Grade 400",
    "size": "#4 (12.7mm)",
    "length": "6m",
    "standard": "CSA G30.18"
  },
  "price": 4200.00,
  "cost_price": 3800.00,
  "stock": 5000,
  "min_stock": 500,
  "unit": {"zh-CN": "吨", "en-US": "Tonne"},
  "weight": 888.00,
  "dimensions": "6000mm×12.7mm×12.7mm",
  "category_id": 4,
  "supplier_id": 1001,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "category": {
    "id": 4,
    "name": {"zh-CN": "钢筋", "en-US": "Rebar"},
    "slug": "rebar"
  },
  "images": [
    {
      "id": 1,
      "image_url": "https://cdn.tigu.com/products/rebar-grade400-12-main.jpg",
      "alt_text": "Grade 400 Rebar #4 Main Image",
      "is_primary": true,
      "sort_order": 1,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "videos": [
    {
      "id": 1,
      "title": {"zh-CN": "Grade 400钢筋产品演示", "en-US": "Grade 400 Rebar Product Demo"},
      "description": {"zh-CN": "展示Grade 400钢筋的特性和应用", "en-US": "Showcasing Grade 400 rebar features and applications"},
      "video_url": "https://cdn.tigu.com/videos/rebar-grade400-demo.mp4",
      "thumbnail_url": "https://cdn.tigu.com/videos/thumbnails/rebar-grade400-demo.jpg",
      "video_type": "product_demo",
      "duration": 180,
      "quality": "1080p",
      "format": "mp4",
      "is_active": true,
      "view_count": 245,
      "like_count": 18,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST `/api/v1/products/`
Create a new product (requires authentication).

**Request Body:**
```json
{
  "sku": "NEW-PRODUCT-001",
  "name": {"zh-CN": "新产品", "en-US": "New Product"},
  "description": {"zh-CN": "产品描述", "en-US": "Product description"},
  "short_description": {"zh-CN": "简短描述", "en-US": "Short description"},
  "specifications": {"material": "Steel", "grade": "A36"},
  "price": 1000.00,
  "cost_price": 800.00,
  "stock": 100,
  "min_stock": 10,
  "unit": {"zh-CN": "件", "en-US": "Piece"},
  "weight": 10.5,
  "dimensions": "100mm×50mm×25mm",
  "category_id": 1,
  "supplier_id": 1001,
  "is_active": true
}
```

### PUT `/api/v1/products/{product_id}`
Update product (requires authentication).

### DELETE `/api/v1/products/{product_id}`
Delete product (soft delete, requires authentication).

### GET `/api/v1/products/low-stock/`
Get products with low stock (requires authentication).

### PATCH `/api/v1/products/{product_id}/stock`
Update product stock (requires authentication).

**Request Body:**
```json
{
  "stock": 150,
  "min_stock": 20
}
```

---

## 📋 Order Endpoints

### GET `/api/v1/orders/`
Get orders with pagination and filters (requires authentication).

**Query Parameters:**
- `page` (default: 1): Page number
- `per_page` (default: 20, max: 100): Items per page
- `status`: Filter by order status (pending, confirmed, processing, shipped, delivered, cancelled, refunded)
- `payment_status`: Filter by payment status (pending, paid, failed, refunded)
- `buyer_company_id`: Filter by buyer company
- `supplier_company_id`: Filter by supplier company

**Response:**
```json
{
  "items": [
    {
      "id": 300001,
      "order_number": "ORD-20240101-A1B2C3D4",
      "buyer_company_id": 1002,
      "buyer_user_id": 2,
      "supplier_company_id": 1001,
      "status": "confirmed",
      "payment_status": "pending",
      "subtotal": 210000.00,
      "tax_amount": 0.00,
      "shipping_amount": 0.00,
      "discount_amount": 0.00,
      "total_amount": 210000.00,
      "delivery_address": {
        "street": "456 Construction Ave",
        "city": "Toronto",
        "province": "ON",
        "postal_code": "M5V 3A8",
        "country": "Canada"
      },
      "delivery_contact": {
        "name": "Jane Smith",
        "phone": "+1-416-555-0124",
        "email": "jane@constructioncorp.ca"
      },
      "requested_delivery_date": "2024-01-15T00:00:00Z",
      "notes": "Please deliver to construction site entrance",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "items": [
        {
          "id": 1,
          "product_id": 100001,
          "quantity": 50,
          "unit_price": 4200.00,
          "total_price": 210000.00,
          "product_name": {"zh-CN": "Grade 400 螺纹钢筋 #4", "en-US": "Grade 400 Rebar #4"},
          "product_sku": "REBAR-GRADE400-12",
          "product_specifications": {
            "material": "Grade 400",
            "size": "#4 (12.7mm)",
            "length": "6m",
            "standard": "CSA G30.18"
          },
          "created_at": "2024-01-01T00:00:00Z"
        }
      ]
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 20,
  "pages": 2
}
```

### GET `/api/v1/orders/{order_id}`
Get order by ID (requires authentication).

### POST `/api/v1/orders/`
Create a new order (requires authentication).

**Request Body:**
```json
{
  "buyer_company_id": 1002,
  "supplier_company_id": 1001,
  "delivery_address": {
    "street": "456 Construction Ave",
    "city": "Toronto",
    "province": "ON",
    "postal_code": "M5V 3A8",
    "country": "Canada"
  },
  "delivery_contact": {
    "name": "Jane Smith",
    "phone": "+1-416-555-0124",
    "email": "jane@constructioncorp.ca"
  },
  "requested_delivery_date": "2024-01-15T00:00:00Z",
  "notes": "Please deliver to construction site entrance",
  "items": [
    {
      "product_id": 100001,
      "quantity": 50,
      "unit_price": 4200.00
    }
  ]
}
```

### PUT `/api/v1/orders/{order_id}`
Update order (requires authentication).

**Request Body:**
```json
{
  "status": "processing",
  "payment_status": "paid",
  "notes": "Updated delivery instructions"
}
```

---

## 💰 Quotation Endpoints

### GET `/api/v1/orders/quotations/`
Get quotations with pagination and filters (requires authentication).

**Query Parameters:**
- `page` (default: 1): Page number
- `per_page` (default: 20, max: 100): Items per page
- `status`: Filter by quotation status (draft, sent, viewed, accepted, rejected, expired)
- `buyer_company_id`: Filter by buyer company
- `supplier_company_id`: Filter by supplier company

### GET `/api/v1/orders/quotations/{quotation_id}`
Get quotation by ID (requires authentication).

**Response:**
```json
{
  "id": 400001,
  "quotation_number": "QUO-20240101-E5F6G7H8",
  "buyer_company_id": 1002,
  "buyer_user_id": 2,
  "supplier_company_id": 1001,
  "supplier_user_id": 1,
  "status": "sent",
  "subtotal": 295000.00,
  "tax_amount": 0.00,
  "discount_amount": 0.00,
  "total_amount": 295000.00,
  "valid_until": "2024-01-31T23:59:59Z",
  "payment_terms": "Net 30 days",
  "delivery_terms": "FOB Toronto",
  "notes": "Bulk pricing applied for large quantity order",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "sent_at": "2024-01-01T10:00:00Z",
  "items": [
    {
      "id": 1,
      "product_id": 100003,
      "quantity": 50,
      "unit_price": 5900.00,
      "total_price": 295000.00,
      "description": "6m length, A106 Grade B seamless pipe, ASTM standard",
      "specifications": {
        "material": "A106 Grade B",
        "size": "6 inch",
        "schedule": "SCH40",
        "length": "6m"
      },
      "brand": "Tenaris",
      "model": "A106GrB-6\"SCH40",
      "delivery_time": 5,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST `/api/v1/orders/quotations/`
Create a new quotation (requires authentication).

**Request Body:**
```json
{
  "buyer_company_id": 1002,
  "buyer_user_id": 2,
  "supplier_company_id": 1001,
  "valid_until": "2024-01-31T23:59:59Z",
  "payment_terms": "Net 30 days",
  "delivery_terms": "FOB Toronto",
  "notes": "Bulk pricing applied for large quantity order",
  "items": [
    {
      "product_id": 100003,
      "quantity": 50,
      "unit_price": 5900.00,
      "description": "6m length, A106 Grade B seamless pipe, ASTM standard",
      "specifications": {
        "material": "A106 Grade B",
        "size": "6 inch",
        "schedule": "SCH40",
        "length": "6m"
      },
      "brand": "Tenaris",
      "model": "A106GrB-6\"SCH40",
      "delivery_time": 5
    }
  ]
}
```

### PUT `/api/v1/orders/quotations/{quotation_id}`
Update quotation (requires authentication).

### POST `/api/v1/orders/quotations/{quotation_id}/send`
Send quotation to buyer (requires authentication).

### POST `/api/v1/orders/quotations/{quotation_id}/accept`
Accept quotation and create order (requires authentication).

### POST `/api/v1/orders/quotations/{quotation_id}/reject`
Reject quotation (requires authentication).

---

## 🏥 Health Check Endpoints

### GET `/`
Root endpoint with API information.

**Response:**
```json
{
  "message": "Welcome to Tigu B2B Building Materials Marketplace",
  "version": "1.0.0",
  "docs_url": "/docs",
  "api_version": "v1"
}
```

### GET `/api/v1/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Tigu B2B Building Materials Marketplace",
  "version": "1.0.0"
}
```

---

## 📊 Response Status Codes

- `200 OK`: Successful GET, PUT, PATCH requests
- `201 Created`: Successful POST requests
- `204 No Content`: Successful DELETE requests
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation errors
- `423 Locked`: Account temporarily locked
- `500 Internal Server Error`: Server error

---

## 🔧 Error Response Format

All error responses follow this format:
```json
{
  "detail": "Error message description"
}
```

For validation errors:
```json
{
  "detail": [
    {
      "loc": ["field_name"],
      "msg": "Field validation error message",
      "type": "validation_error_type"
    }
  ]
}
```

---

## 🚀 Getting Started

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables:**
   ```bash
   export DATABASE_URL="mysql+pymysql://user:password@localhost/tigu_db"
   export SECRET_KEY="your-secret-key-here"
   ```

3. **Run the Server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access API Documentation:**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

---

## 📝 Notes

- All timestamps are in UTC format
- Multilingual fields use JSON format with language codes (zh-CN, en-US)
- Pagination is 1-indexed
- All monetary values are in decimal format
- File uploads for images and videos are not yet implemented (URLs are used)
- Email notifications for password reset are not yet implemented
- Advanced search and filtering capabilities can be extended
- Rate limiting and advanced security features should be added for production use 