# Redis Key Schema

Single source of truth for **live state**. PostgreSQL used only for finalized data.

## Game State

| Key | Type | Purpose |
|-----|------|---------|
| `game:{id}:state` | hash | Phase: `CARD_SELECTION` \| `active` \| `FINISHED`; cache fields (winner_id, call_count, etc.) |
| `game:{id}:live` | hash | Live engine state: status, current_index, winner_card_id, winner_user_id, call_interval, started_at |
| `game:{id}:called_numbers` | list | Ordered list of called numbers (live) |
| `game:{id}:cards_taken` | set or hash | Card numbers taken (for card selection phase) |

## Locks

| Key | Type | Purpose |
|-----|------|---------|
| `game:creation:lock` | string | Global game creation lock |
| `game:{id}:number_calling_lock` | string | One number call at a time |
| `game:{id}:bingo_claim_lock` | string | One bingo claim at a time |
| `card:{card_number}:lock` | string | Card assignment lock |

## Bingo / Winners

| Key | Type | Purpose |
|-----|------|---------|
| `game:{id}:bingo_window` | — | Bingo claim window / timing |
| `game:{id}:bingo_winners` | set | Winner card/user IDs (live) |

## Per-Card (Live)

| Key | Type | Purpose |
|-----|------|---------|
| `game:{id}:card:{card_id}:marked` | set | Marked numbers on card (live) |
| `card:{card_id}:marked_numbers` | set | Legacy/cache marked numbers |
| `card:{card_id}:marked_count` | string | Count (legacy) |

## System Players (Redis-only, no DB)

| Key | Type | Purpose |
|-----|------|---------|
| `game:{id}:system_players` | hash | card_number -> JSON {name, card_number, card_layout}; **no DB user, no balance** |
| `game:{id}:system_card:{card_number}:marked` | set | Marked numbers on that system player's card |

## Non-Game (Out of Band)

| Key | Type | Purpose |
|-----|------|---------|
| `register:lock:{telegram_id}` | string | Registration lock |
| `reward:lock:{user_id}` | string | Reward processing lock |
| `referral:lock:{referrer_id}` | string | Referral lock |
| Rate limit keys | string | Per action/identifier |

## Cleanup

On game end, Celery must delete (or expire):

- `game:{id}:state`
- `game:{id}:live`
- `game:{id}:called_numbers`
- `game:{id}:cards_taken`
- `game:{id}:number_calling_lock`
- `game:{id}:bingo_claim_lock`
- `game:{id}:bingo_window`
- `game:{id}:bingo_winners`
- `game:{id}:card:*:marked`
- `game:{id}:system_players`
- `game:{id}:system_card:*:marked`

Non-game keys (registration, rewards, rate limit) have their own TTLs.
