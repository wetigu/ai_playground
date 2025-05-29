-- TiguB2B平台模拟数据填充脚本
-- 基于 tigusql.sql 数据库结构
-- 创建日期: 2025-05-29
-- 包含所有表的示例数据

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
USE `tigu_b2b`;

-- ========================================
-- 1. 清理现有数据（开发环境）
-- ========================================
DELETE FROM `video_interactions`;
DELETE FROM `video_analytics`;
DELETE FROM `video_chapters`;
DELETE FROM `product_videos`;
DELETE FROM `product_images`;
DELETE FROM `shipment_tracking`;
DELETE FROM `shipments`;
DELETE FROM `payments`;
DELETE FROM `invoices`;
DELETE FROM `settlement_statements`;
DELETE FROM `payment_terms`;
DELETE FROM `quotation_items`;
DELETE FROM `quotations`;
DELETE FROM `quotation_request_items`;
DELETE FROM `quotation_requests`;
DELETE FROM `order_items`;
DELETE FROM `orders`;
DELETE FROM `products`;
DELETE FROM `categories`;
DELETE FROM `supplier_performance`;
DELETE FROM `suppliers`;
DELETE FROM `user_company_roles`;
DELETE FROM `user_sessions`;
DELETE FROM `users`;
DELETE FROM `companies`;
DELETE FROM `audit_logs`;
DELETE FROM `encrypted_business_data`;
DELETE FROM `system_metrics`;

-- ========================================
-- 2. 插入企业数据
-- ========================================

-- 插入企业信息
INSERT INTO `companies` (`id`, `company_code`, `company_name`, `company_type`, `business_license`, `tax_number`, `legal_representative`, `registered_address`, `business_scope`, `credit_rating`, `credit_limit`, `payment_terms`, `is_verified`) VALUES
(1001, 'COMP001', '{"zh-CN": "多伦多建材集团有限公司", "en-US": "Toronto Building Materials Group Inc."}', 'supplier', 'ON-123456789', 'BN123456789RT0001', 'John Zhang', '1000 Bay Street, Toronto, ON M5S 3A1', '{"zh-CN": "建筑材料批发，钢材销售", "en-US": "Building materials wholesale, steel sales"}', 'AA', 5000000.00, 45, true),
(1002, 'COMP002', '{"zh-CN": "温哥华钢铁贸易有限公司", "en-US": "Vancouver Steel Trading Ltd."}', 'supplier', 'BC-234567890', 'BN234567890RT0001', 'Li Gangqiang', '888 Burrard Street, Vancouver, BC V6Z 1X9', '{"zh-CN": "钢材贸易，金属制品销售", "en-US": "Steel trading, metal products sales"}', 'A', 3000000.00, 30, true),
(1003, 'COMP003', '{"zh-CN": "蒙特利尔水泥制品厂", "en-US": "Montreal Cement Products Factory"}', 'supplier', 'QC-345678901', 'BN345678901RT0001', 'Wang Shuini', '168 Industrial Blvd, Montreal, QC H4T 1Z2', '{"zh-CN": "水泥制品生产销售", "en-US": "Cement products manufacturing and sales"}', 'A', 2000000.00, 30, true),
(2001, 'DECO001', '{"zh-CN": "东方装饰工程有限公司", "en-US": "Oriental Decoration Engineering Inc."}', 'buyer', 'ON-456789012', 'BN456789012RT0001', 'Chen Zhuangxiu', '500 King Street West, Toronto, ON M5V 1L7', '{"zh-CN": "建筑装饰工程设计施工", "en-US": "Architectural decoration engineering design and construction"}', 'AA', 0, 30, true),
(2002, 'DECO002', '{"zh-CN": "华美建筑装饰公司", "en-US": "Huamei Construction Decoration Company"}', 'buyer', 'BC-567890123', 'BN567890123RT0001', 'Liu Huamei', '1055 West Georgia Street, Vancouver, BC V6E 3P3', '{"zh-CN": "室内外装饰设计施工", "en-US": "Indoor and outdoor decoration design and construction"}', 'A', 0, 15, true),
(2003, 'PROJ001', '{"zh-CN": "龙城房地产开发有限公司", "en-US": "Longcheng Real Estate Development Corp."}', 'buyer', 'AB-678901234', 'BN678901234RT0001', 'Zhao Longcheng', '250 6 Ave SW, Calgary, AB T2P 3H7', '{"zh-CN": "房地产开发经营", "en-US": "Real estate development and operation"}', 'AAA', 0, 45, true);

