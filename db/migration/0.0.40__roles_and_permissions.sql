-- Migration: 0.0.40__roles_and_permissions.sql
-- Description: Database roles and permissions for application users
-- Created: 2025

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

-- Grant usage on schema (assuming public schema, adjust if using custom schema)
GRANT USAGE ON SCHEMA public TO app_user;
GRANT USAGE ON SCHEMA public TO app_readonly;
GRANT USAGE ON SCHEMA public TO app_migrator;

-- Grant all privileges on all tables to app_user (RLS will enforce access control)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;

-- Grant usage on sequences (for UUID generation and serial columns)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- Grant execute on functions
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO app_user;

-- Grant read-only access
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;

-- Grant all privileges to migrator (for running migrations)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_migrator;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_migrator;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO app_migrator;

-- ============================================================================
-- SET DEFAULT PRIVILEGES FOR FUTURE OBJECTS
-- ============================================================================

-- Set default privileges for tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO app_readonly;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT ALL PRIVILEGES ON TABLES TO app_migrator;

-- Set default privileges for sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO app_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT ALL PRIVILEGES ON SEQUENCES TO app_migrator;

-- Set default privileges for functions
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT EXECUTE ON FUNCTIONS TO app_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT ALL PRIVILEGES ON FUNCTIONS TO app_migrator;

-- ============================================================================
-- CREATE HELPER FUNCTIONS FOR ROLE-BASED ACCESS
-- ============================================================================

-- Function to check if current user can access a tenant
CREATE OR REPLACE FUNCTION can_access_tenant(check_tenant_id UUID) RETURNS BOOLEAN AS $$
BEGIN
    -- System admins can access all tenants
    IF is_system_admin() THEN
        RETURN TRUE;
    END IF;
    
    -- Others can only access their own tenant
    RETURN check_tenant_id = current_tenant_id();
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- Function to check if current user can access a student
CREATE OR REPLACE FUNCTION can_access_student(check_student_id UUID) RETURNS BOOLEAN AS $$
DECLARE
    student_tenant_id UUID;
BEGIN
    -- System admins can access all students
    IF is_system_admin() THEN
        RETURN TRUE;
    END IF;
    
    -- Get student's tenant
    SELECT tenant_id INTO student_tenant_id
    FROM student_accounts
    WHERE student_id = check_student_id;
    
    -- Students can access themselves
    IF is_student() AND check_student_id = current_user_id() THEN
        RETURN student_tenant_id = current_tenant_id();
    END IF;
    
    -- Tutors can access assigned students
    IF is_tutor() THEN
        RETURN student_tenant_id = current_tenant_id() AND
               EXISTS (
                   SELECT 1 FROM student_tutor_assignments
                   WHERE student_id = check_student_id
                   AND tutor_id = (SELECT tutor_id FROM tutor_accounts WHERE tutor_id = current_user_id())
                   AND status = 'active'
               );
    END IF;
    
    -- Tenant admins can access students in their tenant
    IF is_tenant_admin() THEN
        RETURN student_tenant_id = current_tenant_id();
    END IF;
    
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- Function to check if current user can access a tutor
CREATE OR REPLACE FUNCTION can_access_tutor(check_tutor_id UUID) RETURNS BOOLEAN AS $$
DECLARE
    tutor_tenant_id UUID;
BEGIN
    -- System admins can access all tutors
    IF is_system_admin() THEN
        RETURN TRUE;
    END IF;
    
    -- Get tutor's tenant
    SELECT tenant_id INTO tutor_tenant_id
    FROM tutor_accounts
    WHERE tutor_id = check_tutor_id;
    
    -- Tutors can access themselves
    IF is_tutor() AND check_tutor_id = (SELECT tutor_id FROM tutor_accounts WHERE tutor_id = current_user_id()) THEN
        RETURN tutor_tenant_id = current_tenant_id();
    END IF;
    
    -- Students can access their assigned tutor
    IF is_student() THEN
        RETURN tutor_tenant_id = current_tenant_id() AND
               EXISTS (
                   SELECT 1 FROM student_tutor_assignments
                   WHERE student_id = current_user_id()
                   AND tutor_id = check_tutor_id
                   AND status = 'active'
               );
    END IF;
    
    -- Tenant admins can access tutors in their tenant
    IF is_tenant_admin() THEN
        RETURN tutor_tenant_id = current_tenant_id();
    END IF;
    
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- ============================================================================
-- CREATE VIEWS FOR COMMON QUERIES (OPTIONAL)
-- ============================================================================

-- View for active students with their tutor assignments
CREATE VIEW v_active_students_with_tutors AS
SELECT
    s.student_id,
    s.tenant_id,
    s.username,
    s.email,
    s.grade_level,
    s.account_status,
    s.assigned_tutor_id,
    t.name AS tutor_name,
    t.email AS tutor_email,
    sta.assigned_at,
    sta.status AS assignment_status
FROM student_accounts s
LEFT JOIN student_tutor_assignments sta ON s.student_id = sta.student_id AND sta.status = 'active'
LEFT JOIN tutor_accounts t ON sta.tutor_id = t.tutor_id
WHERE s.account_status = 'active';

-- Grant access to views
GRANT SELECT ON v_active_students_with_tutors TO app_user;
GRANT SELECT ON v_active_students_with_tutors TO app_readonly;

-- View for competition leaderboards
CREATE VIEW v_competition_leaderboard AS
SELECT
    cs.competition_id,
    cs.student_id,
    sa.username AS student_username,
    sa.grade_level,
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
FROM competition_sessions cs
JOIN student_accounts sa ON cs.student_id = sa.student_id
WHERE cs.status = 'completed';

-- Grant access to competition leaderboard view
GRANT SELECT ON v_competition_leaderboard TO app_user;
GRANT SELECT ON v_competition_leaderboard TO app_readonly;

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

