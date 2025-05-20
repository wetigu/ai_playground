tigu_platform_frontend /
├── README.md
├── package.json               # workspaces: ["backend", "frontend", "shared"]
├── tsconfig.json              # 前端 TS 配置
├── pyproject.toml             # 后端 Poetry 配置（可放在根，也可移到 backend/）
├── poetry.lock
├── backend/
│   ├── README.md
│   ├── .env.example
│   ├── Dockerfile
│   ├── alembic.ini
│   ├── migrations/
│   ├── scripts/
│   ├── app/
│   │   └── … （同上方案 A 中 app/ 结构）
│   ├── tests/
│   └── requirements.txt
├── frontend/                   # Vue.js + PWA 结构（同上节）
│   ├── public/
│   ├── src/
│   ├── vite.config.ts
│   └── package.json
└── shared/                     # 跨前后端共用：类型定义、工具函数
    ├── package.json
    └── src/
        ├── types/             # 如 Product、Order 接口定义
        └── utils/             # 通用 JS/TS 函数
