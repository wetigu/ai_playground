<template>
  <div id="app">
    <header>
      <nav>
        <router-link to="/">Home</router-link> |
        <router-link to="/about">About</router-link>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
    <footer>
      <p>&copy; {{ currentYear }} Tigu Platform</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const currentYear = computed(() => new Date().getFullYear());
</script>

<style lang="scss">
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin: 0;
  padding: 0;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
  padding: 20px;
}

header {
  background-color: #f8f9fa;
  padding: 20px;
}

nav {
  padding: 10px 0;
  
  a {
    font-weight: bold;
    color: #2c3e50;
    text-decoration: none;
    margin: 0 10px;
    
    &.router-link-exact-active {
      color: #42b983;
    }
  }
}

footer {
  background-color: #f8f9fa;
  padding: 20px;
  margin-top: auto;
}
</style>
