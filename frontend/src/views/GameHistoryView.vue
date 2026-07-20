<template>
  <div class="history-view">
    <header class="page-header">
      <h1>GAME HISTORY</h1>
      <ReloadButton :loading="loading" @reload="loadHistory" />
    </header>

    <LoadingState v-if="loading && !history.length" message="Loading game history…" />

    <div v-else-if="error" class="error-banner">
      <p>{{ error }}</p>
      <button type="button" class="retry-btn" @click="loadHistory">Try again</button>
    </div>

    <EmptyState
      v-else-if="!history.length"
      icon="🎮"
      title="No games yet"
      message="Your recent bingo games will appear here after you play."
    />

    <div v-else class="history-list">
      <article v-for="item in history" :key="item.id" class="history-card">
        <div class="card-top">
          <h2>Game {{ item.code }}</h2>
          <span class="status" :class="item.result.toLowerCase()">{{ item.result }}</span>
        </div>
        <p class="date">{{ item.date }}</p>
        <div class="stats-grid">
          <div class="stat-pill">Stake: {{ formatMoney(item.stake) }}</div>
          <div class="stat-pill">Prize: {{ formatMoney(item.prize) }}</div>
          <div class="stat-pill">My Boards: #{{ item.myCard ?? '—' }}</div>
          <div class="stat-pill winner-pill">🏆 Winners' Boards: #{{ item.winnerCard ?? '—' }}</div>
        </div>
        <p class="winner-count">Winner count: {{ item.winnerCount }}</p>
      </article>
      <p class="footer-note">Showing recent {{ history.length }} games</p>
    </div>
  </div>
</template>

<script>
import ReloadButton from '../components/ui/ReloadButton.vue'
import LoadingState from '../components/ui/LoadingState.vue'
import EmptyState from '../components/ui/EmptyState.vue'
import { listGames, getCurrentUser } from '../services/api'
import { formatMoney, formatDateTime, formatGameCode } from '../utils/format'

export default {
  name: 'GameHistoryView',
  components: { ReloadButton, LoadingState, EmptyState },
  data() {
    return {
      loading: false,
      error: null,
      history: [],
      userId: null
    }
  },
  async mounted() {
    await this.loadHistory()
  },
  methods: {
    formatMoney,
    async loadHistory() {
      this.loading = true
      this.error = null
      try {
        const user = await getCurrentUser()
        this.userId = user.id

        const data = await listGames(1)
        const games = Array.isArray(data?.results) ? data.results : (Array.isArray(data) ? data : [])

        this.history = games
          .filter(game => this.userPlayed(game))
          .map(game => this.mapGameEntry(game))
      } catch (err) {
        console.error('History load failed:', err)
        this.error = err.response?.data?.error || 'Failed to load game history.'
        this.history = []
      } finally {
        this.loading = false
      }
    },
    userPlayed(game) {
      const cards = game.gamecards || []
      return cards.some(card => {
        const uid = card.user?.id ?? card.user
        return Number(uid) === Number(this.userId)
      })
    },
    mapGameEntry(game) {
      const myCard = (game.gamecards || []).find(card => {
        const uid = card.user?.id ?? card.user
        return Number(uid) === Number(this.userId)
      })

      const winnerCards = (game.gamecards || []).filter(c => c.is_winner)
      const winnerCard = winnerCards[0]?.card_number ?? null

      let winnerCount = winnerCards.length
      if (!winnerCount && game.winner) winnerCount = 1
      if (!winnerCount && game.status === 'completed') winnerCount = 0

      const won = !!myCard?.is_winner
      const lost = game.status === 'completed' && myCard && !myCard.is_winner

      return {
        id: game.id,
        code: formatGameCode(game.id),
        date: formatDateTime(game.completed_at || game.created_at),
        stake: game.bet_amount ?? 0,
        prize: game.total_derash ?? game.derash_amount ?? 0,
        myCard: myCard?.card_number ?? null,
        winnerCard: winnerCard ?? '—',
        winnerCount,
        result: won ? 'WIN' : (lost ? 'LOSS' : (game.status === 'completed' ? 'LOSS' : 'PENDING'))
      }
    }
  }
}
</script>

<style scoped>
.history-view {
  padding: 16px;
  max-width: 480px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.page-header h1 {
  font-size: 18px;
  font-weight: 800;
  color: var(--primary-dark);
  letter-spacing: 0.04em;
}

.error-banner {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  text-align: center;
  box-shadow: var(--card-shadow);
}

.error-banner p {
  color: #b91c1c;
  font-weight: 600;
  margin: 0 0 12px;
}

.retry-btn {
  border: none;
  background: var(--primary-dark);
  color: #fff;
  padding: 10px 18px;
  border-radius: 999px;
  font-weight: 700;
  cursor: pointer;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.history-card {
  background: #fff;
  border-radius: 18px;
  padding: 16px;
  box-shadow: var(--card-shadow);
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.card-top h2 {
  margin: 0;
  font-size: 15px;
  font-weight: 800;
  color: var(--primary-dark);
}

.status {
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.04em;
}

.status.win {
  color: #15803d;
}

.status.loss {
  color: #991b1b;
}

.status.pending {
  color: #b45309;
}

.date {
  margin: 6px 0 12px;
  font-size: 12px;
  color: rgba(74, 8, 88, 0.65);
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.stat-pill {
  background: rgba(201, 182, 228, 0.45);
  border-radius: 12px;
  padding: 10px;
  font-size: 11px;
  font-weight: 700;
  color: var(--primary-dark);
  line-height: 1.35;
}

.winner-pill {
  grid-column: span 2;
}

.winner-count {
  margin: 10px 0 0;
  font-size: 12px;
  color: rgba(74, 8, 88, 0.7);
  font-weight: 600;
}

.footer-note {
  text-align: center;
  font-size: 12px;
  color: rgba(74, 8, 88, 0.55);
  margin: 8px 0 0;
}
</style>
