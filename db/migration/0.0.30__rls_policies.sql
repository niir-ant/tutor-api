-- Migration: 0.0.30__rls_policies.sql
-- Description: Row Level Security (RLS) policies for multi-tenant data isolation
-- Created: 2025

-- Set search path to tutor schema
SET search_path TO tutor, public;

-- ============================================================================
-- DROP POLICIES (in reverse dependency order)
-- ============================================================================

-- Drop all policies first
DO $$ 
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT schemaname, tablename, policyname FROM pg_policies WHERE schemaname = 'tutor') LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON %I.%I', r.policyname, r.schemaname, r.tablename);
    END LOOP;
END $$;

-- ============================================================================
-- ENABLE ROW LEVEL SECURITY
-- ============================================================================

ALTER TABLE tutor.tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor.tenant_domains ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor.subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor.user_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor.user_subject_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor.student_subject_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor.tutor_subject_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor.tenant_admin_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor.system_admin_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor.password_reset_otp ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor.authentication_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor.questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor.quiz_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor.answer_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor.hints ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor.student_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor.student_tutor_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor.messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor.competitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor.competition_registrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor.competition_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor.audit_logs ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- HELPER FUNCTIONS FOR RLS
-- ============================================================================

-- ============================================================================
-- DROP HELPER FUNCTIONS
-- ============================================================================

DROP FUNCTION IF EXISTS tutor.set_context(UUID, UUID, tutor.user_role);
DROP FUNCTION IF EXISTS tutor.has_tutor_role_for_subject(UUID);
DROP FUNCTION IF EXISTS tutor.has_student_role_for_subject(UUID);
DROP FUNCTION IF EXISTS tutor.is_student();
DROP FUNCTION IF EXISTS tutor.is_tutor();
DROP FUNCTION IF EXISTS tutor.is_tenant_admin();
DROP FUNCTION IF EXISTS tutor.is_system_admin();
DROP FUNCTION IF EXISTS tutor.current_user_id();
DROP FUNCTION IF EXISTS tutor.current_user_role();
DROP FUNCTION IF EXISTS tutor.current_tenant_id();

-- ============================================================================
-- CREATE CONTEXT MANAGEMENT FUNCTIONS
-- ============================================================================

-- Function to set transaction-local context for RLS
-- This function MUST be called at the beginning of each transaction
-- DO NOT use SET commands directly - use this function instead
CREATE OR REPLACE FUNCTION tutor.set_context(
    p_tenant_id UUID,
    p_user_id UUID,
    p_user_role tutor.user_role
) RETURNS VOID AS $$
BEGIN
    -- Validate inputs
    IF p_tenant_id IS NULL AND p_user_role != 'system_admin' THEN
        RAISE EXCEPTION 'tenant_id cannot be NULL for non-system-admin users';
    END IF;
    
    IF p_user_id IS NULL THEN
        RAISE EXCEPTION 'user_id cannot be NULL';
    END IF;
    
    IF p_user_role IS NULL THEN
        RAISE EXCEPTION 'user_role cannot be NULL';
    END IF;
    
    -- Set transaction-local context variables (automatically rolled back on transaction end)
    -- FALSE parameter makes it transaction-local (equivalent to SET LOCAL)
    -- For system_admin with NULL tenant_id, the variable will be set but current_tenant_id()
    -- will return NULL (which is correct - system_admin can access all tenants)
    PERFORM set_config('app.current_tenant_id', COALESCE(p_tenant_id::TEXT, ''), FALSE);
    PERFORM set_config('app.current_user_id', p_user_id::TEXT, FALSE);
    PERFORM set_config('app.current_user_role', p_user_role::TEXT, FALSE);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission to app_user
GRANT EXECUTE ON FUNCTION tutor.set_context(UUID, UUID, tutor.user_role) TO app_user;

-- ============================================================================
-- CREATE HELPER FUNCTIONS FOR RLS
-- ============================================================================

-- Function to get current user's tenant_id from context
-- Reads from transaction-local context set by tutor.set_context()
-- Returns NULL for system_admin (empty string is converted to NULL)
CREATE OR REPLACE FUNCTION tutor.current_tenant_id() RETURNS UUID AS $$
DECLARE
    v_tenant_id_text TEXT;
BEGIN
    v_tenant_id_text := current_setting('app.current_tenant_id', TRUE);
    -- Empty string means system_admin (access all tenants) - return NULL
    IF v_tenant_id_text = '' OR v_tenant_id_text IS NULL THEN
        RETURN NULL;
    END IF;
    RETURN v_tenant_id_text::UUID;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to get current user's role from context
-- Reads from transaction-local context set by tutor.set_context()
CREATE OR REPLACE FUNCTION tutor.current_user_role() RETURNS tutor.user_role AS $$
BEGIN
    RETURN current_setting('app.current_user_role', TRUE)::tutor.user_role;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to get current user's ID from context
-- Reads from transaction-local context set by tutor.set_context()
CREATE OR REPLACE FUNCTION tutor.current_user_id() RETURNS UUID AS $$
BEGIN
    RETURN current_setting('app.current_user_id', TRUE)::UUID;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to check if user is system admin
