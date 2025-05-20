#!/bin/bash

# Create the main project directory
MAIN_DIR="tigu_frontend_vue"

mkdir -p "$MAIN_DIR"
cd "$MAIN_DIR" || exit

echo "Creating frontend project structure in $(pwd)"

# Create subdirectories
mkdir -p public
mkdir -p src/assets/{images,styles}
mkdir -p src/components/{common,layout,forms}
mkdir -p src/views
mkdir -p src/router
mkdir -p src/store/modules
mkdir -p src/composables
mkdir -p src/services
mkdir -p src/types
mkdir -p src/utils
mkdir -p tests/unit
mkdir -p tests/e2e

# Create root level files

cat << 'EOF_README' > README.md
# tigu_platform_frontend

Vue.js + PWA frontend for the Tigu platform.

## Project Structure

- `public/`: Static assets that will be served as-is.
- `src/`: Main source code.
  - `assets/`: Static assets that will be processed by the build system.
  - `components/`: Reusable Vue components.
  - `views/`: Page components corresponding to routes.
  - `router/`: Vue Router configuration.
  - `store/`: Vuex/Pinia store for state management.
  - `composables/`: Vue composition API functions.
  - `services/`: API client services.
  - `types/`: TypeScript type definitions.
  - `utils/`: Utility functions.
- `tests/`: Test suite.
- `.env.example`: Example environment variables.
- `vite.config.ts`: Vite configuration.
- `tsconfig.json`: TypeScript configuration.

## Setup

1. Clone the repository.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Copy `.env.example` to `.env` and update the variables.
4. Start the development server:
   ```bash
   npm run dev
   ```
5. Build for production:
   ```bash
   npm run build
   ```
EOF_README

cat << 'EOF_ENV' > .env.example
# API URL
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Feature flags
VITE_ENABLE_PWA=true
VITE_ENABLE_ANALYTICS=false

# App configuration
VITE_APP_TITLE=Tigu Platform
EOF_ENV

cat << 'EOF_PACKAGE' > package.json
{
  "name": "tigu-platform-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc --noEmit && vite build",
    "preview": "vite preview",
    "test:unit": "vitest",
    "test:e2e": "cypress open",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix --ignore-path .gitignore"
  },
  "dependencies": {
    "axios": "^1.4.0",
    "pinia": "^2.1.4",
    "vue": "^3.3.4",
    "vue-router": "^4.2.4",
    "@vueuse/core": "^10.2.1"
  },
  "devDependencies": {
    "@types/node": "^20.4.5",
    "@vitejs/plugin-vue": "^4.2.3",
    "@vue/eslint-config-typescript": "^11.0.3",
    "@vue/test-utils": "^2.4.1",
    "cypress": "^12.17.2",
    "eslint": "^8.45.0",
    "eslint-plugin-vue": "^9.15.1",
    "sass": "^1.64.1",
    "typescript": "~5.1.6",
    "vite": "^4.4.7",
    "vite-plugin-pwa": "^0.16.4",
    "vitest": "^0.33.0",
    "vue-tsc": "^1.8.8"
  }
}
EOF_PACKAGE

cat << 'EOF_VITE' > vite.config.ts
import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import { VitePWA } from 'vite-plugin-pwa';
import { fileURLToPath, URL } from 'node:url';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on mode
  const env = loadEnv(mode, process.cwd());

  return {
    plugins: [
      vue(),
      // PWA plugin configuration
      VitePWA({
        registerType: 'autoUpdate',
        includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
        manifest: {
          name: 'Tigu Platform',
          short_name: 'Tigu',
          description: 'Tigu Platform - B2B Marketplace',
          theme_color: '#ffffff',
          icons: [
            {
              src: 'pwa-192x192.png',
              sizes: '192x192',
              type: 'image/png'
            },
            {
              src: 'pwa-512x512.png',
              sizes: '512x512',
              type: 'image/png'
            }
          ]
        }
      })
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      port: 3000,
      // Proxy API requests to backend during development
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      }
    },
    build: {
      // Output directory for production build
      outDir: 'dist',
      // Generate sourcemaps for production build
      sourcemap: true
    }
  };
});
EOF_VITE