-- ========================================
-- 3. 插入用户数据
-- ========================================

-- 插入用户信息
INSERT INTO `users` (`id`, `user_code`, `email`, `hashed_password`, `full_name`, `phone`, `auth_provider`, `is_active`, `is_superuser`, `is_verified`, `email_verified_at`, `default_company_id`) VALUES
(10001, 'U001', 'admin@tigu.com', '$2b$12$LQv3c1yqBwkVsvGOB7srCON4fQpaj5mQq5oL5sDi.w8kB8zF9Q2Qe', 'System Administrator', '+1-416-555-0001', 'email', true, true, true, NOW(), NULL),
(10002, 'U002', 'john.zhang@toronto-materials.com', '$2b$12$LQv3c1yqBwkVsvGOB7srCON4fQpaj5mQq5oL5sDi.w8kB8zF9Q2Qe', 'John Zhang', '+1-416-555-0002', 'email', true, false, true, NOW(), 1001),
(10003, 'U003', 'li.gangqiang@vancouver-steel.com', '$2b$12$LQv3c1yqBwkVsvGOB7srCON4fQpaj5mQq5oL5sDi.w8kB8zF9Q2Qe', 'Li Gangqiang', '+1-604-555-0003', 'email', true, false, true, NOW(), 1002),
(10004, 'U004', 'wang.shuini@montreal-cement.com', '$2b$12$LQv3c1yqBwkVsvGOB7srCON4fQpaj5mQq5oL5sDi.w8kB8zF9Q2Qe', 'Wang Shuini', '+1-514-555-0004', 'email', true, false, true, NOW(), 1003),
(10005, 'U005', 'chen.zhuangxiu@oriental-deco.com', '$2b$12$LQv3c1yqBwkVsvGOB7srCON4fQpaj5mQq5oL5sDi.w8kB8zF9Q2Qe', 'Chen Zhuangxiu', '+1-416-555-0005', 'email', true, false, true, NOW(), 2001),
(10006, 'U006', 'liu.huamei@huamei-deco.com', '$2b$12$LQv3c1yqBwkVsvGOB7srCON4fQpaj5mQq5oL5sDi.w8kB8zF9Q2Qe', 'Liu Huamei', '+1-604-555-0006', 'email', true, false, true, NOW(), 2002),
(10007, 'U007', 'zhao.longcheng@longcheng-re.com', '$2b$12$LQv3c1yqBwkVsvGOB7srCON4fQpaj5mQq5oL5sDi.w8kB8zF9Q2Qe', 'Zhao Longcheng', '+1-403-555-0007', 'email', true, false, true, NOW(), 2003),
(10008, 'U008', 'sales@toronto-materials.com', '$2b$12$LQv3c1yqBwkVsvGOB7srCON4fQpaj5mQq5oL5sDi.w8kB8zF9Q2Qe', 'Toronto Materials Sales', '+1-416-555-0008', 'email', true, false, true, NOW(), 1001),
(10009, 'U009', 'procurement@oriental-deco.com', '$2b$12$LQv3c1yqBwkVsvGOB7srCON4fQpaj5mQq5oL5sDi.w8kB8zF9Q2Qe', 'Oriental Decoration Procurement', '+1-416-555-0009', 'email', true, false, true, NOW(), 2001),
(10010, 'U010', 'finance@huamei-deco.com', '$2b$12$LQv3c1yqBwkVsvGOB7srCON4fQpaj5mQq5oL5sDi.w8kB8zF9Q2Qe', 'Huamei Finance', '+1-604-555-0010', 'email', true, false, true, NOW(), 2002);

