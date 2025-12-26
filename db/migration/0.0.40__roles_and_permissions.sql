-- Migration: 0.0.40__roles_and_permissions.sql
-- Description: Database roles and permissions for application users
-- Created: 2025

-- ============================================================================
-- CREATE SCHEMA
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS tutor;

-- ============================================================================
-- DROP EXISTING OBJECTS
-- ============================================================================

-- Drop views
DROP VIEW IF EXISTS tutor.v_active_students_with_tutors CASCADE;
DROP VIEW IF EXISTS tutor.v_competition_leaderboard CASCADE;

-- Drop functions
DROP FUNCTION IF EXISTS tutor.can_access_tenant(UUID) CASCADE;
DROP FUNCTION IF EXISTS tutor.can_access_student(UUID) CASCADE;
DROP FUNCTION IF EXISTS tutor.can_access_tutor(UUID) CASCADE;

-- Drop roles (if they exist, they will be recreated)
-- Note: DROP ROLE IF EXISTS may fail if roles have dependencies
-- We'll handle this by recreating roles with OR REPLACE semantics where possible

-- ============================================================================
-- CREATE APPLICATION ROLES
-- ============================================================================

-- Application role (used by the API application)
CREATE ROLE app_user WITH LOGIN PASSWORD 'CHANGE_ME_IN_PRODUCTION';

-- Read-only role for reporting/analytics
CREATE ROLE app_readonly WITH LOGIN PASSWORD 'CHANGE_ME_IN_PRODUCTION';

-- Migration role (for running migrations)
CREATE ROLE app_migrator WITH LOGIN PASSWORD 'CHANGE_ME_IN_PRODUCTION';

-- ============================================================================
-- GRANT PERMISSIONS TO APPLICATION ROLE
-- ============================================================================

-- Grant usage on schema
GRANT USAGE ON SCHEMA tutor TO app_user;
GRANT USAGE ON SCHEMA tutor TO app_readonly;
GRANT USAGE ON SCHEMA tutor TO app_migrator;

-- Grant all privileges on all tables to app_user (RLS will enforce access control)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA tutor TO app_user;

-- Grant usage on sequences (for UUID generation and serial columns)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA tutor TO app_user;

-- Grant execute on functions
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA tutor TO app_user;

-- Grant read-only access
GRANT SELECT ON ALL TABLES IN SCHEMA tutor TO app_readonly;

-- Grant all privileges to migrator (for running migrations)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA tutor TO app_migrator;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA tutor TO app_migrator;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA tutor TO app_migrator;

-- ============================================================================
-- SET DEFAULT PRIVILEGES FOR FUTURE OBJECTS
-- ============================================================================

-- Set default privileges for tables
ALTER DEFAULT PRIVILEGES IN SCHEMA tutor
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA tutor
    GRANT SELECT ON TABLES TO app_readonly;

ALTER DEFAULT PRIVILEGES IN SCHEMA tutor
    GRANT ALL PRIVILEGES ON TABLES TO app_migrator;

-- Set default privileges for sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA tutor
    GRANT USAGE, SELECT ON SEQUENCES TO app_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA tutor
    GRANT ALL PRIVILEGES ON SEQUENCES TO app_migrator;

-- Set default privileges for functions
ALTER DEFAULT PRIVILEGES IN SCHEMA tutor
    GRANT EXECUTE ON FUNCTIONS TO app_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA tutor
    GRANT ALL PRIVILEGES ON FUNCTIONS TO app_migrator;

-- ============================================================================
-- CREATE HELPER FUNCTIONS FOR ROLE-BASED ACCESS
-- ============================================================================

-- Function to check if current user can access a tenant
CREATE OR REPLACE FUNCTION tutor.can_access_tenant(check_tenant_id UUID) RETURNS BOOLEAN AS $$
BEGIN
    -- System admins can access all tenants
    IF tutor.is_system_admin() THEN
        RETURN TRUE;
    END IF;
    
    -- Others can only access their own tenant
    RETURN check_tenant_id = tutor.current_tenant_id();
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- Function to check if current user can access a student
CREATE OR REPLACE FUNCTION tutor.can_access_student(check_student_id UUID) RETURNS BOOLEAN AS $$
DECLARE
    student_tenant_id UUID;
BEGIN
    -- System admins can access all students
    IF tutor.is_system_admin() THEN
        RETURN TRUE;
    END IF;
    
    -- Get student's tenant
    SELECT tenant_id INTO student_tenant_id
    FROM tutor.user_accounts
    WHERE user_id = check_student_id;
    
    -- Students can access themselves
    IF tutor.is_student() AND check_student_id = tutor.current_user_id() THEN
        RETURN student_tenant_id = tutor.current_tenant_id();
    END IF;
    
    -- Tutors can access assigned students (for subjects where they have tutor role)
    IF tutor.is_tutor() THEN
        RETURN student_tenant_id = tutor.current_tenant_id() AND
               EXISTS (
                   SELECT 1 FROM tutor.student_tutor_assignments sta
                   JOIN tutor.user_subject_roles usr ON usr.user_id = tutor.current_user_id()
                   WHERE sta.student_id = check_student_id
                   AND sta.tutor_id = tutor.current_user_id()
                   AND sta.subject_id = usr.subject_id
                   AND usr.role = 'tutor'
                   AND usr.status = 'active'
                   AND sta.status = 'active'
               );
    END IF;
    
    -- Tenant admins can access students in their tenant
    IF tutor.is_tenant_admin() THEN
        RETURN student_tenant_id = tutor.current_tenant_id();
    END IF;
    
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- Function to check if current user can access a tutor
CREATE OR REPLACE FUNCTION tutor.can_access_tutor(check_tutor_id UUID) RETURNS BOOLEAN AS $$
DECLARE
    tutor_tenant_id UUID;