CREATE OR REPLACE FUNCTION tutor.is_system_admin() RETURNS BOOLEAN AS $$
BEGIN
    RETURN tutor.current_user_role() = 'system_admin';
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to check if user is tenant admin
CREATE OR REPLACE FUNCTION tutor.is_tenant_admin() RETURNS BOOLEAN AS $$
BEGIN
    RETURN tutor.current_user_role() = 'tenant_admin';
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to check if user is tutor
CREATE OR REPLACE FUNCTION tutor.is_tutor() RETURNS BOOLEAN AS $$
BEGIN
    RETURN tutor.current_user_role() = 'tutor';
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to check if user is student
CREATE OR REPLACE FUNCTION tutor.is_student() RETURNS BOOLEAN AS $$
BEGIN
    RETURN tutor.current_user_role() = 'student';
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to check if current user has student role for a subject
CREATE OR REPLACE FUNCTION tutor.has_student_role_for_subject(check_subject_id UUID) RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM tutor.user_subject_roles
        WHERE user_id = tutor.current_user_id()
        AND subject_id = check_subject_id
        AND role = 'student'
        AND status = 'active'
    );
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to check if current user has tutor role for a subject
CREATE OR REPLACE FUNCTION tutor.has_tutor_role_for_subject(check_subject_id UUID) RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM tutor.user_subject_roles
        WHERE user_id = tutor.current_user_id()
        AND subject_id = check_subject_id
        AND role = 'tutor'
        AND status = 'active'
    );
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- TENANTS RLS POLICIES
-- ============================================================================

-- System admins can see all tenants
DROP POLICY IF EXISTS tenants_select_system_admin ON tutor.tenants;
CREATE POLICY tenants_select_system_admin ON tutor.tenants
    FOR SELECT
    USING (tutor.is_system_admin());

-- Tenant admins can see their own tenant
DROP POLICY IF EXISTS tenants_select_tenant_admin ON tutor.tenants;
CREATE POLICY tenants_select_tenant_admin ON tutor.tenants
    FOR SELECT
    USING (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin());

-- System admins can insert/update/delete tenants
DROP POLICY IF EXISTS tenants_modify_system_admin ON tutor.tenants;
CREATE POLICY tenants_modify_system_admin ON tutor.tenants
    FOR ALL
    USING (tutor.is_system_admin())
    WITH CHECK (tutor.is_system_admin());

-- ============================================================================
-- TENANT DOMAINS RLS POLICIES
-- ============================================================================

-- System admins can see all domains
DROP POLICY IF EXISTS tenant_domains_select_system_admin ON tutor.tenant_domains;
CREATE POLICY tenant_domains_select_system_admin ON tutor.tenant_domains
    FOR SELECT
    USING (tutor.is_system_admin());

-- Tenant admins can see domains for their tenant
DROP POLICY IF EXISTS tenant_domains_select_tenant_admin ON tutor.tenant_domains;
CREATE POLICY tenant_domains_select_tenant_admin ON tutor.tenant_domains
    FOR SELECT
    USING (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin());

-- System admins can modify domains
DROP POLICY IF EXISTS tenant_domains_modify_system_admin ON tutor.tenant_domains;
CREATE POLICY tenant_domains_modify_system_admin ON tutor.tenant_domains
    FOR ALL
    USING (tutor.is_system_admin())
    WITH CHECK (tutor.is_system_admin());

-- Everyone can see active subjects (system-wide)
DROP POLICY IF EXISTS subjects_select_all ON subjects;
=============================
-- SUBJECTS RLS POLICIES
-- ============================================================================

-- Everyone can see active subjects (system-wide)
DROP POLICY IF EXISTS subjects_select_all ON tutor.subjects;
CREATE POLICY subjects_select_all ON tutor.subjects
    FOR SELECT
    USING (status = 'active');

-- System admins can see all subjects
DROP POLICY IF EXISTS subjects_select_system_admin ON tutor.subjects;
CREATE POLICY subjects_select_system_admin ON tutor.subjects
    FOR SELECT
    USING (tutor.is_system_admin());

-- System admins can modify subjects
DROP POLICY IF EXISTS subjects_modify_system_admin ON tutor.subjects;
CREATE POLICY subjects_modify_system_admin ON tutor.subjects
    FOR ALL
    USING (tutor.is_system_admin())
    WITH CHECK (tutor.is_system_admin());

-- ============================================================================
-- USER ACCOUNTS RLS POLICIES
-- ============================================================================

-- Users can see their own account
DROP POLICY IF EXISTS user_accounts_select_self ON tutor.user_accounts;
CREATE POLICY user_accounts_select_self ON tutor.user_accounts
    FOR SELECT
    USING (user_id = tutor.current_user_id());

-- Tutors can see users they are assigned to (for any subject)
DROP POLICY IF EXISTS user_accounts_select_tutor ON tutor.user_accounts;
CREATE POLICY user_accounts_select_tutor ON tutor.user_accounts
    FOR SELECT
    USING (
        tenant_id = tutor.current_tenant_id() AND
        tutor.is_tutor() AND
        EXISTS (
            SELECT 1 FROM tutor.student_tutor_assignments
            WHERE student_id = tutor.user_accounts.user_id
            AND tutor_id = tutor.current_user_id()
            AND status = 'active'
        )
    );

-- Tenant admins can see users in their tenant
DROP POLICY IF EXISTS user_accounts_select_tenant_admin ON tutor.user_accounts;
CREATE POLICY user_accounts_select_tenant_admin ON tutor.user_accounts
    FOR SELECT
    USING (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin());

-- System admins can see all users
DROP POLICY IF EXISTS user_accounts_select_system_admin ON tutor.user_accounts;
CREATE POLICY user_accounts_select_system_admin ON tutor.user_accounts
    FOR SELECT
    USING (tutor.is_system_admin());

-- Users can update their own account (limited fields)
DROP POLICY IF EXISTS user_accounts_update_self ON tutor.user_accounts;
CREATE POLICY user_accounts_update_self ON tutor.user_accounts
    FOR UPDATE
    USING (user_id = tutor.current_user_id())
    WITH CHECK (user_id = tutor.current_user_id());

