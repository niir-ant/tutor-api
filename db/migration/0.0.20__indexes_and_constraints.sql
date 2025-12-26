-- Migration: 0.0.20__indexes_and_constraints.sql
-- Description: Indexes and additional constraints for performance and data integrity
-- Created: 2025

-- ============================================================================
-- TENANT INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_tenants_status ON tenants(status);
CREATE INDEX IF NOT EXISTS idx_tenants_tenant_code ON tenants(tenant_code);
CREATE INDEX IF NOT EXISTS idx_tenant_domains_tenant_id ON tenant_domains(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tenant_domains_domain ON tenant_domains(domain);
CREATE INDEX IF NOT EXISTS idx_tenant_domains_status ON tenant_domains(status);
CREATE INDEX IF NOT EXISTS idx_tenant_domains_primary ON tenant_domains(tenant_id, is_primary) WHERE is_primary = TRUE;

-- ============================================================================
-- SUBJECT INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_subjects_status ON subjects(status);
CREATE INDEX IF NOT EXISTS idx_subjects_subject_code ON subjects(subject_code);
CREATE INDEX IF NOT EXISTS idx_subjects_type ON subjects(type);
CREATE INDEX IF NOT EXISTS idx_subjects_grade_levels ON subjects USING GIN(grade_levels);

-- ============================================================================
-- USER ACCOUNT INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_student_accounts_tenant_id ON student_accounts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_student_accounts_email ON student_accounts(email);
CREATE INDEX IF NOT EXISTS idx_student_accounts_username ON student_accounts(username);
CREATE INDEX IF NOT EXISTS idx_student_accounts_status ON student_accounts(account_status);
CREATE INDEX IF NOT EXISTS idx_student_accounts_assigned_tutor ON student_accounts(assigned_tutor_id) WHERE assigned_tutor_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_student_accounts_grade_level ON student_accounts(grade_level) WHERE grade_level IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_tutor_accounts_tenant_id ON tutor_accounts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tutor_accounts_email ON tutor_accounts(email);
CREATE INDEX IF NOT EXISTS idx_tutor_accounts_username ON tutor_accounts(username);
CREATE INDEX IF NOT EXISTS idx_tutor_accounts_status ON tutor_accounts(status);

CREATE INDEX IF NOT EXISTS idx_administrator_accounts_tenant_id ON administrator_accounts(tenant_id) WHERE tenant_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_administrator_accounts_email ON administrator_accounts(email);
CREATE INDEX IF NOT EXISTS idx_administrator_accounts_username ON administrator_accounts(username);
CREATE INDEX IF NOT EXISTS idx_administrator_accounts_role ON administrator_accounts(role);
CREATE INDEX IF NOT EXISTS idx_administrator_accounts_status ON administrator_accounts(status);

-- ============================================================================
-- AUTHENTICATION INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_password_reset_otp_student_id ON password_reset_otp(student_id) WHERE student_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_password_reset_otp_tutor_id ON password_reset_otp(tutor_id) WHERE tutor_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_password_reset_otp_admin_id ON password_reset_otp(admin_id) WHERE admin_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_password_reset_otp_email ON password_reset_otp(email);
CREATE INDEX IF NOT EXISTS idx_password_reset_otp_expires_at ON password_reset_otp(expires_at);
CREATE INDEX IF NOT EXISTS idx_password_reset_otp_used ON password_reset_otp(used) WHERE used = FALSE;

CREATE INDEX IF NOT EXISTS idx_authentication_tokens_student_id ON authentication_tokens(student_id) WHERE student_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_authentication_tokens_tutor_id ON authentication_tokens(tutor_id) WHERE tutor_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_authentication_tokens_admin_id ON authentication_tokens(admin_id) WHERE admin_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_authentication_tokens_expires_at ON authentication_tokens(expires_at);
CREATE INDEX IF NOT EXISTS idx_authentication_tokens_revoked ON authentication_tokens(revoked) WHERE revoked = FALSE;
CREATE INDEX IF NOT EXISTS idx_authentication_tokens_access_token ON authentication_tokens(access_token);

-- ============================================================================
-- QUESTION AND QUIZ INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_questions_tenant_id ON questions(tenant_id) WHERE tenant_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_questions_subject_id ON questions(subject_id);
CREATE INDEX IF NOT EXISTS idx_questions_subject_code ON questions(subject_code);
CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty);
CREATE INDEX IF NOT EXISTS idx_questions_question_type ON questions(question_type);
CREATE INDEX IF NOT EXISTS idx_questions_grade_level ON questions(grade_level) WHERE grade_level IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_questions_created_at ON questions(created_at);