-- ========================================
-- 4. 插入用户企业关联
-- ========================================

INSERT INTO `user_company_roles` (`id`, `user_id`, `company_id`, `role`, `is_active`) VALUES
(1, 10002, 1001, 'admin', true),
(2, 10003, 1002, 'admin', true),
(3, 10004, 1003, 'admin', true),
(4, 10005, 2001, 'admin', true),
(5, 10006, 2002, 'admin', true),
(6, 10007, 2003, 'admin', true),
(7, 10008, 1001, 'purchaser', true),
(8, 10009, 2001, 'purchaser', true),
(9, 10010, 2002, 'finance', true);

-- ========================================
-- 5. 插入供应商信息
-- ========================================

INSERT INTO `suppliers` (`id`, `company_id`, `supplier_code`, `supplier_tier`, `main_categories`, `warehouse_locations`, `delivery_capabilities`, `min_order_amount`, `lead_time_days`, `quality_rating`, `service_rating`, `cooperation_years`, `is_preferred`) VALUES
(1, 1001, 'SUP001', 'tier1', '["钢材", "建筑材料", "金属制品"]', '["Toronto Downtown Warehouse", "Mississauga Industrial Park"]', '["GTA Delivery", "Canada-wide Logistics", "Port Direct Ship"]', 10000.00, 3, 4.5, 4.3, 5, true),
(2, 1002, 'SUP002', 'tier1', '["钢材", "有色金属", "管材"]', '["Vancouver Port Warehouse", "Surrey Distribution Center"]', '["Lower Mainland Delivery", "Western Canada Logistics"]', 15000.00, 5, 4.2, 4.1, 3, true),
(3, 1003, 'SUP003', 'tier2', '["水泥", "混凝土", "建筑砂浆"]', '["Montreal Factory", "Laval Distribution Center"]', '["Quebec Province Delivery", "Eastern Canada Logistics"]', 5000.00, 7, 4.0, 3.8, 2, false);

-- ========================================
-- 6. 插入产品分类（扩展）
-- ========================================

INSERT INTO `categories` (`id`, `category_code`, `name`, `description`, `parent_id`, `is_active`, `sort_order`) VALUES
(4, 'REBAR', '{"zh-CN": "螺纹钢", "en-US": "Rebar"}', '{"zh-CN": "建筑用螺纹钢筋", "en-US": "Construction rebar"}', 2, true, 1),
(5, 'PIPE', '{"zh-CN": "钢管", "en-US": "Steel Pipe"}', '{"zh-CN": "各类钢管产品", "en-US": "Various steel pipe products"}', 2, true, 2),
(6, 'CEMENT_GENERAL', '{"zh-CN": "通用水泥", "en-US": "General Purpose Cement"}', '{"zh-CN": "通用硅酸盐水泥", "en-US": "General Purpose Portland Cement"}', 3, true, 1),
(7, 'CEMENT_HIGH_EARLY', '{"zh-CN": "早强水泥", "en-US": "High Early Strength Cement"}', '{"zh-CN": "高早期强度硅酸盐水泥", "en-US": "High Early Strength Portland Cement"}', 3, true, 2);

-- ========================================
-- 7. 插入产品数据
-- ========================================

