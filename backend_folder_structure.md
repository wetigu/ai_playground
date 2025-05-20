tigu_backend_fastapi/
├── README.md
├── .env.example               # 环境变量示例
├── pyproject.toml             # Poetry／Poetry-managed project
├── poetry.lock
├── Dockerfile                 # 容器化部署
├── alembic.ini                # 数据库迁移配置
├── migrations/                # Alembic 自动生成的迁移脚本
│   └── versions/
├── scripts/                   # 启动、部署、初始化脚本
│   ├── start.sh
│   └── init_db.sh
├── app/                       # 源码根目录
│   ├── main.py                # FastAPI 实例与中间件注册
│   ├── core/
│   │   ├── config.py          # pydantic Settings
│   │   ├── security.py        # 加密、JWT 策略
│   │   └── logging.py
│   ├── api/                   # 路由层
│   │   ├── deps.py            # 依赖注入（数据库、用户、权限等）
│   │   ├── v1/                # 版本化路由
│   │   │   ├── routers/
│   │   │   │   ├── orders.py
│   │   │   │   ├── products.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── models/                # ORM 模型（SQLAlchemy）
│   │   ├── order.py
│   │   ├── product.py
│   │   └── user.py
│   ├── schemas/               # Pydantic DTO（请求/响应定义）
│   │   ├── order.py
│   │   ├── product.py
│   │   └── user.py
│   ├── crud/                  # CRUD 服务（封装通用操作）
│   │   ├── order.py
│   │   └── product.py
│   ├── services/              # 业务模块（payment、email、etc.）
│   │   ├── payment_gateway.py
│   │   └── notification.py
│   ├── db/                    # 数据库相关
│   │   ├── base.py            # Base model、session 创建
│   │   └── init.py
│   └── utils/                 # 辅助工具函数
│       ├── pagination.py
│       └── exceptions.py
├── tests/                     # pytest 单元 & 集成测试
│   ├── conftest.py
│   └── test_products.py
└── requirements.txt           # 或使用 pyproject.toml + poetry.lock
