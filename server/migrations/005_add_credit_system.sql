-- User accounts table
CREATE TABLE IF NOT EXISTS users (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Credit balance tracking
CREATE TABLE IF NOT EXISTS credit_balances (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id VARCHAR REFERENCES users(id),
  session_id TEXT,
  credits INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_credit_balances_user_id ON credit_balances(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_balances_session_id ON credit_balances(session_id);

-- Credit transactions
CREATE TABLE IF NOT EXISTS credit_transactions (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
  balance_id VARCHAR NOT NULL REFERENCES credit_balances(id),
  type TEXT NOT NULL,
  amount INTEGER NOT NULL,
  description TEXT,
  file_type TEXT,
  dodo_payment_id TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_credit_transactions_balance_id ON credit_transactions(balance_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_type ON credit_transactions(type);
