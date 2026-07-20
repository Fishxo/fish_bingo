import { getCurrentGame, getMyCard } from '../services/api'

/**
 * Resolve where "Play Game" should navigate using existing game APIs.
 * @returns {Promise<{ path: string, game: object|null }>}
 */
export async function resolvePlayGameRoute() {
  try {
    const game = await getCurrentGame()
    if (!game) {
      return { path: '/select-card', game: null }
    }

    if (game.status === 'active') {
      try {
        const card = await getMyCard(game.id)
        if (card) {
          return { path: '/game', game }
        }
      } catch {
        // User has no card yet — join via card selection
      }
      return { path: '/select-card', game }
    }

    if (game.status === 'waiting') {
      return { path: '/select-card', game }
    }

    return { path: '/select-card', game }
  } catch (error) {
    if (error.response?.status === 404) {
      return { path: '/select-card', game: null }
    }
    throw error
  }
}