cat << 'EOF_TSCONFIG' > tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,

    /* Paths */
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
EOF_TSCONFIG

cat << 'EOF_TSCONFIG_NODE' > tsconfig.node.json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
EOF_TSCONFIG_NODE

# Create index.html
cat << 'EOF_INDEX_HTML' > index.html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" href="/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="Tigu Platform - B2B Marketplace" />
    <title>Tigu Platform</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
EOF_INDEX_HTML

# Create public files
touch public/favicon.ico
touch public/robots.txt
cat << 'EOF_ROBOTS' > public/robots.txt
User-agent: *
Allow: /
EOF_ROBOTS

# Create main.ts
cat << 'EOF_MAIN' > src/main.ts
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import './assets/styles/main.scss';

const app = createApp(App);

app.use(createPinia());
app.use(router);

app.mount('#app');
EOF_MAIN

# Create App.vue
cat << 'EOF_APP' > src/App.vue
<template>
  <div id="app">
    <header>
      <nav>
        <router-link to="/">Home</router-link> |
        <router-link to="/about">About</router-link>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
    <footer>
      <p>&copy; {{ currentYear }} Tigu Platform</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const currentYear = computed(() => new Date().getFullYear());
</script>

<style lang="scss">
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin: 0;
  padding: 0;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
  padding: 20px;
}

header {
  background-color: #f8f9fa;
  padding: 20px;
}

nav {
  padding: 10px 0;
  
  a {
    font-weight: bold;
    color: #2c3e50;
    text-decoration: none;
    margin: 0 10px;
    
    &.router-link-exact-active {
      color: #42b983;
    }
  }
}

footer {
  background-color: #f8f9fa;
  padding: 20px;
  margin-top: auto;
}
</style>
EOF_APP

# Create router index.ts
mkdir -p src/router
cat << 'EOF_ROUTER' > src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue')
    }
  ]
});

export default router;
EOF_ROUTER

# Create views
mkdir -p src/views
cat << 'EOF_HOME_VIEW' > src/views/HomeView.vue
<template>
  <div class="home">
    <h1>Welcome to Tigu Platform</h1>
    <p>A B2B marketplace for construction materials</p>
  </div>
</template>

<script setup lang="ts">
// Component logic goes here
</script>

<style scoped lang="scss">
.home {
  padding: 20px;
  
  h1 {
    color: #42b983;
  }
}
</style>
EOF_HOME_VIEW

cat << 'EOF_ABOUT_VIEW' > src/views/AboutView.vue
<template>
  <div class="about">
    <h1>About Tigu Platform</h1>
    <p>Tigu Platform is a B2B marketplace connecting suppliers and buyers in the construction industry.</p>
  </div>
</template>

<style scoped lang="scss">
.about {
  padding: 20px;
  
  h1 {
    color: #42b983;
  }
}
</style>
EOF_ABOUT_VIEW

# Create store with Pinia
mkdir -p src/store
cat << 'EOF_STORE' > src/store/index.ts
// Main store exports
// Import and export your modules here
export * from './modules/counter';
EOF_STORE

mkdir -p src/store/modules
cat << 'EOF_COUNTER_STORE' > src/store/modules/counter.ts
import { defineStore } from 'pinia';

export const useCounterStore = defineStore('counter', {
  state: () => ({
    count: 0
  }),
  getters: {
    doubleCount: (state) => state.count * 2
  },
  actions: {
    increment() {
      this.count++;
    },
    decrement() {
      this.count--;
    }
  }
});
EOF_COUNTER_STORE

# Create API service
mkdir -p src/services
cat << 'EOF_API_SERVICE' > src/services/api.ts
import axios from 'axios';