-- Tenant admins can modify users in their tenant
DROP POLICY IF EXISTS user_accounts_modify_tenant_admin ON tutor.user_accounts;
CREATE POLICY user_accounts_modify_tenant_admin ON tutor.user_accounts
    FOR ALL
    USING (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin())
    WITH CHECK (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin());

-- System admins can modify all users
DROP POLICY IF EXISTS user_accounts_modify_system_admin ON tutor.user_accounts;
CREATE POLICY user_accounts_modify_system_admin ON tutor.user_accounts
    FOR ALL
    USING (tutor.is_system_admin())
    WITH CHECK (tutor.is_system_admin());

-- Tutors can see their own account
-- ============================================================================
-- USER SUBJECT ROLES RLS POLICIES
-- ============================================================================

-- Users can see their own role assignments
DROP POLICY IF EXISTS user_subject_roles_select_self ON tutor.user_subject_roles;
CREATE POLICY user_subject_roles_select_self ON tutor.user_subject_roles
    FOR SELECT
    USING (user_id = tutor.current_user_id());

-- Tenant admins can see role assignments in their tenant
DROP POLICY IF EXISTS user_subject_roles_select_tenant_admin ON tutor.user_subject_roles;
CREATE POLICY user_subject_roles_select_tenant_admin ON tutor.user_subject_roles
    FOR SELECT
    USING (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin());

-- System admins can see all role assignments
DROP POLICY IF EXISTS user_subject_roles_select_system_admin ON tutor.user_subject_roles;
CREATE POLICY user_subject_roles_select_system_admin ON tutor.user_subject_roles
    FOR SELECT
    USING (tutor.is_system_admin());

-- Tenant admins can modify role assignments in their tenant
DROP POLICY IF EXISTS user_subject_roles_modify_tenant_admin ON tutor.user_subject_roles;
CREATE POLICY user_subject_roles_modify_tenant_admin ON tutor.user_subject_roles
    FOR ALL
    USING (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin())
    WITH CHECK (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin());

-- System admins can modify all role assignments
DROP POLICY IF EXISTS user_subject_roles_modify_system_admin ON tutor.user_subject_roles;
CREATE POLICY user_subject_roles_modify_system_admin ON tutor.user_subject_roles
    FOR ALL
    USING (tutor.is_system_admin())
    WITH CHECK (tutor.is_system_admin());

-- ============================================================================
-- STUDENT SUBJECT PROFILES RLS POLICIES
-- ============================================================================

-- Students can see their own profiles
DROP POLICY IF EXISTS student_subject_profiles_select_self ON tutor.student_subject_profiles;
CREATE POLICY student_subject_profiles_select_self ON tutor.student_subject_profiles
    FOR SELECT
    USING (user_id = tutor.current_user_id());

-- Tutors can see profiles of their assigned students (for the subject)
DROP POLICY IF EXISTS student_subject_profiles_select_tutor ON tutor.student_subject_profiles;
CREATE POLICY student_subject_profiles_select_tutor ON tutor.student_subject_profiles
    FOR SELECT
    USING (
        tenant_id = tutor.current_tenant_id() AND
        tutor.is_tutor() AND
        EXISTS (
            SELECT 1 FROM tutor.student_tutor_assignments
            WHERE student_id = tutor.student_subject_profiles.user_id
            AND tutor_id = tutor.current_user_id()
            AND subject_id = tutor.student_subject_profiles.subject_id
            AND status = 'active'
        )
    );

-- Tenant admins can see profiles in their tenant
DROP POLICY IF EXISTS student_subject_profiles_select_tenant_admin ON tutor.student_subject_profiles;
CREATE POLICY student_subject_profiles_select_tenant_admin ON tutor.student_subject_profiles
    FOR SELECT
    USING (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin());

-- System admins can see all profiles
DROP POLICY IF EXISTS student_subject_profiles_select_system_admin ON tutor.student_subject_profiles;
CREATE POLICY student_subject_profiles_select_system_admin ON tutor.student_subject_profiles
    FOR SELECT
    USING (tutor.is_system_admin());

-- Students can update their own profiles
DROP POLICY IF EXISTS student_subject_profiles_update_self ON tutor.student_subject_profiles;
CREATE POLICY student_subject_profiles_update_self ON tutor.student_subject_profiles
    FOR UPDATE
    USING (user_id = tutor.current_user_id())
    WITH CHECK (user_id = tutor.current_user_id());

-- Tenant admins can modify profiles in their tenant
DROP POLICY IF EXISTS student_subject_profiles_modify_tenant_admin ON tutor.student_subject_profiles;
CREATE POLICY student_subject_profiles_modify_tenant_admin ON tutor.student_subject_profiles
    FOR ALL
    USING (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin())
    WITH CHECK (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin());

-- System admins can modify all profiles
DROP POLICY IF EXISTS student_subject_profiles_modify_system_admin ON tutor.student_subject_profiles;
CREATE POLICY student_subject_profiles_modify_system_admin ON tutor.student_subject_profiles
    FOR ALL
    USING (tutor.is_system_admin())
    WITH CHECK (tutor.is_system_admin());

-- ============================================================================
-- TUTOR SUBJECT PROFILES RLS POLICIES
-- ============================================================================

-- Tutors can see their own profiles
DROP POLICY IF EXISTS tutor_subject_profiles_select_self ON tutor.tutor_subject_profiles;
CREATE POLICY tutor_subject_profiles_select_self ON tutor.tutor_subject_profiles
    FOR SELECT
    USING (user_id = tutor.current_user_id());

