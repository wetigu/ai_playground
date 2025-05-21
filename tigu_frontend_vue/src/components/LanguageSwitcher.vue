<template>
  <div class="language-switcher">
    <div class="dropdown">
      <button class="dropdown-toggle" type="button" @click="toggleDropdown">
        {{ currentLanguageLabel }}
        <span class="caret"></span>
      </button>
      <div class="dropdown-menu" v-show="showDropdown">
        <a href="#" @click.prevent="changeLanguage('en')" :class="{ active: currentLang === 'en' }">
          {{ t('language.en') }}
        </a>
        <a href="#" @click.prevent="changeLanguage('zh')" :class="{ active: currentLang === 'zh' }">
          {{ t('language.zh') }}
        </a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { locale, t } = useI18n();
const currentLang = computed(() => locale.value);
const currentLanguageLabel = computed(() => t(`language.${currentLang.value}`));
const showDropdown = ref(false);

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value;
};

const changeLanguage = (lang: string) => {
  locale.value = lang;
  showDropdown.value = false;
  
  // Save language preference to localStorage
  localStorage.setItem('language', lang);
};
</script>

<style scoped>
.language-switcher {
  position: relative;
  display: inline-block;
}

.dropdown-toggle {
  display: flex;
  align-items: center;
  background-color: transparent;
  border: none;
  cursor: pointer;
  padding: 8px 12px;
  font-size: 0.9rem;
  color: #333;
}

.caret {
  display: inline-block;
  width: 0;
  height: 0;
  margin-left: 5px;
  border-top: 4px solid;
  border-right: 4px solid transparent;
  border-left: 4px solid transparent;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  z-index: 100;
  min-width: 120px;
  background-color: white;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.dropdown-menu a {
  display: block;
  padding: 8px 12px;
  color: #333;
  text-decoration: none;
}

.dropdown-menu a:hover, 
.dropdown-menu a.active {
  background-color: #f0f0f0;
}

@media (max-width: 768px) {
  .dropdown-menu {
    right: 0;
    left: auto;
  }
}
</style> 