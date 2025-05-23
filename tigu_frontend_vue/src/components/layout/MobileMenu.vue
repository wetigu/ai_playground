<template>
  <div class="mobile-menu" :class="{ 'is-active': isActive }">
    <div class="mobile-menu-overlay" @click="closeMenu"></div>
    
    <div class="mobile-menu-container">
      <div class="mobile-menu-header">
        <h2>{{ t('header.menu') || 'Menu' }}</h2>
        <button class="close-btn" @click="closeMenu">✕</button>
      </div>
      
      <div class="mobile-menu-content">
        <div class="mobile-search">
          <input type="text" :placeholder="t('header.search')" aria-label="Search">
          <button>🔍</button>
        </div>
        
        <div class="mobile-user-actions">
          <button class="user-action-btn">
            <span class="icon">👤</span>
            <span>{{ t('header.account') }}</span>
          </button>
          <button class="user-action-btn">
            <span class="icon">📍</span>
            <span>{{ t('header.storeFinder') || 'Store Finder' }}</span>
          </button>
          <button class="user-action-btn">
            <span class="icon">🛒</span>
            <span>{{ t('header.cart') }}</span>
          </button>
        </div>
        
        <nav class="mobile-nav">
          <ul class="mobile-nav-list">
            <li>
              <router-link to="./shop" @click="closeMenu">{{ t('header.products') }}</router-link>
            </li>
            <li class="expandable">
              <div class="expand-header">
                <router-link to="./departments">{{ t('header.departments') || 'Departments' }}</router-link>
                <button class="expand-btn" @click="toggleSubmenu('departments')">
                  {{ expandedMenus.includes('departments') ? '−' : '+' }}
                </button>
              </div>
              <ul v-if="expandedMenus.includes('departments')" class="submenu">
                <li><router-link to="/category/building-materials" @click="closeMenu">{{ t('home.categories.building') }}</router-link></li>
                <li><router-link to="./departments/tools" @click="closeMenu">{{ t('home.categories.tools') }}</router-link></li>
                <li><router-link to="./departments/doors-windows" @click="closeMenu">{{ t('home.categories.doors') || 'Doors & Windows' }}</router-link></li>
                <li><router-link to="./departments/furniture" @click="closeMenu">{{ t('home.categories.furniture') || 'Furniture' }}</router-link></li>
                <li><router-link to="./departments/lighting" @click="closeMenu">{{ t('home.categories.lighting') || 'Lighting' }}</router-link></li>
                <li><router-link to="./departments/electrical" @click="closeMenu">{{ t('home.categories.electrical') }}</router-link></li>
              </ul>
            </li>
            <li>
              <router-link to="./deals" @click="closeMenu">{{ t('header.deals') }}</router-link>
            </li>
            <li class="expandable">
              <div class="expand-header">
                <router-link to="./services">{{ t('header.services') }}</router-link>
                <button class="expand-btn" @click="toggleSubmenu('services')">
                  {{ expandedMenus.includes('services') ? '−' : '+' }}
                </button>
              </div>
              <ul v-if="expandedMenus.includes('services')" class="submenu">
                <li><router-link to="./services/delivery" @click="closeMenu">{{ t('home.services.delivery') }}</router-link></li>
                <li><router-link to="./services/installation" @click="closeMenu">{{ t('home.services.installation') }}</router-link></li>
                <li><router-link to="./services/project-management" @click="closeMenu">{{ t('home.services.design') }}</router-link></li>
              </ul>
            </li>
            <li>
              <router-link to="./ideas" @click="closeMenu">{{ t('header.diy') }}</router-link>
            </li>
          </ul>
        </nav>
        
        <div class="language-switcher-container">
          <LanguageSwitcher />
        </div>
      </div>
      
      <div class="mobile-menu-footer">
        <div class="contact-info">
          <h3>{{ t('footer.customerService') }}</h3>
          <p>1-800-555-1234</p>
          <p>{{ t('footer.businessHours') || 'Mon-Sat: 8am-9pm, Sun: 9am-6pm' }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import LanguageSwitcher from '@/components/LanguageSwitcher.vue';

const { t } = useI18n();
const { isActive } = defineProps<{
  isActive: boolean
}>();

const emits = defineEmits(['close']);

const expandedMenus = ref<string[]>([]);

function toggleSubmenu(menuId: string) {
  if (expandedMenus.value.includes(menuId)) {
    expandedMenus.value = expandedMenus.value.filter(id => id !== menuId);
  } else {
    expandedMenus.value.push(menuId);
  }
}

function closeMenu() {
  emits('close');
}
</script>

<style scoped lang="scss">
// Variables
$primary-color: #f96302; // Home Depot orange
$secondary-color: #0a5ca7; // Home Depot blue
$white: #fff;
$dark-gray: #333;
$light-gray: #f8f9fa;
$border-color: #e0e0e0;
$animation-duration: 0.3s;

.mobile-menu {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000;
  visibility: hidden;
  
  &.is-active {
    visibility: visible;
    
    .mobile-menu-overlay {
      opacity: 1;
    }
    
    .mobile-menu-container {
      transform: translateX(0);
    }
  }
}

.mobile-menu-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  opacity: 0;
  transition: opacity $animation-duration ease;
}