-- Students can see profiles of their assigned tutors (for the subject)
DROP POLICY IF EXISTS tutor_subject_profiles_select_student ON tutor.tutor_subject_profiles;
CREATE POLICY tutor_subject_profiles_select_student ON tutor.tutor_subject_profiles
    FOR SELECT
    USING (
        tenant_id = tutor.current_tenant_id() AND
        tutor.is_student() AND
        EXISTS (
            SELECT 1 FROM tutor.student_tutor_assignments
            WHERE student_id = tutor.current_user_id()
            AND tutor_id = tutor.tutor_subject_profiles.user_id
            AND subject_id = tutor.tutor_subject_profiles.subject_id
            AND status = 'active'
        )
    );

-- Tenant admins can see profiles in their tenant
DROP POLICY IF EXISTS tutor_subject_profiles_select_tenant_admin ON tutor.tutor_subject_profiles;
CREATE POLICY tutor_subject_profiles_select_tenant_admin ON tutor.tutor_subject_profiles
    FOR SELECT
    USING (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin());

-- System admins can see all profiles
DROP POLICY IF EXISTS tutor_subject_profiles_select_system_admin ON tutor.tutor_subject_profiles;
CREATE POLICY tutor_subject_profiles_select_system_admin ON tutor.tutor_subject_profiles
    FOR SELECT
    USING (tutor.is_system_admin());

-- Tutors can update their own profiles
DROP POLICY IF EXISTS tutor_subject_profiles_update_self ON tutor.tutor_subject_profiles;
CREATE POLICY tutor_subject_profiles_update_self ON tutor.tutor_subject_profiles
    FOR UPDATE
    USING (user_id = tutor.current_user_id())
    WITH CHECK (user_id = tutor.current_user_id());

-- Tenant admins can modify profiles in their tenant
DROP POLICY IF EXISTS tutor_subject_profiles_modify_tenant_admin ON tutor.tutor_subject_profiles;
CREATE POLICY tutor_subject_profiles_modify_tenant_admin ON tutor.tutor_subject_profiles
    FOR ALL
    USING (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin())
    WITH CHECK (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin());

-- System admins can modify all profiles
DROP POLICY IF EXISTS tutor_subject_profiles_modify_system_admin ON tutor.tutor_subject_profiles;
CREATE POLICY tutor_subject_profiles_modify_system_admin ON tutor.tutor_subject_profiles
    FOR ALL
    USING (tutor.is_system_admin())
    WITH CHECK (tutor.is_system_admin());

-- ============================================================================
-- TENANT ADMIN ACCOUNTS RLS POLICIES
-- ============================================================================

-- Tenant admins can see their own account
DROP POLICY IF EXISTS tenant_admin_accounts_select_self ON tutor.tenant_admin_accounts;
CREATE POLICY tenant_admin_accounts_select_self ON tutor.tenant_admin_accounts
    FOR SELECT
    USING (user_id = tutor.current_user_id());

-- Tenant admins can see other tenant admins in their tenant
DROP POLICY IF EXISTS tenant_admin_accounts_select_tenant_admin ON tutor.tenant_admin_accounts;
CREATE POLICY tenant_admin_accounts_select_tenant_admin ON tutor.tenant_admin_accounts
    FOR SELECT
    USING (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin());

-- System admins can see all tenant admins
DROP POLICY IF EXISTS tenant_admin_accounts_select_system_admin ON tutor.tenant_admin_accounts;
CREATE POLICY tenant_admin_accounts_select_system_admin ON tutor.tenant_admin_accounts
    FOR SELECT
    USING (tutor.is_system_admin());

-- Tenant admins can update their own account
DROP POLICY IF EXISTS tenant_admin_accounts_update_self ON tutor.tenant_admin_accounts;
CREATE POLICY tenant_admin_accounts_update_self ON tutor.tenant_admin_accounts
    FOR UPDATE
    USING (user_id = tutor.current_user_id())
    WITH CHECK (user_id = tutor.current_user_id());

-- System admins can modify all tenant admins
DROP POLICY IF EXISTS tenant_admin_accounts_modify_system_admin ON tutor.tenant_admin_accounts;
CREATE POLICY tenant_admin_accounts_modify_system_admin ON tutor.tenant_admin_accounts
    FOR ALL
    USING (tutor.is_system_admin())
    WITH CHECK (tutor.is_system_admin());

-- ============================================================================
-- SYSTEM ADMIN ACCOUNTS RLS POLICIES
-- ============================================================================

-- System admins can see their own account
DROP POLICY IF EXISTS system_admin_accounts_select_self ON tutor.system_admin_accounts;
CREATE POLICY system_admin_accounts_select_self ON tutor.system_admin_accounts
    FOR SELECT
    USING (admin_id = tutor.current_user_id());

-- System admins can see all system admins
DROP POLICY IF EXISTS system_admin_accounts_select_system_admin ON tutor.system_admin_accounts;
CREATE POLICY system_admin_accounts_select_system_admin ON tutor.system_admin_accounts
    FOR SELECT
    USING (tutor.is_system_admin());

-- App migrator role can see all system admin accounts (for migrations and setup)
DROP POLICY IF EXISTS system_admin_accounts_select_migrator ON tutor.system_admin_accounts;
CREATE POLICY system_admin_accounts_select_migrator ON tutor.system_admin_accounts
    FOR SELECT
    USING (current_user = 'app_migrator');

-- System admins can modify all system admins
DROP POLICY IF EXISTS system_admin_accounts_modify_system_admin ON tutor.system_admin_accounts;
CREATE POLICY system_admin_accounts_modify_system_admin ON tutor.system_admin_accounts
    FOR ALL
    USING (tutor.is_system_admin())
    WITH CHECK (tutor.is_system_admin());

