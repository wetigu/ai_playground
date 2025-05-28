-- 梯谷B2B平台数据库初始化脚本
-- 基于 tigu_database_design_wiki.md 设计文档
-- 创建日期: 2024-01-15
-- MySQL 8.0+

-- 设置字符集和时区
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
SET TIME_ZONE = '+08:00';

-- 创建数据库
CREATE DATABASE IF NOT EXISTS `tigu_b2b` 
    DEFAULT CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE `tigu_b2b`;

-- ========================================
-- 1. 用户管理表
-- ========================================

-- 用户表
CREATE TABLE `users` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `user_code` VARCHAR(20) UNIQUE,
    `email` VARCHAR(255) NOT NULL UNIQUE,
    `hashed_password` VARCHAR(255) NOT NULL,
    `full_name` VARCHAR(255),
    `phone` VARCHAR(20),
    `avatar_url` VARCHAR(500),
    `is_active` BOOLEAN DEFAULT TRUE,
    `is_superuser` BOOLEAN DEFAULT FALSE,
    `is_verified` BOOLEAN DEFAULT FALSE,
    `last_login_at` TIMESTAMP NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_email` (`email`),
    INDEX `idx_user_code` (`user_code`),
    INDEX `idx_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 企业信息表
CREATE TABLE `companies` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `company_code` VARCHAR(50) UNIQUE NOT NULL,
    `company_name` JSON NOT NULL COMMENT '多语言公司名称',
    `company_type` ENUM('supplier', 'buyer', 'both') NOT NULL,
    `business_license` VARCHAR(100) UNIQUE,
    `tax_number` VARCHAR(50),
    `legal_representative` VARCHAR(100),
    `registered_address` TEXT,
    `business_scope` JSON COMMENT '多语言经营范围',
    `credit_rating` ENUM('AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'C') DEFAULT 'B',
    `credit_limit` DECIMAL(15,2) DEFAULT 0,
    `payment_terms` INT DEFAULT 30 COMMENT '账期天数',
    `is_verified` BOOLEAN DEFAULT FALSE,
    `verification_docs` JSON,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_company_code` (`company_code`),
    INDEX `idx_company_type` (`company_type`),
    INDEX `idx_verified` (`is_verified`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='企业信息表';

-- 用户企业关联表
CREATE TABLE `user_company_roles` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `user_id` BIGINT UNSIGNED,
    `company_id` BIGINT UNSIGNED,
    `role` ENUM('admin', 'purchaser', 'finance', 'viewer') DEFAULT 'viewer',
    `is_active` BOOLEAN DEFAULT TRUE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `unique_user_company` (`user_id`, `company_id`),
    INDEX `idx_user` (`user_id`),
    INDEX `idx_company` (`company_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户企业关联表';

-- ========================================
-- 2. 供应商管理表
-- ========================================

-- 供应商详细信息表
CREATE TABLE `suppliers` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `company_id` BIGINT UNSIGNED,
    `supplier_code` VARCHAR(50) UNIQUE,
    `supplier_tier` ENUM('tier1', 'tier2', 'tier3') DEFAULT 'tier2',
    `main_categories` JSON COMMENT '主营品类',
    `warehouse_locations` JSON COMMENT '仓库位置',
    `delivery_capabilities` JSON COMMENT '配送能力',
    `min_order_amount` DECIMAL(10,2),
    `lead_time_days` INT DEFAULT 7,
    `quality_rating` DECIMAL(3,2) DEFAULT 3.00,
    `service_rating` DECIMAL(3,2) DEFAULT 3.00,
    `cooperation_years` INT DEFAULT 0,
    `is_preferred` BOOLEAN DEFAULT FALSE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`) ON DELETE CASCADE,
    INDEX `idx_company` (`company_id`),
    INDEX `idx_supplier_code` (`supplier_code`),
    INDEX `idx_tier` (`supplier_tier`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='供应商详细信息表';

-- 供应商绩效分析表
CREATE TABLE `supplier_performance` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `supplier_id` BIGINT UNSIGNED,
    `period_start` DATE,
    `period_end` DATE,
    `total_orders` INT DEFAULT 0,
    `on_time_delivery_rate` DECIMAL(5,2),
    `quality_score` DECIMAL(3,2),
    `price_competitiveness` DECIMAL(3,2),
    `response_time_avg` DECIMAL(5,2) COMMENT '平均响应时间(小时)',
    `complaint_count` INT DEFAULT 0,
    `return_rate` DECIMAL(5,2),
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`supplier_id`) REFERENCES `suppliers`(`id`),
    INDEX `idx_supplier` (`supplier_id`),
    INDEX `idx_period` (`period_start`, `period_end`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='供应商绩效分析表';

-- ========================================
-- 3. 产品与分类管理
-- ========================================

-- 产品分类表
CREATE TABLE `categories` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `category_code` VARCHAR(50) UNIQUE NOT NULL,
    `name` JSON NOT NULL COMMENT '多语言名称',
    `description` JSON COMMENT '多语言描述',
    `parent_id` BIGINT UNSIGNED,
    `is_active` BOOLEAN DEFAULT TRUE,
    `sort_order` INT DEFAULT 0,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`parent_id`) REFERENCES `categories`(`id`) ON DELETE SET NULL,
    INDEX `idx_parent` (`parent_id`),
    INDEX `idx_active` (`is_active`),
    INDEX `idx_code` (`category_code`),
    INDEX `idx_sort` (`sort_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='产品分类表';

-- 产品表
CREATE TABLE `products` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `sku` VARCHAR(100) NOT NULL UNIQUE,
    `name` JSON NOT NULL COMMENT '多语言产品名称',
    `description` JSON COMMENT '多语言产品描述',
    `short_description` JSON COMMENT '多语言简短描述',
    `specifications` JSON COMMENT '规格参数（可包含多语言）',
    `meta_keywords` JSON COMMENT 'SEO关键词（多语言）',
    `meta_description` JSON COMMENT 'SEO描述（多语言）',
    `price` DECIMAL(10,2) NOT NULL,
    `cost_price` DECIMAL(10,2),
    `stock` INT NOT NULL DEFAULT 0,
    `min_stock` INT DEFAULT 0,
    `unit` JSON DEFAULT ('{"zh-CN": "件", "en-US": "Piece"}'),
    `weight` DECIMAL(8,2),
    `dimensions` VARCHAR(100),
    `category_id` BIGINT UNSIGNED,
    `supplier_id` BIGINT UNSIGNED,
    `is_active` BOOLEAN DEFAULT TRUE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`category_id`) REFERENCES `categories`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`supplier_id`) REFERENCES `companies`(`id`) ON DELETE SET NULL,
    INDEX `idx_sku` (`sku`),
    INDEX `idx_category` (`category_id`),
    INDEX `idx_supplier` (`supplier_id`),
    INDEX `idx_active` (`is_active`),
    INDEX `idx_price` (`price`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='产品表';

-- 产品图片表
CREATE TABLE `product_images` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `product_id` BIGINT UNSIGNED,
    `image_url` VARCHAR(500) NOT NULL,
    `alt_text` VARCHAR(255),
    `is_primary` BOOLEAN DEFAULT FALSE,
    `sort_order` INT DEFAULT 0,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`product_id`) REFERENCES `products`(`id`) ON DELETE CASCADE,
    INDEX `idx_product` (`product_id`),
    INDEX `idx_primary` (`is_primary`),
    INDEX `idx_sort` (`sort_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='产品图片表';

-- ========================================
-- 4. 订单管理
-- ========================================

-- 订单表
CREATE TABLE `orders` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `order_number` VARCHAR(50) NOT NULL UNIQUE,
    `company_id` BIGINT UNSIGNED COMMENT '采购企业',
    `supplier_id` BIGINT UNSIGNED COMMENT '供应商企业',
    `user_id` BIGINT UNSIGNED COMMENT '下单用户',
    `order_type` ENUM('standard', 'urgent', 'scheduled') DEFAULT 'standard',
    `status` ENUM('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
    `subtotal_amount` DECIMAL(15,2) COMMENT '小计金额',
    `tax_amount` DECIMAL(15,2) DEFAULT 0 COMMENT '税费',
    `shipping_fee` DECIMAL(15,2) DEFAULT 0 COMMENT '运费',
    `total_amount` DECIMAL(15,2) NOT NULL COMMENT '总金额',
    `payment_terms` INT DEFAULT 30 COMMENT '账期天数',
    `expected_delivery_date` DATE COMMENT '期望交付日期',
    `project_name` VARCHAR(255) COMMENT '项目名称',
    `project_address` TEXT COMMENT '项目地址',
    `shipping_address` TEXT COMMENT '配送地址',
    `contact_person` VARCHAR(100) COMMENT '联系人',
    `contact_phone` VARCHAR(20) COMMENT '联系电话',
    `approval_status` ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    `approver_id` BIGINT UNSIGNED COMMENT '审批人',
    `approved_at` TIMESTAMP NULL,
    `notes` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`),
    FOREIGN KEY (`supplier_id`) REFERENCES `companies`(`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`),
    FOREIGN KEY (`approver_id`) REFERENCES `users`(`id`),
    INDEX `idx_order_number` (`order_number`),
    INDEX `idx_company` (`company_id`),
    INDEX `idx_supplier` (`supplier_id`),
    INDEX `idx_user` (`user_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单表';

-- 订单项表
CREATE TABLE `order_items` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `order_id` BIGINT UNSIGNED,
    `product_id` BIGINT UNSIGNED,
    `quantity` INT NOT NULL,
    `unit_price` DECIMAL(10,2) NOT NULL,
    `total_price` DECIMAL(12,2) NOT NULL,
    `specifications` TEXT COMMENT '特殊规格要求',
    `notes` TEXT COMMENT '备注',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`order_id`) REFERENCES `orders`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`product_id`) REFERENCES `products`(`id`) ON DELETE CASCADE,
    INDEX `idx_order` (`order_id`),
    INDEX `idx_product` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单项表';

-- ========================================
-- 5. 询价比价系统
-- ========================================

-- 询价单表
CREATE TABLE `quotation_requests` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `request_number` VARCHAR(50) UNIQUE,
    `company_id` BIGINT UNSIGNED,
    `requestor_id` BIGINT UNSIGNED COMMENT '询价人',
    `title` VARCHAR(255),
    `description` TEXT,
    `expected_delivery_date` DATE,
    `delivery_address` TEXT,
    `status` ENUM('draft', 'published', 'closed') DEFAULT 'draft',
    `deadline` TIMESTAMP COMMENT '报价截止时间',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`),
    FOREIGN KEY (`requestor_id`) REFERENCES `users`(`id`),
    INDEX `idx_company` (`company_id`),
    INDEX `idx_requestor` (`requestor_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_deadline` (`deadline`),
    INDEX `idx_request_number` (`request_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='询价单表';

-- 询价单明细表
CREATE TABLE `quotation_request_items` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `request_id` BIGINT UNSIGNED,
    `product_id` BIGINT UNSIGNED,
    `quantity` INT NOT NULL,
    `specifications` TEXT COMMENT '规格要求',
    `max_price` DECIMAL(10,2) COMMENT '预算上限',
    `notes` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`request_id`) REFERENCES `quotation_requests`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`product_id`) REFERENCES `products`(`id`),
    INDEX `idx_request` (`request_id`),
    INDEX `idx_product` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='询价单明细表';

-- 报价单表
CREATE TABLE `quotations` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `quotation_number` VARCHAR(50) UNIQUE,
    `request_id` BIGINT UNSIGNED,
    `supplier_id` BIGINT UNSIGNED,
    `quoter_id` BIGINT UNSIGNED COMMENT '报价人',
    `total_amount` DECIMAL(15,2),
    `valid_until` DATE COMMENT '报价有效期',
    `delivery_days` INT COMMENT '交付天数',
    `payment_terms` INT COMMENT '付款条款',
    `warranty_period` INT COMMENT '质保期',
    `notes` TEXT,
    `status` ENUM('draft', 'submitted', 'selected', 'rejected') DEFAULT 'draft',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`request_id`) REFERENCES `quotation_requests`(`id`),
    FOREIGN KEY (`supplier_id`) REFERENCES `companies`(`id`),
    FOREIGN KEY (`quoter_id`) REFERENCES `users`(`id`),
    INDEX `idx_request` (`request_id`),
    INDEX `idx_supplier` (`supplier_id`),
    INDEX `idx_quoter` (`quoter_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_quotation_number` (`quotation_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='报价单表';

-- 报价单明细表
CREATE TABLE `quotation_items` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `quotation_id` BIGINT UNSIGNED,
    `request_item_id` BIGINT UNSIGNED COMMENT '对应询价项',
    `product_id` BIGINT UNSIGNED,
    `quantity` INT NOT NULL,
    `unit_price` DECIMAL(10,2) NOT NULL,
    `total_price` DECIMAL(12,2) NOT NULL,
    `specifications` TEXT COMMENT '供应商规格说明',
    `brand` VARCHAR(100) COMMENT '品牌',
    `model` VARCHAR(100) COMMENT '型号',
    `delivery_days` INT COMMENT '交付天数',
    `notes` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`quotation_id`) REFERENCES `quotations`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`request_item_id`) REFERENCES `quotation_request_items`(`id`),
    FOREIGN KEY (`product_id`) REFERENCES `products`(`id`),
    INDEX `idx_quotation` (`quotation_id`),
    INDEX `idx_request_item` (`request_item_id`),
    INDEX `idx_product` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='报价单明细表';