INSERT INTO `products` (`id`, `sku`, `name`, `description`, `short_description`, `specifications`, `price`, `cost_price`, `stock`, `min_stock`, `unit`, `weight`, `dimensions`, `category_id`, `supplier_id`, `is_active`) VALUES
(100001, 'REBAR-GRADE400-12', '{"zh-CN": "Grade 400 螺纹钢筋 #4", "en-US": "Grade 400 Rebar #4"}', '{"zh-CN": "Grade 400等级螺纹钢筋，#4规格，广泛用于建筑结构", "en-US": "Grade 400 rebar, #4 size, widely used in building structures"}', '{"zh-CN": "#4 Grade 400螺纹钢", "en-US": "#4 Grade 400 Rebar"}', '{"material": "Grade 400", "size": "#4 (12.7mm)", "length": "6m", "standard": "CSA G30.18"}', 4200.00, 3800.00, 5000, 500, '{"zh-CN": "吨", "en-US": "Tonne"}', 888.00, '6000mm×12.7mm×12.7mm', 4, 1001, true),
(100002, 'REBAR-GRADE400-16', '{"zh-CN": "Grade 400 螺纹钢筋 #5", "en-US": "Grade 400 Rebar #5"}', '{"zh-CN": "Grade 400等级螺纹钢筋，#5规格，适用于中型建筑工程", "en-US": "Grade 400 rebar, #5 size, suitable for medium construction projects"}', '{"zh-CN": "#5 Grade 400螺纹钢", "en-US": "#5 Grade 400 Rebar"}', '{"material": "Grade 400", "size": "#5 (15.9mm)", "length": "6m", "standard": "CSA G30.18"}', 4250.00, 3850.00, 3000, 300, '{"zh-CN": "吨", "en-US": "Tonne"}', 1578.00, '6000mm×15.9mm×15.9mm', 4, 1001, true),
(100003, 'PIPE-SEAMLESS-159', '{"zh-CN": "无缝钢管 6\\\" SCH40", "en-US": "Seamless Steel Pipe 6\\\" SCH40"}', '{"zh-CN": "无缝钢管，6英寸SCH40，用于流体输送", "en-US": "Seamless steel pipe, 6\\\" SCH40, for fluid transmission"}', '{"zh-CN": "6\\\" SCH40无缝钢管", "en-US": "6\\\" SCH40 Seamless Pipe"}', '{"material": "A106 Grade B", "size": "6\\\" (159mm)", "schedule": "SCH40", "length": "6m", "standard": "ASTM A106"}', 5800.00, 5200.00, 2000, 200, '{"zh-CN": "吨", "en-US": "Tonne"}', 2240.00, '6000mm×159mm×7.1mm', 5, 1002, true),
(100004, 'CEMENT-GP-50KG', '{"zh-CN": "通用硅酸盐水泥 50kg", "en-US": "General Purpose Portland Cement 50kg"}', '{"zh-CN": "通用硅酸盐水泥，50kg包装，适用于一般建筑工程", "en-US": "General purpose Portland cement, 50kg package, suitable for general construction"}', '{"zh-CN": "通用水泥", "en-US": "GP Cement"}', '{"brand": "Lafarge", "type": "General Purpose", "package": "50kg bag", "standard": "CSA A3001"}', 480.00, 420.00, 10000, 1000, '{"zh-CN": "吨", "en-US": "Tonne"}', 50.00, '500mm×350mm×120mm', 6, 1003, true),
(100005, 'CEMENT-HE-50KG', '{"zh-CN": "早强硅酸盐水泥 50kg", "en-US": "High Early Strength Portland Cement 50kg"}', '{"zh-CN": "高早期强度硅酸盐水泥，50kg包装，高强度等级", "en-US": "High early strength Portland cement, 50kg package, high strength grade"}', '{"zh-CN": "早强水泥", "en-US": "HE Cement"}', '{"brand": "Lafarge", "type": "High Early Strength", "package": "50kg bag", "standard": "CSA A3001"}', 520.00, 460.00, 8000, 800, '{"zh-CN": "吨", "en-US": "Tonne"}', 50.00, '500mm×350mm×120mm', 7, 1003, true);

-- ========================================
-- 8. 插入产品图片
-- ========================================