-- App migrator role can insert/update system admin accounts (for initial setup)
DROP POLICY IF EXISTS system_admin_accounts_modify_migrator ON tutor.system_admin_accounts;
CREATE POLICY system_admin_accounts_modify_migrator ON tutor.system_admin_accounts
    FOR ALL
    USING (current_user = 'app_migrator')
    WITH CHECK (current_user = 'app_migrator');

-- ============================================================================
-- QUIZ SESSIONS RLS POLICIES
-- ============================================================================

-- Students can see their own sessions (must have student role for the subject)
DROP POLICY IF EXISTS quiz_sessions_select_student ON tutor.quiz_sessions;
CREATE POLICY quiz_sessions_select_student ON tutor.quiz_sessions
    FOR SELECT
    USING (
        student_id = tutor.current_user_id() 
        AND tutor.is_student() 
        AND tenant_id = tutor.current_tenant_id()
        AND tutor.has_student_role_for_subject(subject_id)
    );

-- Tutors can see sessions of their assigned students (for the subject)
DROP POLICY IF EXISTS quiz_sessions_select_tutor ON tutor.quiz_sessions;
CREATE POLICY quiz_sessions_select_tutor ON tutor.quiz_sessions
    FOR SELECT
    USING (
        tenant_id = tutor.current_tenant_id() AND
        tutor.is_tutor() AND
        tutor.has_tutor_role_for_subject(subject_id) AND
        EXISTS (
            SELECT 1 FROM tutor.student_tutor_assignments
            WHERE student_id = tutor.quiz_sessions.student_id
            AND tutor_id = tutor.current_user_id()
            AND subject_id = tutor.quiz_sessions.subject_id
            AND status = 'active'
        )
    );

-- Tenant admins can see sessions in their tenant
DROP POLICY IF EXISTS quiz_sessions_select_tenant_admin ON tutor.quiz_sessions;
CREATE POLICY quiz_sessions_select_tenant_admin ON tutor.quiz_sessions
    FOR SELECT
    USING (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin());

-- System admins can see all sessions
DROP POLICY IF EXISTS quiz_sessions_select_system_admin ON tutor.quiz_sessions;
CREATE POLICY quiz_sessions_select_system_admin ON tutor.quiz_sessions
    FOR SELECT
    USING (tutor.is_system_admin());

-- Students can create/update their own sessions (must have student role for the subject)
DROP POLICY IF EXISTS quiz_sessions_modify_student ON tutor.quiz_sessions;
CREATE POLICY quiz_sessions_modify_student ON tutor.quiz_sessions
    FOR ALL
    USING (
        student_id = tutor.current_user_id() 
        AND tutor.is_student() 
        AND tenant_id = tutor.current_tenant_id()
        AND tutor.has_student_role_for_subject(subject_id)
    )
    WITH CHECK (
        student_id = tutor.current_user_id() 
        AND tutor.is_student() 
        AND tenant_id = tutor.current_tenant_id()
        AND tutor.has_student_role_for_subject(subject_id)
    );

-- ============================================================================
-- ANSWER SUBMISSIONS RLS POLICIES
-- ============================================================================

-- Students can see their own submissions
DROP POLICY IF EXISTS answer_submissions_select_student ON tutor.answer_submissions;
CREATE POLICY answer_submissions_select_student ON tutor.answer_submissions
    FOR SELECT
    USING (student_id = tutor.current_user_id() AND tutor.is_student() AND tenant_id = tutor.current_tenant_id());

-- Tutors can see submissions of their assigned students (for the subject)
DROP POLICY IF EXISTS answer_submissions_select_tutor ON tutor.answer_submissions;
CREATE POLICY answer_submissions_select_tutor ON tutor.answer_submissions
    FOR SELECT
    USING (
        tenant_id = tutor.current_tenant_id() AND
        tutor.is_tutor() AND
        EXISTS (
            SELECT 1 FROM tutor.student_tutor_assignments sta
            JOIN tutor.quiz_sessions qs ON qs.session_id = tutor.answer_submissions.session_id
            WHERE sta.student_id = tutor.answer_submissions.student_id
            AND sta.tutor_id = tutor.current_user_id()
            AND sta.subject_id = qs.subject_id
            AND sta.status = 'active'
        )
    );

-- Tenant admins can see submissions in their tenant
DROP POLICY IF EXISTS answer_submissions_select_tenant_admin ON tutor.answer_submissions;
CREATE POLICY answer_submissions_select_tenant_admin ON tutor.answer_submissions
    FOR SELECT
    USING (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin());

-- System admins can see all submissions
DROP POLICY IF EXISTS answer_submissions_select_system_admin ON tutor.answer_submissions;
CREATE POLICY answer_submissions_select_system_admin ON tutor.answer_submissions
    FOR SELECT
    USING (tutor.is_system_admin());

-- Students can create their own submissions
DROP POLICY IF EXISTS answer_submissions_modify_student ON tutor.answer_submissions;
CREATE POLICY answer_submissions_modify_student ON tutor.answer_submissions
    FOR ALL
    USING (student_id = tutor.current_user_id() AND tutor.is_student() AND tenant_id = tutor.current_tenant_id())
    WITH CHECK (student_id = tutor.current_user_id() AND tutor.is_student() AND tenant_id = tutor.current_tenant_id());

-- ============================================================================
-- STUDENT PROGRESS RLS POLICIES
-- ============================================================================

-- Students can see their own progress
DROP POLICY IF EXISTS student_progress_select_student ON tutor.student_progress;
CREATE POLICY student_progress_select_student ON tutor.student_progress
    FOR SELECT
    USING (student_id = tutor.current_user_id() AND tutor.is_student() AND tenant_id = tutor.current_tenant_id());

