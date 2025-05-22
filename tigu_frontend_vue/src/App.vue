<template>
  <div id="app">
    <header class="header">
      <div class="top-banner">
        <div class="container">
          <div class="promo-message">{{ t('app.promo') || 'Save up to 30% on Select Products - Limited Time Only!' }}</div>
          <div class="language-selector">
            <LanguageSwitcher />
          </div>
        </div>
      </div>
      <div class="header-main container">
        <div class="logo">
          <router-link to="./">
            <h1>{{ t('app.title') }}</h1>
          </router-link>
        </div>
        <div class="search-bar">
          <input type="text" :placeholder="t('header.search')" aria-label="Search">
          <button class="search-button">
            <span class="icon">🔍</span>
          </button>
        </div>
        <div class="header-actions">
          <button class="location-btn">
            <span class="icon">📍</span> 
            <span class="text">{{ t('header.storeFinder') || 'Store Finder' }}</span>
          </button>
          <button class="account-btn">
            <span class="icon">👤</span>
            <span class="text">{{ t('header.account') }}</span>
          </button>
          <button class="cart-btn">
            <span class="icon">🛒</span>
            <span class="text">{{ t('header.cart') }}</span>
          </button>
        </div>
        <button class="mobile-menu-btn" @click="openMobileMenu">
          <span class="icon">☰</span>
        </button>
      </div>
      <nav class="main-nav">
        <div class="container">
          <ul class="nav-list">
            <li><router-link to="./shop">{{ t('header.products') }}</router-link></li>
            <li><router-link to="./departments">{{ t('header.departments') || 'Departments' }}</router-link></li>
            <li><router-link to="./deals">{{ t('header.deals') }}</router-link></li>
            <li><router-link to="./services">{{ t('header.services') }}</router-link></li>
            <li><router-link to="./ideas">{{ t('header.diy') }}</router-link></li>
          </ul>
        </div>
      </nav>
    </header>
    
    <main>
      <router-view />
    </main>
    
    <footer class="footer">
      <div class="container">
        <div class="footer-grid">
          <div class="footer-section">
            <h4>{{ t('footer.customerService') }}</h4>
            <ul>
              <li><a href="#">{{ t('footer.help') }}</a></li>
              <li><a href="#">{{ t('footer.orderStatus') }}</a></li>
              <li><a href="#">{{ t('footer.returns') }}</a></li>
              <li><a href="#">{{ t('footer.contact') }}</a></li>
            </ul>
          </div>
          <div class="footer-section">
            <h4>{{ t('footer.about') }}</h4>
            <ul>
              <li><a href="#">{{ t('footer.companyInfo') || 'Company Info' }}</a></li>
              <li><a href="#">{{ t('footer.careers') }}</a></li>
              <li><a href="#">{{ t('footer.responsibility') || 'Corporate Responsibility' }}</a></li>
              <li><a href="#">{{ t('footer.investors') }}</a></li>
            </ul>
          </div>
          <div class="footer-section">
            <h4>Services</h4>
            <ul>
              <li><a href="#">Professional Services</a></li>
              <li><a href="#">Installation Services</a></li>
              <li><a href="#">Delivery Options</a></li>
              <li><a href="#">Financing Options</a></li>
            </ul>
          </div>
          <div class="footer-section">
            <h4>Connect With Us</h4>
            <div class="social-icons">
              <a href="#" aria-label="Facebook">📱</a>
              <a href="#" aria-label="Twitter">📱</a>
              <a href="#" aria-label="Instagram">📱</a>
              <a href="#" aria-label="Pinterest">📱</a>
              <a href="#" aria-label="YouTube">📱</a>
            </div>
            <div class="app-downloads">
              <p>Get Our Mobile App</p>
              <div class="app-links">
                <a href="#">App Store</a>
                <a href="#">Google Play</a>
              </div>
            </div>
          </div>
        </div>
        <div class="footer-bottom">
          <p>{{ t('footer.copyright', { year: currentYear }) }}</p>
          <div class="footer-links">
            <a href="#">{{ t('footer.privacy') || 'Privacy Policy' }}</a>
            <a href="#">{{ t('footer.terms') || 'Terms of Use' }}</a>
            <a href="#">{{ t('footer.accessibility') || 'Accessibility' }}</a>
          </div>
        </div>
      </div>
    </footer>
    
    <!-- Mobile Menu -->
    <MobileMenu :is-active="mobileMenuActive" @close="closeMobileMenu" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import MobileMenu from '@/components/layout/MobileMenu.vue';
import LanguageSwitcher from '@/components/LanguageSwitcher.vue';

const { t } = useI18n();
const currentYear = computed(() => new Date().getFullYear());
const mobileMenuActive = ref(false);

function openMobileMenu() {
  mobileMenuActive.value = true;
  document.body.classList.add('no-scroll');
}

function closeMobileMenu() {
  mobileMenuActive.value = false;
  document.body.classList.remove('no-scroll');
}

