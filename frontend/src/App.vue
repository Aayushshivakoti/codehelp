<template>
  <div id="app">
    <!-- Floating Dark Mode Toggle -->
    <button @click="toggleTheme" class="floating-theme-toggle" :title="isDark ? 'Light Mode' : 'Dark Mode'">
      <span v-if="isDark">☀️</span>
      <span v-else>🌙</span>
    </button>
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      isDark: false
    }
  },
  mounted() {
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme === 'dark') {
      this.isDark = true
      document.body.classList.add('dark-theme')
    } else {
      this.isDark = false
      document.body.classList.remove('dark-theme')
    }
  },
  methods: {
    toggleTheme() {
      this.isDark = !this.isDark
      if (this.isDark) {
        document.body.classList.add('dark-theme')
        localStorage.setItem('theme', 'dark')
      } else {
        document.body.classList.remove('dark-theme')
        localStorage.setItem('theme', 'light')
      }
    }
  }
}
</script>

<style>
#app {
  min-height: 100vh;
  background-color: var(--bg-app, #f8fafc);
  transition: background-color 0.3s;
}
</style>