-- Tutors can see progress of their assigned students (for any subject)
DROP POLICY IF EXISTS student_progress_select_tutor ON tutor.student_progress;
CREATE POLICY student_progress_select_tutor ON tutor.student_progress
    FOR SELECT
    USING (
        tenant_id = tutor.current_tenant_id() AND
        tutor.is_tutor() AND
        EXISTS (
            SELECT 1 FROM tutor.student_tutor_assignments
            WHERE student_id = tutor.student_progress.student_id
            AND tutor_id = tutor.current_user_id()
            AND status = 'active'
        )
    );

-- Tenant admins can see progress in their tenant
DROP POLICY IF EXISTS student_progress_select_tenant_admin ON tutor.student_progress;
CREATE POLICY student_progress_select_tenant_admin ON tutor.student_progress
    FOR SELECT
    USING (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin());

-- System admins can see all progress
DROP POLICY IF EXISTS student_progress_select_system_admin ON tutor.student_progress;
CREATE POLICY student_progress_select_system_admin ON tutor.student_progress
    FOR SELECT
    USING (tutor.is_system_admin());

-- ============================================================================
-- QUESTIONS RLS POLICIES
-- ============================================================================

-- Everyone can see questions (system-wide or tenant-specific)
DROP POLICY IF EXISTS questions_select_all ON tutor.questions;
CREATE POLICY questions_select_all ON tutor.questions
    FOR SELECT
    USING (
        tenant_id IS NULL OR
        tenant_id = tutor.current_tenant_id() OR
        tutor.is_system_admin()
    );

-- System admins can modify questions
DROP POLICY IF EXISTS questions_modify_system_admin ON tutor.questions;
CREATE POLICY questions_modify_system_admin ON tutor.questions
    FOR ALL
    USING (tutor.is_system_admin())
    WITH CHECK (tutor.is_system_admin());

-- ============================================================================
-- HINTS RLS POLICIES
-- ============================================================================

-- Students can see hints for questions they're working on
DROP POLICY IF EXISTS hints_select_student ON tutor.hints;
CREATE POLICY hints_select_student ON tutor.hints
    FOR SELECT
    USING (
        tenant_id = tutor.current_tenant_id() AND
        tutor.is_student()
    );

-- Tutors and admins can see hints
DROP POLICY IF EXISTS hints_select_authorized ON tutor.hints;
CREATE POLICY hints_select_authorized ON tutor.hints
    FOR SELECT
    USING (
        tenant_id = tutor.current_tenant_id() AND
        (tutor.is_tutor() OR tutor.is_tenant_admin() OR tutor.is_system_admin())
    );

-- System admins can modify hints
DROP POLICY IF EXISTS hints_modify_system_admin ON tutor.hints;
CREATE POLICY hints_modify_system_admin ON tutor.hints
    FOR ALL
    USING (tutor.is_system_admin())
    WITH CHECK (tutor.is_system_admin());

-- ============================================================================
-- STUDENT-TUTOR ASSIGNMENTS RLS POLICIES
-- ============================================================================

-- Tutors can see their own assignments (for subjects where they have tutor role)
DROP POLICY IF EXISTS student_tutor_assignments_select_tutor ON tutor.student_tutor_assignments;
CREATE POLICY student_tutor_assignments_select_tutor ON tutor.student_tutor_assignments
    FOR SELECT
    USING (
        tenant_id = tutor.current_tenant_id() AND
        tutor.is_tutor() AND
        tutor_id = tutor.current_user_id() AND
        tutor.has_tutor_role_for_subject(subject_id)
    );

-- Students can see their assignment
DROP POLICY IF EXISTS student_tutor_assignments_select_student ON tutor.student_tutor_assignments;
CREATE POLICY student_tutor_assignments_select_student ON tutor.student_tutor_assignments
    FOR SELECT
    USING (
        tenant_id = tutor.current_tenant_id() AND
        tutor.is_student() AND
        student_id = tutor.current_user_id()
    );

-- Tenant admins can see assignments in their tenant
DROP POLICY IF EXISTS student_tutor_assignments_select_tenant_admin ON tutor.student_tutor_assignments;
CREATE POLICY student_tutor_assignments_select_tenant_admin ON tutor.student_tutor_assignments
    FOR SELECT
    USING (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin());

-- System admins can see all assignments
DROP POLICY IF EXISTS student_tutor_assignments_select_system_admin ON tutor.student_tutor_assignments;
CREATE POLICY student_tutor_assignments_select_system_admin ON tutor.student_tutor_assignments
    FOR SELECT
    USING (tutor.is_system_admin());

-- Tenant admins can modify assignments in their tenant
DROP POLICY IF EXISTS student_tutor_assignments_modify_tenant_admin ON tutor.student_tutor_assignments;
CREATE POLICY student_tutor_assignments_modify_tenant_admin ON tutor.student_tutor_assignments
    FOR ALL
    USING (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin())
    WITH CHECK (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin());

-- System admins can modify all assignments
DROP POLICY IF EXISTS student_tutor_assignments_modify_system_admin ON tutor.student_tutor_assignments;
CREATE POLICY student_tutor_assignments_modify_system_admin ON tutor.student_tutor_assignments
    FOR ALL
    USING (tutor.is_system_admin())
    WITH CHECK (tutor.is_system_admin());

-- ============================================================================
-- MESSAGES RLS POLICIES
-- ============================================================================

