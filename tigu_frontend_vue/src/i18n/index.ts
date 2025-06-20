import { createI18n } from 'vue-i18n'

// Use Vite's import.meta.glob to load all locale files
const localeModules = import.meta.glob('./locales/*.json', { eager: true }) as Record<string, { default: any }>

const messages: Record<string, any> = {}
for (const path in localeModules) {
  // Extract locale code from filename, e.g. './locales/en.json' -> 'en'
  const match = path.match(/([a-zA-Z0-9-_]+)\.json$/)
  if (match) {
    const locale = match[1]
    messages[locale] = localeModules[path].default
  }
}

export type MessageSchema = typeof messages['en']

// Detect user's preferred language
function getPreferredLanguage(): 'en' | 'zh' {
  // Check if we're in a browser environment
  if (typeof window === 'undefined') {
    return 'en'; // Default for SSR
  }

  try {
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
  } catch (error) {
    console.warn('Error detecting language preference:', error);
  }

  // Default to English
  return 'en';
}

// Debug: Log the imported messages and effective locale
console.log('[i18n Debug] Loaded messages:', messages);
const effectiveLocale = getPreferredLanguage();
console.log('[i18n Debug] Effective locale for createI18n:', effectiveLocale);

const i18n = createI18n({
  legacy: false,
  locale: effectiveLocale,
  fallbackLocale: 'en',
  messages,
  // Add for easier debugging in browser
  warnHtmlMessage: true,
  missingWarn: true,
  fallbackWarn: true
});

console.log('[i18n Debug] i18n instance created:', i18n.global.locale.value, i18n.global.messages.value);

export default i18n;