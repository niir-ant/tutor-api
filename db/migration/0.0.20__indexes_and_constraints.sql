-- Migration: 0.0.20__indexes_and_constraints.sql
-- Description: Indexes and additional constraints for performance and data integrity
-- Created: 2025

-- Set search path to tutor schema
SET search_path TO tutor, public;

-- ============================================================================
-- DROP INDEXES
-- ============================================================================

-- Drop indexes in reverse order (not critical, but good practice)
DROP INDEX IF EXISTS tutor.idx_messages_unread;
DROP INDEX IF EXISTS tutor.idx_student_tutor_assignments_active;
DROP INDEX IF EXISTS tutor.idx_competitions_active;
DROP INDEX IF EXISTS tutor.idx_messages_content_search;
DROP INDEX IF EXISTS tutor.idx_questions_text_search;
DROP INDEX IF EXISTS tutor.idx_competition_registrations_comp_status;
DROP INDEX IF EXISTS tutor.idx_messages_tenant_conversation;
DROP INDEX IF EXISTS tutor.idx_student_progress_tenant_student;
DROP INDEX IF EXISTS tutor.idx_competitions_tenant_status;
DROP INDEX IF EXISTS tutor.idx_audit_logs_performed_by_role;
DROP INDEX IF EXISTS tutor.idx_audit_logs_timestamp;
DROP INDEX IF EXISTS tutor.idx_audit_logs_target_id;
DROP INDEX IF EXISTS tutor.idx_audit_logs_target_type;
DROP INDEX IF EXISTS tutor.idx_audit_logs_action;
DROP INDEX IF EXISTS tutor.idx_audit_logs_performed_by;
DROP INDEX IF EXISTS tutor.idx_audit_logs_tenant_id;
DROP INDEX IF EXISTS tutor.idx_competition_sessions_started_at;
DROP INDEX IF EXISTS tutor.idx_competition_sessions_status;
DROP INDEX IF EXISTS tutor.idx_competition_sessions_session_id;
DROP INDEX IF EXISTS tutor.idx_competition_sessions_student_id;
DROP INDEX IF EXISTS tutor.idx_competition_sessions_tenant_id;
DROP INDEX IF EXISTS tutor.idx_competition_sessions_competition_id;
DROP INDEX IF EXISTS tutor.idx_competition_registrations_registered_at;
DROP INDEX IF EXISTS tutor.idx_competition_registrations_status;
DROP INDEX IF EXISTS tutor.idx_competition_registrations_student_id;
DROP INDEX IF EXISTS tutor.idx_competition_registrations_tenant_id;
DROP INDEX IF EXISTS tutor.idx_competition_registrations_competition_id;
DROP INDEX IF EXISTS tutor.idx_competitions_created_at;
DROP INDEX IF EXISTS tutor.idx_competitions_registration_end;
DROP INDEX IF EXISTS tutor.idx_competitions_registration_start;
DROP INDEX IF EXISTS tutor.idx_competitions_end_date;
DROP INDEX IF EXISTS tutor.idx_competitions_start_date;
DROP INDEX IF EXISTS tutor.idx_competitions_status;
DROP INDEX IF EXISTS tutor.idx_competitions_subject_id;
DROP INDEX IF EXISTS tutor.idx_competitions_tenant_id;
DROP INDEX IF EXISTS tutor.idx_messages_recipient_sender;
DROP INDEX IF EXISTS tutor.idx_messages_sender_recipient;
DROP INDEX IF EXISTS tutor.idx_messages_deleted_at;
DROP INDEX IF EXISTS tutor.idx_messages_created_at;
DROP INDEX IF EXISTS tutor.idx_messages_status;
DROP INDEX IF EXISTS tutor.idx_messages_conversation_id;
DROP INDEX IF EXISTS tutor.idx_messages_recipient_id;
DROP INDEX IF EXISTS tutor.idx_messages_sender_id;
DROP INDEX IF EXISTS tutor.idx_messages_tenant_id;
DROP INDEX IF EXISTS tutor.idx_student_tutor_assignments_assigned_at;
DROP INDEX IF EXISTS tutor.idx_student_tutor_assignments_status;
DROP INDEX IF EXISTS tutor.idx_student_tutor_assignments_subject_tutor;
DROP INDEX IF EXISTS tutor.idx_student_tutor_assignments_subject_student;
DROP INDEX IF EXISTS tutor.idx_student_tutor_assignments_tutor_id;
DROP INDEX IF EXISTS tutor.idx_student_tutor_assignments_student_id;
DROP INDEX IF EXISTS tutor.idx_student_tutor_assignments_subject_id;
DROP INDEX IF EXISTS tutor.idx_student_tutor_assignments_tenant_id;
DROP INDEX IF EXISTS tutor.idx_student_progress_last_updated;
DROP INDEX IF EXISTS tutor.idx_student_progress_tenant_id;
DROP INDEX IF EXISTS tutor.idx_hints_hint_level;
DROP INDEX IF EXISTS tutor.idx_hints_question_id;
DROP INDEX IF EXISTS tutor.idx_hints_tenant_id;
DROP INDEX IF EXISTS tutor.idx_answer_submissions_is_correct;
DROP INDEX IF EXISTS tutor.idx_answer_submissions_submitted_at;
DROP INDEX IF EXISTS tutor.idx_answer_submissions_session_id;
DROP INDEX IF EXISTS tutor.idx_answer_submissions_student_id;
DROP INDEX IF EXISTS tutor.idx_answer_submissions_question_id;
DROP INDEX IF EXISTS tutor.idx_answer_submissions_tenant_id;
DROP INDEX IF EXISTS tutor.idx_quiz_sessions_completed_at;
DROP INDEX IF EXISTS tutor.idx_quiz_sessions_started_at;
DROP INDEX IF EXISTS tutor.idx_quiz_sessions_status;
DROP INDEX IF EXISTS tutor.idx_quiz_sessions_subject_id;
DROP INDEX IF EXISTS tutor.idx_quiz_sessions_student_id;
DROP INDEX IF EXISTS tutor.idx_quiz_sessions_tenant_id;
DROP INDEX IF EXISTS tutor.idx_questions_created_at;
DROP INDEX IF EXISTS tutor.idx_questions_grade_level;
DROP INDEX IF EXISTS tutor.idx_questions_question_type;
DROP INDEX IF EXISTS tutor.idx_questions_difficulty;
DROP INDEX IF EXISTS tutor.idx_questions_subject_code;
DROP INDEX IF EXISTS tutor.idx_questions_subject_id;
DROP INDEX IF EXISTS tutor.idx_questions_tenant_id;
DROP INDEX IF EXISTS tutor.idx_authentication_tokens_access_token;
DROP INDEX IF EXISTS tutor.idx_authentication_tokens_revoked;
DROP INDEX IF EXISTS tutor.idx_authentication_tokens_expires_at;
DROP INDEX IF EXISTS tutor.idx_authentication_tokens_user_type;
DROP INDEX IF EXISTS tutor.idx_authentication_tokens_user_id;
DROP INDEX IF EXISTS tutor.idx_password_reset_otp_used;
DROP INDEX IF EXISTS tutor.idx_password_reset_otp_expires_at;
DROP INDEX IF EXISTS tutor.idx_password_reset_otp_email;
DROP INDEX IF EXISTS tutor.idx_password_reset_otp_user_id;
DROP INDEX IF EXISTS tutor.idx_system_admin_accounts_role;
DROP INDEX IF EXISTS tutor.idx_system_admin_accounts_status;
DROP INDEX IF EXISTS tutor.idx_system_admin_accounts_username;
DROP INDEX IF EXISTS tutor.idx_system_admin_accounts_email;
DROP INDEX IF EXISTS tutor.idx_tenant_admin_accounts_tenant_id;
DROP INDEX IF EXISTS tutor.idx_tenant_admin_accounts_user_id;
DROP INDEX IF EXISTS tutor.idx_tutor_subject_profiles_tenant_id;
DROP INDEX IF EXISTS tutor.idx_tutor_subject_profiles_subject_id;
DROP INDEX IF EXISTS tutor.idx_tutor_subject_profiles_user_id;
DROP INDEX IF EXISTS tutor.idx_student_subject_profiles_grade_level;
DROP INDEX IF EXISTS tutor.idx_student_subject_profiles_assigned_tutor;
DROP INDEX IF EXISTS tutor.idx_student_subject_profiles_tenant_id;
DROP INDEX IF EXISTS tutor.idx_student_subject_profiles_subject_id;
DROP INDEX IF EXISTS tutor.idx_student_subject_profiles_user_id;
DROP INDEX IF EXISTS tutor.idx_user_subject_roles_active;
DROP INDEX IF EXISTS tutor.idx_user_subject_roles_user_subject;
DROP INDEX IF EXISTS tutor.idx_user_subject_roles_status;
DROP INDEX IF EXISTS tutor.idx_user_subject_roles_role;
DROP INDEX IF EXISTS tutor.idx_user_subject_roles_tenant_id;
DROP INDEX IF EXISTS tutor.idx_user_subject_roles_subject_id;
DROP INDEX IF EXISTS tutor.idx_user_subject_roles_user_id;
DROP INDEX IF EXISTS tutor.idx_user_accounts_active;
DROP INDEX IF EXISTS tutor.idx_user_accounts_tenant_status;
DROP INDEX IF EXISTS tutor.idx_user_accounts_status;
DROP INDEX IF EXISTS tutor.idx_user_accounts_username;
DROP INDEX IF EXISTS tutor.idx_user_accounts_email;
DROP INDEX IF EXISTS tutor.idx_user_accounts_tenant_id;
DROP INDEX IF EXISTS tutor.idx_subjects_grade_levels;
DROP INDEX IF EXISTS tutor.idx_subjects_type;
DROP INDEX IF EXISTS tutor.idx_subjects_subject_code;
DROP INDEX IF EXISTS tutor.idx_subjects_status;
DROP INDEX IF EXISTS tutor.idx_tenant_domains_primary;
DROP INDEX IF EXISTS tutor.idx_tenant_domains_status;
DROP INDEX IF EXISTS tutor.idx_tenant_domains_domain;
DROP INDEX IF EXISTS tutor.idx_tenant_domains_tenant_id;
DROP INDEX IF EXISTS tutor.idx_tenants_tenant_code;
DROP INDEX IF EXISTS tutor.idx_tenants_status;

