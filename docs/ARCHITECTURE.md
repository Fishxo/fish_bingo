# Bingo System Architecture — Blueprint

> **Core goal:** Gameplay must NEVER be affected by watchers, bots, deposits, withdrawals, or registrations.

## High-Level Architecture

```
Telegram Bot
   |
   |----> Django API (REST)
   |
   |----> Mini App (Vue)
               |
               |---- WebSocket Gateway
               |
               |---- REST (non-real-time)
```

## System Layers (Mandatory)

### 1. Interaction Layer
- Telegram Bot
- Vue Mini App
- WebSocket connections  
**NO GAME LOGIC HERE**

### 2. Orchestration Layer (Django)
- Game lifecycle
- Room assignment
- State transitions
- Security & validation  
**NO HEAVY REAL-TIME LOOPS**

### 3. Real-Time Engine (Redis + WebSockets)
- Live card selection
- Live number calling
- Live game state
- Live viewers  
**FAST, IN-MEMORY ONLY**

### 4. Background Workers (Celery)
- Number calling loop
- Fake/system players
- Timers
- Cleanup
- Result finalization  
**NO USER REQUESTS HERE**

### 5. Persistence Layer (PostgreSQL)
- Users
- Transactions
- Completed games
- Audit logs  
**NO LIVE STATE**

---

## Room-Based User Separation (Critical)

Every user belongs to **exactly ONE room at a time** per game.

### ROOM 1 — ACTIVE_GAME (Players)
- Users who selected a card and are competing.
- **WebSocket channel:** `game_{game_id}_players`
- **Receives:** Called numbers, card updates, win announcements.

### ROOM 2 — WATCHERS
- Users who did NOT select a card; watching live.
- **WebSocket channel:** `game_{game_id}_watchers`
- **Receives:** Called numbers, winner info, animations.
- **Does NOT receive:** Per-player card data, player state.

### ROOM 3 — BOT / OTHER TASKS
- Chatting with bot, deposit, withdrawal, transfer, history.
- **NO WebSocket to game.** REST API + Celery only.

---

## Game Flow (Summary)

1. **Game creation** — Celery `create_game()`: PostgreSQL + Redis init.
2. **Card selection** — Redis `game:{id}:cards_taken`; on select: validate → Redis lock → assign → move user to players room; broadcast to both rooms.
3. **Game start** — Timer or min players; lock selection; spawn Celery `start_game(game_id)`.
4. **Number calling** — Celery `call_number(game_id)`: generate → Redis → broadcast to players + watchers.
5. **System players** — Exist only in Redis `game:{id}:system_players`; no DB user/balance/payout.
6. **Win detection** — Validate bingo from Redis; set `game:{id}:state = "FINISHED"`.
7. **Winner broadcast** — To both players and watchers.
8. **Cleanup** — Celery: save to PostgreSQL, clear Redis, next round.

---

## Performance Rules

### Never
- DB queries in WebSocket handlers
- Game loops in Django views
- Shared room for watchers and players
- Redis → DB sync during live play

### Always
- Redis for live state
- PostgreSQL only after game ends
- Celery for timers and loops
- Separate WebSocket channels for players vs watchers

---

## Scaling Guarantee

- 400+ active players
- 2,000+ watchers
- Bot tasks in parallel
- No gameplay lag  
**Scaling = infrastructure only; no rewrite.**

See: `REDIS_KEYS.md`, `WEBSOCKET_EVENTS.md`, `CELERY_TASKS.md`.