-- ========================================
-- 6. 财务结算系统
-- ========================================

-- 账期管理表
CREATE TABLE `payment_terms` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `company_id` BIGINT UNSIGNED,
    `supplier_id` BIGINT UNSIGNED,
    `payment_days` INT DEFAULT 30 COMMENT '账期天数',
    `credit_limit` DECIMAL(15,2),
    `used_credit` DECIMAL(15,2) DEFAULT 0,
    `overdue_amount` DECIMAL(15,2) DEFAULT 0,
    `is_active` BOOLEAN DEFAULT TRUE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`),
    FOREIGN KEY (`supplier_id`) REFERENCES `suppliers`(`id`),
    INDEX `idx_company` (`company_id`),
    INDEX `idx_supplier` (`supplier_id`),
    INDEX `idx_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='账期管理表';

-- 对账单表
CREATE TABLE `settlement_statements` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `statement_number` VARCHAR(50) UNIQUE,
    `company_id` BIGINT UNSIGNED,
    `supplier_id` BIGINT UNSIGNED,
    `period_start` DATE,
    `period_end` DATE,
    `total_amount` DECIMAL(15,2),
    `paid_amount` DECIMAL(15,2) DEFAULT 0,
    `pending_amount` DECIMAL(15,2),
    `status` ENUM('draft', 'confirmed', 'paid', 'disputed') DEFAULT 'draft',
    `due_date` DATE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`),
    FOREIGN KEY (`supplier_id`) REFERENCES `suppliers`(`id`),
    INDEX `idx_statement_number` (`statement_number`),
    INDEX `idx_company` (`company_id`),
    INDEX `idx_supplier` (`supplier_id`),
    INDEX `idx_due_date` (`due_date`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对账单表';

-- 发票管理表
CREATE TABLE `invoices` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `invoice_number` VARCHAR(50) UNIQUE,
    `invoice_type` ENUM('VAT_special', 'VAT_general', 'receipt') DEFAULT 'VAT_general',
    `order_id` BIGINT UNSIGNED,
    `company_id` BIGINT UNSIGNED,
    `supplier_id` BIGINT UNSIGNED,
    `amount` DECIMAL(15,2),
    `tax_amount` DECIMAL(15,2),
    `total_amount` DECIMAL(15,2),
    `invoice_date` DATE,
    `issue_status` ENUM('pending', 'issued', 'received', 'verified') DEFAULT 'pending',
    `invoice_file_url` VARCHAR(500),
    `notes` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`order_id`) REFERENCES `orders`(`id`),
    FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`),
    FOREIGN KEY (`supplier_id`) REFERENCES `suppliers`(`id`),
    INDEX `idx_invoice_number` (`invoice_number`),
    INDEX `idx_order` (`order_id`),
    INDEX `idx_company` (`company_id`),
    INDEX `idx_supplier` (`supplier_id`),
    INDEX `idx_status` (`issue_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='发票管理表';

-- 支付相关表
CREATE TABLE `payments` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `payment_number` VARCHAR(50) UNIQUE COMMENT '支付单号',
    `order_id` BIGINT UNSIGNED,
    `company_id` BIGINT UNSIGNED,
    `supplier_id` BIGINT UNSIGNED,
    `user_id` BIGINT UNSIGNED,
    `amount` DECIMAL(15,2) NOT NULL,
    `currency` VARCHAR(3) DEFAULT 'CNY',
    `payment_method` ENUM('stripe', 'alipay', 'wechat', 'bank_transfer', 'credit') DEFAULT 'stripe',
    `stripe_payment_intent_id` VARCHAR(255),
    `alipay_trade_no` VARCHAR(100),
    `wechat_transaction_id` VARCHAR(100),
    `status` ENUM('pending', 'processing', 'completed', 'failed', 'cancelled', 'refunded') DEFAULT 'pending',
    `payment_date` TIMESTAMP NULL,
    `due_date` DATE,
    `metadata` JSON COMMENT '支付相关元数据',
    `notes` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`order_id`) REFERENCES `orders`(`id`),
    FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`),
    FOREIGN KEY (`supplier_id`) REFERENCES `companies`(`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`),
    INDEX `idx_payment_number` (`payment_number`),
    INDEX `idx_order` (`order_id`),
    INDEX `idx_company` (`company_id`),
    INDEX `idx_supplier` (`supplier_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_payment_method` (`payment_method`),
    INDEX `idx_stripe_intent` (`stripe_payment_intent_id`),
    INDEX `idx_due_date` (`due_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='支付相关表';

-- ========================================
-- 7. 物流配送系统
-- ========================================

-- 物流配送表
CREATE TABLE `shipments` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `shipment_number` VARCHAR(50) UNIQUE,
    `order_id` BIGINT UNSIGNED,
    `logistics_provider` VARCHAR(100) COMMENT '物流商',
    `tracking_number` VARCHAR(100) COMMENT '物流单号',
    `shipment_type` ENUM('direct', 'warehouse', 'pickup') DEFAULT 'direct',
    `departure_address` TEXT COMMENT '发货地址',
    `delivery_address` TEXT COMMENT '收货地址',
    `contact_person` VARCHAR(100) COMMENT '收货联系人',
    `contact_phone` VARCHAR(20) COMMENT '收货电话',
    `estimated_delivery` DATETIME COMMENT '预计送达时间',
    `actual_delivery` DATETIME NULL COMMENT '实际送达时间',
    `status` ENUM('preparing', 'shipped', 'in_transit', 'delivered', 'exception') DEFAULT 'preparing',
    `delivery_fee` DECIMAL(10,2) COMMENT '配送费用',
    `weight` DECIMAL(8,2) COMMENT '重量',
    `volume` DECIMAL(8,2) COMMENT '体积',
    `special_requirements` TEXT COMMENT '特殊要求',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`order_id`) REFERENCES `orders`(`id`),
    INDEX `idx_order` (`order_id`),
    INDEX `idx_tracking` (`tracking_number`),
    INDEX `idx_status` (`status`),
    INDEX `idx_shipment_number` (`shipment_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='物流配送表';

-- 配送轨迹表
CREATE TABLE `shipment_tracking` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `shipment_id` BIGINT UNSIGNED,
    `tracking_time` TIMESTAMP,
    `location` VARCHAR(255),
    `status` VARCHAR(100),
    `description` TEXT,
    `operator` VARCHAR(100) COMMENT '操作员',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`shipment_id`) REFERENCES `shipments`(`id`) ON DELETE CASCADE,
    INDEX `idx_shipment` (`shipment_id`),
    INDEX `idx_time` (`tracking_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='配送轨迹表';

-- ========================================
-- 8. 审计与监控
-- ========================================

-- 业务操作审计表
CREATE TABLE `audit_logs` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `user_id` BIGINT UNSIGNED,
    `company_id` BIGINT UNSIGNED,
    `action_type` VARCHAR(50) COMMENT 'create_order, approve_payment',
    `resource_type` VARCHAR(50) COMMENT 'order, payment, user',
    `resource_id` BIGINT UNSIGNED,
    `old_values` JSON COMMENT '变更前数据',
    `new_values` JSON COMMENT '变更后数据',
    `ip_address` VARCHAR(45),
    `user_agent` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`),
    FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`),
    INDEX `idx_user` (`user_id`),
    INDEX `idx_company` (`company_id`),
    INDEX `idx_resource` (`resource_type`, `resource_id`),
    INDEX `idx_action` (`action_type`),
    INDEX `idx_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='业务操作审计表';

-- 敏感数据加密存储
CREATE TABLE `encrypted_business_data` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `company_id` BIGINT UNSIGNED,
    `data_type` ENUM('contract', 'bank_info', 'tax_cert') NOT NULL,
    `encrypted_content` LONGTEXT COMMENT 'AES加密存储',
    `encryption_key_id` VARCHAR(100),
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`),
    INDEX `idx_company` (`company_id`),
    INDEX `idx_data_type` (`data_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='敏感数据加密存储';

-- 系统性能监控表
CREATE TABLE `system_metrics` (
    `id` BIGINT UNSIGNED PRIMARY KEY,
    `metric_type` VARCHAR(50) COMMENT 'api_response_time, db_query_time',
    `metric_name` VARCHAR(100) COMMENT '/api/v1/products/search',
    `metric_value` DECIMAL(10,4) COMMENT '响应时间(秒)',
    `tags` JSON COMMENT '额外标签信息',
    `recorded_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_type` (`metric_type`),
    INDEX `idx_name` (`metric_name`),
    INDEX `idx_recorded` (`recorded_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统性能监控表';

-- ========================================
-- 9. 雪花算法配置表（可选）
-- ========================================

-- 雪花算法配置表
CREATE TABLE `snowflake_config` (
    `id` INT PRIMARY KEY DEFAULT 1,
    `datacenter_id` INT NOT NULL DEFAULT 1,
    `worker_id` INT NOT NULL DEFAULT 1,
    `epoch_timestamp` BIGINT NOT NULL DEFAULT 1704067200000,
    `last_timestamp` BIGINT NOT NULL DEFAULT 0,
    `sequence_number` INT NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='雪花算法配置表';

-- ========================================
-- 10. 复合索引优化
-- ========================================

-- 复合索引设计
CREATE INDEX `idx_orders_compound` ON `orders`(`company_id`, `status`, `created_at`);
CREATE INDEX `idx_products_compound` ON `products`(`category_id`, `is_active`, `price`);
CREATE INDEX `idx_settlement_compound` ON `settlement_statements`(`due_date`, `status`);

-- ========================================
-- 11. 初始化数据
-- ========================================

-- 插入初始雪花算法配置
INSERT INTO `snowflake_config` (`id`, `datacenter_id`, `worker_id`, `epoch_timestamp`) 
VALUES (1, 1, 1, 1704067200000);

-- 插入根分类
INSERT INTO `categories` (`id`, `category_code`, `name`, `description`, `parent_id`, `is_active`, `sort_order`) 
VALUES 
(1, 'BUILDING_MATERIALS', '{"zh-CN": "建筑材料", "en-US": "Building Materials"}', '{"zh-CN": "建筑工程用材料", "en-US": "Materials for construction"}', NULL, TRUE, 1),
(2, 'STEEL', '{"zh-CN": "钢材", "en-US": "Steel"}', '{"zh-CN": "各类钢材产品", "en-US": "Various steel products"}', 1, TRUE, 1),
(3, 'CEMENT', '{"zh-CN": "水泥", "en-US": "Cement"}', '{"zh-CN": "水泥及相关产品", "en-US": "Cement and related products"}', 1, TRUE, 2);

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- 脚本执行完成提示
SELECT 'Database tigu_b2b has been created successfully!' as message;