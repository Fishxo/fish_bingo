# Celery Task Structure

All game loops, timers, and finalization run in workers. No user requests in these tasks.

## Game Lifecycle

| Task | Responsibility |
|------|-----------------|
| `create_game` | Generate game_id; write base config to PostgreSQL; init Redis keys (`game:{id}:state`, `game:{id}:players`, `game:{id}:cards_taken`) |
| `start_game(game_id)` | Lock card selection; freeze players list; init live state; spawn number-calling chain |
| `call_number(game_id)` | Generate number; store in Redis; broadcast to `players` + `watchers`; chain next or finish |
| Finalization task | Save final result to PostgreSQL; clear Redis keys; broadcast game_ended; redirect clients to card selection / next round |

## System (Fake) Players

| Task / Logic | Responsibility |
|--------------|-----------------|
| System player card selection | Assign cards from Redis only; no DB user; write to `game:{id}:system_players` |
| System player marking | Update Redis card marked state; can trigger win check |
| System player wins | Broadcast winner_declared; **no** DB write, **no** payout |

## Timers & Cleanup

| Task | Responsibility |
|------|-----------------|
| Card selection timer | When time expires or min players: trigger `start_game` |
| Post-game cleanup | Clear Redis keys for game; optionally schedule next `create_game` |

## Rules

- **No** HTTP request handling inside these tasks.
- **No** synchronous DB reads/writes during the live number-calling loop; DB only at start (load config) and end (finalize).
- Broadcast only via channel layer to `game_{id}_players` and `game_{id}_watchers` using the helpers in `api.channels`.
