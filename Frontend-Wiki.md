# 建材 B2B 平台 - 前端文档

欢迎使用建材 B2B 平台前端文档！本文档提供了有关前端架构、设置和开发工作流的全面指南。

## 目录

1. [项目概述](#项目概述)
2. [技术栈](#技术栈)
3. [项目结构](#项目结构)
4. [开发指南](#开发指南)
5. [构建与部署](#构建与部署)
6. [PWA 功能](#pwa-功能)
7. [国际化](#国际化)
8. [测试](#测试)
9. [代码规范](#代码规范)
10. [系统架构图](#系统架构图)
11. [常见问题](#常见问题)

## 项目概述

建材 B2B 平台前端是基于 Vue.js 构建的现代渐进式 Web 应用程序 (PWA)，专为建材行业的企业对企业交易设计。该平台提供了产品展示、商家入驻、订单管理和用户系统等功能。

### 主要功能

- 产品 SKU 矩阵与展示系统
- 商家入驻与管理
- 订单处理与拆分功能
- 客户管理与账期系统
- 数据分析和推荐系统
- 多语言支持

## 技术栈

- **框架**: Vue.js 3.x
- **构建工具**: Vite
- **语言**: TypeScript
- **状态管理**: Pinia
- **路由**: Vue Router
- **API 调用**: Axios
- **样式**: SASS
- **国际化**: Vue I18n
- **PWA 支持**: Vite PWA Plugin
- **测试工具**:
  - 单元测试: Vitest
  - E2E 测试: Cypress

## 项目结构

```
tigu_frontend_vue/
├── README.md              # 项目文档
├── index.html             # HTML 入口点
├── package.json           # NPM 依赖和脚本
├── tsconfig.json          # TypeScript 配置
├── tsconfig.node.json     # Node.js TypeScript 配置
├── vite.config.ts         # Vite 构建配置
├── .env.example           # 环境变量模板
├── .gitignore             # Git 忽略模式
├── public/                # 静态资源
│   ├── favicon.ico        # 网站图标
│   └── robots.txt         # 搜索引擎指令
└── src/                   # 源代码
    ├── main.ts            # 应用程序入口点
    ├── App.vue            # 根 Vue 组件
    ├── assets/            # 项目资源
    │   └── styles/        # CSS/SCSS 样式
    ├── components/        # 可复用 Vue 组件
    │   └── common/        # 通用 UI 组件
    ├── composables/       # Vue 组合式 API 钩子
    ├── router/            # Vue Router 配置
    ├── services/          # 外部服务集成
    │   └── api.ts         # API 客户端
    ├── store/             # Pinia 状态管理
    │   └── modules/       # Store 模块
    ├── types/             # TypeScript 类型定义
    ├── utils/             # 工具函数
    └── views/             # 页面组件
        ├── HomeView.vue   # 首页
        └── AboutView.vue  # 关于页面
├── tests/                 # 测试文件
    ├── unit/              # 单元测试
    └── e2e/               # 端到端测试
```

## 开发指南

### 环境设置

1. **克隆仓库**
   ```bash
   git clone <repository-url>
   cd tigu_frontend_vue
   ```

2. **安装依赖**
   ```bash
   npm install
   ```

3. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件设置必要的变量
   ```

4. **启动开发服务器**
   ```bash
   npm run dev
   ```
   开发服务器将在 http://localhost:5173 运行

### 添加新功能

1. **添加新组件**
   - 在 `src/components` 目录创建新组件
   - 使用 TypeScript 进行类型定义
   - 遵循组件命名规范 (PascalCase)

2. **添加新页面**
   - 在 `src/views` 目录创建新页面组件
   - 在 `src/router/index.ts` 中注册路由

3. **添加新 API 调用**
   - 在 `src/services/api.ts` 添加新的 API 方法
   - 使用 axios 实例进行 HTTP 请求

4. **添加新状态**
   - 在 `src/store/modules` 创建新的状态模块
   - 在 `src/store/index.ts` 注册该模块

## 构建与部署

### 生产构建

```bash
npm run build
```

构建后的文件将生成在 `dist/` 目录，可部署到任何静态文件服务器。

### 构建预览

```bash
npm run preview
```

在本地预览生产构建。

### 持续集成/部署 (CI/CD)

项目可配置使用 GitHub Actions 或其他 CI/CD 平台进行自动部署。常见部署目标：
- AWS S3 + CloudFront
- Azure Static Web Apps
- Vercel
- Netlify

## PWA 功能

本项目支持渐进式 Web 应用 (PWA) 功能，通过以下特性提升用户体验：

- 离线访问主要功能
- 快速加载与缓存
- 可安装到移动设备主屏幕
- 推送通知支持

PWA 配置位于 `vite.config.ts` 的 `VitePWA` 插件部分。

## 国际化

使用 Vue I18n 实现多语言支持：

- 翻译文件位于 `src/i18n/` 目录
- 支持中文和英文
- 添加新语言：
  1. 在 `src/i18n/locales/` 创建新的语言文件
  2. 在 `src/i18n/index.ts` 注册新语言

## 测试

### 单元测试

```bash
npm run test:unit
```

单元测试使用 Vitest，测试文件位于 `tests/unit/` 目录。

### E2E 测试

```bash
npm run test:e2e
```

E2E 测试使用 Cypress，测试文件位于 `tests/e2e/` 目录。

## 代码规范

项目使用 ESLint 和 TypeScript 来确保代码质量和一致性：

- **代码格式化**：使用 ESLint
- **类型检查**：使用 TypeScript
- **组件命名**：使用 PascalCase (如 `ProductCard.vue`)
- **文件命名**：使用 camelCase (如 `userService.ts`)

执行代码检查：
```bash
npm run lint
```

## 系统架构图

![前端系统架构图](frontend_system_diagram.html)

前端系统架构图说明了用户界面层、组件层、状态管理层、服务层、路由层和样式层之间的关系和数据流。

## 常见问题

### Q: 如何添加新的依赖?
A: 使用 npm 添加依赖，例如 `npm install package-name`

### Q: 如何处理 API 错误?
A: 使用 axios 拦截器和 try/catch 处理 API 错误，定义在 `src/services/api.ts`

### Q: 如何实现新的国际化内容?
A: 在相应的语言文件中添加新的翻译键值对，然后使用 `$t('key')` 在组件中使用 