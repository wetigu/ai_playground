# Tigu B2B 前端测试指南

## 目录
1. [测试概述](#测试概述)
2. [单元测试 (Unit Testing)](#单元测试-unit-testing)
3. [端到端测试 (E2E Testing)](#端到端测试-e2e-testing)
4. [GitHub Actions 工作流](#github-actions-工作流)
5. [测试最佳实践](#测试最佳实践)
6. [故障排除](#故障排除)

---

## 测试概述

### 测试金字塔架构
```
    /\
   /  \     E2E Tests (少量) - Cypress
  /____\    
 /      \   Integration Tests (中等)
/________\  Unit Tests (大量) - Jest/Vitest
```

### 技术栈
- **单元测试**: Jest/Vitest + Vue Test Utils + Testing Library
- **E2E测试**: Cypress
- **CI/CD**: GitHub Actions
- **代码覆盖率**: Istanbul/NYC
- **Mock工具**: MSW (Mock Service Worker)
- **部署**: Netlify (预览) + 自定义生产环境

### 项目结构
```
tigu_frontend_vue/
├── src/
├── tests/
│   ├── unit/
│   └── e2e/
├── cypress/
│   ├── e2e/
│   ├── fixtures/
│   ├── support/
│   └── screenshots/
├── package.json
└── cypress.config.js
```

---

## 单元测试 (Unit Testing)

### 1. 环境配置

#### 安装依赖
```bash
# 进入前端项目目录
cd tigu_frontend_vue

# 核心测试依赖
npm install --save-dev jest @vue/test-utils @testing-library/vue
npm install --save-dev @testing-library/jest-dom @testing-library/user-event

# Vue 3 特定依赖
npm install --save-dev @vue/vue3-jest babel-jest

# TypeScript 支持
npm install --save-dev ts-jest @types/jest

# 或者使用 Vitest (推荐用于 Vite 项目)
npm install --save-dev vitest @vitest/ui
```

#### Jest 配置文件 (`jest.config.js`)
```javascript
module.exports = {
  preset: '@vue/cli-plugin-unit-jest/presets/typescript-and-babel',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  moduleFileExtensions: ['js', 'ts', 'json', 'vue'],
  transform: {
    '^.+\\.vue$': '@vue/vue3-jest',
    '^.+\\.(js|jsx)$': 'babel-jest',
    '^.+\\.(ts|tsx)$': 'ts-jest'
  },
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy'
  },
  collectCoverageFrom: [
    'src/**/*.{js,ts,vue}',
    '!src/main.ts',
    '!src/router/index.ts',
    '!**/node_modules/**'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
}
```

#### Vitest 配置文件 (`vitest.config.ts`)
```typescript
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src')
    }
  }
})
```

#### 测试环境设置 (`tests/setup.js`)
```javascript
import '@testing-library/jest-dom'
import { config } from '@vue/test-utils'

// 全局组件注册
config.global.components = {
  // 注册全局组件
}

// Mock全局对象
global.console = {
  ...console,
  warn: jest.fn(),
  error: jest.fn()
}

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
}
global.localStorage = localStorageMock

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
})
```

### 2. Package.json 脚本配置

```json
{
  "scripts": {
    "test:unit": "vitest",
    "test:unit:run": "vitest run",
    "test:unit:coverage": "vitest run --coverage",
    "test:unit:ui": "vitest --ui",
    "test:unit:watch": "vitest --watch",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix --ignore-path .gitignore",
    "type-check": "vue-tsc --noEmit"
  }
}
```

### 3. 组件测试示例

#### 产品卡片组件测试 (`tests/unit/ProductCard.spec.ts`)
```typescript
import { render, screen, fireEvent } from '@testing-library/vue'
import { describe, it, expect, vi } from 'vitest'
import ProductCard from '@/components/ProductCard.vue'

describe('ProductCard.vue', () => {
  const mockProduct = {
    id: 100001,
    sku: 'REBAR-GRADE400-12',
    name: { 'zh-CN': 'Grade 400 螺纹钢筋 #4', 'en-US': 'Grade 400 Rebar #4' },
    price: 4200.00,
    stock: 5000,
    supplier: { name: '多伦多建材集团' }
  }

  it('应该正确渲染产品信息', () => {
    render(ProductCard, {
      props: { product: mockProduct }
    })

    expect(screen.getByText('Grade 400 螺纹钢筋 #4')).toBeInTheDocument()
    expect(screen.getByText('¥4,200.00')).toBeInTheDocument()
    expect(screen.getByText('库存: 5000')).toBeInTheDocument()
  })

  it('应该在点击时触发选择事件', async () => {
    const onSelect = vi.fn()
    render(ProductCard, {
      props: { product: mockProduct },
      attrs: { onSelect }
    })

    const card = screen.getByRole('button')
    await fireEvent.click(card)

    expect(onSelect).toHaveBeenCalledWith(mockProduct)
  })

  it('应该在库存不足时显示警告', () => {
    const lowStockProduct = { ...mockProduct, stock: 10 }
    render(ProductCard, {
      props: { product: lowStockProduct }
    })

    expect(screen.getByText('库存不足')).toBeInTheDocument()
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
```

---

## 端到端测试 (E2E Testing)

### 1. Cypress 配置

#### 安装和配置
```bash
# 在 tigu_frontend_vue 目录下
npm install --save-dev cypress

# 初始化 Cypress
npx cypress open
```

#### Cypress 配置文件 (`cypress.config.js`)
```javascript
import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:4173',
    supportFile: 'cypress/support/e2e.js',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    responseTimeout: 10000,
    setupNodeEvents(on, config) {
      // 实现 node 事件监听器
    },
  },
  component: {
    devServer: {
      framework: 'vue',
      bundler: 'vite',
    },
  },
})
```

#### Cypress 支持文件 (`cypress/support/e2e.js`)
```javascript
// 导入命令
import './commands'

// 全局配置
Cypress.on('uncaught:exception', (err, runnable) => {
  // 防止 Cypress 因为应用程序错误而失败
  return false
})

// 自定义命令
Cypress.Commands.add('login', (email, password) => {
  cy.visit('/login')
  cy.get('[data-testid="email-input"]').type(email)
  cy.get('[data-testid="password-input"]').type(password)
  cy.get('[data-testid="submit-button"]').click()
})

Cypress.Commands.add('addProductToCart', (productId, quantity = 1) => {
  cy.visit(`/products/${productId}`)
  cy.get('[data-testid="quantity-input"]').clear().type(quantity.toString())
  cy.get('[data-testid="add-to-cart"]').click()
})
```

#### 自定义命令类型定义 (`cypress/support/commands.ts`)
```typescript
declare global {
  namespace Cypress {
    interface Chainable {
      login(email: string, password: string): Chainable<void>
      addProductToCart(productId: number, quantity?: number): Chainable<void>
    }
  }
}
```

### 2. E2E 测试示例

#### 用户认证流程测试 (`cypress/e2e/auth.cy.js`)
```javascript
describe('用户认证', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('用户登录流程', () => {
    // 点击登录按钮
    cy.get('[data-testid="login-button"]').click()
    
    // 填写登录表单
    cy.get('[data-testid="email-input"]').type('test@tigu.com')
    cy.get('[data-testid="password-input"]').type('password123')
    
    // 提交表单
    cy.get('[data-testid="submit-button"]').click()
    
    // 验证登录成功
    cy.get('[data-testid="user-menu"]').should('be.visible')
    cy.contains('欢迎回来').should('be.visible')
    
    // 验证URL跳转
    cy.url().should('include', '/dashboard')
  })

  it('登录失败处理', () => {
    cy.get('[data-testid="login-button"]').click()
    
    // 输入错误凭据
    cy.get('[data-testid="email-input"]').type('wrong@email.com')
    cy.get('[data-testid="password-input"]').type('wrongpassword')
    cy.get('[data-testid="submit-button"]').click()
    
    // 验证错误消息
    cy.get('[data-testid="error-message"]').should('contain.text', '用户名或密码错误')
    
    // 验证仍在登录页面
    cy.url().should('include', '/login')
  })

  it('用户注册流程', () => {
    cy.get('[data-testid="register-link"]').click()
    
    // 填写注册表单
    cy.get('[data-testid="company-name"]').type('测试公司')
    cy.get('[data-testid="full-name"]').type('张三')
    cy.get('[data-testid="email"]').type('zhangsan@test.com')
    cy.get('[data-testid="phone"]').type('+1-416-555-0001')
    cy.get('[data-testid="password"]').type('SecurePass123!')
    cy.get('[data-testid="confirm-password"]').type('SecurePass123!')
    
    // 选择公司类型
    cy.get('[data-testid="company-type"]').select('buyer')
    
    // 同意条款
    cy.get('[data-testid="terms-checkbox"]').check()
    
    // 提交注册
    cy.get('[data-testid="register-button"]').click()
    
    // 验证注册成功
    cy.contains('注册成功').should('be.visible')
    cy.contains('请查收验证邮件').should('be.visible')
  })
})
```

#### 产品管理测试 (`cypress/e2e/products.cy.js`)
```javascript
describe('产品管理', () => {
  beforeEach(() => {
    // 登录管理员账户
    cy.login('admin@tigu.com', 'admin123')
    
    // 导航到产品页面
    cy.visit('/products')
  })

  it('查看产品列表', () => {
    // 验证产品列表加载
    cy.get('[data-testid="product-list"]').should('be.visible')
    
    // 验证产品卡片
    cy.get('[data-testid="product-card"]').should('have.length.greaterThan', 0)
    
    // 验证产品信息显示
    cy.get('[data-testid="product-card"]').first().within(() => {
      cy.get('[data-testid="product-name"]').should('be.visible')
      cy.get('[data-testid="product-price"]').should('be.visible')
      cy.get('[data-testid="product-stock"]').should('be.visible')
    })
  })

  it('搜索产品功能', () => {
    // 输入搜索关键词
    cy.get('[data-testid="search-input"]').type('螺纹钢{enter}')
    
    // 验证搜索结果
    cy.get('[data-testid="product-card"]').should('exist')
    
    // 验证所有结果都包含搜索关键词
    cy.get('[data-testid="product-card"]').each(($card) => {
      cy.wrap($card).find('[data-testid="product-name"]').should('contain.text', '螺纹钢')
    })
  })

  it('产品筛选功能', () => {
    // 选择分类筛选
    cy.get('[data-testid="category-filter"]').select('钢材')
    
    // 设置价格范围
    cy.get('[data-testid="min-price"]').type('1000')
    cy.get('[data-testid="max-price"]').type('5000')
    
    // 应用筛选
    cy.get('[data-testid="apply-filter"]').click()
    
    // 验证筛选结果
    cy.get('[data-testid="product-card"]').should('exist')
    
    // 验证价格在范围内
    cy.get('[data-testid="product-card"]').each(($card) => {
      cy.wrap($card).find('[data-testid="product-price"]').invoke('text').then((priceText) => {
        const price = parseFloat(priceText.replace(/[^\d.]/g, ''))
        expect(price).to.be.at.least(1000)
        expect(price).to.be.at.most(5000)
      })
    })
  })

  it('添加产品到购物车', () => {
    // 点击第一个产品
    cy.get('[data-testid="product-card"]').first().click()
    
    // 在产品详情页面设置数量
    cy.get('[data-testid="quantity-input"]').clear().type('10')
    
    // 添加到购物车
    cy.get('[data-testid="add-to-cart"]').click()
    
    // 验证成功消息
    cy.get('[data-testid="success-message"]').should('contain.text', '已添加到购物车')
    
    // 验证购物车图标更新
    cy.get('[data-testid="cart-count"]').should('contain.text', '1')
  })
})
```

#### 订单流程测试 (`cypress/e2e/orders.cy.js`)
```javascript
describe('订单流程', () => {
  it('完整的下单流程', () => {
    // 登录买家账户
    cy.login('buyer@tigu.com', 'buyer123')
    
    // 1. 浏览产品并添加到购物车
    cy.addProductToCart(100001, 5)
    
    // 2. 查看购物车
    cy.get('[data-testid="cart-icon"]').click()
    cy.get('[data-testid="cart-item"]').should('have.length', 1)
    
    // 3. 进入结算页面
    cy.get('[data-testid="checkout-button"]').click()
    
    // 4. 填写配送信息
    cy.get('[data-testid="project-name"]').type('测试项目')
    cy.get('[data-testid="delivery-address"]').type('测试地址123号')
    cy.get('[data-testid="contact-person"]').type('张三')
    cy.get('[data-testid="contact-phone"]').type('+1-416-555-0001')
    
    // 5. 选择支付方式
    cy.get('[data-testid="payment-bank-transfer"]').check()
    
    // 6. 提交订单
    cy.get('[data-testid="submit-order"]').click()
    
    // 7. 验证订单创建成功
    cy.get('[data-testid="order-success"]').should('be.visible')
    cy.get('[data-testid="order-number"]').should('be.visible')
    
    // 8. 验证跳转到订单详情页
    cy.url().should('match', /\/orders\/\d+/)
  })
})
```

### 3. Cypress 最佳实践

#### 数据属性策略
```html
<!-- 使用 data-testid 而不是 class 或 id -->
<button data-testid="submit-button" class="btn btn-primary">提交</button>
<input data-testid="email-input" type="email" />
<div data-testid="product-card">...</div>
```

#### 自定义命令 (`cypress/support/commands.js`)
```javascript
// 登录命令
Cypress.Commands.add('login', (email, password) => {
  cy.session([email, password], () => {
    cy.visit('/login')
    cy.get('[data-testid="email-input"]').type(email)
    cy.get('[data-testid="password-input"]').type(password)
    cy.get('[data-testid="submit-button"]').click()
    cy.url().should('not.include', '/login')
  })
})

// API 拦截
Cypress.Commands.add('mockProductsAPI', () => {
  cy.intercept('GET', '/api/products', { fixture: 'products.json' }).as('getProducts')
})

// 等待加载
Cypress.Commands.add('waitForPageLoad', () => {
  cy.get('[data-testid="loading"]').should('not.exist')
  cy.get('[data-testid="main-content"]').should('be.visible')
})
```

---

## GitHub Actions 工作流

### 1. 主要 CI/CD 工作流 (`.github/workflows/frontend-ci.yml`)

基于实际的工作流文件，我们的 CI/CD 流程包含以下特性：

#### 触发条件
- **自动触发**: 
  - `main` 和 `dev` 分支的 push
  - 针对 `main` 和 `dev` 分支的 Pull Request
  - 只有当 `tigu_frontend_vue/` 目录有变更时才触发

- **手动触发**: 
  - 支持选择环境 (staging/production/development)
  - 支持选择分支
  - 支持跳过测试 (用于热修复)
  - 支持仅部署模式

#### 工作流程详解

```yaml
name: Frontend CI/CD

on:
  # 自动触发
  push:
    branches: [ main, dev ]
    paths:
      - 'tigu_frontend_vue/**'
      - '.github/workflows/frontend-ci.yml'
  pull_request:
    branches: [ main, dev ]
    paths:
      - 'tigu_frontend_vue/**'
  
  # 手动触发
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        default: 'staging'
        type: choice
        options:
        - staging
        - production
        - development
      
      branch:
        description: 'Branch to deploy from'
        required: true
        default: 'dev'
        type: string
      
      skip_tests:
        description: 'Skip tests (for hotfixes)'
        required: false
        default: false
        type: boolean
      
      deploy_only:
        description: 'Only run deployment (skip build)'
        required: false
        default: false
        type: boolean
```

#### Job 1: 测试 (test)
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    if: ${{ !inputs.skip_tests }}
    
    strategy:
      matrix:
        node-version: [18.x, 20.x]
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        ref: ${{ github.event.inputs.branch || github.ref }}
    
    - name: Setup Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
        cache-dependency-path: tigu_frontend_vue/package-lock.json
    
    - name: Install dependencies
      run: npm ci
      working-directory: ./tigu_frontend_vue
    
    - name: Run linting
      run: npm run lint
      working-directory: ./tigu_frontend_vue
    
    - name: Run unit tests
      run: npm run test:unit
      working-directory: ./tigu_frontend_vue
    
    - name: Run type checking
      run: npm run type-check
      working-directory: ./tigu_frontend_vue
    
    - name: Build application
      run: npm run build
      working-directory: ./tigu_frontend_vue
      env:
        NODE_ENV: ${{ github.event.inputs.environment == 'production' && 'production' || 'development' }}
    
    - name: Upload build artifacts
      uses: actions/upload-artifact@v4
      with:
        name: dist-files-${{ matrix.node-version }}
        path: tigu_frontend_vue/dist/
        retention-days: 7
```

#### Job 2: E2E 测试 (e2e-tests)
```yaml
  e2e-tests:
    runs-on: ubuntu-latest
    needs: test
    if: ${{ !inputs.skip_tests && !inputs.deploy_only }}
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        ref: ${{ github.event.inputs.branch || github.ref }}
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20.x'
        cache: 'npm'
        cache-dependency-path: tigu_frontend_vue/package-lock.json
    
    - name: Install dependencies
      run: npm ci
      working-directory: ./tigu_frontend_vue
    
    - name: Install Cypress
      run: npx cypress install
      working-directory: ./tigu_frontend_vue
    
    - name: Build application
      run: npm run build
      working-directory: ./tigu_frontend_vue
    
    - name: Start application
      run: npm run preview &
      working-directory: ./tigu_frontend_vue
    
    - name: Wait for application to start
      run: npx wait-on http://localhost:4173
      working-directory: ./tigu_frontend_vue
    
    - name: Run Cypress e2e tests
      run: npx cypress run
      working-directory: ./tigu_frontend_vue
      env:
        CYPRESS_baseUrl: http://localhost:4173
    
    - name: Upload Cypress screenshots
      uses: actions/upload-artifact@v4
      if: failure()
      with:
        name: cypress-screenshots
        path: tigu_frontend_vue/cypress/screenshots/
    
    - name: Upload Cypress videos
      uses: actions/upload-artifact@v4
      if: failure()
      with:
        name: cypress-videos
        path: tigu_frontend_vue/cypress/videos/
```

#### Job 3: 手动部署 (deploy-manual)
```yaml
  deploy-manual:
    runs-on: ubuntu-latest
    needs: [test, e2e-tests]
    if: github.event_name == 'workflow_dispatch' && always() && (needs.test.result == 'success' || needs.test.result == 'skipped') && (needs.e2e-tests.result == 'success' || needs.e2e-tests.result == 'skipped')
    
    steps:
    - name: Deploy to Staging
      if: github.event.inputs.environment == 'staging'
      run: |
        echo "🚀 Deploying to STAGING environment"
        echo "Branch: ${{ github.event.inputs.branch }}"
        # 添加实际的 staging 部署命令
    
    - name: Deploy to Production
      if: github.event.inputs.environment == 'production'
      run: |
        echo "🚀 Deploying to PRODUCTION environment"
        echo "Branch: ${{ github.event.inputs.branch }}"
        # 添加实际的 production 部署命令
```

#### Job 4: 预览部署 (deploy-preview)
```yaml
  deploy-preview:
    runs-on: ubuntu-latest
    needs: [test, e2e-tests]
    if: github.event_name == 'pull_request'
    
    steps:
    - name: Deploy to Netlify (Preview)
      uses: nwtgck/actions-netlify@v3.0
      with:
        publish-dir: './tigu_frontend_vue/dist'
        production-branch: main
        github-token: ${{ secrets.GITHUB_TOKEN }}
        deploy-message: "Deploy from GitHub Actions"
        enable-pull-request-comment: true
        enable-commit-comment: true
        overwrites-pull-request-comment: true
      env:
        NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
        NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

#### Job 5: 生产部署 (deploy-production)
```yaml
  deploy-production:
    runs-on: ubuntu-latest
    needs: [test, e2e-tests]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    
    steps:
    - name: Deploy to production
      run: |
        echo "Deploy to your production server here"
        echo "Example: rsync, FTP, or cloud deployment"
      # 替换为实际的部署命令
```

### 2. 开发服务器工作流 (`.github/workflows/frontend-dev.yml`)

```yaml
name: Frontend Development Server

on:
  workflow_dispatch:
    inputs:
      port:
        description: 'Port to run the development server on'
        required: false
        default: '5173'
        type: string

jobs:
  run-frontend:
    runs-on: ubuntu-latest
    
    steps:
    - name: Start development server
      run: |
        echo "🚀 Starting Vue.js development server..."
        echo "📁 Project: Tigu Platform Frontend"
        echo "🔗 Will be available at: http://localhost:${{ github.event.inputs.port || '5173' }}"
        npm run dev -- --port ${{ github.event.inputs.port || '5173' }} --host 0.0.0.0
      working-directory: ./tigu_frontend_vue
      env:
        NODE_ENV: development
```

### 3. 工作流使用指南

#### 自动化流程
1. **开发流程**: 
   - 在 `dev` 分支推送代码 → 自动运行测试
   - 创建 PR 到 `main` → 自动运行测试 + Netlify 预览部署
   - 合并到 `main` → 自动运行测试 + 生产部署

2. **手动部署**:
   - 访问 GitHub Actions 页面
   - 选择 "Frontend CI/CD" 工作流
   - 点击 "Run workflow"
   - 选择环境、分支和选项

#### 环境配置
需要在 GitHub 仓库设置中配置以下 Secrets：
```bash
# Netlify 部署
NETLIFY_AUTH_TOKEN=your_netlify_auth_token
NETLIFY_SITE_ID=your_netlify_site_id

# 生产环境部署 (根据实际需求)
PRODUCTION_SERVER_HOST=your_server_host
PRODUCTION_SERVER_USER=your_server_user
PRODUCTION_SSH_KEY=your_ssh_private_key
```

---

## 测试最佳实践

### 1. 测试命名规范

```typescript
// ✅ 好的测试命名
describe('ProductCard 组件', () => {
  it('应该在产品库存不足时显示警告信息', () => {})
  it('应该在点击添加按钮时触发 onAdd 事件', () => {})
  it('应该正确格式化产品价格显示', () => {})
})

// ❌ 不好的测试命名
describe('ProductCard', () => {
  it('test 1', () => {})
  it('should work', () => {})
  it('renders', () => {})
})
```

### 2. 测试数据管理

#### 测试工厂函数 (`tests/factories/product.ts`)
```typescript
export function createMockProduct(overrides = {}) {
  return {
    id: 100001,
    sku: 'TEST-SKU-001',
    name: { 'zh-CN': '测试产品', 'en-US': 'Test Product' },
    price: 1000.00,
    stock: 100,
    category: { id: 1, name: '测试分类' },
    supplier: { id: 1001, name: '测试供应商' },
    ...overrides
  }
}

export function createMockProductList(count = 5) {
  return Array.from({ length: count }, (_, index) =>
    createMockProduct({
      id: 100001 + index,
      sku: `TEST-SKU-${String(index + 1).padStart(3, '0')}`
    })
  )
}
```

#### Cypress Fixtures (`cypress/fixtures/products.json`)
```json
{
  "data": [
    {
      "id": 100001,
      "sku": "REBAR-GRADE400-12",
      "name": {
        "zh-CN": "Grade 400 螺纹钢筋 #4",
        "en-US": "Grade 400 Rebar #4"
      },
      "price": 4200.00,
      "stock": 5000,
      "supplier": {
        "name": "多伦多建材集团"
      }
    }
  ],
  "total": 1
}
```

### 3. 测试覆盖率配置

#### Vitest 覆盖率配置
```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'dist/',
        'cypress/',
        '**/*.d.ts',
        'src/main.ts'
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        },
        'src/components/': {
          branches: 90,
          functions: 90,
          lines: 90,
          statements: 90
        }
      }
    }
  }
})
```

### 4. 测试环境变量

#### 环境配置 (`.env.test`)
```bash
# 测试环境配置
NODE_ENV=test
VITE_API_BASE_URL=http://localhost:3001/api
VITE_MOCK_API=true
VITE_LOG_LEVEL=error
```

---

## 故障排除

### 1. 常见问题解决

#### 问题：Cypress 测试超时
```javascript
// 解决方案：增加超时时间
cy.get('[data-testid="element"]', { timeout: 10000 }).should('be.visible')

// 或在 cypress.config.js 中全局配置
export default defineConfig({
  e2e: {
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    responseTimeout: 10000
  }
})
```

#### 问题：单元测试运行缓慢
```bash
# 解决方案：并行运行测试
npm run test:unit -- --reporter=verbose --threads

# 或在 vitest.config.ts 中配置
export default defineConfig({
  test: {
    threads: true,
    maxThreads: 4
  }
})
```

#### 问题：GitHub Actions 构建失败
```yaml
# 解决方案：检查 Node.js 版本兼容性
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '20.x'  # 确保版本一致
    cache: 'npm'
    cache-dependency-path: tigu_frontend_vue/package-lock.json
```

### 2. 调试技巧

#### 单元测试调试
```bash
# 调试单个测试文件
npm run test:unit -- ProductCard.spec.ts

# 监听模式
npm run test:unit:watch

# UI 模式
npm run test:unit:ui
```

#### Cypress 调试
```bash
# 有头模式运行
npx cypress open

# 调试模式
npx cypress run --headed --no-exit

# 生成测试代码
npx cypress open --e2e
```

#### GitHub Actions 调试
```yaml
# 添加调试步骤
- name: Debug environment
  run: |
    echo "Node version: $(node --version)"
    echo "NPM version: $(npm --version)"
    echo "Working directory: $(pwd)"
    ls -la tigu_frontend_vue/
```

### 3. 性能优化

#### 测试性能优化建议
```typescript
// 1. 使用 vi.mock 而不是实际 API 调用
vi.mock('@/services/api', () => ({
  getProducts: vi.fn().mockResolvedValue(mockProducts)
}))

// 2. 复用测试实例
describe('ProductList', () => {
  let wrapper
  
  beforeAll(() => {
    wrapper = mount(ProductList, { props: mockProps })
  })
  
  afterAll(() => {
    wrapper.unmount()
  })
})

// 3. 并行运行测试
// vitest.config.ts
export default defineConfig({
  test: {
    threads: true,
    isolate: false  // 谨慎使用
  }
})
```

#### Cypress 性能优化
```javascript
// 1. 使用 cy.session 缓存登录状态
cy.session('user-session', () => {
  cy.login('user@example.com', 'password')
})

// 2. 拦截不必要的网络请求
cy.intercept('GET', '**/analytics/**', { statusCode: 200 })

// 3. 使用 cy.request 而不是 UI 操作进行数据设置
cy.request('POST', '/api/products', mockProduct)
```

---

## 总结

这个测试指南基于 Tigu B2B 平台的实际 GitHub Actions 工作流，涵盖了：

1. **单元测试**：使用 Vitest + Vue Test Utils 进行组件和服务测试
2. **E2E 测试**：使用 Cypress 进行端到端用户流程测试
3. **CI/CD 集成**：
   - 多 Node.js 版本测试矩阵
   - 手动部署选项 (staging/production/development)
   - Netlify 预览部署
   - 灵活的触发条件和跳过选项
4. **最佳实践**：测试命名、数据管理、覆盖率配置等

### 关键特性
- **路径过滤**: 只有前端代码变更才触发工作流
- **多环境支持**: staging、production、development
- **灵活部署**: 支持跳过测试、仅部署等选项
- **预览部署**: PR 自动创建 Netlify 预览
- **失败处理**: 自动上传 Cypress 截图和视频

通过遵循这些指南和使用现有的工作流配置，可以确保代码质量，提高开发效率，减少生产环境的 bug。

---

**维护说明**：
- 定期更新测试用例以覆盖新功能
- 监控测试覆盖率，保持在 80% 以上
- 定期审查和优化测试性能
- 保持测试文档的及时更新
- 根据实际部署需求更新工作流中的部署命令 