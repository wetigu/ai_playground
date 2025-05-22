<template>
  <div class="product-card">
    <div v-if="discount" class="discount-badge">{{ discount }}% {{ t('products.off') || 'OFF' }}</div>
    <div v-if="isFavorite" class="favorite-icon">❤️</div>
    <div v-if="isNew" class="new-badge">{{ t('products.new') || 'NEW' }}</div>
    
    <div class="product-image" :style="productImageStyle">
      <div class="quick-view">
        <button @click="$emit('quick-view')">{{ t('products.quickView') || 'Quick View' }}</button>
      </div>
    </div>
    
    <div class="product-details">
      <div class="ratings" v-if="rating">
        <div class="stars" :style="{ '--rating': rating }"></div>
        <span v-if="reviewCount">({{ reviewCount }})</span>
      </div>
      
      <h3 class="product-title">{{ title }}</h3>
      <p class="product-brand" v-if="brand">{{ brand }}</p>
      
      <div class="product-price">
        <span v-if="originalPrice && originalPrice > price" class="original-price">${{ originalPrice.toFixed(2) }}</span>
        <span class="current-price">${{ price.toFixed(2) }}</span>
        <span v-if="unit" class="price-unit">/ {{ unit }}</span>
      </div>
      
      <div class="product-availability" v-if="availability">
        <span :class="['availability', availabilityClass]">{{ availability }}</span>
      </div>
      
      <div class="product-actions">
        <button class="btn-add-cart" @click="$emit('add-to-cart')">{{ t('products.addToCart') }}</button>
        <button class="btn-favorite" @click="$emit('toggle-favorite')">
          <span v-if="isFavorite">❤️</span>
          <span v-else>🤍</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

interface Props {
  imageUrl?: string;
  title: string;
  brand?: string;
  price: number;
  originalPrice?: number;
  unit?: string;
  discount?: number;
  rating?: number;
  reviewCount?: number;
  availability?: string;
  isFavorite?: boolean;
  isNew?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  imageUrl: '',
  title: 'Product Title',
  brand: '',
  price: 0,
  originalPrice: 0,
  unit: '',
  discount: 0,
  rating: 0,
  reviewCount: 0,
  availability: '',
  isFavorite: false,
  isNew: false
});

const productImageStyle = computed(() => {
  if (props.imageUrl) {
    return { backgroundImage: `url(${props.imageUrl})` };
  }
  return { backgroundColor: '#f0f0f0' };
});

const availabilityClass = computed(() => {
  if (!props.availability) return '';
  
  const avail = props.availability.toLowerCase();
  if (avail.includes(t('products.inStock').toLowerCase())) {
    return 'in-stock';
  } else if (avail.includes(t('products.outOfStock').toLowerCase())) {
    return 'out-of-stock';
  } else if (avail.includes(t('products.limitedStock').toLowerCase())) {
    return 'limited';
  }
  
  return '';
});

defineEmits(['add-to-cart', 'toggle-favorite', 'quick-view']);
</script>

<style scoped lang="scss">
// Variables
$primary-color: #f96302; // Home Depot orange
$secondary-color: #0a5ca7; // Home Depot blue
$light-gray: #f8f9fa;
$dark-gray: #333;
$white: #fff;
$border-color: #e0e0e0;
$star-color: #ffc107;

.product-card {
  position: relative;
  background-color: $white;
  border: 1px solid $border-color;
  border-radius: 8px;
  padding: 0;
  transition: all 0.3s ease;
  overflow: hidden;
  
  &:hover {
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    transform: translateY(-5px);
    
    .quick-view {
      opacity: 1;
    }
  }
  
  .discount-badge {
    position: absolute;
    top: 10px;
    right: 10px;
    background-color: $primary-color;
    color: $white;
    font-weight: bold;
    padding: 5px 10px;
    border-radius: 4px;
    z-index: 1;
  }
  
  .favorite-icon {
    position: absolute;
    top: 10px;
    left: 10px;
    z-index: 1;
    font-size: 24px;
  }
  
  .new-badge {
    position: absolute;
    top: 10px;
    left: 10px;
    background-color: $secondary-color;
    color: $white;
    font-weight: bold;
    padding: 5px 10px;
    border-radius: 4px;
    z-index: 1;
  }
}

.product-image {
  height: 200px;
  background-position: center;
  background-size: contain;
  background-repeat: no-repeat;
  border-bottom: 1px solid $border-color;
  position: relative;
  
  .quick-view {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 10px;
    background-color: rgba(0, 0, 0, 0.7);
    text-align: center;
    opacity: 0;
    transition: opacity 0.3s ease;
    
    button {
      background-color: $white;
      color: $dark-gray;
      border: none;
      padding: 8px 15px;
      border-radius: 4px;
      font-weight: bold;
      cursor: pointer;
      
      &:hover {
        background-color: $primary-color;
        color: $white;
      }
    }
  }
}

.product-details {
  padding: 15px;
  
  .ratings {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    
    .stars {
      position: relative;
      display: inline-block;
      font-family: Arial, sans-serif;
      color: #ddd;
      
      &:before {
        content: "★★★★★";
        font-size: 18px;
      }
      
      &:after {
        content: "★★★★★";
        font-size: 18px;
        position: absolute;
        left: 0;
        top: 0;
        color: $star-color;
        overflow: hidden;
        width: calc(var(--rating) * 20%);
      }
    }
    
    span {
      margin-left: 5px;
      color: #777;
      font-size: 14px;
    }
  }
  
  .product-title {
    font-size: 16px;
    margin: 0 0 5px 0;
    font-weight: 500;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  .product-brand {
    font-size: 14px;
    color: #777;
    margin: 0 0 10px 0;
  }
  
  .product-price {
    margin-bottom: 10px;
    
    .original-price {
      color: #999;
      text-decoration: line-through;
      font-size: 14px;
      margin-right: 5px;
    }
    
    .current-price {
      color: $primary-color;
      font-size: 20px;
      font-weight: bold;
    }
    
    .price-unit {
      font-size: 14px;
      color: #777;
    }
  }
  
  .product-availability {
    margin-bottom: 15px;
    
    .availability {
      display: inline-block;
      font-size: 14px;
      padding: 2px 8px;
      border-radius: 4px;
      
      &.in-stock {
        color: #2e7d32;
        background-color: #e8f5e9;
      }
      
      &.out-of-stock {
        color: #d32f2f;
        background-color: #ffebee;
      }
      
      &.limited {
        color: #ed6c02;
        background-color: #fff3e0;
      }
    }
  }
  
  .product-actions {
    display: flex;
    gap: 10px;
    
    .btn-add-cart {
      flex: 1;
      background-color: $primary-color;
      color: $white;
      border: none;
      padding: 10px;
      border-radius: 4px;
      font-weight: bold;
      cursor: pointer;
      transition: background-color 0.3s ease;
      
      &:hover {
        background-color: #e05602; /* Darker shade of primary color instead of using darken() */
      }
    }
    
    .btn-favorite {
      width: 40px;
      background-color: $white;
      border: 1px solid $border-color;
      border-radius: 4px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      
      &:hover {
        border-color: $primary-color;
      }
    }
  }
}

@media (max-width: 768px) {
  .product-image {
    height: 180px;
  }
  
  .product-details {
    padding: 10px;
    
    .product-title {
      font-size: 14px;
    }
    
    .product-price {
      .current-price {
        font-size: 18px;
      }
    }
  }
}
</style> 