.mobile-menu-container {
  position: absolute;
  top: 0;
  right: 0;
  width: 85%;
  max-width: 350px;
  height: 100%;
  background-color: $white;
  transform: translateX(100%);
  transition: transform $animation-duration ease;
  display: flex;
  flex-direction: column;
}

.mobile-menu-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid $border-color;
  
  h2 {
    margin: 0;
    font-size: 20px;
    color: $dark-gray;
  }
  
  .close-btn {
    background: none;
    border: none;
    font-size: 24px;
    color: $dark-gray;
    cursor: pointer;
  }
}

.mobile-menu-content {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
}

.mobile-search {
  margin-bottom: 20px;
  display: flex;
  
  input {
    flex: 1;
    padding: 10px 15px;
    border: 1px solid $border-color;
    border-right: none;
    border-radius: 4px 0 0 4px;
    font-size: 16px;
    
    &:focus {
      outline: none;
      border-color: $primary-color;
    }
  }
  
  button {
    background-color: $primary-color;
    color: $white;
    border: none;
    padding: 0 15px;
    border-radius: 0 4px 4px 0;
    cursor: pointer;
  }
}

.mobile-user-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
  
  .user-action-btn {
    flex: 1;
    min-width: 100px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 10px;
    background-color: $light-gray;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    
    .icon {
      font-size: 24px;
      margin-bottom: 5px;
    }
    
    span {
      font-size: 14px;
    }
    
    &:hover {
      background-color: #e8e9eb; /* Slightly darker shade of light gray */
    }
  }
}

.mobile-nav {
  .mobile-nav-list {
    list-style: none;
    padding: 0;
    margin: 0;
    
    > li {
      border-bottom: 1px solid $border-color;
      
      > a, .expand-header > a {
        display: block;
        padding: 15px;
        color: $dark-gray;
        text-decoration: none;
        font-weight: bold;
        
        &:hover, &.router-link-active {
          color: $primary-color;
        }
      }
      
      &.expandable {
        .expand-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          
          a {
            flex: 1;
          }
          
          .expand-btn {
            background: none;
            border: none;
            font-size: 24px;
            color: $dark-gray;
            padding: 0 15px;
            cursor: pointer;
          }
        }
        
        .submenu {
          list-style: none;
          padding: 0;
          margin: 0;
          background-color: $light-gray;
          
          li {
            a {
              display: block;
              padding: 12px 15px 12px 30px;
              color: $dark-gray;
              text-decoration: none;
              
              &:hover, &.router-link-active {
                color: $primary-color;
              }
            }
          }
        }
      }
    }
  }
}

.mobile-menu-footer {
  padding: 15px;
  background-color: $light-gray;
  border-top: 1px solid $border-color;
  
  .contact-info {
    text-align: center;
    
    h3 {
      margin: 0 0 10px 0;
      font-size: 16px;
      color: $dark-gray;
    }
    
    p {
      margin: 0 0 5px 0;
      font-size: 14px;
      color: #666;
    }
  }
}

.language-switcher-container {
  margin-top: 20px;
  padding: 10px 0;
  border-top: 1px solid $border-color;
}
</style> 