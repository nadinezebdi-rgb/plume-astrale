-- Migration: Journal Email Logs Table
-- Created: 2026-06-22
-- Purpose: Track daily journal email sends for idempotence (one email per user per day)

CREATE TABLE IF NOT EXISTS journal_email_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    sent_date DATE NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'sent' CHECK (status IN ('sent', 'failed', 'bounced')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Ensure one email per user per day
CREATE UNIQUE INDEX IF NOT EXISTS idx_journal_email_logs_user_date 
    ON journal_email_logs (user_id, sent_date);

-- Index for querying by date
CREATE INDEX IF NOT EXISTS idx_journal_email_logs_sent_date 
    ON journal_email_logs (sent_date DESC);

-- Index for querying by user
CREATE INDEX IF NOT EXISTS idx_journal_email_logs_user_id 
    ON journal_email_logs (user_id);
