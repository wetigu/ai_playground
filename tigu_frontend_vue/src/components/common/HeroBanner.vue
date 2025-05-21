<template>
  <section class="hero-banner" :style="backgroundStyle">
    <div class="container">
      <div class="hero-content">
        <h1 v-if="title">{{ title }}</h1>
        <h2 v-if="subtitle">{{ subtitle }}</h2>
        <p v-if="description">{{ description }}</p>
        <router-link v-if="buttonText && buttonLink" :to="buttonLink" class="btn btn-primary">
          {{ buttonText }}
        </router-link>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  backgroundImage?: string;
  title?: string;
  subtitle?: string;
  description?: string;
  buttonText?: string;
  buttonLink?: string;
}

const props = withDefaults(defineProps<Props>(), {
  backgroundImage: '/images/hero-bg.jpg',
  title: '',
  subtitle: '',
  description: '',
  buttonText: '',
  buttonLink: '/'
});

const backgroundStyle = computed(() => {
  return {
    background: `linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url(${props.backgroundImage}) center/cover no-repeat`
  };
});
</script>

<style scoped lang="scss">
$primary-color: #f96302; // Home Depot orange
$white: #fff;
$breakpoint-md: 768px;
$breakpoint-sm: 576px;

.hero-banner {
  color: $white;
  padding: 100px 0;
  text-align: center;
  
  .hero-content {
    max-width: 600px;
    margin: 0 auto;
    
    h1 {
      font-size: 48px;
      margin-bottom: 10px;
    }
    
    h2 {
      font-size: 32px;
      margin-bottom: 20px;
    }
    
    p {
      font-size: 18px;
      margin-bottom: 30px;
    }
  }
  
  .btn {
    display: inline-block;
    padding: 12px 24px;
    border-radius: 4px;
    font-weight: bold;
    text-decoration: none;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &.btn-primary {
      background-color: $primary-color;
      color: $white;
      
      &:hover {
        background-color: darken($primary-color, 10%);
      }
    }
  }
}

@media (max-width: $breakpoint-md) {
  .hero-banner {
    padding: 60px 0;
    
    .hero-content {
      h1 {
        font-size: 36px;
      }
      
      h2 {
        font-size: 24px;
      }
    }
  }
}

@media (max-width: $breakpoint-sm) {
  .hero-banner {
    padding: 40px 0;
    
    .hero-content {
      h1 {
        font-size: 28px;
      }
      
      h2 {
        font-size: 20px;
      }
      
      p {
        font-size: 16px;
      }
    }
  }
}
</style> 