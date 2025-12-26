-- Migration: 0.0.30__rls_policies.sql
-- Description: Row Level Security (RLS) policies for multi-tenant data isolation
-- Created: 2024

-- ============================================================================
-- ENABLE ROW LEVEL SECURITY
-- ============================================================================

ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_domains ENABLE ROW LEVEL SECURITY;
ALTER TABLE subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE administrator_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE password_reset_otp ENABLE ROW LEVEL SECURITY;
ALTER TABLE authentication_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE answer_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE hints ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_tutor_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE competition_registrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE competition_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- HELPER FUNCTIONS FOR RLS
-- ============================================================================

-- Function to get current user's tenant_id from JWT claim
-- This assumes the application sets a session variable 'app.current_tenant_id'
CREATE OR REPLACE FUNCTION current_tenant_id() RETURNS UUID AS $$
BEGIN
    RETURN current_setting('app.current_tenant_id', TRUE)::UUID;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to get current user's role from JWT claim
CREATE OR REPLACE FUNCTION current_user_role() RETURNS user_role AS $$
BEGIN
    RETURN current_setting('app.current_user_role', TRUE)::user_role;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to get current user's ID from JWT claim
CREATE OR REPLACE FUNCTION current_user_id() RETURNS UUID AS $$
BEGIN
    RETURN current_setting('app.current_user_id', TRUE)::UUID;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to check if user is system admin
CREATE OR REPLACE FUNCTION is_system_admin() RETURNS BOOLEAN AS $$
BEGIN
    RETURN current_user_role() IN ('system_admin', 'super_admin');
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to check if user is tenant admin
CREATE OR REPLACE FUNCTION is_tenant_admin() RETURNS BOOLEAN AS $$
BEGIN
    RETURN current_user_role() = 'tenant_admin';
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to check if user is tutor
CREATE OR REPLACE FUNCTION is_tutor() RETURNS BOOLEAN AS $$
BEGIN
    RETURN current_user_role() = 'tutor';
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to check if user is student
CREATE OR REPLACE FUNCTION is_student() RETURNS BOOLEAN AS $$
BEGIN
    RETURN current_user_role() = 'student';
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- TENANTS RLS POLICIES
-- ============================================================================

-- System admins can see all tenants
CREATE POLICY tenants_select_system_admin ON tenants
    FOR SELECT
    USING (is_system_admin());

-- Tenant admins can see their own tenant
CREATE POLICY tenants_select_tenant_admin ON tenants
    FOR SELECT
    USING (tenant_id = current_tenant_id() AND is_tenant_admin());

-- System admins can insert/update/delete tenants
CREATE POLICY tenants_modify_system_admin ON tenants
    FOR ALL
    USING (is_system_admin())
    WITH CHECK (is_system_admin());

-- ============================================================================
-- TENANT DOMAINS RLS POLICIES
-- ============================================================================

-- System admins can see all domains
CREATE POLICY tenant_domains_select_system_admin ON tenant_domains
    FOR SELECT
    USING (is_system_admin());

-- Tenant admins can see domains for their tenant
CREATE POLICY tenant_domains_select_tenant_admin ON tenant_domains
    FOR SELECT
    USING (tenant_id = current_tenant_id() AND is_tenant_admin());

-- System admins can modify domains
CREATE POLICY tenant_domains_modify_system_admin ON tenant_domains
    FOR ALL
    USING (is_system_admin())
    WITH CHECK (is_system_admin());

-- ============================================================================
-- SUBJECTS RLS POLICIES
-- ============================================================================

-- Everyone can see active subjects (system-wide)
CREATE POLICY subjects_select_all ON subjects
    FOR SELECT
    USING (status = 'active');

-- System admins can see all subjects
CREATE POLICY subjects_select_system_admin ON subjects
    FOR SELECT
    USING (is_system_admin());

-- System admins can modify subjects
CREATE POLICY subjects_modify_system_admin ON subjects
    FOR ALL
    USING (is_system_admin())
    WITH CHECK (is_system_admin());

-- ============================================================================
-- STUDENT ACCOUNTS RLS POLICIES
-- ============================================================================

