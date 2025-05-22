<template>
  <div class="home">
    <!-- Hero Banner -->
    <HeroBanner 
      :title="t('home.hero.title')"
      :subtitle="t('home.hero.subtitle')"
      :description="t('home.heroBannerDesc') || 'Shop now for the best deals on construction materials'"
      :buttonText="t('home.hero.shopNow')"
      buttonLink="./shop"
    />

    <!-- Categories Section -->
    <section class="categories-section">
      <div class="container">
        <h2 class="section-title">{{ t('home.categories.title') }}</h2>
        <div class="category-grid">
          <div class="category-card">
            <div class="category-img">🧱</div>
            <h3>{{ t('home.categories.building') }}</h3>
            <router-link to="./category/building-materials">{{ t('home.hero.shopNow') }}</router-link>
          </div>
          <div class="category-card">
            <div class="category-img">🔨</div>
            <h3>{{ t('home.categories.tools') }}</h3>
            <router-link to="./category/tools">{{ t('home.hero.shopNow') }}</router-link>
          </div>
          <div class="category-card">
            <div class="category-img">🚪</div>
            <h3>{{ t('home.categories.doors') }}</h3>
            <router-link to="./category/doors-windows">{{ t('home.hero.shopNow') }}</router-link>
          </div>
          <div class="category-card">
            <div class="category-img">🪑</div>
            <h3>{{ t('home.categories.furniture') }}</h3>
            <router-link to="./category/furniture">{{ t('home.hero.shopNow') }}</router-link>
          </div>
          <div class="category-card">
            <div class="category-img">💡</div>
            <h3>{{ t('home.categories.lighting') }}</h3>
            <router-link to="./category/lighting">{{ t('home.hero.shopNow') }}</router-link>
          </div>
          <div class="category-card">
            <div class="category-img">🔌</div>
            <h3>{{ t('home.categories.electrical') }}</h3>
            <router-link to="./category/electrical">{{ t('home.hero.shopNow') }}</router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- Deals Section -->
    <section class="deals-section">
      <div class="container">
        <h2 class="section-title">{{ t('home.deals.title') }}</h2>
        <div class="deals-grid">
          <ProductCard
            :price="960"
            :originalPrice="1200"
            title="Structural Steel"
            :discount="20"
            :rating="4.5"
            :reviewCount="128"
            :availability="t('products.inStock')"
            @add-to-cart="addToCart"
            @toggle-favorite="toggleFavorite"
          />
          <ProductCard
            :price="509"
            :originalPrice="599"
            title="Power Tool Set"
            :discount="15"
            :rating="4.8"
            :reviewCount="95"
            availability="Limited Stock"
            @add-to-cart="addToCart"
            @toggle-favorite="toggleFavorite"
          />
          <ProductCard
            :price="33.75"
            :originalPrice="45"
            title="Premium Lumber"
            :discount="25"
            :rating="4.2"
            :reviewCount="67"
            :availability="t('products.inStock')"
            @add-to-cart="addToCart"
            @toggle-favorite="toggleFavorite"
          />
          <ProductCard
            :price="245"
            :originalPrice="350"
            title="Bathroom Fixtures"
            :discount="30"
            :rating="4.7"
            :reviewCount="42"
            :availability="t('products.inStock')"
            @add-to-cart="addToCart"
            @toggle-favorite="toggleFavorite"
          />
        </div>
      </div>
    </section>

    <!-- Services Section -->
    <section class="services-section">
      <div class="container">
        <h2 class="section-title">{{ t('home.services.title') }}</h2>
        <div class="services-grid">
          <div class="service-card">
            <div class="service-icon">🚚</div>
            <h3>{{ t('home.services.delivery') }}</h3>
            <p>{{ t('home.services.deliveryDesc') || 'Get your materials delivered to your job site' }}</p>
            <router-link to="./services/delivery" class="btn btn-outline">{{ t('home.learnMore') || 'Learn More' }}</router-link>
          </div>
          <div class="service-card">
            <div class="service-icon">🛠️</div>
            <h3>{{ t('home.services.installation') }}</h3>
            <p>{{ t('home.services.installationDesc') || 'Professional installation services' }}</p>
            <router-link to="./services/installation" class="btn btn-outline">{{ t('home.learnMore') || 'Learn More' }}</router-link>
          </div>
          <div class="service-card">
            <div class="service-icon">📋</div>
            <h3>{{ t('home.services.design') }}</h3>
            <p>{{ t('home.services.designDesc') || 'Let us help you manage your construction project' }}</p>
            <router-link to="./services/project-management" class="btn btn-outline">{{ t('home.learnMore') || 'Learn More' }}</router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- Newsletter Section -->
    <section class="newsletter-section">
      <div class="container">
        <div class="newsletter-content">
          <h2>{{ t('home.newsletter.title') || 'Sign Up for Our Newsletter' }}</h2>
          <p>{{ t('home.newsletter.subtitle') || 'Get the latest deals and product updates' }}</p>
          <div class="newsletter-form">
            <input type="email" :placeholder="t('home.newsletter.emailPlaceholder') || 'Enter your email'">
            <button class="btn btn-primary">{{ t('home.newsletter.subscribe') || 'Subscribe' }}</button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import HeroBanner from '@/components/common/HeroBanner.vue';
