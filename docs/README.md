# Bingo backend — architecture and contracts

- **[ARCHITECTURE.md](ARCHITECTURE.md)** — System layers, room separation, game flow
- **[REDIS_KEYS.md](REDIS_KEYS.md)** — Redis key schema (live state)
- **[WEBSOCKET_EVENTS.md](WEBSOCKET_EVENTS.md)** — WebSocket channels and event routing
- **[CELERY_TASKS.md](CELERY_TASKS.md)** — Celery task structure and responsibilities

Implementation entry points:

- **Rooms / broadcast:** `api/channels.py` — `broadcast_to_game_rooms`, `batch_broadcast_to_game_rooms`
- **Consumer:** `api/consumers.py` — joins `game_{id}_players` and/or `game_{id}_watchers` by `role`
- **Redis:** `api/redis_utils.py` — keys and live state helpers
- **Batch broadcast:** `api/redis_utils.batch_broadcast_to_game` delegates to `channels.batch_broadcast_to_game_rooms`