-- Students can see their own account
CREATE POLICY student_accounts_select_self ON student_accounts
    FOR SELECT
    USING (student_id = current_user_id() AND is_student());

-- Tutors can see their assigned students
CREATE POLICY student_accounts_select_tutor ON student_accounts
    FOR SELECT
    USING (
        tenant_id = current_tenant_id() AND
        is_tutor() AND
        EXISTS (
            SELECT 1 FROM student_tutor_assignments
            WHERE student_id = student_accounts.student_id
            AND tutor_id = (SELECT tutor_id FROM tutor_accounts WHERE tutor_id = current_user_id())
            AND status = 'active'
        )
    );

-- Tenant admins can see students in their tenant
CREATE POLICY student_accounts_select_tenant_admin ON student_accounts
    FOR SELECT
    USING (tenant_id = current_tenant_id() AND is_tenant_admin());

-- System admins can see all students
CREATE POLICY student_accounts_select_system_admin ON student_accounts
    FOR SELECT
    USING (is_system_admin());

-- Students can update their own account (limited fields)
CREATE POLICY student_accounts_update_self ON student_accounts
    FOR UPDATE
    USING (student_id = current_user_id() AND is_student())
    WITH CHECK (student_id = current_user_id() AND is_student());

-- Tenant admins can modify students in their tenant
CREATE POLICY student_accounts_modify_tenant_admin ON student_accounts
    FOR ALL
    USING (tenant_id = current_tenant_id() AND is_tenant_admin())
    WITH CHECK (tenant_id = current_tenant_id() AND is_tenant_admin());

-- System admins can modify all students
CREATE POLICY student_accounts_modify_system_admin ON student_accounts
    FOR ALL
    USING (is_system_admin())
    WITH CHECK (is_system_admin());

-- ============================================================================
-- TUTOR ACCOUNTS RLS POLICIES
-- ============================================================================

-- Tutors can see their own account
CREATE POLICY tutor_accounts_select_self ON tutor_accounts
    FOR SELECT
    USING (tutor_id = current_user_id() AND is_tutor());

-- Students can see their assigned tutor
CREATE POLICY tutor_accounts_select_student ON tutor_accounts
    FOR SELECT
    USING (
        tenant_id = current_tenant_id() AND
        is_student() AND
        EXISTS (
            SELECT 1 FROM student_tutor_assignments
            WHERE student_id = current_user_id()
            AND tutor_id = tutor_accounts.tutor_id
            AND status = 'active'
        )
    );

-- Tenant admins can see tutors in their tenant
CREATE POLICY tutor_accounts_select_tenant_admin ON tutor_accounts
    FOR SELECT
    USING (tenant_id = current_tenant_id() AND is_tenant_admin());

-- System admins can see all tutors
CREATE POLICY tutor_accounts_select_system_admin ON tutor_accounts
    FOR SELECT
    USING (is_system_admin());

-- Tutors can update their own account (limited fields)
CREATE POLICY tutor_accounts_update_self ON tutor_accounts
    FOR UPDATE
    USING (tutor_id = current_user_id() AND is_tutor())
    WITH CHECK (tutor_id = current_user_id() AND is_tutor());

-- Tenant admins can modify tutors in their tenant
CREATE POLICY tutor_accounts_modify_tenant_admin ON tutor_accounts
    FOR ALL
    USING (tenant_id = current_tenant_id() AND is_tenant_admin())
    WITH CHECK (tenant_id = current_tenant_id() AND is_tenant_admin());

-- System admins can modify all tutors
CREATE POLICY tutor_accounts_modify_system_admin ON tutor_accounts
    FOR ALL
    USING (is_system_admin())
    WITH CHECK (is_system_admin());

-- ============================================================================
-- ADMINISTRATOR ACCOUNTS RLS POLICIES
-- ============================================================================

-- Admins can see their own account
CREATE POLICY administrator_accounts_select_self ON administrator_accounts
    FOR SELECT
    USING (admin_id = current_user_id());

-- Tenant admins can see other tenant admins in their tenant
CREATE POLICY administrator_accounts_select_tenant_admin ON administrator_accounts
    FOR SELECT
    USING (
        tenant_id = current_tenant_id() AND
        is_tenant_admin() AND
        role = 'tenant_admin'
    );