CREATE INDEX IF NOT EXISTS idx_quiz_sessions_tenant_id ON quiz_sessions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_student_id ON quiz_sessions(student_id);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_subject_id ON quiz_sessions(subject_id);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_status ON quiz_sessions(status);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_started_at ON quiz_sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_completed_at ON quiz_sessions(completed_at) WHERE completed_at IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_answer_submissions_tenant_id ON answer_submissions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_answer_submissions_question_id ON answer_submissions(question_id);
CREATE INDEX IF NOT EXISTS idx_answer_submissions_student_id ON answer_submissions(student_id);
CREATE INDEX IF NOT EXISTS idx_answer_submissions_session_id ON answer_submissions(session_id);
CREATE INDEX IF NOT EXISTS idx_answer_submissions_submitted_at ON answer_submissions(submitted_at);
CREATE INDEX IF NOT EXISTS idx_answer_submissions_is_correct ON answer_submissions(is_correct);

CREATE INDEX IF NOT EXISTS idx_hints_tenant_id ON hints(tenant_id);
CREATE INDEX IF NOT EXISTS idx_hints_question_id ON hints(question_id);
CREATE INDEX IF NOT EXISTS idx_hints_hint_level ON hints(hint_level);

CREATE INDEX IF NOT EXISTS idx_student_progress_tenant_id ON student_progress(tenant_id);
CREATE INDEX IF NOT EXISTS idx_student_progress_last_updated ON student_progress(last_updated);

-- ============================================================================
-- TUTOR-STUDENT RELATIONSHIP INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_student_tutor_assignments_tenant_id ON student_tutor_assignments(tenant_id);
CREATE INDEX IF NOT EXISTS idx_student_tutor_assignments_student_id ON student_tutor_assignments(student_id);
CREATE INDEX IF NOT EXISTS idx_student_tutor_assignments_tutor_id ON student_tutor_assignments(tutor_id);
CREATE INDEX IF NOT EXISTS idx_student_tutor_assignments_status ON student_tutor_assignments(status);
CREATE INDEX IF NOT EXISTS idx_student_tutor_assignments_assigned_at ON student_tutor_assignments(assigned_at);

