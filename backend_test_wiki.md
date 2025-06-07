# Tigu B2B 后端API测试指南

## 📋 目录
1. [综合测试指南](#综合测试指南)
2. [项目概述](#项目概述)
3. [数据库架构](#数据库架构)
4. [API端点测试](#api端点测试)
5. [认证测试](#认证测试)
6. [产品API测试](#产品api测试)
7. [订单API测试](#订单api测试)
8. [自动化测试脚本](#自动化测试脚本)
9. [测试环境配置](#测试环境配置)

---

## 综合测试指南

### 🧪 完整API测试框架

我们现在提供了一个专业级的API测试框架，包含115+个自动化测试用例，覆盖认证、产品、订单、公司管理等所有核心功能。

**📖 详细测试指南**: 请参阅 [`tigu_backend_fastapi/TESTING.md`](tigu_backend_fastapi/TESTING.md)

#### 🚀 快速开始测试

```bash
# 进入后端目录
cd tigu_backend_fastapi

# 运行所有测试
./run_tests.sh

# 运行特定模块测试
./run_tests.sh -t auth      # 认证测试
./run_tests.sh -t products  # 产品测试
./run_tests.sh -t orders    # 订单测试
./run_tests.sh -t companies # 公司测试
```

#### 📊 测试覆盖范围

| 测试模块 | 测试数量 | 覆盖功能 |
|---------|---------|---------|
| **认证测试** | 25+ | 注册、登录、密码管理、Token处理 |
| **产品测试** | 30+ | CRUD操作、分类、搜索、权限控制 |
| **订单测试** | 35+ | 创建、状态管理、支付流程 |
| **公司测试** | 20+ | 资料管理、用户角色、认证流程 |

#### 🔧 测试工具特性

- ✅ **并行执行** - 快速反馈
- ✅ **覆盖率报告** - HTML/XML格式
- ✅ **CI/CD集成** - GitHub Actions自动化
- ✅ **专业文档** - 完整使用指南

> **注意**: 以下是手动测试的详细说明，用于理解API设计和数据结构。对于自动化测试，请使用上述测试框架。

---

## 项目概述

### 🏗️ 技术栈
- **后端框架**: FastAPI + Python 3.8+
- **数据库**: MySQL 8.0 (tigu_b2b)
- **ORM**: SQLAlchemy + PyMySQL
- **认证**: JWT Bearer Token
- **API文档**: Swagger UI (自动生成)
- **ID生成**: 雪花算法 (BigInt)

### 📁 实际项目结构
```
tigu_backend_fastapi/
├── tigu_backend_fastapi/
│   └── app/
│       ├── main.py                    # FastAPI应用入口
│       ├── api/v1/
│       │   ├── api.py                 # 路由注册
│       │   └── routers/
│       │       ├── auth.py            # 认证端点
│       │       ├── products.py        # 产品端点
│       │       └── orders.py          # 订单端点
│       ├── models/                    # SQLAlchemy模型
│       │   ├── user.py               # 用户/公司/会话模型
│       │   ├── product.py            # 产品/分类模型
│       │   └── order.py              # 订单/报价模型
│       ├── schemas/                   # Pydantic模型
│       ├── core/                     # 核心配置
│       ├── utils/
│       │   └── id_generator.py       # 雪花算法ID生成
│       └── db/                       # 数据库配置
├── tigusql.sql                       # 数据库初始化脚本
├── mock_data.sql                     # 测试数据
├── restart_ubuntu.sh                 # Ubuntu启动脚本
├── dev.sh                           # 开发脚本
├── test_auth.sh                     # 认证测试脚本
└── pyproject.toml                   # Poetry配置
```

### 🌐 API基础信息
- **Base URL**: `http://localhost:8000`
- **API前缀**: `/api/v1`
- **文档地址**: `http://localhost:8000/docs` (Swagger UI)
- **认证方式**: Bearer Token (JWT)

---

## 数据库架构

### 🗄️ 核心表结构

#### 用户管理表
```sql
-- 用户表 (BIGINT主键，非自增)
users: id, email, hashed_password, full_name, phone, auth_provider, is_active, is_superuser

-- 用户会话表
user_sessions: id, user_id, session_token, refresh_token, expires_at, is_active

-- 企业信息表
companies: id, company_code, company_name(JSON), company_type, business_license, tax_number

-- 用户企业关联表 (注意：无updated_at字段)
user_company_roles: id, user_id, company_id, role, is_active, created_at
```

#### 产品管理表
```sql
-- 产品分类表
categories: id, category_code, name(JSON), description(JSON), parent_id, is_active

-- 产品表
products: id, sku, name(JSON), description(JSON), price, stock, category_id, supplier_id

-- 产品图片表
product_images: id, product_id, image_url, alt_text, is_primary, sort_order

-- 产品视频表 (新增)
product_videos: id, product_id, video_url, title(JSON), video_type, duration, view_count
```

#### 订单管理表
```sql
-- 订单表
orders: id, order_number, buyer_company_id, supplier_company_id, status, payment_status

-- 订单项表
order_items: id, order_id, product_id, quantity, unit_price, total_price

-- 报价表
quotations: id, quotation_number, buyer_company_id, supplier_company_id, status

-- 报价项表
quotation_items: id, quotation_id, product_id, quantity, unit_price, total_price
```

### 🔑 ID生成策略
```python
# 使用雪花算法生成BigInt ID
from app.utils.id_generator import generate_id

user_id = generate_id()        # 返回BigInt类型
company_id = generate_id()     # 非自增，手动赋值
```

### 🌍 多语言JSON字段
```json
// 产品名称示例
{
  "zh-CN": "Grade 400 螺纹钢筋 #4",
  "en-US": "Grade 400 Rebar #4"
}

// 公司名称示例  
{
  "zh-CN": "加拿大钢铁供应有限公司",
  "en-US": "Canadian Steel Supply Ltd"
}
```

---

## API端点测试

### 🔍 端点概览

#### 认证端点 (`/api/v1/auth`)
- `POST /register` - 用户注册
- `POST /login` - 用户登录  
- `POST /refresh-token` - 刷新Token
- `POST /logout` - 登出
- `GET /profile` - 获取用户信息

#### 产品端点 (`/api/v1/products`)
- `GET /` - 获取产品列表 (分页+过滤)
- `GET /{product_id}` - 获取单个产品
- `GET /categories` - 获取分类列表
- `POST /` - 创建产品 (需认证)
- `PUT /{product_id}` - 更新产品 (需认证)

#### 订单端点 (`/api/v1/orders`)
- `GET /` - 获取订单列表 (需认证)
- `POST /` - 创建订单 (需认证)
- `GET /{order_id}` - 获取订单详情 (需认证)
- `POST /quotations/` - 创建报价 (需认证)

---

## 认证测试

### 🔐 JWT认证流程

#### 1. 用户注册
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123456!",
    "full_name": "Test User",
    "phone": "1234567890",
    "company_name": "Test Company",
    "company_type": "buyer",
    "business_license": "TEST123",
    "tax_number": "TAX123"
  }'
```

**期望响应**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1734567890123456,
    "email": "test@example.com",
    "full_name": "Test User",
    "default_company_id": 1734567890789012
  }
}
```

#### 2. 用户登录
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123456!"
  }'
```

#### 3. 使用Token访问保护端点
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "http://localhost:8000/api/v1/auth/profile"
```

### 🧪 认证测试脚本
```bash
# 使用内置测试脚本
./test_auth.sh

# 或使用开发脚本
./dev.sh auth-test
```

---

## 产品API测试

### 📦 产品端点测试

#### 1. 获取产品列表 (无需认证)
```bash
# 基础查询
curl "http://localhost:8000/api/v1/products/"

# 分页查询
curl "http://localhost:8000/api/v1/products/?page=1&per_page=10"

# 搜索产品
curl "http://localhost:8000/api/v1/products/?search=rebar"

# 价格范围过滤
curl "http://localhost:8000/api/v1/products/?min_price=3000&max_price=5000"

# 按分类过滤
curl "http://localhost:8000/api/v1/products/?category_id=1"

# 按供应商过滤
curl "http://localhost:8000/api/v1/products/?supplier_id=1001"

# 仅显示有库存产品
curl "http://localhost:8000/api/v1/products/?in_stock=true"

# 组合过滤
curl "http://localhost:8000/api/v1/products/?search=steel&min_price=1000&category_id=1&page=1&per_page=5"
```

#### 2. 获取单个产品
```bash
# 使用测试数据中的产品ID
curl "http://localhost:8000/api/v1/products/100001"
curl "http://localhost:8000/api/v1/products/100002"
curl "http://localhost:8000/api/v1/products/100003"
```

#### 3. 获取产品分类
```bash
# 获取所有分类
curl "http://localhost:8000/api/v1/products/categories"

# 获取顶级分类
curl "http://localhost:8000/api/v1/products/categories?parent_id="

# 获取子分类
curl "http://localhost:8000/api/v1/products/categories?parent_id=1"
```

### 📊 测试数据参数

基于 `mock_data.sql` 中的实际数据:

#### 产品ID
- `100001` - Grade 400 Rebar #4 (螺纹钢筋)
- `100002` - Steel Pipe 4" Schedule 40 (钢管)  
- `100003` - General Purpose Portland Cement (通用水泥)
- `100004` - High Early Strength Portland Cement (早强水泥)
- `100005` - Structural Steel Plate A36 (结构钢板)

#### 分类ID
- `1` - Steel Materials (钢材)
- `2` - Cement & Concrete (水泥混凝土)
- `3` - Pipes & Fittings (管道配件)  
- `4` - Reinforcement (钢筋)

#### 供应商ID
- `1001` - Canadian Steel Supply Ltd (加拿大钢铁供应)
- `1002` - Northern Cement Corp (北方水泥公司)
- `1003` - Pacific Building Materials (太平洋建材)

#### 价格范围
- 最低价: $850.00 (水泥)
- 最高价: $12,500.00 (钢板)
- 常用范围: $1000 - $5000

---

## 订单API测试

### 📋 订单管理测试 (需认证)

#### 1. 获取订单列表
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/orders/"

# 按状态过滤
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/orders/?status=pending"

# 按支付状态过滤  
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/orders/?payment_status=paid"
```

#### 2. 创建订单
```bash
curl -X POST "http://localhost:8000/api/v1/orders/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "buyer_company_id": 1002,
    "supplier_company_id": 1001,
    "delivery_address": {
      "street": "123 Construction St",
      "city": "Toronto",
      "province": "ON",
      "postal_code": "M5V 1A1",
      "country": "Canada"
    },
    "delivery_contact": {
      "name": "John Smith",
      "phone": "+1-416-555-0123",
      "email": "john@construction.ca"
    },
    "requested_delivery_date": "2024-02-15T00:00:00Z",
    "notes": "Urgent delivery required",
    "items": [
      {
        "product_id": 100001,
        "quantity": 10,
        "unit_price": 4200.00
      },
      {
        "product_id": 100002,  
        "quantity": 5,
        "unit_price": 2850.00
      }
    ]
  }'
```

#### 3. 获取订单详情
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/orders/1000000001"
```

#### 4. 创建报价
```bash
curl -X POST "http://localhost:8000/api/v1/orders/quotations/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "buyer_company_id": 1002,
    "supplier_company_id": 1001,
    "quotation_type": "formal",
    "valid_until": "2024-02-28T23:59:59Z",
    "terms_conditions": "Standard terms apply",
    "notes": "Best price offer",
    "items": [
      {
        "product_id": 100001,
        "quantity": 50,
        "unit_price": 4100.00,
        "description": "Grade 400 Rebar bulk discount",
        "delivery_time": "5-7 business days"
      }
    ]
  }'
```

---

## 自动化测试脚本

### 🔗 专业测试框架

**强烈推荐**: 使用我们的新测试框架，查看详细指南 [`tigu_backend_fastapi/TESTING.md`](tigu_backend_fastapi/TESTING.md)

该框架提供：
- ✅ **115+自动化测试用例** - 全面覆盖所有API
- ✅ **一键测试执行** - `./run_tests.sh`
- ✅ **详细覆盖率报告** - HTML格式报告
- ✅ **CI/CD集成** - GitHub Actions自动化

### 🚀 开发脚本使用

#### 启动服务器
```bash
# Ubuntu/Linux
./restart_ubuntu.sh
./dev.sh start

# Windows (PowerShell)
poetry run uvicorn tigu_backend_fastapi.app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 运行测试
```bash
# 认证测试
./dev.sh auth-test

# 服务器健康检查
./dev.sh test

# 清理缓存
./dev.sh clean

# 停止服务器
./dev.sh kill
```

### 📝 自定义测试脚本

#### 产品API测试脚本
```bash
#!/bin/bash
# test_products.sh

BASE_URL="http://localhost:8000/api/v1/products"

echo "🧪 Testing Products API"
echo "======================"

# 1. 测试产品列表
echo "1. Testing product list..."
curl -s "$BASE_URL/" | jq '.total'

# 2. 测试搜索
echo "2. Testing search..."
curl -s "$BASE_URL/?search=rebar" | jq '.items | length'

# 3. 测试单个产品
echo "3. Testing single product..."
curl -s "$BASE_URL/100001" | jq '.sku'

# 4. 测试分类
echo "4. Testing categories..."
curl -s "$BASE_URL/categories" | jq 'length'

echo "✅ Products API test completed!"
```

#### 订单API测试脚本
```bash
#!/bin/bash  
# test_orders.sh

# 需要先获取认证Token
echo "🔐 Please provide access token:"
read -s ACCESS_TOKEN

BASE_URL="http://localhost:8000/api/v1/orders"
AUTH_HEADER="Authorization: Bearer $ACCESS_TOKEN"

echo "🧪 Testing Orders API"
echo "===================="

# 1. 测试订单列表
echo "1. Testing order list..."
curl -s -H "$AUTH_HEADER" "$BASE_URL/" | jq '.total'

# 2. 测试创建订单
echo "2. Testing order creation..."
ORDER_DATA='{
  "buyer_company_id": 1002,
  "supplier_company_id": 1001,
  "items": [{"product_id": 100001, "quantity": 5, "unit_price": 4200.00}]
}'

curl -s -X POST -H "$AUTH_HEADER" -H "Content-Type: application/json" \
  -d "$ORDER_DATA" "$BASE_URL/" | jq '.order_number'

echo "✅ Orders API test completed!"
```

---

## 测试环境配置

### 🛠️ 环境准备

#### 1. 数据库设置
```bash
# 创建测试数据库
mysql -u root -p
CREATE DATABASE tigu_b2b_test;

# 导入数据库结构
mysql -u root -p tigu_b2b_test < tigusql.sql

# 导入测试数据
mysql -u root -p tigu_b2b_test < mock_data.sql
```

#### 2. 环境变量配置
```bash
# .env 文件
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/tigu_b2b_test
SECRET_KEY=your-test-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
```

#### 3. Python依赖安装
```bash
# 使用Poetry
poetry install

# 或使用pip
pip install -r requirements.txt
```

### ✅ 测试检查清单

#### 基础功能测试
- [ ] 服务器启动成功 (`http://localhost:8000`)
- [ ] API文档可访问 (`http://localhost:8000/docs`)
- [ ] 数据库连接正常
- [ ] 雪花算法ID生成正常

#### 认证功能测试
- [ ] 用户注册成功
- [ ] 用户登录成功  
- [ ] Token生效
- [ ] 受保护端点访问正常

#### 产品API测试
- [ ] 产品列表获取正常
- [ ] 搜索功能正常
- [ ] 分页功能正常
- [ ] 过滤功能正常
- [ ] 单个产品详情正常

#### 订单API测试  
- [ ] 订单列表获取正常
- [ ] 订单创建成功
- [ ] 报价创建成功
- [ ] 订单状态更新正常

### 🐛 常见问题排除

#### 1. 模块导入错误
```bash
# 确保在正确目录
cd tigu_backend_fastapi

# 设置Python路径
export PYTHONPATH="$(pwd):$PYTHONPATH"

# 使用Poetry运行
poetry run uvicorn tigu_backend_fastapi.app.main:app --reload
```

#### 2. 数据库连接错误
```bash
# 检查数据库状态
systemctl status mysql

# 检查连接参数
mysql -u username -p database_name

# 检查防火墙设置
sudo ufw status
```

#### 3. ID生成错误
```sql
-- 检查ID是否正确生成
SELECT id FROM users ORDER BY created_at DESC LIMIT 5;

-- 检查是否使用BIGINT
DESCRIBE users;
```

#### 4. JSON字段错误
```sql
-- 检查JSON字段格式
SELECT name FROM products WHERE JSON_VALID(name) = 0;

-- 测试JSON提取
SELECT JSON_EXTRACT(name, '$.zh-CN') FROM products LIMIT 5;
```

---

## 📚 参考资源

### API文档
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

### 相关文件
- `tigusql.sql` - 数据库结构
- `mock_data.sql` - 测试数据
- `tigu_database_design_wiki.md` - 数据库设计文档
- `auth_guide_wiki.md` - 认证方案文档
- `api_endpoints_documentation.md` - API端点文档

### 测试工具
- **curl** - 命令行HTTP客户端
- **jq** - JSON处理工具
- **Postman** - GUI API测试工具
- **HTTPie** - 用户友好的HTTP客户端

---

**最后更新**: 2025年6月 
**版本**: 1.0
**状态**: ✅ 已验证与当前codebase对齐 