// Create axios instance with base URL from environment variables
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle 401 Unauthorized errors
    if (error.response && error.response.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
EOF_API_SERVICE

# Create example component
mkdir -p src/components/common
cat << 'EOF_BUTTON_COMPONENT' > src/components/common/Button.vue
<template>
  <button 
    :class="['btn', `btn-${variant}`, { 'btn-loading': loading }]"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="spinner"></span>
    <slot></slot>
  </button>
</template>

<script setup lang="ts">
defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (value: string) => ['primary', 'secondary', 'danger', 'success'].includes(value)
  },
  loading: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  }
});

defineEmits(['click']);
</script>

<style scoped lang="scss">
.btn {
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  outline: none;
  position: relative;
  
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
  
  &-primary {
    background-color: #42b983;
    color: white;
    
    &:hover:not(:disabled) {
      background-color: darken(#42b983, 10%);
    }
  }
  
  &-secondary {
    background-color: #6c757d;
    color: white;
    
    &:hover:not(:disabled) {
      background-color: darken(#6c757d, 10%);
    }
  }
  
  &-danger {
    background-color: #dc3545;
    color: white;
    
    &:hover:not(:disabled) {
      background-color: darken(#dc3545, 10%);
    }
  }
  
  &-success {
    background-color: #28a745;
    color: white;
    
    &:hover:not(:disabled) {
      background-color: darken(#28a745, 10%);
    }
  }
  
  &-loading {
    .spinner {
      display: inline-block;
      width: 14px;
      height: 14px;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-radius: 50%;
      border-top-color: white;
      animation: spin 1s ease-in-out infinite;
      margin-right: 8px;
    }
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
EOF_BUTTON_COMPONENT

# Create main SCSS file
mkdir -p src/assets/styles
cat << 'EOF_MAIN_SCSS' > src/assets/styles/main.scss
/* Reset and base styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  line-height: 1.6;
}

h1, h2, h3, h4, h5, h6 {
  margin-bottom: 0.5em;
}

p {
  margin-bottom: 1em;
}

a {
  color: #42b983;
  text-decoration: none;
  
  &:hover {
    text-decoration: underline;
  }
}

/* Container */
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 15px;
}

/* Grid */
.row {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -15px;
}

.col {
  flex: 1;
  padding: 0 15px;
}

/* Responsive utilities */
@media (max-width: 768px) {
  .row {
    flex-direction: column;
  }
}
EOF_MAIN_SCSS

# Create types
mkdir -p src/types
cat << 'EOF_TYPES' > src/types/index.ts
// Common types used across the application

export interface User {
  id: number;
  username: string;
  email: string;
  firstName?: string;
  lastName?: string;
  isActive: boolean;
  createdAt: string;
}

export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  category: string;
  imageUrl?: string;
  inStock: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Order {
  id: number;
  userId: number;
  products: OrderItem[];
  totalAmount: number;
  status: 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  createdAt: string;
  updatedAt: string;
}

export interface OrderItem {
  productId: number;
  quantity: number;
  price: number;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}
EOF_TYPES

# Create utils
mkdir -p src/utils
cat << 'EOF_UTILS' > src/utils/index.ts
// Utility functions

/**
 * Format date to a readable string
 */
export function formatDate(date: string | Date): string {
  const d = new Date(date);
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

/**
 * Format currency
 */
export function formatCurrency(amount: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency
  }).format(amount);
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;
  
  return function(...args: Parameters<T>): void {
    const later = () => {
      timeout = null;
      func(...args);
    };
    
    if (timeout !== null) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(later, wait);
  };
}

/**
 * Truncate text with ellipsis
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}
EOF_UTILS

# Create composables
mkdir -p src/composables
cat << 'EOF_COMPOSABLES' > src/composables/useApi.ts
import { ref, Ref } from 'vue';
import api from '@/services/api';
import type { ApiResponse } from '@/types';

export function useApi<T, P = any>(url: string) {
  const data: Ref<T | null> = ref(null);
  const error: Ref<Error | null> = ref(null);
  const loading = ref(false);

  const fetchData = async (params?: P): Promise<void> => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await api.get<ApiResponse<T>>(url, { params });
      data.value = response.data.data;
    } catch (err) {
      error.value = err as Error;
      console.error('API Error:', err);
    } finally {
      loading.value = false;
    }
  };

  const postData = async (payload: any): Promise<T | null> => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await api.post<ApiResponse<T>>(url, payload);
      data.value = response.data.data;
      return response.data.data;
    } catch (err) {
      error.value = err as Error;
      console.error('API Error:', err);
      return null;
    } finally {
      loading.value = false;
    }
  };

  const updateData = async (id: string | number, payload: any): Promise<T | null> => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await api.put<ApiResponse<T>>(`${url}/${id}`, payload);
      data.value = response.data.data;
      return response.data.data;
    } catch (err) {
      error.value = err as Error;
      console.error('API Error:', err);
      return null;
    } finally {
      loading.value = false;
    }
  };

  const deleteData = async (id: string | number): Promise<boolean> => {
    loading.value = true;
    error.value = null;
    
    try {
      await api.delete(`${url}/${id}`);
      return true;
    } catch (err) {
      error.value = err as Error;
      console.error('API Error:', err);
      return false;
    } finally {
      loading.value = false;
    }
  };

  return {
    data,
    error,
    loading,
    fetchData,
    postData,
    updateData,
    deleteData
  };
}
EOF_COMPOSABLES

# Create tests
mkdir -p tests/unit
cat << 'EOF_BUTTON_TEST' > tests/unit/Button.spec.ts
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import Button from '@/components/common/Button.vue';

describe('Button.vue', () => {
  it('renders slot content', () => {
    const wrapper = mount(Button, {
      slots: {
        default: 'Test Button'
      }
    });
    expect(wrapper.text()).toContain('Test Button');
  });

  it('applies variant class', () => {
    const wrapper = mount(Button, {
      props: {
        variant: 'danger'
      }
    });
    expect(wrapper.classes()).toContain('btn-danger');
  });

  it('disables button when disabled prop is true', () => {
    const wrapper = mount(Button, {
      props: {
        disabled: true
      }
    });
    expect(wrapper.attributes('disabled')).toBeDefined();
  });

  it('shows loading spinner when loading prop is true', () => {
    const wrapper = mount(Button, {
      props: {
        loading: true
      }
    });
    expect(wrapper.find('.spinner').exists()).toBe(true);
  });

  it('emits click event when clicked', async () => {
    const wrapper = mount(Button);
    await wrapper.trigger('click');
    expect(wrapper.emitted('click')).toBeTruthy();
  });

  it('does not emit click event when disabled', async () => {
    const wrapper = mount(Button, {
      props: {
        disabled: true
      }
    });
    await wrapper.trigger('click');
    expect(wrapper.emitted('click')).toBeFalsy();
  });
});
EOF_BUTTON_TEST

# Create e2e test
mkdir -p tests/e2e
cat << 'EOF_HOME_E2E' > tests/e2e/home.cy.ts
describe('Home Page', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('displays the welcome message', () => {
    cy.contains('h1', 'Welcome to Tigu Platform');
  });

  it('navigates to About page when clicking the link', () => {
    cy.contains('About').click();
    cy.url().should('include', '/about');
    cy.contains('h1', 'About Tigu Platform');
  });
});
EOF_HOME_E2E

# Create .gitignore
cat << 'EOF_GITIGNORE' > .gitignore
# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

# Dependencies
node_modules
.pnp
.pnp.js

# Build
dist
dist-ssr
*.local
coverage
*.tsbuildinfo

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# Environment variables
.env
.env.local
.env.*.local

# Cypress
cypress/videos
cypress/screenshots
EOF_GITIGNORE

cd ..
echo "Frontend project '$MAIN_DIR' structure created successfully in $(pwd)/$MAIN_DIR"
echo "Remember to 'cd $MAIN_DIR' to start working on the project."