import ProductCard from '@/components/common/ProductCard.vue';

const { t } = useI18n();

// Event handlers
function addToCart() {
  console.log('Product added to cart');
}

function toggleFavorite() {
  console.log('Product favorite toggled');
}
</script>

<style scoped lang="scss">
// Variables
$primary-color: #f96302; // Home Depot orange
$secondary-color: #0a5ca7; // Home Depot blue
$light-gray: #f8f9fa;
$dark-gray: #333;
$white: #fff;
$breakpoint-md: 768px;
$breakpoint-sm: 576px;

.home {
  margin: 0;
  padding: 0;
}

// Buttons
.btn {
  display: inline-block;
  padding: 12px 24px;
  border-radius: 4px;
  font-weight: bold;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  
  &.btn-primary {
    background-color: $primary-color;
    color: $white;
    
    &:hover {
      background-color: #e05602; /* Darker shade of primary color */
    }
  }
  
  &.btn-secondary {
    background-color: $secondary-color;
    color: $white;
    
    &:hover {
      background-color: #084a86; /* Darker shade of secondary color */
    }
  }
  
  &.btn-outline {
    background-color: transparent;
    border: 2px solid $primary-color;
    color: $primary-color;
    
    &:hover {
      background-color: $primary-color;
      color: $white;
    }
  }
}

// Section styling
.section-title {
  font-size: 28px;
  margin-bottom: 30px;
  text-align: center;
  position: relative;
  
  &:after {
    content: '';
    display: block;
    width: 60px;
    height: 4px;
    background-color: $primary-color;
    margin: 10px auto 0;
  }
}

// Categories section
.categories-section {
  padding: 60px 0;
  background-color: $white;
  
  .category-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 20px;
  }
  
  .category-card {
    text-align: center;
    padding: 20px;
    border-radius: 8px;
    background-color: $light-gray;
    transition: transform 0.3s ease;
    
    &:hover {
      transform: translateY(-10px);
    }
    
    .category-img {
      font-size: 48px;
      margin-bottom: 15px;
    }
    
    h3 {
      font-size: 18px;
      margin-bottom: 10px;
    }
    
    a {
      color: $secondary-color;
      font-weight: bold;
      text-decoration: none;
      
      &:hover {
        text-decoration: underline;
      }
    }
  }
}

// Deals section
.deals-section {
  padding: 60px 0;
  background-color: #f0f0f0;
  
  .deals-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 30px;
  }
}

// Services section
.services-section {
  padding: 60px 0;
  background-color: $white;
  
  .services-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 30px;
  }
  
  .service-card {
    text-align: center;
    padding: 30px;
    border: 2px solid $light-gray;
    border-radius: 8px;
    transition: all 0.3s ease;
    
    &:hover {
      border-color: $primary-color;
    }
    
    .service-icon {
      font-size: 60px;
      margin-bottom: 20px;
    }
    
    h3 {
      font-size: 22px;
      margin-bottom: 15px;
    }
    
    p {
      margin-bottom: 20px;
      color: #666;
    }
  }
}

// Newsletter
.newsletter-section {
  padding: 60px 0;
  background-color: $secondary-color;
  color: $white;
  
  .newsletter-content {
    max-width: 600px;
    margin: 0 auto;
    text-align: center;
    
    h2 {
      font-size: 32px;
      margin-bottom: 10px;
    }
    
    p {
      font-size: 18px;
      margin-bottom: 30px;
    }
    
    .newsletter-form {
      display: flex;
      
      input {
        flex: 1;
        padding: 12px 15px;
        border: none;
        border-radius: 4px 0 0 4px;
        font-size: 16px;
      }
      
      .btn {
        border-radius: 0 4px 4px 0;
      }
    }
  }
}

// Responsive styles
@media (max-width: $breakpoint-md) {
  .category-grid {
    grid-template-columns: repeat(3, 1fr) !important;
  }
  
  .deals-grid {
    grid-template-columns: repeat(2, 1fr) !important;
  }
  
  .services-grid {
    grid-template-columns: repeat(2, 1fr) !important;
  }
}

@media (max-width: $breakpoint-sm) {
  .category-grid {
    grid-template-columns: repeat(2, 1fr) !important;
  }
  
  .deals-grid, 
  .services-grid {
    grid-template-columns: 1fr !important;
  }
  
  .newsletter-form {
    flex-direction: column;
    
    input {
      border-radius: 4px !important;
      margin-bottom: 10px;
    }
    
    .btn {
      border-radius: 4px !important;
    }
  }
}
</style>
