# Feka Bingo – Performance & Capacity Analysis (EC2 t3.micro, 20GB)

## Quick answers (t3.micro, 20GB disk, single game)

| What | Safe target | Upper range | Notes |
|------|--------------|-------------|--------|
| **Concurrent players** (with cards) | **~20** | ~30 | ASGI + Redis + CPU limit |
| **Inspectors** (watchers, no cards) | **~40** | ~60 | WebSocket + Channel layer |
| **Players + watchers combined** | **~60** | ~80 | Same box |
| **Fake players per game** | **15–50** | up to 100 | Recommend 15–50 on t3.micro; more = more Celery/Redis |
| **Bot tasks** (deposit/register/transfer at same time) | **~5–15** | — | Single bot process; deposit not offloaded to Celery |

**What to change to improve:** Prefetch on current-game API (done), unify fake-user max from GameSettings, offload bot deposit/withdraw to Celery, remove `time.sleep` from request path (`start_game` / game creation), cap Redis memory and use SCAN instead of `KEYS` in cleanup, keep one active game, monitor WebSocket count and Celery queue length.

---

## Environment assumptions

- **EC2 t3.micro**: 1 vCPU, ~1 GB RAM, 20 GB disk.
- **Stack on one instance**: Django (ASGI + WSGI), Redis, PostgreSQL, Celery worker (concurrency=2), Telegram bot.
- **Single active game** at a time (design: one “current” waiting/active game).

---

## 1. Capacity estimates (current implementation)

### 1.1 Concurrent players (with cards, in the game)

| Metric | Estimate | Notes |
|--------|----------|--------|
| **Concurrent players** | **~15–30** | Players with at least one card in the active game. Bounded by: (a) WebSocket + HTTP load on 1 vCPU, (b) Channel layer capacity (tuned for ~100 in config, but CPU/RAM will cap earlier on t3.micro), (c) DB/Redis when many cards are marked and bingo-checked. |
| **Safe target** | **~20** | For stable latency and no timeouts under normal play. |

Main limits:

- One Django ASGI process handling all WebSockets and Channel layer traffic.
- Each player: 1 WebSocket, plus occasional HTTP (game/cards/claim).
- Celery: one number-call chain every ~3 s + mark + bingo check; 2 worker threads can handle one game comfortably; extra load is from API/WS, not from number calling.

### 1.2 Inspectors (watchers – watching live, no cards)

| Metric | Estimate | Notes |
|--------|----------|--------|
| **Concurrent watchers** | **~30–60** | Same WebSocket consumer, join `game_{id}_watchers`; receive same events (number_called, game_started, winner_declared, etc.). Lighter than players (no card state, no bingo claim). |
| **Safe target** | **~40** | Keep total WS connections (players + watchers) in a range where one ASGI process + Redis stay responsive. |

Total “live” users (players + watchers) on a single game: **~50–80** on t3.micro is a reasonable upper band; **~60** is a safe combined target.

### 1.3 Fake players per game

| Metric | Value | Notes |
|--------|--------|--------|
| **Config** | **15–100** (GameSettings: `system_accounts_min`, `system_accounts_max`) | Defaults: min 15, max 100 (model); some code paths still use fallback 30 for max. |
| **Recommended on t3.micro** | **15–50** | Fewer fake players = less Celery work (mark cards, bingo check), less Redis memory (marked sets per system card), faster finalization. |
| **Max supported** | **100** | Capped in admin (FAKE_USER_NAMES size); each fake = Redis keys + Celery tasks for marking/checking. |

Fake players are processed by Celery (`task_simulate_fake_user_selections`, `task_mark_cards_for_number`, `task_check_bingo_for_number`). With 2 worker threads and one game, **~30–50** fakes is comfortable; **up to 100** is acceptable if you keep real players + watchers modest.

### 1.4 Bot tasks (start, register, deposit, transfer, withdrawal) at the same time

| Task type | Where it runs | Concurrency | Notes |
|-----------|----------------|-------------|--------|
| **/start** | Bot process (async + sync_to_async DB) | Same process as all other bot handlers | Light (create/get user, daily cap check). Many /starts/minute can add up. |
| **/register** (contact) | Bot process | Same | DB + optional Celery `task_process_registration_rewards.delay()`. Rewards offloaded; main path in-process. |
| **Deposit** (Telebirr/CBE, receipt) | Bot process | Same | Heavier (API verify, DB writes). All in-process; can block bot for a few hundred ms per request. |
| **Withdraw / Transfer** | Bot process | Same | DB reads/writes in-process; moderate. |

