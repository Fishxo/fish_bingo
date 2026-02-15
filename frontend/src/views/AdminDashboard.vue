<template>
  <div class="admin-dashboard">
    <div class="dashboard-header">
      <h1>Admin Dashboard</h1>
      <button @click="refreshData" class="refresh-btn">Refresh</button>
    </div>
    
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="data" class="dashboard-content">
      <!-- Statistics will go here -->
      <div class="stats-grid">
        <div class="stat-card">
          <h3>Total Games</h3>
          <p class="stat-value">{{ data.games_total || 0 }}</p>
        </div>
        <div class="stat-card">
          <h3>Total Revenue</h3>
          <p class="stat-value">{{ formatCurrency(data.revenue_total || 0) }}</p>
        </div>
        <!-- Add more stats as needed -->
      </div>
      
      <!-- Deposits and Withdrawals sections will be added -->
    </div>
  </div>
</template>

<script>
import { getAdminDashboardData, refreshDepositsWithdrawals } from '../services/api'

export default {
  name: 'AdminDashboard',
  data() {
    return {
      data: null,
      loading: true,
      error: null
    }
  },
  async mounted() {
    await this.loadData()
  },
  methods: {
    async loadData() {
      this.loading = true
      this.error = null
      try {
        this.data = await getAdminDashboardData()
      } catch (error) {
        console.error('Error loading admin dashboard:', error)
        this.error = error.response?.data?.error || 'Failed to load dashboard data'
      } finally {
        this.loading = false
      }
    },
    async refreshData() {
      await this.loadData()
    },
    formatCurrency(value) {
      return new Intl.NumberFormat('en-ET', { 
        style: 'currency', 
        currency: 'ETB',
        minimumFractionDigits: 2 
      }).format(value)
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.dashboard-header h1 {
  margin: 0;
  color: var(--primary-dark);
}

.refresh-btn {
  padding: 10px 20px;
  background: var(--primary-medium);
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
}

.refresh-btn:hover {
  background: var(--primary-dark);
}

.loading, .error {
  text-align: center;
  padding: 40px;
  font-size: 18px;
}

.error {
  color: #e74c3c;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.stat-card h3 {
  margin: 0 0 10px 0;
  color: var(--gray-dark);
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
}

.stat-value {
  margin: 0;
  font-size: 32px;
  font-weight: 700;
  color: var(--primary-dark);
}
</style>