-- ============================================================================
-- MESSAGING INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_messages_tenant_id ON messages(tenant_id);
CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_recipient_id ON messages(recipient_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id) WHERE conversation_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_deleted_at ON messages(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_messages_sender_recipient ON messages(sender_id, recipient_id);
CREATE INDEX IF NOT EXISTS idx_messages_recipient_sender ON messages(recipient_id, sender_id);

-- ============================================================================
-- COMPETITION INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_competitions_tenant_id ON competitions(tenant_id) WHERE tenant_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_competitions_subject_id ON competitions(subject_id);
CREATE INDEX IF NOT EXISTS idx_competitions_status ON competitions(status);
CREATE INDEX IF NOT EXISTS idx_competitions_start_date ON competitions(start_date);
CREATE INDEX IF NOT EXISTS idx_competitions_end_date ON competitions(end_date);
CREATE INDEX IF NOT EXISTS idx_competitions_registration_start ON competitions(registration_start);
CREATE INDEX IF NOT EXISTS idx_competitions_registration_end ON competitions(registration_end);
CREATE INDEX IF NOT EXISTS idx_competitions_created_at ON competitions(created_at);

CREATE INDEX IF NOT EXISTS idx_competition_registrations_competition_id ON competition_registrations(competition_id);
CREATE INDEX IF NOT EXISTS idx_competition_registrations_tenant_id ON competition_registrations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_competition_registrations_student_id ON competition_registrations(student_id);
CREATE INDEX IF NOT EXISTS idx_competition_registrations_status ON competition_registrations(status);
CREATE INDEX IF NOT EXISTS idx_competition_registrations_registered_at ON competition_registrations(registered_at);

CREATE INDEX IF NOT EXISTS idx_competition_sessions_competition_id ON competition_sessions(competition_id);
CREATE INDEX IF NOT EXISTS idx_competition_sessions_tenant_id ON competition_sessions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_competition_sessions_student_id ON competition_sessions(student_id);
CREATE INDEX IF NOT EXISTS idx_competition_sessions_session_id ON competition_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_competition_sessions_status ON competition_sessions(status);
CREATE INDEX IF NOT EXISTS idx_competition_sessions_started_at ON competition_sessions(started_at);

-- ============================================================================
-- AUDIT LOG INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant_id ON audit_logs(tenant_id) WHERE tenant_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_audit_logs_performed_by ON audit_logs(performed_by);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_target_type ON audit_logs(target_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_target_id ON audit_logs(target_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_logs_performed_by_role ON audit_logs(performed_by_role);

-- ============================================================================
-- COMPOSITE INDEXES FOR COMMON QUERIES
-- ============================================================================

-- Tenant + status combinations
CREATE INDEX IF NOT EXISTS idx_student_accounts_tenant_status ON student_accounts(tenant_id, account_status);
CREATE INDEX IF NOT EXISTS idx_tutor_accounts_tenant_status ON tutor_accounts(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_competitions_tenant_status ON competitions(tenant_id, status) WHERE tenant_id IS NOT NULL;

-- Student progress by tenant and subject
CREATE INDEX IF NOT EXISTS idx_student_progress_tenant_student ON student_progress(tenant_id, student_id);

-- Messages by tenant and conversation
CREATE INDEX IF NOT EXISTS idx_messages_tenant_conversation ON messages(tenant_id, conversation_id) WHERE conversation_id IS NOT NULL AND deleted_at IS NULL;

-- Competition registrations by competition and status
CREATE INDEX IF NOT EXISTS idx_competition_registrations_comp_status ON competition_registrations(competition_id, status);

-- ============================================================================
-- FULL TEXT SEARCH INDEXES (if needed)
-- ============================================================================

-- Enable full text search on questions
CREATE INDEX IF NOT EXISTS idx_questions_text_search ON questions USING GIN(to_tsvector('english', question_text));

-- Enable full text search on messages
CREATE INDEX IF NOT EXISTS idx_messages_content_search ON messages USING GIN(to_tsvector('english', content)) WHERE deleted_at IS NULL;

-- ============================================================================
-- PARTIAL INDEXES FOR ACTIVE RECORDS
-- ============================================================================

-- Active student accounts
CREATE INDEX IF NOT EXISTS idx_student_accounts_active ON student_accounts(tenant_id, account_status) WHERE account_status = 'active';

-- Active tutor accounts
CREATE INDEX IF NOT EXISTS idx_tutor_accounts_active ON tutor_accounts(tenant_id, status) WHERE status = 'active';

-- Active competitions
CREATE INDEX IF NOT EXISTS idx_competitions_active ON competitions(status, start_date, end_date) WHERE status IN ('upcoming', 'active');

-- Active assignments
CREATE INDEX IF NOT EXISTS idx_student_tutor_assignments_active ON student_tutor_assignments(tenant_id, status) WHERE status = 'active';

-- Unread messages
CREATE INDEX IF NOT EXISTS idx_messages_unread ON messages(recipient_id, status, created_at) WHERE status != 'read' AND deleted_at IS NULL;