BEGIN
    -- System admins can access all tutors
    IF tutor.is_system_admin() THEN
        RETURN TRUE;
    END IF;
    
    -- Get tutor's tenant
    SELECT tenant_id INTO tutor_tenant_id
    FROM tutor.user_accounts
    WHERE user_id = check_tutor_id;
    
    -- Tutors can access themselves
    IF tutor.is_tutor() AND check_tutor_id = tutor.current_user_id() THEN
        RETURN tutor_tenant_id = tutor.current_tenant_id();
    END IF;
    
    -- Students can access their assigned tutor (for subjects where they have student role)
    IF tutor.is_student() THEN
        RETURN tutor_tenant_id = tutor.current_tenant_id() AND
               EXISTS (
                   SELECT 1 FROM tutor.student_tutor_assignments sta
                   JOIN tutor.user_subject_roles usr ON usr.user_id = tutor.current_user_id()
                   WHERE sta.student_id = tutor.current_user_id()
                   AND sta.tutor_id = check_tutor_id
                   AND sta.subject_id = usr.subject_id
                   AND usr.role = 'student'
                   AND usr.status = 'active'
                   AND sta.status = 'active'
               );
    END IF;
    
    -- Tenant admins can access tutors in their tenant
    IF tutor.is_tenant_admin() THEN
        RETURN tutor_tenant_id = tutor.current_tenant_id();
    END IF;
    
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- ============================================================================
-- CREATE VIEWS FOR COMMON QUERIES (OPTIONAL)
-- ============================================================================

-- View for active students with their tutor assignments (by subject)
CREATE VIEW tutor.v_active_students_with_tutors AS
SELECT
    u.user_id AS student_id,
    u.tenant_id,
    u.username,
    u.email,
    ssp.grade_level,
    u.account_status,
    sta.tutor_id AS assigned_tutor_id,
    tsp.name AS tutor_name,
    ua.email AS tutor_email,
    sta.assigned_at,
    sta.status AS assignment_status,
    sta.subject_id,
    sub.subject_code,
    sub.name AS subject_name
FROM tutor.user_accounts u
JOIN tutor.user_subject_roles usr ON u.user_id = usr.user_id AND usr.role = 'student' AND usr.status = 'active'
LEFT JOIN tutor.student_subject_profiles ssp ON u.user_id = ssp.user_id AND usr.subject_id = ssp.subject_id
LEFT JOIN tutor.student_tutor_assignments sta ON u.user_id = sta.student_id AND sta.status = 'active' AND usr.subject_id = sta.subject_id
LEFT JOIN tutor.tutor_subject_profiles tsp ON sta.tutor_id = tsp.user_id AND sta.subject_id = tsp.subject_id
LEFT JOIN tutor.user_accounts ua ON sta.tutor_id = ua.user_id
LEFT JOIN tutor.subjects sub ON usr.subject_id = sub.subject_id
WHERE u.account_status = 'active';

-- Grant access to views
GRANT SELECT ON tutor.v_active_students_with_tutors TO app_user;
GRANT SELECT ON tutor.v_active_students_with_tutors TO app_readonly;

-- View for competition leaderboards
CREATE VIEW tutor.v_competition_leaderboard AS
SELECT
    cs.competition_id,
    cs.student_id,
    ua.username AS student_username,
    ssp.grade_level,
    cs.score,
    cs.max_score,
    cs.accuracy,
    cs.completion_time,
    cs.questions_answered,
    cs.completed_at,
    ROW_NUMBER() OVER (
        PARTITION BY cs.competition_id
        ORDER BY cs.score DESC, cs.accuracy DESC, cs.completion_time ASC
    ) AS rank
FROM tutor.competition_sessions cs
JOIN tutor.user_accounts ua ON cs.student_id = ua.user_id
LEFT JOIN tutor.quiz_sessions qs ON cs.session_id = qs.session_id
LEFT JOIN tutor.student_subject_profiles ssp ON ua.user_id = ssp.user_id AND qs.subject_id = ssp.subject_id
WHERE cs.status = 'completed';

-- Grant access to competition leaderboard view
GRANT SELECT ON tutor.v_competition_leaderboard TO app_user;
GRANT SELECT ON tutor.v_competition_leaderboard TO app_readonly;

-- ============================================================================
-- COMMENTS ON ROLES
-- ============================================================================

COMMENT ON ROLE app_user IS 'Application user role with full CRUD access (RLS enforced)';
COMMENT ON ROLE app_readonly IS 'Read-only role for reporting and analytics';
COMMENT ON ROLE app_migrator IS 'Role for running database migrations';

-- ============================================================================
-- SECURITY NOTES
-- ============================================================================

-- IMPORTANT SECURITY NOTES:
-- 1. Change all default passwords before deploying to production
-- 2. Use connection pooling with appropriate user roles
-- 3. RLS policies enforce tenant isolation at the database level
-- 4. Application must set session variables:
--    - app.current_tenant_id (UUID)
--    - app.current_user_id (UUID)
--    - app.current_user_role (user_role enum)
-- 5. Use SSL/TLS for all database connections
-- 6. Regularly audit role permissions and RLS policies
-- 7. Consider using separate schemas for different tenants (advanced multi-tenancy)

