-- Credit grants ("lots") enable FIFO consumption and safe unused-only refunds.
-- This migration is additive and safe to apply to existing databases.

CREATE TABLE IF NOT EXISTS credit_grants (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
  balance_id VARCHAR NOT NULL REFERENCES credit_balances(id),
  amount INTEGER NOT NULL,
  remaining INTEGER NOT NULL,
  description TEXT,
  pack TEXT,
  dodo_payment_id TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_credit_grants_balance_id ON credit_grants(balance_id);
CREATE INDEX IF NOT EXISTS idx_credit_grants_payment_id ON credit_grants(dodo_payment_id);

ALTER TABLE credit_transactions
  ADD COLUMN IF NOT EXISTS grant_id VARCHAR REFERENCES credit_grants(id);

CREATE INDEX IF NOT EXISTS idx_credit_transactions_grant_id ON credit_transactions(grant_id);

