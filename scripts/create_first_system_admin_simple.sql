-- ============================================================================
-- Simple SQL Script to Create First System Admin Account
-- ============================================================================
-- This is a simpler version that requires you to generate the password hash
-- using the Python script first: python scripts/generate_password_hash.py
-- ============================================================================

-- Step 1: Generate password hash using Python script:
--   python scripts/generate_password_hash.py "YourSecurePassword123!"
--
-- Step 2: Replace PASSWORD_HASH_HERE below with the generated hash
--
-- Step 3: Update username, email, and name as needed
--
-- Step 4: Run this script

INSERT INTO administrator_accounts (
    tenant_id,
    username,
    email,
    password_hash,
    name,
    role,
    account_status,
    requires_password_change
) VALUES (
    NULL,  -- System admin has no tenant (MUST be NULL)
    'admin',  -- CHANGE THIS: Your desired username
    'admin@example.com',  -- CHANGE THIS: Your email address
    'PASSWORD_HASH_HERE',  -- REPLACE: Use hash from Python script
    'System Administrator',  -- CHANGE THIS: Your full name
    'system_admin',
    'pending_activation',
    TRUE
)
ON CONFLICT (username) DO UPDATE SET
    email = EXCLUDED.email,
    name = EXCLUDED.name
ON CONFLICT (email) DO UPDATE SET
    username = EXCLUDED.username,
    name = EXCLUDED.name;

-- Verify the account was created
SELECT 
    admin_id,
    username,
    email,
    name,
    role,
    account_status,
    requires_password_change,
    created_at
FROM administrator_accounts
WHERE role = 'system_admin'
ORDER BY created_at DESC
LIMIT 1;


