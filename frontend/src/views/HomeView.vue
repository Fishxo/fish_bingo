<template>
  <div class="home-view">
    <div class="home-content">
      <section class="welcome-card">
        <div class="welcome-bg-circle c1"></div>
        <div class="welcome-bg-circle c2"></div>
        <h1>Welcome to<br>Feka Bingo</h1>
      </section>

      <div class="balance-pill" v-if="balance != null">
        <span class="pill-icon">👛</span>
        <span class="pill-amount">{{ formatMoney(balance) }}</span>
      </div>

      <section class="play-card">
        <button
          type="button"
          class="play-btn"
          :disabled="playing"
          @click="handlePlay"
        >
          <span class="play-tag">Play</span>
          <span class="play-label">{{ playing ? 'Loading…' : 'Play Game' }}</span>
        </button>
        <p v-if="playError" class="error-text">{{ playError }}</p>
      </section>
    </div>
  </div>
</template>

<script>
import { getUserBalance } from '../services/api'
import { resolvePlayGameRoute } from '../utils/playRouting'
import { formatMoney } from '../utils/format'

export default {
  name: 'HomeView',
  data() {
    return {
      balance: null,
      playing: false,
      playError: null
    }
  },
  async mounted() {
    await this.loadBalance()
  },
  methods: {
    formatMoney,
    async loadBalance() {
      try {
        const data = await getUserBalance()
        this.balance = data.balance ?? 0
      } catch {
        this.balance = 0
      }
    },
    async handlePlay() {
      if (this.playing) return
      this.playing = true
      this.playError = null
      try {
        const { path } = await resolvePlayGameRoute()
        await this.$router.push(path)
      } catch (error) {
        console.error('Play routing failed:', error)
        this.playError = error.response?.data?.error || 'Could not start game. Please try again.'
      } finally {
        this.playing = false
      }
    }
  }
}
</script>

<style scoped>
.home-view {
  min-height: 100%;
  padding: 18px 16px 24px;
}

.home-content {
  max-width: 420px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.welcome-card {
  position: relative;
  overflow: hidden;
  border-radius: 28px;
  padding: 42px 24px;
  background: linear-gradient(145deg, #6a0d7a 0%, #4a0858 55%, #3a0648 100%);
  box-shadow: var(--card-shadow-lg);
  text-align: center;
}

.welcome-bg-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
}

.welcome-bg-circle.c1 {
  width: 120px;
  height: 120px;
  top: -30px;
  left: -20px;
}

.welcome-bg-circle.c2 {
  width: 90px;
  height: 90px;
  bottom: -20px;
  right: -10px;
}

.welcome-card h1 {
  position: relative;
  z-index: 1;
  margin: 0;
  color: #fff;
  font-size: 28px;
  font-weight: 800;
  line-height: 1.25;
  letter-spacing: 0.02em;
}

.balance-pill {
  align-self: center;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 18px;
  border-radius: 999px;
  background: var(--primary-dark);
  color: #fff;
  box-shadow: var(--card-shadow);
}

.pill-icon {
  font-size: 16px;
}

.pill-amount {
  font-size: 14px;
  font-weight: 800;
}

.play-card {
  background: rgba(255, 255, 255, 0.55);
  border: 2px solid rgba(106, 13, 122, 0.18);
  border-radius: 24px;
  padding: 24px 18px;
  box-shadow: var(--card-shadow);
}

.play-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 18px 20px;
  border: none;
  border-radius: 999px;
  background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%);
  color: #fff;
  cursor: pointer;
  box-shadow: 0 10px 24px rgba(15, 118, 110, 0.35);
  transition: transform 0.15s ease, opacity 0.15s ease;
}

.play-btn:disabled {
  opacity: 0.75;
  cursor: wait;
}

.play-btn:not(:disabled):active {
  transform: scale(0.98);
}

.play-tag {
  padding: 8px 16px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.22);
  font-size: 14px;
  font-weight: 700;
}

.play-label {
  flex: 1;
  text-align: right;
  font-size: 22px;
  font-weight: 800;
  letter-spacing: 0.02em;
}

.error-text {
  margin: 12px 0 0;
  text-align: center;
  color: #b91c1c;
  font-size: 13px;
  font-weight: 600;
}
</style>
