<template>
  <nav class="bottom-nav" aria-label="Main navigation">
    <router-link
      v-for="item in items"
      :key="item.name"
      :to="item.to"
      class="nav-item"
      :class="{ active: activeTab === item.name }"
    >
      <span class="nav-icon" v-html="item.icon"></span>
      <span class="nav-label">{{ item.label }}</span>
    </router-link>
  </nav>
</template>

<script>
export default {
  name: 'BottomNav',
  props: {
    activeTab: {
      type: String,
      default: 'game'
    }
  },
  data() {
    return {
      items: [
        {
          name: 'game',
          label: 'Game',
          to: '/home',
          icon: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 9h2v2H6V9zm0 4h2v2H6v-2zm4-4h2v2h-2V9zm0 4h2v2h-2v-2zm4-4h2v2h-2V9zm0 4h2v2h-2v-2zM4 6h16a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V8a2 2 0 012-2z"/></svg>'
        },
        {
          name: 'history',
          label: 'History',
          to: '/history',
          icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>'
        },
        {
          name: 'wallet',
          label: 'Wallet',
          to: '/wallet',
          icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="6" width="18" height="13" rx="2"/><path d="M3 10h18"/><circle cx="17" cy="14" r="1.5" fill="currentColor" stroke="none"/></svg>'
        },
        {
          name: 'profile',
          label: 'Profile',
          to: '/profile',
          icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 20c1.5-4 6-6 8-6s6.5 2 8 6"/></svg>'
        }
      ]
    }
  }
}
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
  padding: 10px 12px calc(10px + env(safe-area-inset-bottom, 0px));
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(106, 13, 122, 0.1);
  z-index: 200;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px 4px;
  border-radius: 16px;
  text-decoration: none;
  color: var(--primary-dark);
  transition: background 0.2s ease, color 0.2s ease, transform 0.15s ease;
}

.nav-item.active {
  background: var(--primary-dark);
  color: #fff;
  box-shadow: 0 6px 16px rgba(74, 8, 88, 0.25);
}

.nav-icon :deep(svg) {
  width: 22px;
  height: 22px;
  display: block;
}

.nav-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.02em;
}
</style>
