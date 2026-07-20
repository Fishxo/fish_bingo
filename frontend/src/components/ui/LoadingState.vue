<template>
  <div class="loading-state">
    <div class="spinner" aria-hidden="true"></div>
    <p>{{ message }}</p>
  </div>
</template>

<script>
export default {
  name: 'LoadingState',
  props: {
    message: { type: String, default: 'Loading…' }
  }
}
</script>

<style scoped>
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 48px 20px;
  color: var(--primary-dark);
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(106, 13, 122, 0.15);
  border-top-color: var(--primary-dark);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-state p {
  font-size: 14px;
  font-weight: 600;
  opacity: 0.85;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
