# 梯谷B2B平台数据库设计Wiki

## 目录
1. [项目概述](#1-项目概述)
2. [数据库设计评估](#2-数据库设计评估)
3. [ID生成策略](#3-id生成策略)
4. [多语言支持方案](#4-多语言支持方案)
5. [核心表设计](#5-核心表设计)
6. [最佳实践建议](#6-最佳实践建议)

## 1. 项目概述

### 1.1 业务定位
梯谷B2B平台是专注于建材行业的B2B撮合平台，主要特点：
- **目标用户**：装修公司、工地项目经理、建材供应商
- **核心价值**：数据驱动采购决策、AI推荐供应商
- **业务特点**：账期管理、批量采购、企业客户、复杂供应链

### 1.2 技术架构
- **后端**：FastAPI + Python + MySQL
- **前端**：Vue.js PWA
- **支付**：Stripe + 支付宝 + 微信支付
- **部署**：AWS/Azure云环境

## 2. 数据库设计评估

### 2.1 原设计问题分析

#### ❌ 严重缺陷
1. **B2B业务支持不足**
   - 缺少企业客户管理体系
   - 缺少供应商管理和绩效评估
   - 缺少复杂的企业权限管理

2. **财务系统缺失**
   - 无账期管理机制
   - 缺少对账单和结算流程
   - 无发票管理系统

3. **物流配送缺失**
   - 无物流跟踪体系
   - 缺少配送地址管理
   - 无3PL集成支持

4. **数据分析能力不足**
   - 无采购行为分析
   - 缺少供应商绩效评估
   - 无商业智能支持

### 2.2 改进优先级

#### Phase 1 (立即实施)
- 企业客户管理体系
- 供应商管理体系
- 订单流程优化

#### Phase 2 (3个月内)
- 财务结算系统
- 库存管理增强
- 基础数据分析

#### Phase 3 (6个月内)
- 物流配送系统
- 高级数据分析
- 移动端优化

## 3. ID生成策略

### 3.1 INT AUTO_INCREMENT 问题
- **数值范围限制**：INT最大约42亿
- **高并发性能瓶颈**：全局锁竞争
- **分布式扩展困难**：ID冲突问题

### 3.2 推荐方案：BIGINT + 雪花算法

#### BIGINT AUTO_INCREMENT（基础方案）
```sql
-- 使用BIGINT避免溢出
id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY

-- 分段起始值避免冲突
ALTER TABLE users AUTO_INCREMENT = 100000000;      -- 1亿
ALTER TABLE companies AUTO_INCREMENT = 200000000;  -- 2亿
ALTER TABLE orders AUTO_INCREMENT = 1000000000;    -- 10亿
```

#### 数据库级雪花算法（高并发方案）
```sql
-- 雪花算法配置表
CREATE TABLE snowflake_config (
    id INT PRIMARY KEY DEFAULT 1,
    datacenter_id INT NOT NULL DEFAULT 1,
    worker_id INT NOT NULL DEFAULT 1,
    epoch_timestamp BIGINT NOT NULL DEFAULT 1704067200000,
    last_timestamp BIGINT NOT NULL DEFAULT 0,
    sequence_number INT NOT NULL DEFAULT 0
);

-- 雪花算法ID生成函数
CREATE FUNCTION generate_snowflake_id() RETURNS BIGINT
-- [完整实现见技术文档]
```

#### 业务编码策略
```sql
-- 人类可读的业务编码
user_code: U20240115000001
company_code: C20240115000001
order_number: ORD20240115000001
```

## 4. 多语言支持方案

### 4.1 方案对比

| 方案 | 优势 | 劣势 | 适用场景 |
|------|------|------|----------|
| 独立翻译表 | 灵活性高、查询性能好 | 架构复杂、开发工作量大 | 大型项目、复杂需求 |
| JSON字段 | 简单直观、开发快速 | 查询性能一般、搜索复杂 | 中小型项目、快速开发 |

### 4.2 推荐方案：JSON多语言字段

#### 核心设计原则
```sql
-- 多语言JSON字段设计
name JSON NOT NULL,  -- {"zh-CN": "建筑材料", "en-US": "Building Materials"}
description JSON,    -- {"zh-CN": "描述", "en-US": "Description"}

-- JSON操作函数
CREATE FUNCTION get_json_lang(
    json_field JSON,
    language_code VARCHAR(10),
    fallback_lang VARCHAR(10) DEFAULT 'zh-CN'
) RETURNS TEXT;
```

#### 性能优化
```sql
-- 为常用语言创建生成列索引
ALTER TABLE products 
ADD COLUMN name_zh_cn VARCHAR(255) GENERATED ALWAYS AS 
    (JSON_UNQUOTE(JSON_EXTRACT(name, '$.zh-CN'))) STORED;
CREATE INDEX idx_name_zh_cn ON products(name_zh_cn);
```

## 5. 核心表设计

### 5.1 企业客户管理

```sql
-- 用户表
CREATE TABLE users (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    user_code VARCHAR(20) UNIQUE,           -- 业务编码: U20240115000001
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(20),
    avatar_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_user_code (user_code),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 企业信息表
CREATE TABLE companies (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    company_code VARCHAR(50) UNIQUE NOT NULL,
    company_name JSON NOT NULL,              -- 多语言公司名称
    company_type ENUM('supplier', 'buyer', 'both') NOT NULL,
    business_license VARCHAR(100) UNIQUE,
    tax_number VARCHAR(50),
    legal_representative VARCHAR(100),
    registered_address TEXT,
    business_scope JSON,                     -- 多语言经营范围
    credit_rating ENUM('AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'C') DEFAULT 'B',
    credit_limit DECIMAL(15,2) DEFAULT 0,
    payment_terms INT DEFAULT 30,           -- 账期天数
    is_verified BOOLEAN DEFAULT FALSE,
    verification_docs JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_company_code (company_code),
    INDEX idx_company_type (company_type),
    INDEX idx_verified (is_verified)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 用户企业关联表
CREATE TABLE user_company_roles (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    user_id BIGINT UNSIGNED,
    company_id BIGINT UNSIGNED,
    role ENUM('admin', 'purchaser', 'finance', 'viewer') DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_company (user_id, company_id),
    INDEX idx_user (user_id),
    INDEX idx_company (company_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 5.2 供应商管理

```sql
-- 供应商详细信息表
CREATE TABLE suppliers (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    company_id BIGINT UNSIGNED,
    supplier_code VARCHAR(50) UNIQUE,
    supplier_tier ENUM('tier1', 'tier2', 'tier3') DEFAULT 'tier2',
    main_categories JSON,                   -- 主营品类
    warehouse_locations JSON,               -- 仓库位置
    delivery_capabilities JSON,             -- 配送能力
    min_order_amount DECIMAL(10,2),
    lead_time_days INT DEFAULT 7,
    quality_rating DECIMAL(3,2) DEFAULT 3.00,
    service_rating DECIMAL(3,2) DEFAULT 3.00,
    cooperation_years INT DEFAULT 0,
    is_preferred BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    INDEX idx_company (company_id),
    INDEX idx_supplier_code (supplier_code),
    INDEX idx_tier (supplier_tier)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 供应商绩效分析表
CREATE TABLE supplier_performance (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    supplier_id BIGINT UNSIGNED,
    period_start DATE,
    period_end DATE,
    total_orders INT DEFAULT 0,
    on_time_delivery_rate DECIMAL(5,2),
    quality_score DECIMAL(3,2),
    price_competitiveness DECIMAL(3,2),
    response_time_avg DECIMAL(5,2),         -- 平均响应时间(小时)
    complaint_count INT DEFAULT 0,
    return_rate DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    INDEX idx_supplier (supplier_id),
    INDEX idx_period (period_start, period_end)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 5.3 财务结算系统

```sql
-- 账期管理表
CREATE TABLE payment_terms (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    company_id BIGINT UNSIGNED,
    supplier_id BIGINT UNSIGNED,
    payment_days INT DEFAULT 30,           -- 账期天数
    credit_limit DECIMAL(15,2),
    used_credit DECIMAL(15,2) DEFAULT 0,
    overdue_amount DECIMAL(15,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    INDEX idx_company (company_id),
    INDEX idx_supplier (supplier_id),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 对账单表
CREATE TABLE settlement_statements (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    statement_number VARCHAR(50) UNIQUE,
    company_id BIGINT UNSIGNED,
    supplier_id BIGINT UNSIGNED,
    period_start DATE,
    period_end DATE,
    total_amount DECIMAL(15,2),
    paid_amount DECIMAL(15,2) DEFAULT 0,
    pending_amount DECIMAL(15,2),
    status ENUM('draft', 'confirmed', 'paid', 'disputed') DEFAULT 'draft',
    due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    INDEX idx_statement_number (statement_number),
    INDEX idx_company (company_id),
    INDEX idx_supplier (supplier_id),
    INDEX idx_due_date (due_date),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 发票管理表
CREATE TABLE invoices (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    invoice_number VARCHAR(50) UNIQUE,
    invoice_type ENUM('VAT_special', 'VAT_general', 'receipt') DEFAULT 'VAT_general',
    order_id BIGINT UNSIGNED,
    company_id BIGINT UNSIGNED,
    supplier_id BIGINT UNSIGNED,
    amount DECIMAL(15,2),
    tax_amount DECIMAL(15,2),
    total_amount DECIMAL(15,2),
    invoice_date DATE,
    issue_status ENUM('pending', 'issued', 'received', 'verified') DEFAULT 'pending',
    invoice_file_url VARCHAR(500),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    INDEX idx_invoice_number (invoice_number),
    INDEX idx_order (order_id),
    INDEX idx_company (company_id),
    INDEX idx_supplier (supplier_id),
    INDEX idx_status (issue_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 5.4 产品与分类

```sql
-- 产品分类表（多语言JSON版本）
CREATE TABLE categories (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    category_code VARCHAR(50) UNIQUE NOT NULL,
    name JSON NOT NULL,                     -- 多语言名称
    description JSON,                       -- 多语言描述
    parent_id BIGINT UNSIGNED,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_parent (parent_id),
    INDEX idx_active (is_active),
    INDEX idx_code (category_code),
    INDEX idx_sort (sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 产品表（多语言JSON版本）
CREATE TABLE products (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    sku VARCHAR(100) NOT NULL UNIQUE,
    name JSON NOT NULL,                     -- 多语言产品名称
    description JSON,                       -- 多语言产品描述
    short_description JSON,                 -- 多语言简短描述
    specifications JSON,                    -- 规格参数（可包含多语言）
    meta_keywords JSON,                     -- SEO关键词（多语言）
    meta_description JSON,                  -- SEO描述（多语言）
    
    price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2),
    stock INT NOT NULL DEFAULT 0,
    min_stock INT DEFAULT 0,
    unit JSON DEFAULT ('{"zh-CN": "件", "en-US": "Piece"}'),
    weight DECIMAL(8,2),
    dimensions VARCHAR(100),
    
    category_id BIGINT UNSIGNED,
    supplier_id BIGINT UNSIGNED,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (supplier_id) REFERENCES companies(id) ON DELETE SET NULL,
    INDEX idx_sku (sku),
    INDEX idx_category (category_id),
    INDEX idx_supplier (supplier_id),
    INDEX idx_active (is_active),
    INDEX idx_price (price)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 产品图片表
CREATE TABLE product_images (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    product_id BIGINT UNSIGNED,
    image_url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(255),
    is_primary BOOLEAN DEFAULT FALSE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_product (product_id),
    INDEX idx_primary (is_primary),
    INDEX idx_sort (sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 5.5 订单管理

```sql
-- 改进的订单表
CREATE TABLE orders (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    order_number VARCHAR(50) NOT NULL UNIQUE,
    company_id BIGINT UNSIGNED,             -- 采购企业
    supplier_id BIGINT UNSIGNED,            -- 供应商企业
    user_id BIGINT UNSIGNED,                -- 下单用户
    
    order_type ENUM('standard', 'urgent', 'scheduled') DEFAULT 'standard',
    status ENUM('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
    
    subtotal_amount DECIMAL(15,2),          -- 小计金额
    tax_amount DECIMAL(15,2) DEFAULT 0,     -- 税费
    shipping_fee DECIMAL(15,2) DEFAULT 0,   -- 运费
    total_amount DECIMAL(15,2) NOT NULL,    -- 总金额
    
    payment_terms INT DEFAULT 30,           -- 账期天数
    expected_delivery_date DATE,            -- 期望交付日期
    
    project_name VARCHAR(255),              -- 项目名称
    project_address TEXT,                   -- 项目地址
    shipping_address TEXT,                  -- 配送地址
    contact_person VARCHAR(100),            -- 联系人
    contact_phone VARCHAR(20),              -- 联系电话
    
    approval_status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    approver_id BIGINT UNSIGNED,            -- 审批人
    approved_at TIMESTAMP NULL,
    
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (supplier_id) REFERENCES companies(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (approver_id) REFERENCES users(id),
    
    INDEX idx_order_number (order_number),
    INDEX idx_company (company_id),
    INDEX idx_supplier (supplier_id),
    INDEX idx_user (user_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 订单项表
CREATE TABLE order_items (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    order_id BIGINT UNSIGNED,
    product_id BIGINT UNSIGNED,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    specifications TEXT,                    -- 特殊规格要求
    notes TEXT,                            -- 备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_order (order_id),
    INDEX idx_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 5.6 物流配送

```sql
-- 物流配送表
CREATE TABLE shipments (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    shipment_number VARCHAR(50) UNIQUE,
    order_id BIGINT UNSIGNED,
    logistics_provider VARCHAR(100),        -- 物流商
    tracking_number VARCHAR(100),           -- 物流单号
    shipment_type ENUM('direct', 'warehouse', 'pickup') DEFAULT 'direct',
    
    departure_address TEXT,                 -- 发货地址
    delivery_address TEXT,                  -- 收货地址
    contact_person VARCHAR(100),            -- 收货联系人
    contact_phone VARCHAR(20),              -- 收货电话
    
    estimated_delivery DATETIME,            -- 预计送达时间
    actual_delivery DATETIME NULL,          -- 实际送达时间
    
    status ENUM('preparing', 'shipped', 'in_transit', 'delivered', 'exception') DEFAULT 'preparing',
    delivery_fee DECIMAL(10,2),             -- 配送费用
    weight DECIMAL(8,2),                    -- 重量
    volume DECIMAL(8,2),                    -- 体积
    special_requirements TEXT,              -- 特殊要求
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    INDEX idx_order (order_id),
    INDEX idx_tracking (tracking_number),
    INDEX idx_status (status),
    INDEX idx_shipment_number (shipment_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 配送轨迹表
CREATE TABLE shipment_tracking (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    shipment_id BIGINT UNSIGNED,
    tracking_time TIMESTAMP,
    location VARCHAR(255),
    status VARCHAR(100),
    description TEXT,
    operator VARCHAR(100),                  -- 操作员
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shipment_id) REFERENCES shipments(id) ON DELETE CASCADE,
    INDEX idx_shipment (shipment_id),
    INDEX idx_time (tracking_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 5.7 询价比价系统

```sql
-- 询价单表
CREATE TABLE quotation_requests (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    request_number VARCHAR(50) UNIQUE,
    company_id BIGINT UNSIGNED,
    requestor_id BIGINT UNSIGNED,           -- 询价人
    title VARCHAR(255),
    description TEXT,
    expected_delivery_date DATE,
    delivery_address TEXT,
    status ENUM('draft', 'published', 'closed') DEFAULT 'draft',
    deadline TIMESTAMP,                     -- 报价截止时间
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (requestor_id) REFERENCES users(id),
    INDEX idx_company (company_id),
    INDEX idx_requestor (requestor_id),
    INDEX idx_status (status),
    INDEX idx_deadline (deadline),
    INDEX idx_request_number (request_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 询价单明细表
CREATE TABLE quotation_request_items (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    request_id BIGINT UNSIGNED,
    product_id BIGINT UNSIGNED,
    quantity INT NOT NULL,
    specifications TEXT,                    -- 规格要求
    max_price DECIMAL(10,2),               -- 预算上限
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES quotation_requests(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    INDEX idx_request (request_id),
    INDEX idx_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 报价单表
CREATE TABLE quotations (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    quotation_number VARCHAR(50) UNIQUE,
    request_id BIGINT UNSIGNED,
    supplier_id BIGINT UNSIGNED,
    quoter_id BIGINT UNSIGNED,              -- 报价人
    
    total_amount DECIMAL(15,2),
    valid_until DATE,                       -- 报价有效期
    delivery_days INT,                      -- 交付天数
    payment_terms INT,                      -- 付款条款
    warranty_period INT,                    -- 质保期
    
    notes TEXT,
    status ENUM('draft', 'submitted', 'selected', 'rejected') DEFAULT 'draft',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES quotation_requests(id),
    FOREIGN KEY (supplier_id) REFERENCES companies(id),
    FOREIGN KEY (quoter_id) REFERENCES users(id),
    INDEX idx_request (request_id),
    INDEX idx_supplier (supplier_id),
    INDEX idx_quoter (quoter_id),
    INDEX idx_status (status),
    INDEX idx_quotation_number (quotation_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 报价单明细表
CREATE TABLE quotation_items (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    quotation_id BIGINT UNSIGNED,
    request_item_id BIGINT UNSIGNED,       -- 对应询价项
    product_id BIGINT UNSIGNED,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    specifications TEXT,                    -- 供应商规格说明
    brand VARCHAR(100),                     -- 品牌
    model VARCHAR(100),                     -- 型号
    delivery_days INT,                      -- 交付天数
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (quotation_id) REFERENCES quotations(id) ON DELETE CASCADE,
    FOREIGN KEY (request_item_id) REFERENCES quotation_request_items(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    INDEX idx_quotation (quotation_id),
    INDEX idx_request_item (request_item_id),
    INDEX idx_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## 6. 最佳实践建议

### 6.1 索引优化策略

```sql
-- 复合索引设计
CREATE INDEX idx_orders_compound ON orders(company_id, status, created_at);
CREATE INDEX idx_products_compound ON products(category_id, is_active, price);
CREATE INDEX idx_settlement_compound ON settlement_statements(due_date, status);

-- 多语言字段性能优化
ALTER TABLE products 
ADD COLUMN name_zh_cn VARCHAR(255) GENERATED ALWAYS AS 
    (JSON_UNQUOTE(JSON_EXTRACT(name, '$.zh-CN'))) STORED,
ADD COLUMN name_en_us VARCHAR(255) GENERATED ALWAYS AS 
    (JSON_UNQUOTE(JSON_EXTRACT(name, '$.en-US'))) STORED;

CREATE INDEX idx_name_zh_cn ON products(name_zh_cn);
CREATE INDEX idx_name_en_us ON products(name_en_us);
```

### 6.2 数据安全与审计

```sql
-- 业务操作审计表
CREATE TABLE audit_logs (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    user_id BIGINT UNSIGNED,
    company_id BIGINT UNSIGNED,
    action_type VARCHAR(50),                -- create_order, approve_payment
    resource_type VARCHAR(50),              -- order, payment, user
    resource_id BIGINT UNSIGNED,
    old_values JSON,                        -- 变更前数据
    new_values JSON,                        -- 变更后数据
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (company_id) REFERENCES companies(id),
    INDEX idx_user (user_id),
    INDEX idx_company (company_id),
    INDEX idx_resource (resource_type, resource_id),
    INDEX idx_action (action_type),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 敏感数据加密存储
CREATE TABLE encrypted_business_data (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    company_id BIGINT UNSIGNED,
    data_type ENUM('contract', 'bank_info', 'tax_cert') NOT NULL,
    encrypted_content LONGTEXT,             -- AES加密存储
    encryption_key_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    INDEX idx_company (company_id),
    INDEX idx_data_type (data_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 6.3 性能监控

```sql
-- 系统性能监控表
CREATE TABLE system_metrics (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    metric_type VARCHAR(50),                -- api_response_time, db_query_time
    metric_name VARCHAR(100),               -- /api/v1/products/search
    metric_value DECIMAL(10,4),             -- 响应时间(秒)
    tags JSON,                              -- 额外标签信息
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_type (metric_type),
    INDEX idx_name (metric_name),
    INDEX idx_recorded (recorded_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 支付相关表（补充）
CREATE TABLE payments (
    id BIGINT UNSIGNED PRIMARY KEY,         -- 雪花算法生成的ID
    payment_number VARCHAR(50) UNIQUE,      -- 支付单号
    order_id BIGINT UNSIGNED,
    company_id BIGINT UNSIGNED,
    supplier_id BIGINT UNSIGNED,
    user_id BIGINT UNSIGNED,
    
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CNY',
    payment_method ENUM('stripe', 'alipay', 'wechat', 'bank_transfer', 'credit') DEFAULT 'stripe',
    
    stripe_payment_intent_id VARCHAR(255),
    alipay_trade_no VARCHAR(100),
    wechat_transaction_id VARCHAR(100),
    
    status ENUM('pending', 'processing', 'completed', 'failed', 'cancelled', 'refunded') DEFAULT 'pending',
    
    payment_date TIMESTAMP NULL,
    due_date DATE,
    
    metadata JSON,                          -- 支付相关元数据
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (supplier_id) REFERENCES companies(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    
    INDEX idx_payment_number (payment_number),
    INDEX idx_order (order_id),
    INDEX idx_company (company_id),
    INDEX idx_supplier (supplier_id),
    INDEX idx_status (status),
    INDEX idx_payment_method (payment_method),
    INDEX idx_stripe_intent (stripe_payment_intent_id),
    INDEX idx_due_date (due_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 6.4 数据库配置优化

```sql
-- MySQL配置建议（my.cnf）
[mysqld]
# 基础配置
character_set_server = utf8mb4
collation_server = utf8mb4_unicode_ci
default_time_zone = '+08:00'

# InnoDB优化
innodb_buffer_pool_size = 8G             # 根据内存调整
innodb_log_file_size = 1G
innodb_flush_log_at_trx_commit = 2
innodb_autoinc_lock_mode = 2             # 提高AUTO_INCREMENT性能

# 连接优化
max_connections = 1000
max_connect_errors = 1000000
wait_timeout = 28800

# 查询缓存
query_cache_type = 1
query_cache_size = 256M

# 慢查询日志
slow_query_log = 1
long_query_time = 2
```

### 6.5 部署检查清单

#### 数据库安全
- [ ] 修改默认root密码
- [ ] 创建专用应用用户
- [ ] 配置防火墙规则
- [ ] 启用SSL连接
- [ ] 设置定期备份

#### 性能优化
- [ ] 配置合适的innodb_buffer_pool_size
- [ ] 设置慢查询日志监控
- [ ] 创建必要的复合索引
- [ ] 配置查询缓存
- [ ] 设置连接池参数

#### 监控告警
- [ ] 设置磁盘空间监控
- [ ] 配置数据库连接数告警
- [ ] 监控慢查询数量
- [ ] 设置主从复制监控（如适用）

---

## 更新日志

- **2024-01-15**: 初始版本，包含核心表设计
- **2024-01-15**: 添加ID生成策略和多语言支持
- **2024-01-15**: 补充最佳实践和部署建议

---

## 参考资料

- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)
- [MySQL 8.0参考手册](https://dev.mysql.com/doc/refman/8.0/en/)
- [梯谷项目业务需求文档](./business_readme.md)

#### 雪花算法应用层实现

```python
# app/core/snowflake.py
import time
import threading
from typing import Optional

class SnowflakeGenerator:
    """
    雪花算法ID生成器
    64位ID结构：
    - 1位：固定为0
    - 41位：时间戳(毫秒)
    - 10位：机器ID (5位数据中心 + 5位机器ID)
    - 12位：序列号
    """
    
    def __init__(self, datacenter_id: int = 1, worker_id: int = 1, epoch: int = 1704067200000):
        """
        初始化雪花算法生成器
        
        Args:
            datacenter_id: 数据中心ID (0-31)
            worker_id: 机器ID (0-31)
            epoch: 起始时间戳 (2024-01-01 00:00:00)
        """
        if datacenter_id > 31 or datacenter_id < 0:
            raise ValueError("datacenter_id must be between 0 and 31")
        if worker_id > 31 or worker_id < 0:
            raise ValueError("worker_id must be between 0 and 31")
            
        self.datacenter_id = datacenter_id
        self.worker_id = worker_id
        self.epoch = epoch
        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()
    
    def _get_timestamp(self) -> int:
        """获取当前时间戳(毫秒)"""
        return int(time.time() * 1000)
    
    def _wait_next_millis(self, last_timestamp: int) -> int:
        """等待下一毫秒"""
        timestamp = self._get_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._get_timestamp()
        return timestamp
    
    def generate_id(self) -> int:
        """生成雪花算法ID"""
        with self.lock:
            timestamp = self._get_timestamp()
            
            # 时钟回退检查
            if timestamp < self.last_timestamp:
                raise Exception(f"Clock moved backwards. Refusing to generate id for {self.last_timestamp - timestamp} milliseconds")
            
            # 同一毫秒内序列号递增
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & 0xFFF  # 12位序列号
                if self.sequence == 0:
                    timestamp = self._wait_next_millis(self.last_timestamp)
            else:
                self.sequence = 0
            
            self.last_timestamp = timestamp
            
            # 组装ID
            snowflake_id = (
                ((timestamp - self.epoch) << 22) |  # 41位时间戳
                (self.datacenter_id << 17) |        # 5位数据中心ID
                (self.worker_id << 12) |            # 5位机器ID
                self.sequence                       # 12位序列号
            )
            
            return snowflake_id
    
    def parse_id(self, snowflake_id: int) -> dict:
        """解析雪花算法ID"""
        timestamp = ((snowflake_id >> 22) + self.epoch) / 1000
        datacenter_id = (snowflake_id >> 17) & 0x1F
        worker_id = (snowflake_id >> 12) & 0x1F
        sequence = snowflake_id & 0xFFF
        
        return {
            'timestamp': timestamp,
            'datetime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)),
            'datacenter_id': datacenter_id,
            'worker_id': worker_id,
            'sequence': sequence
        }

# 全局实例
snowflake_generator = SnowflakeGenerator(
    datacenter_id=1,  # 可从环境变量获取
    worker_id=1       # 可从环境变量获取
)

# app/core/database.py
from sqlalchemy import event
from sqlalchemy.orm import Session
from app.core.snowflake import snowflake_generator

def generate_id_for_table(mapper, connection, target):
    """为新记录自动生成雪花算法ID"""
    if hasattr(target, 'id') and target.id is None:
        target.id = snowflake_generator.generate_id()

# 为所有模型注册ID生成事件
@event.listens_for(Session, 'before_flush')
def generate_ids_before_flush(session, flush_context, instances):
    """在flush前为所有新对象生成ID"""
    for obj in session.new:
        if hasattr(obj, 'id') and obj.id is None:
            obj.id = snowflake_generator.generate_id()

# app/models/base.py
from sqlalchemy import Column, BIGINT, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BaseModel(Base):
    """基础模型类"""
    __abstract__ = True
    
    id = Column(BIGINT, primary_key=True, comment="雪花算法生成的ID")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP, server_default=func.now(), 
                       onupdate=func.now(), comment="更新时间")

# app/schemas/base.py
from pydantic import BaseModel as PydanticBase, Field
from typing import Optional
from datetime import datetime

class BaseSchema(PydanticBase):
    """基础Schema类"""
    id: Optional[int] = Field(None, description="雪花算法生成的ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True

# app/crud/base.py
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.base import BaseModel
from app.core.snowflake import snowflake_generator

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseSchema)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.dict(exclude_unset=True)
        
        # 如果没有提供ID，生成雪花算法ID
        if 'id' not in obj_in_data or obj_in_data['id'] is None:
            obj_in_data['id'] = snowflake_generator.generate_id()
            
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

# 使用示例
# app/models/user.py
from sqlalchemy import Column, String, Boolean
from app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    user_code = Column(String(20), unique=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)

# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import user as user_crud
from app.schemas.user import UserCreate, User as UserSchema
from app.core.snowflake import snowflake_generator

router = APIRouter()

@router.post("/", response_model=UserSchema)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """创建新用户"""
    user = user_crud.create(db=db, obj_in=user_in)
    
    # 生成业务编码
    user_code = f"U{user.created_at.strftime('%Y%m%d')}{str(user.id)[-6:].zfill(6)}"
    user_crud.update(db=db, db_obj=user, obj_in={"user_code": user_code})
    
    return user

@router.get("/parse-id/{user_id}")
def parse_user_id(user_id: int) -> Any:
    """解析用户ID的雪花算法信息"""
    try:
        parsed = snowflake_generator.parse_id(user_id)
        return {
            "user_id": user_id,
            "snowflake_info": parsed
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid snowflake ID: {str(e)}")
```

#### ID生成配置

```python
# app/core/config.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # 雪花算法配置
    SNOWFLAKE_DATACENTER_ID: int = int(os.getenv("SNOWFLAKE_DATACENTER_ID", "1"))
    SNOWFLAKE_WORKER_ID: int = int(os.getenv("SNOWFLAKE_WORKER_ID", "1"))
    SNOWFLAKE_EPOCH: int = int(os.getenv("SNOWFLAKE_EPOCH", "1704067200000"))  # 2024-01-01
    
    class Config:
        env_file = ".env"

# Docker Compose配置示例
version: '3.8'
services:
  app1:
    environment:
      - SNOWFLAKE_DATACENTER_ID=1
      - SNOWFLAKE_WORKER_ID=1
  
  app2:
    environment:
      - SNOWFLAKE_DATACENTER_ID=1
      - SNOWFLAKE_WORKER_ID=2
  
  app3:
    environment:
      - SNOWFLAKE_DATACENTER_ID=2
      - SNOWFLAKE_WORKER_ID=1 