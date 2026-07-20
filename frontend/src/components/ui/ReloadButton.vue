<template>
  <button type="button" class="reload-btn" :disabled="loading" @click="$emit('reload')">
    <span class="reload-icon" :class="{ spinning: loading }">↻</span>
    Reload
  </button>
</template>

<script>
export default {
  name: 'ReloadButton',
  props: {
    loading: { type: Boolean, default: false }
  },
  emits: ['reload']
}
</script>

<style scoped>
.reload-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 999px;
  border: 2px solid var(--primary-dark);
  background: #fff;
  color: var(--primary-dark);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.reload-btn:disabled {
  opacity: 0.65;
  cursor: wait;
}

.reload-btn:not(:disabled):active {
  transform: scale(0.98);
}

.reload-icon {
  display: inline-block;
  font-size: 16px;
  line-height: 1;
}

.reload-icon.spinning {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
