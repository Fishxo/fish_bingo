<template>
  <div class="app-shell">
    <main class="shell-content">
      <router-view />
    </main>
    <BottomNav :active-tab="activeTab" />
  </div>
</template>

<script>
import BottomNav from './BottomNav.vue'

export default {
  name: 'AppShell',
  components: { BottomNav },
  computed: {
    activeTab() {
      return this.$route.meta?.navTab || 'game'
    }
  }
}
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: var(--primary-light);
}

.shell-content {
  min-height: 100vh;
  padding-bottom: calc(88px + env(safe-area-inset-bottom, 0px));
}
</style>