-- Users can see messages they sent or received
DROP POLICY IF EXISTS messages_select_participant ON tutor.messages;
CREATE POLICY messages_select_participant ON tutor.messages
    FOR SELECT
    USING (
        tenant_id = tutor.current_tenant_id() AND
        (
            sender_id = tutor.current_user_id() OR
            recipient_id = tutor.current_user_id()
        ) AND
        deleted_at IS NULL
    );

-- Tenant admins can see messages in their tenant
DROP POLICY IF EXISTS messages_select_tenant_admin ON tutor.messages;
CREATE POLICY messages_select_tenant_admin ON tutor.messages
    FOR SELECT
    USING (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin());

-- System admins can see all messages
DROP POLICY IF EXISTS messages_select_system_admin ON tutor.messages;
CREATE POLICY messages_select_system_admin ON tutor.messages
    FOR SELECT
    USING (tutor.is_system_admin());

-- Users can send messages (students to tutors, tutors to students)
DROP POLICY IF EXISTS messages_insert_authorized ON tutor.messages;
CREATE POLICY messages_insert_authorized ON tutor.messages
    FOR INSERT
    WITH CHECK (
        tenant_id = tutor.current_tenant_id() AND
        sender_id = tutor.current_user_id() AND
        (
            (tutor.is_student() AND EXISTS (
                SELECT 1 FROM tutor.student_tutor_assignments
                WHERE student_id = tutor.current_user_id()
                AND tutor_id = tutor.messages.recipient_id
                AND status = 'active'
            )) OR
            (tutor.is_tutor() AND EXISTS (
                SELECT 1 FROM tutor.student_tutor_assignments
                WHERE student_id = tutor.messages.recipient_id
                AND tutor_id = tutor.current_user_id()
                AND status = 'active'
            )) OR
            tutor.is_tenant_admin() OR
            tutor.is_system_admin()
        )
    );

-- Users can update their own messages
DROP POLICY IF EXISTS messages_update_self ON tutor.messages;
CREATE POLICY messages_update_self ON tutor.messages
    FOR UPDATE
    USING (sender_id = tutor.current_user_id() AND tenant_id = tutor.current_tenant_id())
    WITH CHECK (sender_id = tutor.current_user_id() AND tenant_id = tutor.current_tenant_id());

-- Recipients can mark messages as read
DROP POLICY IF EXISTS messages_update_recipient ON tutor.messages;
CREATE POLICY messages_update_recipient ON tutor.messages
    FOR UPDATE
    USING (recipient_id = tutor.current_user_id() AND tenant_id = tutor.current_tenant_id())
    WITH CHECK (recipient_id = tutor.current_user_id() AND tenant_id = tutor.current_tenant_id());

-- ============================================================================
-- COMPETITIONS RLS POLICIES
-- ============================================================================

-- Everyone can see public competitions or competitions in their tenant
DROP POLICY IF EXISTS competitions_select_public ON tutor.competitions;
CREATE POLICY competitions_select_public ON tutor.competitions
    FOR SELECT
    USING (
        visibility = 'public' OR
        (visibility = 'tenant_specific' AND tenant_id = tutor.current_tenant_id()) OR
        tutor.is_system_admin()
    );

-- Students can see competitions they're registered for
DROP POLICY IF EXISTS competitions_select_registered ON tutor.competitions;
CREATE POLICY competitions_select_registered ON tutor.competitions
    FOR SELECT
    USING (
        tutor.is_student() AND
        EXISTS (
            SELECT 1 FROM tutor.competition_registrations
            WHERE competition_id = tutor.competitions.competition_id
            AND student_id = tutor.current_user_id()
        )
    );

-- Tenant admins can see competitions in their tenant
DROP POLICY IF EXISTS competitions_select_tenant_admin ON tutor.competitions;
CREATE POLICY competitions_select_tenant_admin ON tutor.competitions
    FOR SELECT
    USING (
        (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin()) OR
        tutor.is_system_admin()
    );

-- System admins can modify competitions
DROP POLICY IF EXISTS competitions_modify_system_admin ON tutor.competitions;
CREATE POLICY competitions_modify_system_admin ON tutor.competitions
    FOR ALL
    USING (tutor.is_system_admin())
    WITH CHECK (tutor.is_system_admin());

-- Tenant admins can create competitions in their tenant
DROP POLICY IF EXISTS competitions_insert_tenant_admin ON tutor.competitions;
CREATE POLICY competitions_insert_tenant_admin ON tutor.competitions
    FOR INSERT
    WITH CHECK (
        tenant_id = tutor.current_tenant_id() AND
        tutor.is_tenant_admin()
    );

-- ============================================================================
-- COMPETITION REGISTRATIONS RLS POLICIES
-- ============================================================================

-- Students can see their own registrations
DROP POLICY IF EXISTS competition_registrations_select_student ON tutor.competition_registrations;
CREATE POLICY competition_registrations_select_student ON tutor.competition_registrations
    FOR SELECT
    USING (student_id = tutor.current_user_id() AND tutor.is_student() AND tenant_id = tutor.current_tenant_id());

-- Tenant admins can see registrations in their tenant
DROP POLICY IF EXISTS competition_registrations_select_tenant_admin ON tutor.competition_registrations;
CREATE POLICY competition_registrations_select_tenant_admin ON tutor.competition_registrations
    FOR SELECT
    USING (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin());

-- System admins can see all registrations
DROP POLICY IF EXISTS competition_registrations_select_system_admin ON tutor.competition_registrations;
CREATE POLICY competition_registrations_select_system_admin ON tutor.competition_registrations
    FOR SELECT
    USING (tutor.is_system_admin());