-- System admins can see all admins
CREATE POLICY administrator_accounts_select_system_admin ON administrator_accounts
    FOR SELECT
    USING (is_system_admin());

-- System admins can modify all admins
CREATE POLICY administrator_accounts_modify_system_admin ON administrator_accounts
    FOR ALL
    USING (is_system_admin())
    WITH CHECK (is_system_admin());

-- ============================================================================
-- QUIZ SESSIONS RLS POLICIES
-- ============================================================================

-- Students can see their own sessions
CREATE POLICY quiz_sessions_select_student ON quiz_sessions
    FOR SELECT
    USING (student_id = current_user_id() AND is_student() AND tenant_id = current_tenant_id());

-- Tutors can see sessions of their assigned students
CREATE POLICY quiz_sessions_select_tutor ON quiz_sessions
    FOR SELECT
    USING (
        tenant_id = current_tenant_id() AND
        is_tutor() AND
        EXISTS (
            SELECT 1 FROM student_tutor_assignments
            WHERE student_id = quiz_sessions.student_id
            AND tutor_id = (SELECT tutor_id FROM tutor_accounts WHERE tutor_id = current_user_id())
            AND status = 'active'
        )
    );

-- Tenant admins can see sessions in their tenant
CREATE POLICY quiz_sessions_select_tenant_admin ON quiz_sessions
    FOR SELECT
    USING (tenant_id = current_tenant_id() AND is_tenant_admin());

-- System admins can see all sessions
CREATE POLICY quiz_sessions_select_system_admin ON quiz_sessions
    FOR SELECT
    USING (is_system_admin());

-- Students can create/update their own sessions
CREATE POLICY quiz_sessions_modify_student ON quiz_sessions
    FOR ALL
    USING (student_id = current_user_id() AND is_student() AND tenant_id = current_tenant_id())
    WITH CHECK (student_id = current_user_id() AND is_student() AND tenant_id = current_tenant_id());

-- ============================================================================
-- ANSWER SUBMISSIONS RLS POLICIES
-- ============================================================================

-- Students can see their own submissions
CREATE POLICY answer_submissions_select_student ON answer_submissions
    FOR SELECT
    USING (student_id = current_user_id() AND is_student() AND tenant_id = current_tenant_id());

-- Tutors can see submissions of their assigned students
CREATE POLICY answer_submissions_select_tutor ON answer_submissions
    FOR SELECT
    USING (
        tenant_id = current_tenant_id() AND
        is_tutor() AND
        EXISTS (
            SELECT 1 FROM student_tutor_assignments
            WHERE student_id = answer_submissions.student_id
            AND tutor_id = (SELECT tutor_id FROM tutor_accounts WHERE tutor_id = current_user_id())
            AND status = 'active'
        )
    );

-- Tenant admins can see submissions in their tenant
CREATE POLICY answer_submissions_select_tenant_admin ON answer_submissions
    FOR SELECT
    USING (tenant_id = current_tenant_id() AND is_tenant_admin());

-- System admins can see all submissions
CREATE POLICY answer_submissions_select_system_admin ON answer_submissions
    FOR SELECT
    USING (is_system_admin());

-- Students can create their own submissions
CREATE POLICY answer_submissions_modify_student ON answer_submissions
    FOR ALL
    USING (student_id = current_user_id() AND is_student() AND tenant_id = current_tenant_id())
    WITH CHECK (student_id = current_user_id() AND is_student() AND tenant_id = current_tenant_id());

-- ============================================================================
-- STUDENT PROGRESS RLS POLICIES
-- ============================================================================

-- Students can see their own progress
CREATE POLICY student_progress_select_student ON student_progress
    FOR SELECT
    USING (student_id = current_user_id() AND is_student() AND tenant_id = current_tenant_id());

-- Tutors can see progress of their assigned students
CREATE POLICY student_progress_select_tutor ON student_progress
    FOR SELECT
    USING (
        tenant_id = current_tenant_id() AND
        is_tutor() AND
        EXISTS (
            SELECT 1 FROM student_tutor_assignments
            WHERE student_id = student_progress.student_id
            AND tutor_id = (SELECT tutor_id FROM tutor_accounts WHERE tutor_id = current_user_id())
            AND status = 'active'
        )
    );