- **Rough capacity**: **~5–15** concurrent bot “actions” (e.g. deposits, transfers, registers) without queuing heavily, depending on DB and external API latency. Bot remains responsive for **tens of concurrent** lighter operations (e.g. /start, /play) if DB is fast.
- **Bottleneck**: Single bot process; deposit/withdraw/transfer are **not** offloaded to Celery, so a burst of deposits will serialize in the bot and can increase response time.

---

## 2. Summary table (t3.micro, single game)

| Role | Safe target | Upper range | Main bottleneck |
|------|-------------|-------------|------------------|
| **Concurrent players** (with cards) | ~20 | ~30 | ASGI + Redis + CPU |
| **Inspectors** (watchers only) | ~40 | ~60 | WebSocket connections + Channel layer |
| **Players + watchers combined** | ~60 | ~80 | Same |
| **Fake players per game** | 15–50 | up to 100 | Celery + Redis (recommend 15–50 on t3.micro) |
| **Bot tasks** (deposit/transfer/register, etc.) | ~5–15 concurrent | — | Single bot process + DB |

---

## 3. What can be changed to improve performance and consistency

### 3.1 Application / code

1. **Prefetch on current-game API**  
   - Ensure `Game.objects.select_related(...).prefetch_related('gamecards', ...)` (or equivalent) so one request doesn’t do N+1 for gamecards and related.  
   - Reduces DB load for players and watchers polling or loading game state.

2. **Unify `system_accounts_max` fallback**  
   - Some code still uses `30` when the attribute is missing; model default is 100. Use a single constant or always read from GameSettings so behavior is consistent and you can tune fakes per game from admin.

3. **Offload heavy bot work to Celery**  
   - Move deposit verification (Telebirr/CBE API call + receipt creation + balance update) to a Celery task; bot only enqueues and returns “processing” or “success” when done.  
   - Same for withdrawal/transfer if they do multiple DB writes or external calls.  
   - Improves bot responsiveness under concurrent deposits/withdrawals.

4. **DB connection handling**  
   - Bot already uses `ensure_db_connection()` and `sync_to_async`; keep it. For Django, consider `CONN_MAX_AGE` (e.g. 60) in production to avoid constant connect/disconnect under load, if not already set.

5. **Channel layer capacity**  
   - `capacity: 1500` is already set for ~100 users. On t3.micro you’ll hit CPU/RAM before channel capacity; no need to reduce it unless you want to lower memory.

6. **Redis cleanup**  
   - Ensure `cleanup_game_redis_keys` and any game live-state cleanup run on every game end so Redis memory doesn’t grow with stale keys.

7. **Watchers vs players**  
   - Frontend already uses `role=player` vs `role=watcher`; watchers get the same events with less per-connection state. Good to keep; no change needed unless you add watcher-specific features.

### 3.2 Infrastructure / ops

8. **One active game**  
   - Keep the “single current game” design on t3.micro; multiple simultaneous games would multiply Celery and Redis load.

9. **Celery**  
   - Keep `-Q gameplay,registration,default` and `--concurrency=2` as in comments. If you upgrade to t3.small, consider concurrency=4.

10. **Redis**  
    - Single instance is fine. Set `maxmemory` and `maxmemory-policy` (e.g. `volatile-lru`) so Redis doesn’t use more than ~200–300 MB on t3.micro.

11. **Monitoring**  
    - Log or metricize: current-game response time, WebSocket connection count, Celery queue lengths (gameplay vs registration), Redis memory. Helps validate “safe” targets (e.g. ~20 players, ~40 watchers, 15–50 fakes).

12. **Disk**  
    - 20 GB is enough for OS, app, PostgreSQL, logs; ensure log rotation and DB vacuum so disk doesn’t fill.

### 3.3 Consistency and flow

13. **Game state**  
    - Already Redis-first during play (called numbers, card markings, bingo window); DB at finalization. Keeps one source of truth per game and avoids mid-game DB overload.

14. **Locks**  
    - Existing Redis locks (number calling, bingo claim, card selection) prevent races; keep TTLs short so a crashed process doesn’t block the game long.

15. **Polling fallback**  
    - When WebSocket is down, frontend polls (10 s active game, 1 s card selection). Intervals are already relaxed; ensure only one active game is returned so polling load stays predictable.

---

## 4. Quick reference

- **Concurrent players**: ~20 safe, ~30 upper.
- **Inspectors (watchers)**: ~40 safe, ~60 upper.
- **Fake players per game**: 15–50 recommended on t3.micro; up to 100 supported.
- **Bot**: ~5–15 concurrent heavy actions (deposit/withdraw/transfer); offload deposit (and optionally withdraw/transfer) to Celery to improve responsiveness.
- **Improvements**: prefetch on current-game API, unify fake-user max from GameSettings, offload bot deposit (and heavy) work to Celery, ensure Redis cleanup on game end, keep one active game, monitor WS count and Celery queues.
