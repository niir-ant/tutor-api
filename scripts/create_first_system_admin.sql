-- ============================================================================
-- Script to Create First System Admin Account
-- ============================================================================
-- This script creates the first system administrator account.
-- System admins have tenant_id = NULL (they don't belong to any tenant).
--
-- IMPORTANT: Before running this script:
-- 1. Generate a password hash using the Python helper script:
--    python scripts/generate_password_hash.py
-- 2. Replace the PASSWORD_HASH placeholder below with the generated hash
-- 3. Update the username, email, and name fields as needed
-- ============================================================================

-- Option 1: Using pgcrypto extension (if available)
-- First, enable the extension if not already enabled:
-- CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Generate a temporary password (you can change this)
-- For production, use a strong random password
DO $$
DECLARE
    temp_password TEXT := 'TempPassword123!';  -- CHANGE THIS to a secure password
    password_hash TEXT;
    admin_username TEXT := 'admin';  -- CHANGE THIS to your desired username
    admin_email TEXT := 'admin@example.com';  -- CHANGE THIS to your email
    admin_name TEXT := 'System Administrator';  -- CHANGE THIS to your name
BEGIN
    -- Generate bcrypt hash using pgcrypto
    -- Note: pgcrypto uses bcrypt by default with cost factor 4
    -- For better security, you may want to use Python script instead
    password_hash := crypt(temp_password, gen_salt('bf', 12));
    
    -- Insert the system admin account
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
        NULL,  -- System admin has no tenant
        admin_username,
        admin_email,
        password_hash,
        admin_name,
        'system_admin',
        'pending_activation',
        TRUE
    )
    ON CONFLICT (username) DO NOTHING
    ON CONFLICT (email) DO NOTHING;
    
    -- Display the temporary password (for first login)
    RAISE NOTICE '========================================';
    RAISE NOTICE 'System Admin Account Created!';
    RAISE NOTICE 'Username: %', admin_username;
    RAISE NOTICE 'Email: %', admin_email;
    RAISE NOTICE 'Temporary Password: %', temp_password;
    RAISE NOTICE '========================================';
    RAISE NOTICE 'IMPORTANT: Change password on first login!';
    RAISE NOTICE 'Login with any valid tenant domain (system admin can use any domain)';
    RAISE NOTICE '========================================';
END $$;

-- ============================================================================
-- Alternative: Manual INSERT (if pgcrypto is not available)
-- ============================================================================
-- Uncomment and use this if pgcrypto extension is not available.
-- You MUST generate the password hash using the Python script first:
-- python scripts/generate_password_hash.py
--
-- INSERT INTO administrator_accounts (
--     tenant_id,
--     username,
--     email,
--     password_hash,
--     name,
--     role,
--     account_status,
--     requires_password_change
-- ) VALUES (
--     NULL,  -- System admin has no tenant
--     'admin',  -- CHANGE THIS
--     'admin@example.com',  -- CHANGE THIS
--     'PASSWORD_HASH_HERE',  -- REPLACE with hash from Python script
--     'System Administrator',  -- CHANGE THIS
--     'system_admin',
--     'pending_activation',
--     TRUE
-- )
-- ON CONFLICT (username) DO NOTHING
-- ON CONFLICT (email) DO NOTHING;
-- ============================================================================

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