-- Tenant admins can see progress in their tenant
CREATE POLICY student_progress_select_tenant_admin ON student_progress
    FOR SELECT
    USING (tenant_id = current_tenant_id() AND is_tenant_admin());

-- System admins can see all progress
CREATE POLICY student_progress_select_system_admin ON student_progress
    FOR SELECT
    USING (is_system_admin());

-- ============================================================================
-- QUESTIONS RLS POLICIES
-- ============================================================================

-- Everyone can see questions (system-wide or tenant-specific)
CREATE POLICY questions_select_all ON questions
    FOR SELECT
    USING (
        tenant_id IS NULL OR
        tenant_id = current_tenant_id() OR
        is_system_admin()
    );

-- System admins can modify questions
CREATE POLICY questions_modify_system_admin ON questions
    FOR ALL
    USING (is_system_admin())
    WITH CHECK (is_system_admin());

-- ============================================================================
-- HINTS RLS POLICIES
-- ============================================================================

-- Students can see hints for questions they're working on
CREATE POLICY hints_select_student ON hints
    FOR SELECT
    USING (
        tenant_id = current_tenant_id() AND
        is_student()
    );

-- Tutors and admins can see hints
CREATE POLICY hints_select_authorized ON hints
    FOR SELECT
    USING (
        tenant_id = current_tenant_id() AND
        (is_tutor() OR is_tenant_admin() OR is_system_admin())
    );

-- System admins can modify hints
CREATE POLICY hints_modify_system_admin ON hints
    FOR ALL
    USING (is_system_admin())
    WITH CHECK (is_system_admin());

-- ============================================================================
-- STUDENT-TUTOR ASSIGNMENTS RLS POLICIES
-- ============================================================================

-- Tutors can see their own assignments
CREATE POLICY student_tutor_assignments_select_tutor ON student_tutor_assignments
    FOR SELECT
    USING (
        tenant_id = current_tenant_id() AND
        is_tutor() AND
        tutor_id = (SELECT tutor_id FROM tutor_accounts WHERE tutor_id = current_user_id())
    );

-- Students can see their assignment
CREATE POLICY student_tutor_assignments_select_student ON student_tutor_assignments
    FOR SELECT
    USING (
        tenant_id = current_tenant_id() AND
        is_student() AND
        student_id = current_user_id()
    );

-- Tenant admins can see assignments in their tenant
CREATE POLICY student_tutor_assignments_select_tenant_admin ON student_tutor_assignments
    FOR SELECT
    USING (tenant_id = current_tenant_id() AND is_tenant_admin());

-- System admins can see all assignments
CREATE POLICY student_tutor_assignments_select_system_admin ON student_tutor_assignments
    FOR SELECT
    USING (is_system_admin());

-- Tenant admins can modify assignments in their tenant
CREATE POLICY student_tutor_assignments_modify_tenant_admin ON student_tutor_assignments
    FOR ALL
    USING (tenant_id = current_tenant_id() AND is_tenant_admin())
    WITH CHECK (tenant_id = current_tenant_id() AND is_tenant_admin());

-- System admins can modify all assignments
CREATE POLICY student_tutor_assignments_modify_system_admin ON student_tutor_assignments
    FOR ALL
    USING (is_system_admin())
    WITH CHECK (is_system_admin());

-- ============================================================================
-- MESSAGES RLS POLICIES
-- ============================================================================

-- Users can see messages they sent or received
CREATE POLICY messages_select_participant ON messages
    FOR SELECT
    USING (
        tenant_id = current_tenant_id() AND
        (
            sender_id = current_user_id() OR
            recipient_id = current_user_id()
        ) AND
        deleted_at IS NULL
    );

-- Tenant admins can see messages in their tenant
CREATE POLICY messages_select_tenant_admin ON messages
    FOR SELECT
    USING (tenant_id = current_tenant_id() AND is_tenant_admin());