-- Students can register for competitions
DROP POLICY IF EXISTS competition_registrations_insert_student ON tutor.competition_registrations;
CREATE POLICY competition_registrations_insert_student ON tutor.competition_registrations
    FOR INSERT
    WITH CHECK (
        student_id = tutor.current_user_id() AND
        tutor.is_student() AND
        tenant_id = tutor.current_tenant_id()
    );

-- Students can cancel their own registrations
DROP POLICY IF EXISTS competition_registrations_update_student ON tutor.competition_registrations;
CREATE POLICY competition_registrations_update_student ON tutor.competition_registrations
    FOR UPDATE
    USING (student_id = tutor.current_user_id() AND tutor.is_student() AND tenant_id = tutor.current_tenant_id())
    WITH CHECK (student_id = tutor.current_user_id() AND tutor.is_student() AND tenant_id = tutor.current_tenant_id());

-- Admins can modify registrations
DROP POLICY IF EXISTS competition_registrations_modify_admin ON tutor.competition_registrations;
CREATE POLICY competition_registrations_modify_admin ON tutor.competition_registrations
    FOR ALL
    USING (
        (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin()) OR
        tutor.is_system_admin()
    )
    WITH CHECK (
        (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin()) OR
        tutor.is_system_admin()
    );

-- ============================================================================
-- COMPETITION SESSIONS RLS POLICIES
-- ============================================================================

-- Students can see their own competition sessions
DROP POLICY IF EXISTS competition_sessions_select_student ON tutor.competition_sessions;
CREATE POLICY competition_sessions_select_student ON tutor.competition_sessions
    FOR SELECT
    USING (student_id = tutor.current_user_id() AND tutor.is_student() AND tenant_id = tutor.current_tenant_id());

-- Tenant admins can see sessions in their tenant
DROP POLICY IF EXISTS competition_sessions_select_tenant_admin ON tutor.competition_sessions;
CREATE POLICY competition_sessions_select_tenant_admin ON tutor.competition_sessions
    FOR SELECT
    USING (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin());

-- System admins can see all sessions
DROP POLICY IF EXISTS competition_sessions_select_system_admin ON tutor.competition_sessions;
CREATE POLICY competition_sessions_select_system_admin ON tutor.competition_sessions
    FOR SELECT
    USING (tutor.is_system_admin());

-- Students can create their own competition sessions
DROP POLICY IF EXISTS competition_sessions_modify_student ON tutor.competition_sessions;
CREATE POLICY competition_sessions_modify_student ON tutor.competition_sessions
    FOR ALL
    USING (student_id = current_user_id() AND is_student() AND tenant_id = current_tenant_id())
    WITH CHECK (student_id = tutor.current_user_id() AND tutor.is_student() AND tenant_id = tutor.current_tenant_id());

-- ============================================================================
-- AUTHENTICATION TABLES RLS POLICIES
-- ============================================================================

-- Users can see their own OTPs (tenant-scoped users only)
DROP POLICY IF EXISTS password_reset_otp_select_self ON tutor.password_reset_otp;
CREATE POLICY password_reset_otp_select_self ON tutor.password_reset_otp
    FOR SELECT
    USING (user_id = tutor.current_user_id());

-- Users can insert their own OTPs
DROP POLICY IF EXISTS password_reset_otp_insert_self ON tutor.password_reset_otp;
CREATE POLICY password_reset_otp_insert_self ON tutor.password_reset_otp
    FOR INSERT
    WITH CHECK (user_id = tutor.current_user_id());

-- Users can update their own OTPs
DROP POLICY IF EXISTS password_reset_otp_update_self ON tutor.password_reset_otp;
CREATE POLICY password_reset_otp_update_self ON tutor.password_reset_otp
    FOR UPDATE
    USING (user_id = tutor.current_user_id());

-- Users can see their own tokens
DROP POLICY IF EXISTS authentication_tokens_select_self ON tutor.authentication_tokens;
CREATE POLICY authentication_tokens_select_self ON tutor.authentication_tokens
    FOR SELECT
    USING (
        (user_type = 'tenant_user' AND user_id = tutor.current_user_id()) OR
        (user_type = 'system_admin' AND user_id = tutor.current_user_id() AND tutor.is_system_admin())
    );

-- Users can modify their own tokens
DROP POLICY IF EXISTS authentication_tokens_modify_self ON tutor.authentication_tokens;
CREATE POLICY authentication_tokens_modify_self ON tutor.authentication_tokens
    FOR ALL
    USING (
        (user_type = 'tenant_user' AND user_id = tutor.current_user_id()) OR
        (user_type = 'system_admin' AND user_id = tutor.current_user_id() AND tutor.is_system_admin())
    )
    WITH CHECK (
        (user_type = 'tenant_user' AND user_id = tutor.current_user_id()) OR
        (user_type = 'system_admin' AND user_id = tutor.current_user_id() AND tutor.is_system_admin())
    );

-- ============================================================================
-- AUDIT LOGS RLS POLICIES
-- ============================================================================

-- Tenant admins can see audit logs for their tenant
DROP POLICY IF EXISTS audit_logs_select_tenant_admin ON tutor.audit_logs;
CREATE POLICY audit_logs_select_tenant_admin ON tutor.audit_logs
    FOR SELECT
    USING (tenant_id = tutor.current_tenant_id() AND tutor.is_tenant_admin());

-- System admins can see all audit logs
DROP POLICY IF EXISTS audit_logs_select_system_admin ON tutor.audit_logs;
CREATE POLICY audit_logs_select_system_admin ON tutor.audit_logs
    FOR SELECT
    USING (tutor.is_system_admin());

-- Only system can insert audit logs (via application)
-- This is typically done by the application layer, not directly by users

