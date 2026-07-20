<template>
  <div class="wallet-view">
    <header class="wallet-header-card">
      <div class="header-top">
        <div>
          <p class="eyebrow">WALLET</p>
          <h1>{{ formatMoney(totalBalance) }}</h1>
          <p class="sub">Total balance</p>
        </div>
        <ReloadButton :loading="loading" @reload="loadWallet" />
      </div>

      <div class="tab-switch">
        <button
          type="button"
          class="tab-btn"
          :class="{ active: activeTab === 'balances' }"
          @click="activeTab = 'balances'"
        >
          BALANCES
        </button>
        <button
          type="button"
          class="tab-btn"
          :class="{ active: activeTab === 'history' }"
          @click="activeTab = 'history'"
        >
          HISTORY
        </button>
      </div>
    </header>

    <LoadingState v-if="loading && !loaded" message="Loading wallet…" />

    <div v-else-if="error" class="error-banner">
      <p>{{ error }}</p>
      <button type="button" class="retry-btn" @click="loadWallet">Try again</button>
    </div>

    <template v-else>
      <section v-if="activeTab === 'balances'" class="balances-panel">
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
      </section>

      <section v-else class="history-panel">
        <EmptyState
          v-if="!walletHistory.length"
          icon="💳"
          title="No transactions yet"
          message="Deposits and withdrawals will show up here."
        />
        <div v-else class="tx-list">
          <article v-for="tx in walletHistory" :key="tx.id" class="tx-card">
            <div class="tx-top">
              <span class="tx-type" :class="tx.transaction_type">{{ txLabel(tx.transaction_type) }}</span>
              <span class="tx-amount" :class="{ positive: tx.amount > 0, negative: tx.amount < 0 }">
                {{ tx.amount > 0 ? '+' : '' }}{{ formatMoney(tx.amount) }}
              </span>
            </div>
            <p class="tx-date">{{ formatDateTime(tx.created_at) }}</p>
            <p v-if="tx.description" class="tx-desc">{{ tx.description }}</p>
          </article>
        </div>
      </section>
    </template>
  </div>
</template>

<script>
import ReloadButton from '../components/ui/ReloadButton.vue'
import LoadingState from '../components/ui/LoadingState.vue'
import EmptyState from '../components/ui/EmptyState.vue'
import { getWalletInfo, getUserBalance } from '../services/api'
import { formatMoney, formatDateTime } from '../utils/format'

export default {
  name: 'WalletView',
  components: { ReloadButton, LoadingState, EmptyState },
  data() {
    return {
      loading: false,
      loaded: false,
      error: null,
      activeTab: 'balances',
      totalBalance: 0,
      mainBalance: 0,
      bonusBalance: 0,
      depositedTotal: 0,
      transactions: []
    }
  },
  computed: {
    walletHistory() {
      return (this.transactions || []).filter(tx =>
        ['deposit', 'withdraw'].includes(tx.transaction_type)
      )
    }
  },
  async mounted() {
    await this.loadWallet()
  },
  methods: {
    formatMoney,
    formatDateTime,
    txLabel(type) {
      if (type === 'deposit') return 'Deposit'
      if (type === 'withdraw') return 'Withdrawal'
      return type
    },
    async loadWallet() {
      this.loading = true
      this.error = null
      try {
        const [wallet, balanceSplit] = await Promise.all([
          getWalletInfo(),
          getUserBalance()
        ])

        this.totalBalance = wallet.balance ?? balanceSplit.balance ?? 0
        this.mainBalance = balanceSplit.withdrawable_balance ?? 0
        this.bonusBalance = balanceSplit.unwithdrawable_balance ?? 0
        this.transactions = wallet.transactions || []

        this.depositedTotal = this.transactions
          .filter(tx => tx.transaction_type === 'deposit')
          .reduce((sum, tx) => sum + Math.max(0, Number(tx.amount) || 0), 0)

        this.loaded = true
      } catch (err) {
        console.error('Wallet load failed:', err)
        this.error = err.response?.data?.error || 'Failed to load wallet.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.wallet-view {
  padding: 16px;
  max-width: 480px;
  margin: 0 auto;
}

.wallet-header-card {
  background: #fff;
  border-radius: 20px;
  padding: 18px;
  box-shadow: var(--card-shadow);
  margin-bottom: 16px;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.eyebrow {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: rgba(74, 8, 88, 0.55);
  margin: 0 0 6px;
}

.wallet-header-card h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 800;
  color: var(--primary-dark);
}

.sub {
  margin: 4px 0 0;
  font-size: 12px;
  color: rgba(74, 8, 88, 0.55);
}

.tab-switch {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  background: rgba(201, 182, 228, 0.35);
  padding: 6px;
  border-radius: 999px;
}

.tab-btn {
  border: none;
  background: transparent;
  color: var(--primary-dark);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.04em;
  padding: 10px 8px;
  border-radius: 999px;
  cursor: pointer;
}

.tab-btn.active {
  background: var(--primary-dark);
  color: #fff;
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

.tx-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tx-card {
  background: #fff;
  border-radius: 16px;
  padding: 14px 16px;
  box-shadow: var(--card-shadow);
}

.tx-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.tx-type {
  font-size: 13px;
  font-weight: 800;
  color: var(--primary-dark);
  text-transform: capitalize;
}

.tx-type.deposit { color: #15803d; }
.tx-type.withdraw { color: #991b1b; }

.tx-amount {
  font-size: 14px;
  font-weight: 800;
}

.tx-amount.positive { color: #15803d; }
.tx-amount.negative { color: #991b1b; }

.tx-date {
  margin: 6px 0 0;
  font-size: 12px;
  color: rgba(74, 8, 88, 0.6);
}

.tx-desc {
  margin: 6px 0 0;
  font-size: 12px;
  color: rgba(74, 8, 88, 0.75);
  line-height: 1.4;
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