-- System admins can see all messages
CREATE POLICY messages_select_system_admin ON messages
    FOR SELECT
    USING (is_system_admin());

-- Users can send messages (students to tutors, tutors to students)
CREATE POLICY messages_insert_authorized ON messages
    FOR INSERT
    WITH CHECK (
        tenant_id = current_tenant_id() AND
        sender_id = current_user_id() AND
        (
            (is_student() AND EXISTS (
                SELECT 1 FROM student_tutor_assignments
                WHERE student_id = current_user_id()
                AND tutor_id = messages.recipient_id
                AND status = 'active'
            )) OR
            (is_tutor() AND EXISTS (
                SELECT 1 FROM student_tutor_assignments
                WHERE student_id = messages.recipient_id
                AND tutor_id = current_user_id()
                AND status = 'active'
            )) OR
            is_tenant_admin() OR
            is_system_admin()
        )
    );

-- Users can update their own messages
CREATE POLICY messages_update_self ON messages
    FOR UPDATE
    USING (sender_id = current_user_id() AND tenant_id = current_tenant_id())
    WITH CHECK (sender_id = current_user_id() AND tenant_id = current_tenant_id());

-- Recipients can mark messages as read
CREATE POLICY messages_update_recipient ON messages
    FOR UPDATE
    USING (recipient_id = current_user_id() AND tenant_id = current_tenant_id())
    WITH CHECK (recipient_id = current_user_id() AND tenant_id = current_tenant_id());

-- ============================================================================
-- COMPETITIONS RLS POLICIES
-- ============================================================================

-- Everyone can see public competitions or competitions in their tenant
CREATE POLICY competitions_select_public ON competitions
    FOR SELECT
    USING (
        visibility = 'public' OR
        (visibility = 'tenant_specific' AND tenant_id = current_tenant_id()) OR
        is_system_admin()
    );

-- Students can see competitions they're registered for
CREATE POLICY competitions_select_registered ON competitions
    FOR SELECT
    USING (
        is_student() AND
        EXISTS (
            SELECT 1 FROM competition_registrations
            WHERE competition_id = competitions.competition_id
            AND student_id = current_user_id()
        )
    );

-- Tenant admins can see competitions in their tenant
CREATE POLICY competitions_select_tenant_admin ON competitions
    FOR SELECT
    USING (
        (tenant_id = current_tenant_id() AND is_tenant_admin()) OR
        is_system_admin()
    );

-- System admins can modify competitions
CREATE POLICY competitions_modify_system_admin ON competitions
    FOR ALL
    USING (is_system_admin())
    WITH CHECK (is_system_admin());

-- Tenant admins can create competitions in their tenant
CREATE POLICY competitions_insert_tenant_admin ON competitions
    FOR INSERT
    WITH CHECK (
        tenant_id = current_tenant_id() AND
        is_tenant_admin()
    );

-- ============================================================================
-- COMPETITION REGISTRATIONS RLS POLICIES
-- ============================================================================

-- Students can see their own registrations
CREATE POLICY competition_registrations_select_student ON competition_registrations
    FOR SELECT
    USING (student_id = current_user_id() AND is_student() AND tenant_id = current_tenant_id());

-- Tenant admins can see registrations in their tenant
CREATE POLICY competition_registrations_select_tenant_admin ON competition_registrations
    FOR SELECT
    USING (tenant_id = current_tenant_id() AND is_tenant_admin());

-- System admins can see all registrations
CREATE POLICY competition_registrations_select_system_admin ON competition_registrations
    FOR SELECT
    USING (is_system_admin());

-- Students can register for competitions
CREATE POLICY competition_registrations_insert_student ON competition_registrations
    FOR INSERT
    WITH CHECK (
        student_id = current_user_id() AND
        is_student() AND
        tenant_id = current_tenant_id()
    );

-- Students can cancel their own registrations
CREATE POLICY competition_registrations_update_student ON competition_registrations
    FOR UPDATE
    USING (student_id = current_user_id() AND is_student() AND tenant_id = current_tenant_id())
    WITH CHECK (student_id = current_user_id() AND is_student() AND tenant_id = current_tenant_id());