// Check if the service worker is registered
onMounted(() => {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('./sw.js')
      .then(registration => {
        console.log('ServiceWorker registration successful with scope: ', registration.scope);
      })
      .catch(error => {
        console.error('ServiceWorker registration failed: ', error);
      });
  }
});
</script>

<style lang="scss">
// Use modern Sass directive with explicit namespace
@use '@/assets/styles/main.scss';

// Variables
$primary-color: #f96302; // Home Depot orange
$secondary-color: #0a5ca7; // Home Depot blue
$light-gray: #f8f9fa;
$dark-gray: #333;
$white: #fff;
$breakpoint-md: 768px;
$breakpoint-sm: 576px;

// Reset
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: $dark-gray;
  line-height: 1.6;
  font-size: 16px;
  
  &.no-scroll {
    overflow: hidden;
  }
}

// Container
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 15px;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

main {
  flex: 1;
  padding: 20px 0;
}

// Header
.header {
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.top-banner {
  background-color: $primary-color;
  color: $white;
  padding: 8px 0;
  text-align: center;
  font-weight: bold;
}

.header-main {
  display: flex;
  align-items: center;
  padding: 15px;
  flex-wrap: wrap;
  
  .logo {
    margin-right: 20px;
    
    h1 {
      color: $primary-color;
      font-size: 28px;
      margin: 0;
    }
    
    a {
      text-decoration: none;
    }
  }
  
  .search-bar {
    flex: 1;
    display: flex;
    max-width: 600px;
    margin: 0 20px;
    
    input {
      flex: 1;
      padding: 10px 15px;
      border: 2px solid #ddd;
      border-right: none;
      border-radius: 4px 0 0 4px;
      font-size: 16px;
      
      &:focus {
        outline: none;
        border-color: $primary-color;
      }
    }
    
    .search-button {
      background-color: $primary-color;
      color: $white;
      border: none;
      border-radius: 0 4px 4px 0;
      padding: 0 15px;
      cursor: pointer;
    }
  }
  
  .header-actions {
    display: flex;
    align-items: center;
    
    button {
      background: none;
      border: none;
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-left: 15px;
      cursor: pointer;
      font-size: 14px;
      
      .icon {
        font-size: 20px;
        margin-bottom: 5px;
      }
    }
  }
  
  .mobile-menu-btn {
    display: none;
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
  }
}

.main-nav {
  background-color: $secondary-color;
  padding: 10px 0;
  
  .nav-list {
    list-style: none;
    display: flex;
    margin: 0;
    padding: 0;
    
    li {
      margin-right: 20px;
      
      a {
        color: $white;
        text-decoration: none;
        font-weight: bold;
        padding: 5px 10px;
        
        &:hover, &.router-link-active {
          background-color: rgba(255, 255, 255, 0.2);
          border-radius: 4px;
        }
      }
    }
  }
}

// Footer
.footer {
  background-color: $dark-gray;
  color: $white;
  padding: 40px 0 20px;
  margin-top: auto;
  
  a {
    color: #ccc;
    text-decoration: none;
    
    &:hover {
      color: $white;
      text-decoration: underline;
    }
  }
  
  .footer-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 30px;
    margin-bottom: 30px;
  }
  
  .footer-section {
    h4 {
      color: $white;
      margin-bottom: 15px;
      font-size: 18px;
    }
    
    ul {
      list-style: none;
      
      li {
        margin-bottom: 10px;
      }
    }
  }
  
  .social-icons {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    
    a {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 36px;
      height: 36px;
      background-color: rgba(255, 255, 255, 0.1);
      border-radius: 50%;
      
      &:hover {
        background-color: $primary-color;
      }
    }
  }
  
  .app-downloads {
    margin-top: 15px;
    
    p {
      margin-bottom: 10px;
    }
    
    .app-links {
      display: flex;
      gap: 10px;
      
      a {
        display: inline-block;
        padding: 8px 12px;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        
        &:hover {
          background-color: $primary-color;
          text-decoration: none;
        }
      }
    }
  }
  
  .footer-bottom {
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding-top: 20px;
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    
    p {
      margin: 0;
    }
    
    .footer-links {
      display: flex;
      gap: 20px;
    }
  }
}

// Responsive styles
@media (max-width: $breakpoint-md) {
  .header-main {
    .search-bar {
      order: 3;
      margin: 15px 0 0;
      max-width: 100%;
      width: 100%;
    }
    
    .header-actions {
      margin-left: auto;
      
      button .text {
        display: none;
      }
    }
  }
  
  .main-nav .nav-list {
    flex-wrap: wrap;
    
    li {
      margin-bottom: 10px;
    }
  }
  
  .footer-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .footer-bottom {
    flex-direction: column;
    text-align: center;
    
    p {
      margin-bottom: 15px;
    }
  }
}

@media (max-width: $breakpoint-sm) {
  .header-main {
    justify-content: space-between;
    
    .logo {
      margin-right: 0;
    }
    
    .mobile-menu-btn {
      display: block;
    }
    
    .header-actions {
      display: none;
    }
  }
  
  .main-nav {
    display: none;
  }
  
  .footer-grid {
    grid-template-columns: 1fr;
  }
}
</style>
