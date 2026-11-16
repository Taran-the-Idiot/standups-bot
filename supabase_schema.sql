-- Run this once in the Supabase SQL editor before starting the bot.
-- One row per Slack channel the bot knows about.
create table if not exists public.channel_states (
    channel_id              text primary key,
    active                  boolean not null default false,
    timezone                text not null default 'UTC',
    standup_frequency       text,
    reminder_interval_hours integer,
    next_standup_at         timestamptz,
    next_reminder_at        timestamptz,
    reminder_end_at         timestamptz,
    ping_group_id           text,
    ping_group_users        jsonb not null default '[]'::jsonb,
    last_standup_ts         text,
    last_thread_ts          text,
    last_thread_users       jsonb not null default '[]'::jsonb,
    updated_at              timestamptz not null default now()
);

-- The bot connects with the service role key, which bypasses RLS. Enabling RLS
-- with no policies keeps the table closed to the public anon key.
alter table public.channel_states enable row level security;
