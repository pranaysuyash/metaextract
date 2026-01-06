-- Create test user with credits for verification (minimal columns)
BEGIN;

-- First, create test user in users table with minimal columns
INSERT INTO users (id, email, username, password, tier, created_at)
SELECT 'test-user-for-verification', 'test@example.com', 'testuser', 'testpassword123', 'free', NOW()
WHERE NOT EXISTS (
  SELECT 1 FROM users WHERE id = 'test-user-for-verification'
);

-- Then create credit balance for test user
INSERT INTO credit_balances (user_id, session_id, credits)
SELECT 'test-user-for-verification', NULL, 100
WHERE NOT EXISTS (
  SELECT 1 FROM credit_balances WHERE user_id = 'test-user-for-verification'
);

-- Show result
SELECT user_id, credits FROM credit_balances WHERE user_id = 'test-user-for-verification';

COMMIT;
