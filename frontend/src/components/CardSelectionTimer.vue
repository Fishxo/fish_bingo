<template>
  <div class="timer card-selection-timer">
    <div class="timer-display">
      <span class="timer-seconds">{{ formattedSeconds }}</span>
      <span class="timer-sep">:</span>
      <span class="timer-centiseconds">{{ formattedCentiseconds }}</span>
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
      centiseconds: 0,
      tickInterval: null
    }
  },
  computed: {
    formattedSeconds() {
      return String(Math.max(0, Math.floor(this.remainingSeconds))).padStart(2, '0')
    },
    formattedCentiseconds() {
      return String(Math.min(99, Math.floor((this.remainingSeconds % 1) * 100))).padStart(2, '0')
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
    }, 50) // Update every 50ms for fast-moving centiseconds (urgency)
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
  align-items: baseline;
  gap: 2px;
  color: var(--primary-dark);
  background: white;
  padding: 6px 12px;
  border-radius: 10px;
  white-space: nowrap;
  box-shadow: var(--card-shadow);
  border: 2px solid var(--primary-medium);
}
.card-selection-timer .timer-seconds {
  font-size: 22px;
  font-weight: 700;
  line-height: 1;
}
.card-selection-timer .timer-sep {
  font-size: 18px;
  font-weight: 600;
  opacity: 0.8;
}
.card-selection-timer .timer-centiseconds {
  font-size: 13px;
  font-weight: 600;
  opacity: 0.85;
}
</style>
