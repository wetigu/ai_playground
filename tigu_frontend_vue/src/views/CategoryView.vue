<template>
  <main class="category-view">
    <div class="container">
      <div class="category-header">
        <h1>{{ categoryTitle }}</h1>
        <p v-if="categoryDescription">{{ categoryDescription }}</p>
      </div>

      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="error" class="error-container">
        <p>{{ error }}</p>
        <button @click="fetchCategoryProducts" class="retry-button">重试</button>
      </div>

      <div v-else-if="products.length === 0" class="empty-container">
        <div class="empty-state">
          <img src="@/assets/icons/empty-box.svg" alt="No products" class="empty-icon" />
          <h2>暂无产品</h2>
          <p>该分类下暂时没有产品，请稍后再试或浏览其他分类。</p>
          <router-link to="/" class="btn-primary">返回首页</router-link>
        </div>
      </div>

      <div v-else class="products-grid">
        <div v-for="product in products" :key="product.id" class="product-card">
          <div class="product-image">
            <img :src="product.image_url" :alt="product.name" />
          </div>
          <div class="product-info">
            <h3>{{ product.name }}</h3>
            <p class="product-description">{{ product.description }}</p>
            <div class="product-price">
              ¥{{ product.price.toFixed(2) }}
            </div>
            <button class="add-to-cart-btn" @click="addToCart(product)">加入购物车</button>
          </div>
        </div>
      </div>

      <div v-if="products.length > 0" class="pagination">
        <button 
          :disabled="currentPage === 1" 
          @click="changePage(currentPage - 1)"
          class="pagination-btn"
        >
          上一页
        </button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button 
          :disabled="currentPage === totalPages" 
          @click="changePage(currentPage + 1)"
          class="pagination-btn"
        >
          下一页
        </button>
      </div>
    </div>
  </main>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/services/api';
import { Product, Category, PaginatedResponse } from '@/types';

export default defineComponent({
  name: 'CategoryView',
  
  setup() {
    const route = useRoute();
    const loading = ref(true);
    const error = ref('');
    const products = ref<Product[]>([]);
    const category = ref<Category | null>(null);
    const currentPage = ref(1);
    const totalPages = ref(1);
    const perPage = 12;
    
    const categoryTitle = computed(() => {
      return category.value?.name || '建材产品';
    });
    
    const categoryDescription = computed(() => {
      return category.value?.description || '';
    });
    
    const categorySlug = computed(() => {
      return route.params.slug as string;
    });

    const fetchCategoryProducts = async () => {
      loading.value = true;
      error.value = '';
      
      try {
        // First get the category details
        const categoryResponse = await api.get<Category>(`/categories/${categorySlug.value}`);
        category.value = categoryResponse.data;
        
        // Then fetch products in that category with pagination
        const productsResponse = await api.get<PaginatedResponse<Product>>('/products', {
          params: {
            category_slug: categorySlug.value,
            page: currentPage.value,
            per_page: perPage
          }
        });
        
        products.value = productsResponse.data.items;
        totalPages.value = Math.ceil(productsResponse.data.total / perPage);
      } catch (err) {
        console.error('Error fetching category products:', err);
        error.value = '获取产品数据失败，请稍后再试';
      } finally {
        loading.value = false;
      }
    };
    
    const changePage = (page: number) => {
      currentPage.value = page;
    };
    
    const addToCart = (product: Product) => {
      // Implement cart functionality here or emit an event
      console.log('Adding to cart:', product);
      // This would typically call a store action
    };
    
    // Fetch products when component mounts
    onMounted(fetchCategoryProducts);
    
    // Refetch when route params change (different category)
    watch(() => route.params.slug, fetchCategoryProducts);
    
    // Refetch when page changes
    watch(currentPage, fetchCategoryProducts);
    
    return {
      loading,
      error,
      products,
      categoryTitle,
      categoryDescription,
      currentPage,
      totalPages,
      fetchCategoryProducts,
      changePage,
      addToCart
    };
  }
});
</script>

<style scoped>
.category-view {
  padding: 2rem 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.category-header {
  margin-bottom: 2rem;
  text-align: center;
}

.category-header h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.loading-spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 4px solid #3498db;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container {
  text-align: center;
  padding: 2rem;
  background-color: #fff3f3;
  border-radius: 8px;
  margin: 2rem 0;
}

.retry-button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}

.empty-container {
  text-align: center;
  padding: 3rem 0;
}

.empty-state {
  max-width: 400px;
  margin: 0 auto;
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin-bottom: 1rem;
}

.btn-primary {
  display: inline-block;
  background-color: #3498db;
  color: white;
  text-decoration: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  margin-top: 1rem;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 2rem;
}

.product-card {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.product-card:hover {
  transform: translateY(-5px);
}

.product-image {
  height: 200px;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.product-card:hover .product-image img {
  transform: scale(1.05);
}

.product-info {
  padding: 1rem;
}

.product-info h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.product-description {
  color: #666;
  font-size: 0.9rem;
  height: 3em;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-price {
  font-size: 1.2rem;
  font-weight: bold;
  color: #e74c3c;
  margin: 0.5rem 0;
}

.add-to-cart-btn {
  width: 100%;
  padding: 0.5rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.add-to-cart-btn:hover {
  background-color: #2980b9;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 2rem;
}

.pagination-btn {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin: 0 0.5rem;
}

.pagination-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.page-info {
  margin: 0 1rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 1rem;
  }
  
  .product-image {
    height: 160px;
  }
  
  .product-info h3 {
    font-size: 1rem;
  }
}
</style> 