INSERT INTO `product_images` (`id`, `product_id`, `image_url`, `alt_text`, `is_primary`, `sort_order`) VALUES
(1, 100001, 'https://cdn.tigu.com/products/rebar-grade400-12-main.jpg', 'Grade 400 Rebar #4 Main Image', true, 1),
(2, 100001, 'https://cdn.tigu.com/products/rebar-grade400-12-detail.jpg', 'Grade 400 Rebar #4 Detail Image', false, 2),
(3, 100002, 'https://cdn.tigu.com/products/rebar-grade400-16-main.jpg', 'Grade 400 Rebar #5 Main Image', true, 1),
(4, 100003, 'https://cdn.tigu.com/products/pipe-seamless-6inch-main.jpg', 'Seamless Steel Pipe 6\\" Main Image', true, 1),
(5, 100004, 'https://cdn.tigu.com/products/cement-gp-main.jpg', 'Lafarge GP Cement Main Image', true, 1),
(6, 100005, 'https://cdn.tigu.com/products/cement-he-main.jpg', 'Lafarge HE Cement Main Image', true, 1);

-- ========================================
-- 9. 插入产品视频
-- ========================================

INSERT INTO `product_videos` (`id`, `product_id`, `video_url`, `thumbnail_url`, `title`, `description`, `video_type`, `duration`, `file_size`, `is_primary`, `sort_order`, `view_count`, `cdn_url`, `upload_status`) VALUES
(1, 100001, 'https://video.tigu.com/products/rebar-demo.mp4', 'https://cdn.tigu.com/thumbnails/rebar-demo.jpg', '{"zh-CN": "螺纹钢产品介绍", "en-US": "Rebar Product Introduction"}', '{"zh-CN": "详细介绍Grade 400螺纹钢的特性和应用", "en-US": "Detailed introduction to Grade 400 rebar characteristics and applications"}', 'product_demo', 180, 52428800, true, 1, 1250, 'https://cdn.tigu.com/videos/rebar-demo.mp4', 'ready'),
(2, 100003, 'https://video.tigu.com/products/pipe-installation.mp4', 'https://cdn.tigu.com/thumbnails/pipe-installation.jpg', '{"zh-CN": "钢管安装指南", "en-US": "Steel Pipe Installation Guide"}', '{"zh-CN": "无缝钢管的正确安装方法演示", "en-US": "Demonstration of proper seamless steel pipe installation methods"}', 'installation', 300, 78643200, true, 1, 890, 'https://cdn.tigu.com/videos/pipe-installation.mp4', 'ready'),
(3, 100004, 'https://video.tigu.com/products/cement-factory-tour.mp4', 'https://cdn.tigu.com/thumbnails/cement-factory.jpg', '{"zh-CN": "Lafarge水泥工厂参观", "en-US": "Lafarge Cement Factory Tour"}', '{"zh-CN": "Lafarge水泥生产工厂实地参观", "en-US": "On-site tour of Lafarge cement production factory"}', 'factory_tour', 420, 125829120, false, 2, 2100, 'https://cdn.tigu.com/videos/cement-factory-tour.mp4', 'ready');

-- ========================================
-- 10. 插入视频章节
-- ========================================

INSERT INTO `video_chapters` (`id`, `video_id`, `chapter_title`, `start_time`, `end_time`, `chapter_type`, `sort_order`) VALUES
(1, 1, '{"zh-CN": "产品概述", "en-US": "Product Overview"}', 0, 45, 'intro', 1),
(2, 1, '{"zh-CN": "技术规格", "en-US": "Technical Specifications"}', 45, 120, 'features', 2),
(3, 1, '{"zh-CN": "应用场景", "en-US": "Application Scenarios"}', 120, 180, 'usage', 3),
(4, 2, '{"zh-CN": "安装准备", "en-US": "Installation Preparation"}', 0, 60, 'intro', 1),
(5, 2, '{"zh-CN": "安装步骤", "en-US": "Installation Steps"}', 60, 240, 'installation', 2),
(6, 2, '{"zh-CN": "安全注意事项", "en-US": "Safety Precautions"}', 240, 300, 'safety', 3);

