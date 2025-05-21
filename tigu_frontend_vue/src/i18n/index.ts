import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import zh from './locales/zh.json'

export type MessageSchema = typeof en

// Detect user's preferred language
function getPreferredLanguage(): 'en' | 'zh' {
  // First check localStorage
  const savedLanguage = localStorage.getItem('language') as 'en' | 'zh' | null;
  if (savedLanguage && ['en', 'zh'].includes(savedLanguage)) {
    return savedLanguage as 'en' | 'zh';
  }

  // Then check browser language
  const browserLang = navigator.language.split('-')[0];
  if (browserLang === 'zh') {
    return 'zh';
  }

  // Default to English
  return 'en';
}

const i18n = createI18n({
  legacy: false,
  locale: getPreferredLanguage(),
  fallbackLocale: 'en',
  messages: {
    en,
    zh
  }
})

export default i18n 