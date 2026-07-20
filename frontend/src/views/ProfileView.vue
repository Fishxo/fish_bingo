<template>
  <div class="profile-view">
    <LoadingState v-if="loading && !profile" message="Loading profile…" />

    <div v-else-if="error" class="error-banner">
      <p>{{ error }}</p>
      <button type="button" class="retry-btn" @click="loadProfile">Try again</button>
    </div>

    <template v-else-if="profile">
      <p class="section-label">ACCOUNT</p>
      <section class="account-card">
        <div class="avatar">{{ avatarLetter }}</div>
        <div class="account-info">
          <h2>@{{ profile.username || 'player' }}</h2>
          <p v-if="profile.phone_number">📞 {{ profile.phone_number }}</p>
          <p v-else class="muted">Player ID: {{ profile.id }}</p>
        </div>
      </section>

      <div class="hero-balance">
        <p class="hero-label">TOTAL BALANCE</p>
        <p class="hero-value">{{ formatMoney(totalBalance) }}</p>
      </div>

      <div class="split-grid">
        <div class="split-card">
          <span class="split-label">MAIN</span>
          <span class="split-value">{{ formatMoney(mainBalance) }}</span>
        </div>
        <div class="split-card">
          <span class="split-label">BONUS</span>
          <span class="split-value">{{ formatMoney(bonusBalance) }}</span>
        </div>
        <div class="split-card">
          <span class="split-label">DEPOSITED</span>
          <span class="split-value">{{ formatMoney(depositedTotal) }}</span>
        </div>
      </div>

      <p class="section-label">STATS</p>
      <section class="stats-card">
        <div class="stat-row">
          <span>💸 Total Withdrawal</span>
          <strong>{{ formatMoney(stats.totalWithdrawal) }}</strong>
        </div>
        <div class="stat-row">
          <span>🏆 Games Won</span>
          <strong>{{ stats.gamesWon }}</strong>
        </div>
        <div class="stat-row">
          <span>🎮 Games Played</span>
          <strong>{{ stats.gamesPlayed }}</strong>
        </div>
      </section>

      <section class="actions-card">
        <button type="button" class="action-btn" @click="closeApp">Close Mini App</button>
      </section>
    </template>
  </div>
</template>

<script>
import LoadingState from '../components/ui/LoadingState.vue'
import { getCurrentUser, getUserBalance, getWalletInfo, listGames } from '../services/api'
import { formatMoney } from '../utils/format'
import { getTelegramWebApp } from '../services/telegram'

export default {
  name: 'ProfileView',
  components: { LoadingState },
  data() {
    return {
      loading: false,
      error: null,
      profile: null,
      totalBalance: 0,
      mainBalance: 0,
      bonusBalance: 0,
      depositedTotal: 0,
      stats: {
        totalWithdrawal: 0,
        gamesWon: 0,
        gamesPlayed: 0
      }
    }
  },
  computed: {
    avatarLetter() {
      const name = this.profile?.username || this.profile?.first_name || 'P'
      return String(name).charAt(0).toUpperCase()
    }
  },
  async mounted() {
    await this.loadProfile()
  },
  methods: {
    formatMoney,
    async loadProfile() {
      this.loading = true
      this.error = null
      try {
        const [profile, balance, wallet, gamesData] = await Promise.all([
          getCurrentUser(),
          getUserBalance(),
          getWalletInfo(),
          listGames(1).catch(() => ({ results: [] }))
        ])

        this.profile = profile
        this.totalBalance = balance.balance ?? wallet.balance ?? profile.balance ?? 0
        this.mainBalance = balance.withdrawable_balance ?? profile.withdrawable_balance ?? 0
        this.bonusBalance = balance.unwithdrawable_balance ?? profile.unwithdrawable_balance ?? 0

        const txs = wallet.transactions || []
        this.depositedTotal = txs
          .filter(tx => tx.transaction_type === 'deposit')
          .reduce((sum, tx) => sum + Math.max(0, Number(tx.amount) || 0), 0)

        const totalWithdrawal = txs
          .filter(tx => tx.transaction_type === 'withdraw')
          .reduce((sum, tx) => sum + Math.abs(Number(tx.amount) || 0), 0)

        const games = Array.isArray(gamesData?.results) ? gamesData.results : []
        const played = games.filter(g => (g.gamecards || []).some(c => {
          const uid = c.user?.id ?? c.user
          return Number(uid) === Number(profile.id)
        }))
        const won = played.filter(g => (g.gamecards || []).some(c => {
          const uid = c.user?.id ?? c.user
          return Number(uid) === Number(profile.id) && c.is_winner
        }))

        this.stats = {
          totalWithdrawal,
          gamesWon: won.length,
          gamesPlayed: played.length
        }
      } catch (err) {
        console.error('Profile load failed:', err)
        this.error = err.response?.data?.error || 'Failed to load profile.'
      } finally {
        this.loading = false
      }
    },
    closeApp() {
      const tg = getTelegramWebApp()
      if (tg?.close) {
        tg.close()
      } else {
        window.close()
      }
    }
  }
}
</script>

<style scoped>
.profile-view {
  padding: 16px;
  max-width: 480px;
  margin: 0 auto;
}

.section-label {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: rgba(74, 8, 88, 0.55);
  margin: 0 0 10px;
}

.account-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #fff;
  border-radius: 20px;
  padding: 16px;
  box-shadow: var(--card-shadow);
  margin-bottom: 16px;
}

.avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6a0d7a, #4a0858);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 800;
  flex-shrink: 0;
}

.account-info h2 {
  margin: 0 0 4px;
  font-size: 16px;
  font-weight: 800;
  color: var(--primary-dark);
}

.account-info p {
  margin: 0;
  font-size: 13px;
  color: rgba(74, 8, 88, 0.75);
}

.account-info .muted {
  opacity: 0.7;
}

.hero-balance {
  background: linear-gradient(135deg, #6a0d7a 0%, #4a0858 100%);
  border-radius: 22px;
  padding: 24px 20px;
  color: #fff;
  box-shadow: var(--card-shadow-lg);
  margin-bottom: 14px;
}

.hero-label {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.08em;
  opacity: 0.85;
  margin: 0 0 8px;
}

.hero-value {
  margin: 0;
  font-size: 34px;
  font-weight: 800;
}

.split-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 18px;
}

.split-card {
  background: #fff;
  border-radius: 16px;
  padding: 14px 10px;
  box-shadow: var(--card-shadow);
  display: flex;
  flex-direction: column;
  gap: 8px;
  text-align: center;
}

.split-label {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.06em;
  color: rgba(74, 8, 88, 0.65);
}

.split-value {
  font-size: 13px;
  font-weight: 800;
  color: var(--primary-dark);
}

.stats-card {
  background: #fff;
  border-radius: 20px;
  padding: 8px 0;
  box-shadow: var(--card-shadow);
  margin-bottom: 16px;
}

.stat-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(106, 13, 122, 0.08);
  font-size: 14px;
  color: var(--primary-dark);
}

.stat-row:last-child {
  border-bottom: none;
}

.stat-row strong {
  font-size: 14px;
}

.actions-card {
  background: #fff;
  border-radius: 20px;
  padding: 16px;
  box-shadow: var(--card-shadow);
}

.action-btn {
  width: 100%;
  border: 2px solid rgba(106, 13, 122, 0.2);
  background: #fff;
  color: var(--primary-dark);
  padding: 14px;
  border-radius: 14px;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
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
</style>