-- ========================================
-- 11. 插入订单数据
-- ========================================

INSERT INTO `orders` (`id`, `order_number`, `company_id`, `supplier_id`, `user_id`, `order_type`, `status`, `subtotal_amount`, `tax_amount`, `shipping_fee`, `total_amount`, `payment_terms`, `expected_delivery_date`, `project_name`, `project_address`, `shipping_address`, `contact_person`, `contact_phone`, `approval_status`, `approver_id`, `approved_at`) VALUES
(200001, 'ORD-2024-001', 2001, 1001, 10005, 'standard', 'confirmed', 84000.00, 10920.00, 2000.00, 96920.00, 30, '2024-02-15', 'Oriental Plaza Tower A Renovation', '100 King Street East, Toronto, ON M5C 1G6', '100 King Street East Construction Site, Toronto, ON', 'Chen Zhuangxiu', '+1-416-555-0005', 'approved', 10005, NOW()),
(200002, 'ORD-2024-002', 2002, 1002, 10006, 'urgent', 'processing', 58000.00, 7540.00, 1500.00, 67040.00, 15, '2024-02-10', 'Huamei Tower Steel Structure Project', '200 Burrard Street, Vancouver, BC V6C 3L6', '200 Burrard Street Construction Site, Vancouver, BC', 'Liu Huamei', '+1-604-555-0006', 'approved', 10006, NOW()),
(200003, 'ORD-2024-003', 2003, 1003, 10007, 'standard', 'shipped', 24000.00, 3120.00, 800.00, 27920.00, 45, '2024-02-20', 'Longcheng Gardens Foundation Project', '300 6 Ave SW, Calgary, AB T2P 3C4', 'Longcheng Gardens Construction Site, Calgary, AB', 'Zhao Longcheng', '+1-403-555-0007', 'approved', 10007, NOW());

-- ========================================
-- 12. 插入订单项数据
-- ========================================

INSERT INTO `order_items` (`id`, `order_id`, `product_id`, `quantity`, `unit_price`, `total_price`, `specifications`, `notes`) VALUES
(1, 200001, 100001, 20, 4200.00, 84000.00, '6m length, requires mill test certificate', 'Project urgent, please prioritize'),
(2, 200002, 100003, 10, 5800.00, 58000.00, '6m length, requires NDE test report', 'Steel structure main beam piping'),
(3, 200003, 100004, 50, 480.00, 24000.00, '50kg bags, requires quality test report', 'Foundation concrete use');

-- ========================================
-- 13. 插入询价单数据
-- ========================================

INSERT INTO `quotation_requests` (`id`, `request_number`, `company_id`, `requestor_id`, `title`, `description`, `expected_delivery_date`, `delivery_address`, `status`, `deadline`) VALUES
(300001, 'RFQ-2024-001', 2001, 10009, 'Oriental Tower Building Materials RFQ', 'Building materials procurement for Oriental Tower project, including steel and cement', '2024-03-01', '500 King Street West, Toronto, ON M5V 1L7', 'published', '2024-01-25 18:00:00'),
(300002, 'RFQ-2024-002', 2002, 10006, 'Huamei Project Phase 2 Materials RFQ', 'Various building materials RFQ for Huamei project phase 2', '2024-03-15', '1055 West Georgia Street, Vancouver, BC V6E 3P3', 'published', '2024-01-28 17:00:00');

INSERT INTO `quotation_request_items` (`id`, `request_id`, `product_id`, `quantity`, `specifications`, `max_price`, `notes`) VALUES
(1, 300001, 100001, 100, '6m length, Grade 400', 4300.00, 'Requires mill test certificate'),
(2, 300001, 100004, 200, '50kg bags, requires quality test report', 490.00, 'Batch delivery acceptable'),
(3, 300002, 100003, 50, '6m length, A106 Grade B material', 5900.00, 'Requires NDE testing');

