<template>
  <div class="timer card-selection-timer">
    <div class="timer-display">
      <span class="timer-text">{{ formattedTime }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CardSelectionTimer',
  props: {
    seconds: {
      type: Number,
      default: 0
    },
    totalSeconds: {
      type: Number,
      default: 20
    },
    gameCreatedAt: {
      type: [String, Date],
      default: null
    }
  },
  data() {
    return {
      remainingSeconds: 0,
      tickInterval: null
    }
  },
  computed: {
    formattedTime() {
      const s = Math.max(0, Math.floor(this.remainingSeconds))
      const m = Math.floor(s / 60)
      const sec = s % 60
      return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
    }
  },
  watch: {
    seconds: {
      immediate: true,
      handler(val) {
        if (!this.gameCreatedAt && val >= 0) {
          this.remainingSeconds = val
        }
      }
    },
    gameCreatedAt: {
      handler(val) {
        if (val) {
          this.updateRemaining()
        }
      }
    }
  },
  mounted() {
    this.updateRemaining()
    this.tickInterval = setInterval(() => {
      this.updateRemaining()
    }, 1000)
  },
  beforeUnmount() {
    if (this.tickInterval) {
      clearInterval(this.tickInterval)
    }
  },
  methods: {
    updateRemaining() {
      if (this.gameCreatedAt && this.totalSeconds) {
        const start = new Date(this.gameCreatedAt).getTime()
        const elapsed = (Date.now() - start) / 1000
        this.remainingSeconds = Math.max(0, this.totalSeconds - elapsed)
      } else if (this.seconds >= 0) {
        this.remainingSeconds = this.seconds
      }
    }
  }
}
</script>

<style scoped>
.card-selection-timer .timer-display {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-dark);
  background: white;
  padding: 6px 12px;
  border-radius: 10px;
  white-space: nowrap;
  box-shadow: var(--card-shadow);
  border: 2px solid var(--primary-medium);
}
.card-selection-timer .timer-text {
  font-size: 1rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
  letter-spacing: 0.02em;
}
</style>
