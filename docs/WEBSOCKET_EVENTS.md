# WebSocket Event Contract & Rooms

## Channels (Django Channels Group Names)

| Channel | Who Joins | Purpose |
|---------|-----------|---------|
| `game_{game_id}_players` | Users who selected a card | Competing; get full updates |
| `game_{game_id}_watchers` | Users watching without a card | Called numbers, winner info only |

Client connects with role: `ws/game/{game_id}/?role=player` or `?role=watcher`. Backend joins exactly one group per connection.

## Events → Room Routing

| Event | Players | Watchers | Notes |
|-------|---------|----------|--------|
| `number_called` | ✅ | ✅ | Both rooms |
| `game_started` | ✅ | ✅ | Both rooms |
| `game_ended` | ✅ | ✅ | Both rooms |
| `winner_declared` | ✅ | ✅ | Winner + card for display |
| `card_selected` | ✅ | ✅ | Which card number taken (no per-player card data) |
| `admin_message` | ✅ | ✅ | Optional admin broadcast |
| Card/player state (future) | ✅ | ❌ | Players only |

All current events are broadcast to **both** rooms unless we add players-only events later.

## Event Payloads (Reference)

- **number_called:** `{ number, letter, call_index?, ... }`
- **game_started:** `{ ... }`
- **game_ended:** `{ status, no_winner?, completed_at?, ... }`
- **winner_declared:** `{ winner?, winners?, prize, winner_card?, card_layout?, ... }`
- **card_selected:** `{ card_number, available_cards?, ... }`
- **batch_events:** `{ events: [ { type, data }, ... ] }`

## Connection

- **URL:** `ws/game/{game_id}/` or `ws/game/{game_id}/?role=player` | `?role=watcher`
- **Query:** `role=player` (user has a card) | `role=watcher` (no card, watching). Optional; if omitted, backend joins the client to both rooms for backward compatibility.
- **Frontend:** When instantiating `WebSocketService(gameId)`, you can later extend the connect URL to append `?role=player` or `?role=watcher` based on whether the user has selected a card (e.g. from CardSelectionView use `role=watcher` until card selected, then reconnect with `role=player` or keep single connection and default to both).
- **Ping/pong:** Client may send `{ "type": "ping" }`; server replies `{ "type": "pong" }`.