-- ========================================
-- 14. 插入报价单数据
-- ========================================

INSERT INTO `quotations` (`id`, `quotation_number`, `request_id`, `supplier_id`, `quoter_id`, `total_amount`, `valid_until`, `delivery_days`, `payment_terms`, `warranty_period`, `status`) VALUES
(400001, 'QUO-2024-001', 300001, 1001, 10002, 516000.00, '2024-02-25', 7, 30, 12, 'submitted'),
(400002, 'QUO-2024-002', 300001, 1003, 10004, 96000.00, '2024-02-25', 10, 30, 6, 'submitted'),
(400003, 'QUO-2024-003', 300002, 1002, 10003, 295000.00, '2024-02-28', 5, 15, 12, 'submitted');

INSERT INTO `quotation_items` (`id`, `quotation_id`, `request_item_id`, `product_id`, `quantity`, `unit_price`, `total_price`, `specifications`, `brand`, `model`, `delivery_days`) VALUES
(1, 400001, 1, 100001, 100, 4200.00, 420000.00, '6m length, Grade 400, CSA G30.18 compliant', 'ArcelorMittal', 'Grade400-#4', 7),
(2, 400002, 2, 100004, 200, 480.00, 96000.00, '50kg bags, General Purpose Portland cement', 'Lafarge', 'GP Type 10', 10),
(3, 400003, 3, 100003, 50, 5900.00, 295000.00, '6m length, A106 Grade B seamless pipe, ASTM standard', 'Tenaris', 'A106GrB-6\\"SCH40', 5);

-- ========================================
-- 15. 插入支付数据
-- ========================================

INSERT INTO `payments` (`id`, `payment_number`, `order_id`, `company_id`, `supplier_id`, `user_id`, `amount`, `payment_method`, `status`, `payment_date`, `due_date`) VALUES
(500001, 'PAY-2024-001', 200001, 2001, 1001, 10005, 96920.00, 'bank_transfer', 'completed', '2024-01-20 14:30:00', '2024-02-19'),
(500002, 'PAY-2024-002', 200002, 2002, 1002, 10006, 67040.00, 'credit', 'pending', NULL, '2024-02-09'),
(500003, 'PAY-2024-003', 200003, 2003, 1003, 10007, 27920.00, 'bank_transfer', 'processing', NULL, '2024-03-05');

-- ========================================
-- 16. 插入物流数据
-- ========================================

INSERT INTO `shipments` (`id`, `shipment_number`, `order_id`, `logistics_provider`, `tracking_number`, `shipment_type`, `departure_address`, `delivery_address`, `contact_person`, `contact_phone`, `estimated_delivery`, `status`, `delivery_fee`, `weight`) VALUES
(600001, 'SHIP-2024-001', 200001, 'CN Rail Logistics', 'CNR2024012001', 'direct', '1000 Bay Street, Toronto, ON M5S 3A1', '100 King Street East Construction Site, Toronto, ON', 'Chen Zhuangxiu', '+1-416-555-0005', '2024-01-25 09:00:00', 'in_transit', 2000.00, 17760.00),
(600002, 'SHIP-2024-002', 200003, 'Purolator Freight', 'PUR2024012002', 'warehouse', '168 Industrial Blvd, Montreal, QC H4T 1Z2', 'Longcheng Gardens Construction Site, Calgary, AB', 'Zhao Longcheng', '+1-403-555-0007', '2024-01-28 10:00:00', 'delivered', 800.00, 2500.00);