-- ============================================================================
-- TENANT INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_tenants_status ON tutor.tenants(status);
CREATE INDEX IF NOT EXISTS idx_tenants_tenant_code ON tutor.tenants(tenant_code);
CREATE INDEX IF NOT EXISTS idx_tenant_domains_tenant_id ON tutor.tenant_domains(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tenant_domains_domain ON tutor.tenant_domains(domain);
CREATE INDEX IF NOT EXISTS idx_tenant_domains_status ON tutor.tenant_domains(status);
CREATE INDEX IF NOT EXISTS idx_tenant_domains_primary ON tutor.tenant_domains(tenant_id, is_primary) WHERE is_primary = TRUE;

-- ============================================================================
-- SUBJECT INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_subjects_status ON tutor.subjects(status);
CREATE INDEX IF NOT EXISTS idx_subjects_subject_code ON tutor.subjects(subject_code);
CREATE INDEX IF NOT EXISTS idx_subjects_type ON tutor.subjects(type);
CREATE INDEX IF NOT EXISTS idx_subjects_grade_levels ON tutor.subjects USING GIN(grade_levels);

-- ============================================================================
-- USER ACCOUNT INDEXES
-- ============================================================================

-- User accounts indexes
CREATE INDEX IF NOT EXISTS idx_user_accounts_tenant_id ON tutor.user_accounts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_user_accounts_email ON tutor.user_accounts(email);
CREATE INDEX IF NOT EXISTS idx_user_accounts_username ON tutor.user_accounts(username);
CREATE INDEX IF NOT EXISTS idx_user_accounts_status ON tutor.user_accounts(account_status);
CREATE INDEX IF NOT EXISTS idx_user_accounts_tenant_status ON tutor.user_accounts(tenant_id, account_status);
CREATE INDEX IF NOT EXISTS idx_user_accounts_active ON tutor.user_accounts(tenant_id, account_status) WHERE account_status = 'active';

-- User subject roles indexes
CREATE INDEX IF NOT EXISTS idx_user_subject_roles_user_id ON tutor.user_subject_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_subject_roles_subject_id ON tutor.user_subject_roles(subject_id);
CREATE INDEX IF NOT EXISTS idx_user_subject_roles_tenant_id ON tutor.user_subject_roles(tenant_id);
CREATE INDEX IF NOT EXISTS idx_user_subject_roles_role ON tutor.user_subject_roles(role);
CREATE INDEX IF NOT EXISTS idx_user_subject_roles_status ON tutor.user_subject_roles(status);
CREATE INDEX IF NOT EXISTS idx_user_subject_roles_user_subject ON tutor.user_subject_roles(user_id, subject_id);
CREATE INDEX IF NOT EXISTS idx_user_subject_roles_active ON tutor.user_subject_roles(user_id, subject_id, role) WHERE status = 'active';

-- Student subject profiles indexes
CREATE INDEX IF NOT EXISTS idx_student_subject_profiles_user_id ON tutor.student_subject_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_student_subject_profiles_subject_id ON tutor.student_subject_profiles(subject_id);
CREATE INDEX IF NOT EXISTS idx_student_subject_profiles_tenant_id ON tutor.student_subject_profiles(tenant_id);
CREATE INDEX IF NOT EXISTS idx_student_subject_profiles_assigned_tutor ON tutor.student_subject_profiles(assigned_tutor_id) WHERE assigned_tutor_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_student_subject_profiles_grade_level ON tutor.student_subject_profiles(grade_level) WHERE grade_level IS NOT NULL;

-- Tutor subject profiles indexes
CREATE INDEX IF NOT EXISTS idx_tutor_subject_profiles_user_id ON tutor.tutor_subject_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_tutor_subject_profiles_subject_id ON tutor.tutor_subject_profiles(subject_id);
CREATE INDEX IF NOT EXISTS idx_tutor_subject_profiles_tenant_id ON tutor.tutor_subject_profiles(tenant_id);

-- Tenant admin accounts indexes
CREATE INDEX IF NOT EXISTS idx_tenant_admin_accounts_user_id ON tutor.tenant_admin_accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_tenant_admin_accounts_tenant_id ON tutor.tenant_admin_accounts(tenant_id);

-- System admin accounts indexes
CREATE INDEX IF NOT EXISTS idx_system_admin_accounts_email ON tutor.system_admin_accounts(email);
CREATE INDEX IF NOT EXISTS idx_system_admin_accounts_username ON tutor.system_admin_accounts(username);
CREATE INDEX IF NOT EXISTS idx_system_admin_accounts_status ON tutor.system_admin_accounts(account_status);
CREATE INDEX IF NOT EXISTS idx_system_admin_accounts_role ON tutor.system_admin_accounts(role);

-- ============================================================================
-- AUTHENTICATION INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_password_reset_otp_user_id ON tutor.password_reset_otp(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_otp_email ON tutor.password_reset_otp(email);
CREATE INDEX IF NOT EXISTS idx_password_reset_otp_expires_at ON tutor.password_reset_otp(expires_at);
CREATE INDEX IF NOT EXISTS idx_password_reset_otp_used ON tutor.password_reset_otp(used) WHERE used = FALSE;

CREATE INDEX IF NOT EXISTS idx_authentication_tokens_user_id ON tutor.authentication_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_authentication_tokens_user_type ON tutor.authentication_tokens(user_type);
CREATE INDEX IF NOT EXISTS idx_authentication_tokens_expires_at ON tutor.authentication_tokens(expires_at);
CREATE INDEX IF NOT EXISTS idx_authentication_tokens_revoked ON tutor.authentication_tokens(revoked) WHERE revoked = FALSE;
CREATE INDEX IF NOT EXISTS idx_authentication_tokens_access_token ON tutor.authentication_tokens(access_token);

-- ============================================================================
-- QUESTION AND QUIZ INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_questions_tenant_id ON tutor.questions(tenant_id) WHERE tenant_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_questions_subject_id ON tutor.questions(subject_id);
CREATE INDEX IF NOT EXISTS idx_questions_subject_code ON tutor.questions(subject_code);
CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON tutor.questions(difficulty);
CREATE INDEX IF NOT EXISTS idx_questions_question_type ON tutor.questions(question_type);
CREATE INDEX IF NOT EXISTS idx_questions_grade_level ON tutor.questions(grade_level) WHERE grade_level IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_questions_created_at ON tutor.questions(created_at);

CREATE INDEX IF NOT EXISTS idx_quiz_sessions_tenant_id ON tutor.quiz_sessions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_student_id ON tutor.quiz_sessions(student_id);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_subject_id ON tutor.quiz_sessions(subject_id);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_status ON tutor.quiz_sessions(status);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_started_at ON tutor.quiz_sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_completed_at ON tutor.quiz_sessions(completed_at) WHERE completed_at IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_answer_submissions_tenant_id ON tutor.answer_submissions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_answer_submissions_question_id ON tutor.answer_submissions(question_id);
CREATE INDEX IF NOT EXISTS idx_answer_submissions_student_id ON tutor.answer_submissions(student_id);
CREATE INDEX IF NOT EXISTS idx_answer_submissions_session_id ON tutor.answer_submissions(session_id);
CREATE INDEX IF NOT EXISTS idx_answer_submissions_submitted_at ON tutor.answer_submissions(submitted_at);
CREATE INDEX IF NOT EXISTS idx_answer_submissions_is_correct ON tutor.answer_submissions(is_correct);

CREATE INDEX IF NOT EXISTS idx_hints_tenant_id ON tutor.hints(tenant_id);
CREATE INDEX IF NOT EXISTS idx_hints_question_id ON tutor.hints(question_id);
CREATE INDEX IF NOT EXISTS idx_hints_hint_level ON tutor.hints(hint_level);

CREATE INDEX IF NOT EXISTS idx_student_progress_tenant_id ON tutor.student_progress(tenant_id);
CREATE INDEX IF NOT EXISTS idx_student_progress_last_updated ON tutor.student_progress(last_updated);

-- ============================================================================
-- TUTOR-STUDENT RELATIONSHIP INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_student_tutor_assignments_tenant_id ON tutor.student_tutor_assignments(tenant_id);
CREATE INDEX IF NOT EXISTS idx_student_tutor_assignments_subject_id ON tutor.student_tutor_assignments(subject_id);
CREATE INDEX IF NOT EXISTS idx_student_tutor_assignments_student_id ON tutor.student_tutor_assignments(student_id);
CREATE INDEX IF NOT EXISTS idx_student_tutor_assignments_tutor_id ON tutor.student_tutor_assignments(tutor_id);
CREATE INDEX IF NOT EXISTS idx_student_tutor_assignments_status ON tutor.student_tutor_assignments(status);
CREATE INDEX IF NOT EXISTS idx_student_tutor_assignments_assigned_at ON tutor.student_tutor_assignments(assigned_at);
CREATE INDEX IF NOT EXISTS idx_student_tutor_assignments_subject_student ON tutor.student_tutor_assignments(subject_id, student_id);
CREATE INDEX IF NOT EXISTS idx_student_tutor_assignments_subject_tutor ON tutor.student_tutor_assignments(subject_id, tutor_id);

-- ============================================================================
-- MESSAGING INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_messages_tenant_id ON tutor.messages(tenant_id);
CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON tutor.messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_recipient_id ON tutor.messages(recipient_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON tutor.messages(conversation_id) WHERE conversation_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_messages_status ON tutor.messages(status);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON tutor.messages(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_deleted_at ON tutor.messages(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_messages_sender_recipient ON tutor.messages(sender_id, recipient_id);
CREATE INDEX IF NOT EXISTS idx_messages_recipient_sender ON tutor.messages(recipient_id, sender_id);

-- ============================================================================
-- COMPETITION INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_competitions_tenant_id ON tutor.competitions(tenant_id) WHERE tenant_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_competitions_subject_id ON tutor.competitions(subject_id);
CREATE INDEX IF NOT EXISTS idx_competitions_status ON tutor.competitions(status);
CREATE INDEX IF NOT EXISTS idx_competitions_start_date ON tutor.competitions(start_date);
CREATE INDEX IF NOT EXISTS idx_competitions_end_date ON tutor.competitions(end_date);
CREATE INDEX IF NOT EXISTS idx_competitions_registration_start ON tutor.competitions(registration_start);
CREATE INDEX IF NOT EXISTS idx_competitions_registration_end ON tutor.competitions(registration_end);
CREATE INDEX IF NOT EXISTS idx_competitions_created_at ON tutor.competitions(created_at);

CREATE INDEX IF NOT EXISTS idx_competition_registrations_competition_id ON tutor.competition_registrations(competition_id);
CREATE INDEX IF NOT EXISTS idx_competition_registrations_tenant_id ON tutor.competition_registrations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_competition_registrations_student_id ON tutor.competition_registrations(student_id);
CREATE INDEX IF NOT EXISTS idx_competition_registrations_status ON tutor.competition_registrations(status);
CREATE INDEX IF NOT EXISTS idx_competition_registrations_registered_at ON tutor.competition_registrations(registered_at);

CREATE INDEX IF NOT EXISTS idx_competition_sessions_competition_id ON tutor.competition_sessions(competition_id);
CREATE INDEX IF NOT EXISTS idx_competition_sessions_tenant_id ON tutor.competition_sessions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_competition_sessions_student_id ON tutor.competition_sessions(student_id);
CREATE INDEX IF NOT EXISTS idx_competition_sessions_session_id ON tutor.competition_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_competition_sessions_status ON tutor.competition_sessions(status);
CREATE INDEX IF NOT EXISTS idx_competition_sessions_started_at ON tutor.competition_sessions(started_at);

-- ============================================================================
-- AUDIT LOG INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant_id ON tutor.audit_logs(tenant_id) WHERE tenant_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_audit_logs_performed_by ON tutor.audit_logs(performed_by);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON tutor.audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_target_type ON tutor.audit_logs(target_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_target_id ON tutor.audit_logs(target_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON tutor.audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_logs_performed_by_role ON tutor.audit_logs(performed_by_role);

-- ============================================================================
-- COMPOSITE INDEXES FOR COMMON QUERIES
-- ============================================================================

-- Tenant + status combinations
CREATE INDEX IF NOT EXISTS idx_competitions_tenant_status ON tutor.competitions(tenant_id, status) WHERE tenant_id IS NOT NULL;

-- Student progress by tenant and subject
CREATE INDEX IF NOT EXISTS idx_student_progress_tenant_student ON tutor.student_progress(tenant_id, student_id);

-- Messages by tenant and conversation
CREATE INDEX IF NOT EXISTS idx_messages_tenant_conversation ON tutor.messages(tenant_id, conversation_id) WHERE conversation_id IS NOT NULL AND deleted_at IS NULL;

-- Competition registrations by competition and status
CREATE INDEX IF NOT EXISTS idx_competition_registrations_comp_status ON tutor.competition_registrations(competition_id, status);

-- ============================================================================
-- FULL TEXT SEARCH INDEXES (if needed)
-- ============================================================================

-- Enable full text search on questions
CREATE INDEX IF NOT EXISTS idx_questions_text_search ON tutor.questions USING GIN(to_tsvector('english', question_text));

-- Enable full text search on messages
CREATE INDEX IF NOT EXISTS idx_messages_content_search ON tutor.messages USING GIN(to_tsvector('english', content)) WHERE deleted_at IS NULL;

-- ============================================================================
-- PARTIAL INDEXES FOR ACTIVE RECORDS
-- ============================================================================

-- Active competitions
CREATE INDEX IF NOT EXISTS idx_competitions_active ON tutor.competitions(status, start_date, end_date) WHERE status IN ('upcoming', 'active');

-- Active assignments
CREATE INDEX IF NOT EXISTS idx_student_tutor_assignments_active ON tutor.student_tutor_assignments(tenant_id, subject_id, status) WHERE status = 'active';

-- Unread messages
CREATE INDEX IF NOT EXISTS idx_messages_unread ON tutor.messages(recipient_id, status, created_at) WHERE status != 'read' AND deleted_at IS NULL;

