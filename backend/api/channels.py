"""
WebSocket channel room names and broadcast helpers.

Room separation (see docs/ARCHITECTURE.md):
- game_{game_id}_players: users who selected a card (competing)
- game_{game_id}_watchers: users watching without a card

All broadcasts go to BOTH rooms by default unless specified otherwise.
Legacy single group game_{game_id} is supported for backward compatibility during migration.
"""

from asgiref.sync import async_to_sync

# Room name templates (Django Channels group names)
def room_players(game_id):
    return f"game_{game_id}_players"

def room_watchers(game_id):
    return f"game_{game_id}_watchers"

def room_legacy(game_id):
    """Legacy single group; use for backward compat until all clients send role."""
    return f"game_{game_id}"


def _send_to_group(channel_layer, group_name, event_type, event_data):
    """Send one event to one group."""
    async_to_sync(channel_layer.group_send)(
        group_name,
        {"type": event_type, "data": event_data}
    )


def _get_channel_layer():
    from channels.layers import get_channel_layer
    return get_channel_layer()


def broadcast_to_game_rooms(game_id, event_type, event_data, rooms="both", use_legacy=True):
    """
    Broadcast one event to game rooms.

    Args:
        game_id: Game ID (int or str).
        event_type: Handler method name on consumer (e.g. 'number_called', 'winner_declared').
        event_data: Dict payload (key 'data' in consumer event).
        rooms: 'both' | 'players' | 'watchers'
        use_legacy: If True, also send to legacy group game_{id} for backward compatibility.

    Returns:
        bool: True if sent, False on error.
    """
    try:
        channel_layer = _get_channel_layer()
        gid = int(game_id) if isinstance(game_id, str) and game_id.isdigit() else game_id
        groups = []

        if rooms in ("both", "players"):
            groups.append(room_players(gid))
        if rooms in ("both", "watchers"):
            groups.append(room_watchers(gid))
        if use_legacy:
            groups.append(room_legacy(gid))

        for group_name in groups:
            _send_to_group(channel_layer, group_name, event_type, event_data)

        return True
    except Exception as e:
        import logging
        logging.getLogger(__name__).exception("broadcast_to_game_rooms failed: %s", e)
        return False


def batch_broadcast_to_game_rooms(game_id, events, rooms="both", use_legacy=True):
    """
    Broadcast multiple events. Sends as batch_events if len(events) > 1, else single event.

    Args:
        game_id: Game ID.
        events: List of dicts with 'type' and 'data' keys.
        rooms: 'both' | 'players' | 'watchers'
        use_legacy: If True, also send to legacy group.

    Returns:
        bool: True if sent, False on error.
    """
    if not events:
        return False

    try:
        channel_layer = _get_channel_layer()
        gid = int(game_id) if isinstance(game_id, str) and game_id.isdigit() else game_id
        groups = []
        if rooms in ("both", "players"):
            groups.append(room_players(gid))
        if rooms in ("both", "watchers"):
            groups.append(room_watchers(gid))
        if use_legacy:
            groups.append(room_legacy(gid))

        if len(events) == 1:
            ev = events[0]
            for group_name in groups:
                _send_to_group(channel_layer, group_name, ev["type"], ev["data"])
        else:
            for group_name in groups:
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {"type": "batch_events", "data": {"events": events}}
                )

        return True
    except Exception as e:
        import logging
        logging.getLogger(__name__).exception("batch_broadcast_to_game_rooms failed: %s", e)
        return False
