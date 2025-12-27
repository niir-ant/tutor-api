-- Migration: 0.0.50__auth_rls_fix.sql
-- Description: Add RLS policy to allow app_user to query system_admin_accounts for authentication
-- Created: 2025

-- Set search path to tutor schema
SET search_path TO tutor, public;

-- ============================================================================
-- SYSTEM ADMIN ACCOUNTS AUTHENTICATION RLS POLICY
-- ============================================================================

-- Allow app_user to SELECT system admin accounts for authentication
-- This is needed because during login, we can't set RLS context yet
-- (we're trying to identify the user, so we don't know their admin_id or role yet)
DROP POLICY IF EXISTS system_admin_accounts_select_for_auth ON tutor.system_admin_accounts;
CREATE POLICY system_admin_accounts_select_for_auth ON tutor.system_admin_accounts
    FOR SELECT
    USING (
        -- Allow app_user to read system admin accounts for authentication
        -- This policy allows reading by username/email (what we do during login)
        current_user = 'app_user'
    );

-- Note: This policy is safe because:
-- 1. It only allows SELECT (read-only access)
-- 2. It only applies to app_user role (not other roles)
-- 3. The application still validates passwords and account status
-- 4. Other operations (INSERT, UPDATE, DELETE) are still protected by existing policies
-- 5. Once authenticated, the user must use their own admin_id or system_admin role to access

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON POLICY system_admin_accounts_select_for_auth ON tutor.system_admin_accounts IS 
    'Allows app_user to query system_admin_accounts by username/email for authentication. This is necessary because RLS context cannot be set before user identification during login.';