INSERT INTO `shipment_tracking` (`id`, `shipment_id`, `tracking_time`, `location`, `status`, `description`, `operator`) VALUES
(1, 600001, '2024-01-22 08:00:00', 'Toronto Downtown Warehouse', 'Shipped', 'Goods dispatched from warehouse', 'Zhang Driver'),
(2, 600001, '2024-01-22 14:30:00', 'Toronto Highway 401', 'In Transit', 'Goods in transit', 'Li Driver'),
(3, 600001, '2024-01-23 09:15:00', 'King Street East Area', 'Out for Delivery', 'Goods arrived at destination area, preparing for delivery', 'Wang Driver'),
(4, 600002, '2024-01-26 10:00:00', 'Montreal Departure Point', 'Shipped', 'Goods loaded and shipped', 'Chen Driver'),
(5, 600002, '2024-01-27 15:30:00', 'Calgary Downtown', 'Delivered', 'Goods delivered and signed', 'Zhao Longcheng');

-- ========================================
-- 17. 插入发票数据
-- ========================================

INSERT INTO `invoices` (`id`, `invoice_number`, `invoice_type`, `order_id`, `company_id`, `supplier_id`, `amount`, `tax_amount`, `total_amount`, `invoice_date`, `issue_status`) VALUES
(700001, 'INV-2024-001', 'VAT_special', 200001, 2001, 1001, 84000.00, 10920.00, 94920.00, '2024-01-21', 'issued'),
(700002, 'INV-2024-002', 'VAT_general', 200003, 2003, 1003, 24000.00, 3120.00, 27120.00, '2024-01-27', 'received');

-- ========================================
-- 18. 插入视频分析数据
-- ========================================

INSERT INTO `video_analytics` (`id`, `video_id`, `user_id`, `company_id`, `action_type`, `watch_duration`, `watch_percentage`, `device_type`, `browser`) VALUES
(1, 1, 10005, 2001, 'view', 180, 100.00, 'Desktop', 'Chrome'),
(2, 1, 10006, 2002, 'view', 90, 50.00, 'Mobile', 'Safari'),
(3, 1, 10007, 2003, 'complete', 180, 100.00, 'Desktop', 'Firefox'),
(4, 2, 10005, 2001, 'view', 240, 80.00, 'Desktop', 'Chrome'),
(5, 3, 10009, 2001, 'view', 300, 71.43, 'Tablet', 'Chrome');

-- ========================================
-- 19. 插入视频互动数据
-- ========================================

INSERT INTO `video_interactions` (`id`, `video_id`, `user_id`, `interaction_type`, `content`, `timestamp_in_video`) VALUES
(1, 1, 10005, 'like', NULL, NULL),
(2, 1, 10006, 'comment', 'This rebar quality looks good, what about the pricing?', 120),
(3, 1, 10007, 'bookmark', NULL, NULL),
(4, 2, 10005, 'like', NULL, NULL),
(5, 2, 10005, 'comment', 'Installation steps are very clear, helpful for our project', 180);

-- ========================================
-- 20. 插入审计日志
-- ========================================

INSERT INTO `audit_logs` (`id`, `user_id`, `company_id`, `action_type`, `resource_type`, `resource_id`, `old_values`, `new_values`, `ip_address`) VALUES
(1, 10005, 2001, 'create_order', 'order', 200001, '{}', '{"order_number": "ORD-2024-001", "total_amount": 96920.00}', '192.168.1.100'),
(2, 10005, 2001, 'approve_order', 'order', 200001, '{"approval_status": "pending"}', '{"approval_status": "approved"}', '192.168.1.100'),
(3, 10006, 2002, 'create_order', 'order', 200002, '{}', '{"order_number": "ORD-2024-002", "total_amount": 67040.00}', '192.168.1.101');

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- 脚本执行完成提示
SELECT 'Mock data has been inserted successfully!' as message;
SELECT 
    'Companies: 6, Users: 10, Products: 5, Orders: 3, Videos: 3' as summary,
    'All tables populated with realistic B2B construction materials data for Canadian market' as description; 