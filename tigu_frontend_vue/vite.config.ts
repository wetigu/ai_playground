import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import { VitePWA } from 'vite-plugin-pwa';
import { fileURLToPath, URL } from 'node:url';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on mode
  const env = loadEnv(mode, process.cwd());

  return {
    // Use relative paths instead of absolute
    base: './',
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
          background_color: '#ffffff',
          display: 'standalone',
          orientation: 'portrait',
          start_url: './',
          categories: ['shopping', 'business', 'productivity'],
          screenshots: [
            {
              src: './screenshots/mobile-1.png',
              sizes: '750x1334',
              type: 'image/png',
              platform: 'narrow'
            },
            {
              src: './screenshots/desktop-1.png',
              sizes: '1280x800',
              type: 'image/png',
              platform: 'wide'
            }
          ],
          icons: [
            {
              src: './pwa-192x192.png',
              sizes: '192x192',
              type: 'image/png'
            },
            {
              src: './pwa-512x512.png',
              sizes: '512x512',
              type: 'image/png',
              purpose: 'any'
            },
            {
              src: './pwa-512x512-mask.png',
              sizes: '512x512',
              type: 'image/png',
              purpose: 'maskable'
            }
          ],
          shortcuts: [
            {
              name: 'Products',
              short_name: 'Products',
              description: 'Browse all products',
              url: './shop',
              icons: [{ src: './shortcuts/products.png', sizes: '96x96' }]
            },
            {
              name: 'Deals',
              short_name: 'Deals',
              description: 'View special deals',
              url: './deals',
              icons: [{ src: './shortcuts/deals.png', sizes: '96x96' }]
            }
          ],
          related_applications: [
            {
              platform: 'play',
              url: 'https://play.google.com/store/apps/details?id=com.tigu.platform'
            },
            {
              platform: 'itunes',
              url: 'https://apps.apple.com/app/tigu-platform/id123456789'
            }
          ]
        },
        workbox: {
          runtimeCaching: [
            {
              urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
              handler: 'CacheFirst',
              options: {
                cacheName: 'google-fonts-cache',
                expiration: {
                  maxEntries: 10,
                  maxAgeSeconds: 60 * 60 * 24 * 365 // 1 year
                }
              }
            },
            {
              urlPattern: /^https:\/\/fonts\.gstatic\.com\/.*/i,
              handler: 'CacheFirst',
              options: {
                cacheName: 'gstatic-fonts-cache',
                expiration: {
                  maxEntries: 10,
                  maxAgeSeconds: 60 * 60 * 24 * 365 // 1 year
                }
              }
            },
            {
              urlPattern: /\.(?:png|jpg|jpeg|svg|gif)$/,
              handler: 'CacheFirst',
              options: {
                cacheName: 'images-cache',
                expiration: {
                  maxEntries: 50,
                  maxAgeSeconds: 60 * 60 * 24 * 30 // 30 days
                }
              }
            },
            {
              urlPattern: /^https:\/\/api\.tigu\.com\/api/,
              handler: 'NetworkFirst',
              options: {
                cacheName: 'api-cache',
                expiration: {
                  maxEntries: 100,
                  maxAgeSeconds: 60 * 60 // 1 hour
                },
                networkTimeoutSeconds: 10
              }
            }
          ]
        }
      })
    ],
    css: {
      devSourcemap: true,
      preprocessorOptions: {
        scss: {
          charset: false
        }
      }
    },
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
    },    build: {
      // Output directory for production build
      outDir: 'dist',
      // Generate sourcemaps for production build
      sourcemap: true
    },
    test: {
      // Use happy-dom for testing environment
      environment: 'happy-dom',
      // Include test files
      include: ['tests/unit/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}']
    }
  };
});
