"""Persist per-channel standup state in a Supabase table.

The table layout lives in supabase_schema.sql. Rows are built from the same
dict shape that standup_logic.serialize_channels produces, so all the
normalisation and defaulting for missing/old values stays in standup_logic.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone

from supabase import Client, create_client

from standup_logic import ChannelState, deserialize_channels, serialize_channels

def _table_name() -> str:
    return os.environ.get("SUPABASE_STATE_TABLE", "channel_states")

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required")
        _client = create_client(url, key)
    return _client


def load_channels() -> dict[str, ChannelState]:
    response = get_client().table(_table_name()).select("*").execute()
    raw = {row["channel_id"]: row for row in (response.data or [])}
    return deserialize_channels(raw)


def save_channels(channels: dict[str, ChannelState]) -> None:
    if not channels:
        return
    now = datetime.now(timezone.utc).isoformat()
    rows = [
        {"channel_id": channel_id, **data, "updated_at": now}
        for channel_id, data in serialize_channels(channels).items()
    ]
    get_client().table(_table_name()).upsert(rows, on_conflict="channel_id").execute()