-- Admins can modify registrations
CREATE POLICY competition_registrations_modify_admin ON competition_registrations
    FOR ALL
    USING (
        (tenant_id = current_tenant_id() AND is_tenant_admin()) OR
        is_system_admin()
    )
    WITH CHECK (
        (tenant_id = current_tenant_id() AND is_tenant_admin()) OR
        is_system_admin()
    );

-- ============================================================================
-- COMPETITION SESSIONS RLS POLICIES
-- ============================================================================

-- Students can see their own competition sessions
CREATE POLICY competition_sessions_select_student ON competition_sessions
    FOR SELECT
    USING (student_id = current_user_id() AND is_student() AND tenant_id = current_tenant_id());

-- Tenant admins can see sessions in their tenant
CREATE POLICY competition_sessions_select_tenant_admin ON competition_sessions
    FOR SELECT
    USING (tenant_id = current_tenant_id() AND is_tenant_admin());

-- System admins can see all sessions
CREATE POLICY competition_sessions_select_system_admin ON competition_sessions
    FOR SELECT
    USING (is_system_admin());

-- Students can create their own competition sessions
CREATE POLICY competition_sessions_modify_student ON competition_sessions
    FOR ALL
    USING (student_id = current_user_id() AND is_student() AND tenant_id = current_tenant_id())
    WITH CHECK (student_id = current_user_id() AND is_student() AND tenant_id = current_tenant_id());

-- ============================================================================
-- AUTHENTICATION TABLES RLS POLICIES
-- ============================================================================

-- Users can see their own OTPs and tokens
CREATE POLICY password_reset_otp_select_self ON password_reset_otp
    FOR SELECT
    USING (
        (student_id = current_user_id() AND is_student()) OR
        (tutor_id = current_user_id() AND is_tutor()) OR
        (admin_id = current_user_id() AND (is_tenant_admin() OR is_system_admin()))
    );

-- Users can insert their own OTPs
CREATE POLICY password_reset_otp_insert_self ON password_reset_otp
    FOR INSERT
    WITH CHECK (
        (student_id = current_user_id() AND is_student()) OR
        (tutor_id = current_user_id() AND is_tutor()) OR
        (admin_id = current_user_id() AND (is_tenant_admin() OR is_system_admin()))
    );

-- Users can update their own OTPs
CREATE POLICY password_reset_otp_update_self ON password_reset_otp
    FOR UPDATE
    USING (
        (student_id = current_user_id() AND is_student()) OR
        (tutor_id = current_user_id() AND is_tutor()) OR
        (admin_id = current_user_id() AND (is_tenant_admin() OR is_system_admin()))
    );

-- Similar policies for authentication_tokens
CREATE POLICY authentication_tokens_select_self ON authentication_tokens
    FOR SELECT
    USING (
        (student_id = current_user_id() AND is_student()) OR
        (tutor_id = current_user_id() AND is_tutor()) OR
        (admin_id = current_user_id() AND (is_tenant_admin() OR is_system_admin()))
    );

CREATE POLICY authentication_tokens_modify_self ON authentication_tokens
    FOR ALL
    USING (
        (student_id = current_user_id() AND is_student()) OR
        (tutor_id = current_user_id() AND is_tutor()) OR
        (admin_id = current_user_id() AND (is_tenant_admin() OR is_system_admin()))
    )
    WITH CHECK (
        (student_id = current_user_id() AND is_student()) OR
        (tutor_id = current_user_id() AND is_tutor()) OR
        (admin_id = current_user_id() AND (is_tenant_admin() OR is_system_admin()))
    );

-- ============================================================================
-- AUDIT LOGS RLS POLICIES
-- ============================================================================

-- Tenant admins can see audit logs for their tenant
CREATE POLICY audit_logs_select_tenant_admin ON audit_logs
    FOR SELECT
    USING (tenant_id = current_tenant_id() AND is_tenant_admin());

-- System admins can see all audit logs
CREATE POLICY audit_logs_select_system_admin ON audit_logs
    FOR SELECT
    USING (is_system_admin());

-- Only system can insert audit logs (via application)
-- This is typically done by the application layer, not directly by users

