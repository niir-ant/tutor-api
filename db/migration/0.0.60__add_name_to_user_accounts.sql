-- Migration: 0.0.60__add_name_to_user_accounts.sql
-- Description: Add name column to user_accounts table
-- Created: 2025

-- Set search path to tutor schema
SET search_path TO tutor, public;

-- Add name column to user_accounts table
ALTER TABLE tutor.user_accounts 
    ADD COLUMN IF NOT EXISTS name VARCHAR(255);

-- Migrate existing data:
-- For tutors: Copy name from tutor_subject_profiles if available, otherwise use username
UPDATE tutor.user_accounts ua
SET name = COALESCE(
    (SELECT tsp.name FROM tutor.tutor_subject_profiles tsp WHERE tsp.user_id = ua.user_id AND tsp.name IS NOT NULL LIMIT 1),
    ua.username
)
WHERE EXISTS (
    SELECT 1 FROM tutor.user_subject_roles usr 
    WHERE usr.user_id = ua.user_id 
    AND usr.role = 'tutor' 
    AND usr.status = 'active'
);

-- For tenant admins: Copy name from tenant_admin_accounts
UPDATE tutor.user_accounts ua
SET name = taa.name
FROM tutor.tenant_admin_accounts taa
WHERE ua.user_id = taa.user_id
AND ua.name IS NULL;

-- For students: Use username as name
UPDATE tutor.user_accounts ua
SET name = ua.username
WHERE ua.name IS NULL
AND EXISTS (
    SELECT 1 FROM tutor.user_subject_roles usr 
    WHERE usr.user_id = ua.user_id 
    AND usr.role = 'student' 
    AND usr.status = 'active'
);

-- Set default for any remaining NULL values to username
UPDATE tutor.user_accounts
SET name = username
WHERE name IS NULL;

-- Add comment
COMMENT ON COLUMN tutor.user_accounts.name IS 'Display name for the user (defaults to username if not set)';

