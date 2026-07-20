<template>
  <div class="empty-state">
    <div class="empty-icon" aria-hidden="true">{{ icon }}</div>
    <h3>{{ title }}</h3>
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script>
export default {
  name: 'EmptyState',
  props: {
    icon: { type: String, default: '📭' },
    title: { type: String, default: 'Nothing here yet' },
    message: { type: String, default: '' }
  }
}
</script>

<style scoped>
.empty-state {
  text-align: center;
  padding: 40px 24px;
  color: var(--primary-dark);
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.empty-state h3 {
  font-size: 16px;
  font-weight: 800;
  margin: 0 0 8px;
}

.empty-state p {
  font-size: 13px;
  opacity: 0.75;
  margin: 0;
  line-height: 1.5;
}
</style>
