<template>
  <transition name="slide-in">
    <div v-if="showInstallPrompt" class="install-prompt">
      <div class="prompt-content">
        <div class="prompt-header">
          <img src="/pwa-192x192.png" alt="Tigu Platform" class="app-icon" />
          <div class="app-info">
            <h3>{{ t('pwa.installTitle') || 'Install Tigu Platform' }}</h3>
            <p>{{ t('pwa.installSubtitle') || 'Get our app for faster access' }}</p>
          </div>
        </div>
        <div class="prompt-actions">
          <button class="btn-install" @click="installApp">
            {{ t('pwa.installButton') || 'Install' }}
          </button>
          <button class="btn-later" @click="closePrompt">
            {{ t('pwa.laterButton') || 'Later' }}
          </button>
        </div>
        <button class="btn-close" @click="closePrompt">✕</button>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const showInstallPrompt = ref(false);
const deferredPrompt = ref<any>(null);

// Event handler for beforeinstallprompt
const handleBeforeInstallPrompt = (e: Event) => {
  // Prevent Chrome 76+ from automatically showing the prompt
  e.preventDefault();
  // Stash the event so it can be triggered later
  deferredPrompt.value = e;
  
  // Check if the user has previously dismissed or installed
  const hasPromptBeenDismissed = localStorage.getItem('pwa-install-dismissed');
  if (!hasPromptBeenDismissed) {
    // Wait a few seconds before showing the prompt
    setTimeout(() => {
      showInstallPrompt.value = true;
    }, 3000);
  }
};

// Function to install the app
const installApp = async () => {
  if (!deferredPrompt.value) return;
  
  // Show the install prompt
  deferredPrompt.value.prompt();
  
  // Wait for the user to respond to the prompt
  const choiceResult = await deferredPrompt.value.userChoice;
  
  if (choiceResult.outcome === 'accepted') {
    console.log('User accepted the install prompt');
  } else {
    console.log('User dismissed the install prompt');
  }
  
  // Clear the deferredPrompt variable
  deferredPrompt.value = null;
  showInstallPrompt.value = false;
};

// Function to close the prompt
const closePrompt = () => {
  showInstallPrompt.value = false;
  // Store in localStorage that the user has dismissed the prompt
  localStorage.setItem('pwa-install-dismissed', 'true');
};

onMounted(() => {
  // Listen for the beforeinstallprompt event
  window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
  
  // Check if the app is already installed or running as standalone
  if (window.matchMedia('(display-mode: standalone)').matches || 
      window.navigator.standalone === true) {
    // App is already installed, don't show the prompt
    return;
  }
});

onBeforeUnmount(() => {
  // Remove the event listener when component is unmounted
  window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
});
</script>

<style scoped lang="scss">
.install-prompt {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: #fff;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  border-top: 4px solid #f96302;
  padding: 15px;
}

.prompt-content {
  display: flex;
  flex-direction: column;
  max-width: 500px;
  margin: 0 auto;
  position: relative;
}

.prompt-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.app-icon {
  width: 48px;
  height: 48px;
  margin-right: 15px;
  border-radius: 8px;
}

.app-info {
  flex: 1;
  
  h3 {
    margin: 0 0 5px;
    font-size: 18px;
  }
  
  p {
    margin: 0;
    color: #666;
    font-size: 14px;
  }
}

.prompt-actions {
  display: flex;
  gap: 10px;
}

.btn-install {
  flex: 2;
  background-color: #f96302;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 10px 15px;
  font-weight: bold;
  cursor: pointer;
  
  &:hover {
    background-color: #e05602;
  }
}

.btn-later {
  flex: 1;
  background-color: transparent;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px 15px;
  cursor: pointer;
  
  &:hover {
    background-color: #f8f8f8;
  }
}

.btn-close {
  position: absolute;
  top: 0;
  right: 0;
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 5px;
  color: #666;
}

// Animation
.slide-in-enter-active,
.slide-in-leave-active {
  transition: transform 0.3s ease-out;
}

.slide-in-enter-from,
.slide-in-leave-to {
  transform: translateY(100%);
}
</style> 