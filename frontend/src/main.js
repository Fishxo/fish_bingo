import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import { initTelegramWebApp, getInitData } from './services/telegram'
import { registerTelegram } from './services/api'
import './style.css'

import AppShell from './components/layout/AppShell.vue'
import HomeView from './views/HomeView.vue'
import GameHistoryView from './views/GameHistoryView.vue'
import WalletView from './views/WalletView.vue'
import ProfileView from './views/ProfileView.vue'
import WaitingView from './views/WaitingView.vue'
import GameCompletedView from './views/GameCompletedView.vue'
import CardSelectionView from './views/CardSelectionView.vue'
import ActiveGameView from './views/ActiveGameView.vue'
import AdminDashboard from './views/AdminDashboard.vue'
import SecondAdminDashboard from './views/SecondAdminDashboard.vue'
import SecondAdminLogin from './views/SecondAdminLogin.vue'

const routes = [
  {
    path: '/',
    component: AppShell,
    children: [
      { path: '', redirect: '/home' },
      { path: 'home', name: 'home', component: HomeView, meta: { navTab: 'game' } },
      { path: 'history', name: 'history', component: GameHistoryView, meta: { navTab: 'history' } },
      { path: 'wallet', name: 'wallet', component: WalletView, meta: { navTab: 'wallet' } },
      { path: 'profile', name: 'profile', component: ProfileView, meta: { navTab: 'profile' } },
    ]
  },
  { path: '/waiting', name: 'waiting', component: WaitingView },
  { path: '/completed', name: 'completed', component: GameCompletedView },
  { path: '/select-card', name: 'select-card', component: CardSelectionView },
  { path: '/game', name: 'game', component: ActiveGameView },
  { path: '/admin-dashboard', name: 'admin-dashboard', component: AdminDashboard },
  { path: '/secondadmin', name: 'second-admin-dashboard', component: SecondAdminDashboard },
  { path: '/secondadmin/login', name: 'second-admin-login', component: SecondAdminLogin },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const gameplayRoutes = ['game', 'select-card', 'completed', 'waiting']

  if (to.name === 'game' && from.name !== 'game') {
    try {
      const { getCurrentGame } = await import('./services/api')
      const game = await getCurrentGame()
      if (game.status === 'waiting') {
        next('/select-card')
        return
      }
      if (game.status === 'completed') {
        next('/completed')
        return
      }
    } catch (error) {
      if (error.response?.status === 404) {
        next('/home')
        return
      }
    }
  }

  if (from.name === null && gameplayRoutes.includes(to.name)) {
    // Direct deep links to gameplay routes still allowed
    next()
    return
  }

  next()
})

const isTelegramApp = initTelegramWebApp()

if (isTelegramApp) {
  const initData = getInitData()
  if (initData && typeof initData === 'string' && initData.length > 0) {
    registerTelegram(initData)
      .then(async (data) => {
        console.log('✅ Telegram authentication successful:', data.user_id)

        if (data.user && !data.user.phone_number) {
          try {
            const { getInitDataRaw } = await import('./services/telegram')
            const initDataRaw = getInitDataRaw()

            if (initDataRaw && initDataRaw.user && initDataRaw.user.phone_number) {
              const { updateUserPhone } = await import('./services/api')
              await updateUserPhone(initDataRaw.user.phone_number)
              console.log('✅ Phone number saved from initData:', initDataRaw.user.phone_number)
            } else {
              console.warn('⚠️ Phone number not available. User needs to share phone number through Telegram bot.')
            }
          } catch (error) {
            console.warn('⚠️ Phone number retrieval failed:', error)
          }
        }
      })
      .catch((error) => {
        console.error('❌ Telegram authentication failed:', error)
      })
  } else {
    console.warn('⚠️ Telegram Web App detected but no initData available')
  }
}

const app = createApp(App)
app.use(router)
app.mount('#app')
