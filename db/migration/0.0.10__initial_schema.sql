-- Migration: 0.0.10__initial_schema.sql
-- Description: Initial database schema for Quiz API with multi-tenancy support
-- Created: 2025

-- ============================================================================
-- CREATE SCHEMA
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS tutor;

-- Set search path to tutor schema
SET search_path TO tutor, public;

-- ============================================================================
-- DROP STATEMENTS (in reverse dependency order)
-- ============================================================================

-- Drop triggers first
DROP TRIGGER IF EXISTS update_competitions_updated_at ON tutor.competitions;
DROP TRIGGER IF EXISTS update_messages_updated_at ON tutor.messages;
DROP TRIGGER IF EXISTS update_system_admin_accounts_updated_at ON tutor.system_admin_accounts;
DROP TRIGGER IF EXISTS update_tenant_admin_accounts_updated_at ON tutor.tenant_admin_accounts;
DROP TRIGGER IF EXISTS update_tutor_subject_profiles_updated_at ON tutor.tutor_subject_profiles;
DROP TRIGGER IF EXISTS update_student_subject_profiles_updated_at ON tutor.student_subject_profiles;
DROP TRIGGER IF EXISTS update_user_subject_roles_updated_at ON tutor.user_subject_roles;
DROP TRIGGER IF EXISTS update_user_accounts_updated_at ON tutor.user_accounts;
DROP TRIGGER IF EXISTS update_subjects_updated_at ON tutor.subjects;
DROP TRIGGER IF EXISTS update_tenant_domains_updated_at ON tutor.tenant_domains;
DROP TRIGGER IF EXISTS update_tenants_updated_at ON tutor.tenants;

-- Drop functions
DROP FUNCTION IF EXISTS tutor.update_updated_at_column();

-- Drop tables (in reverse dependency order)
DROP TABLE IF EXISTS tutor.audit_logs CASCADE;
DROP TABLE IF EXISTS tutor.competition_sessions CASCADE;
DROP TABLE IF EXISTS tutor.competition_registrations CASCADE;
DROP TABLE IF EXISTS tutor.competitions CASCADE;
DROP TABLE IF EXISTS tutor.messages CASCADE;
DROP TABLE IF EXISTS tutor.student_tutor_assignments CASCADE;
DROP TABLE IF EXISTS tutor.student_progress CASCADE;
DROP TABLE IF EXISTS tutor.hints CASCADE;
DROP TABLE IF EXISTS tutor.answer_submissions CASCADE;
DROP TABLE IF EXISTS tutor.quiz_sessions CASCADE;
DROP TABLE IF EXISTS tutor.questions CASCADE;
DROP TABLE IF EXISTS tutor.authentication_tokens CASCADE;
DROP TABLE IF EXISTS tutor.password_reset_otp CASCADE;
DROP TABLE IF EXISTS tutor.system_admin_accounts CASCADE;
DROP TABLE IF EXISTS tutor.tenant_admin_accounts CASCADE;
DROP TABLE IF EXISTS tutor.tutor_subject_profiles CASCADE;
DROP TABLE IF EXISTS tutor.student_subject_profiles CASCADE;
DROP TABLE IF EXISTS tutor.user_subject_roles CASCADE;
DROP TABLE IF EXISTS tutor.user_accounts CASCADE;
DROP TABLE IF EXISTS tutor.subjects CASCADE;
DROP TABLE IF EXISTS tutor.tenant_domains CASCADE;
DROP TABLE IF EXISTS tutor.tenants CASCADE;

-- Drop types/enums
DROP TYPE IF EXISTS tutor.user_type CASCADE;
DROP TYPE IF EXISTS tutor.visibility_type CASCADE;
DROP TYPE IF EXISTS tutor.competition_session_status CASCADE;
DROP TYPE IF EXISTS tutor.assignment_status CASCADE;
DROP TYPE IF EXISTS tutor.user_role CASCADE;
DROP TYPE IF EXISTS tutor.message_status CASCADE;
DROP TYPE IF EXISTS tutor.registration_status CASCADE;
DROP TYPE IF EXISTS tutor.competition_status CASCADE;
DROP TYPE IF EXISTS tutor.session_status CASCADE;
DROP TYPE IF EXISTS tutor.validation_method CASCADE;
DROP TYPE IF EXISTS tutor.subject_type CASCADE;
DROP TYPE IF EXISTS tutor.question_type CASCADE;
DROP TYPE IF EXISTS tutor.question_difficulty CASCADE;
DROP TYPE IF EXISTS tutor.subject_status CASCADE;
DROP TYPE IF EXISTS tutor.domain_status CASCADE;
DROP TYPE IF EXISTS tutor.tenant_status CASCADE;
DROP TYPE IF EXISTS tutor.account_status CASCADE;

-- ============================================================================
-- ENABLE EXTENSIONS
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- CREATE CUSTOM TYPES/ENUMS
-- ============================================================================

-- Create custom types/enums
CREATE TYPE tutor.account_status AS ENUM ('pending_activation', 'active', 'inactive', 'locked', 'suspended');
CREATE TYPE tutor.tenant_status AS ENUM ('active', 'inactive', 'suspended');
CREATE TYPE tutor.domain_status AS ENUM ('active', 'inactive');
CREATE TYPE tutor.subject_status AS ENUM ('active', 'inactive', 'archived');
CREATE TYPE tutor.question_difficulty AS ENUM ('beginner', 'intermediate', 'advanced');
CREATE TYPE tutor.question_type AS ENUM ('multiple_choice', 'short_answer', 'code_completion', 'code_writing', 'fill_blank', 'true_false');
CREATE TYPE tutor.subject_type AS ENUM ('academic', 'programming', 'language', 'science', 'other');
CREATE TYPE tutor.validation_method AS ENUM ('ai_semantic', 'code_execution', 'exact_match', 'ai_structured');
CREATE TYPE tutor.session_status AS ENUM ('in_progress', 'completed', 'expired', 'abandoned');
CREATE TYPE tutor.competition_status AS ENUM ('upcoming', 'active', 'ended', 'cancelled');
CREATE TYPE tutor.registration_status AS ENUM ('registered', 'confirmed', 'cancelled');
CREATE TYPE tutor.message_status AS ENUM ('sent', 'delivered', 'read', 'deleted');
CREATE TYPE tutor.user_role AS ENUM ('student', 'tutor', 'tenant_admin', 'system_admin');
CREATE TYPE tutor.assignment_status AS ENUM ('active', 'inactive');
CREATE TYPE tutor.competition_session_status AS ENUM ('in_progress', 'completed', 'expired', 'abandoned');
CREATE TYPE tutor.visibility_type AS ENUM ('public', 'private', 'tenant_specific');

-- ============================================================================
-- TENANT MANAGEMENT TABLES
-- ============================================================================

-- Tenants table
CREATE TABLE tutor.tenants (
    tenant_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status tutor.tenant_status NOT NULL DEFAULT 'active',
    primary_domain VARCHAR(255),
    contact_info JSONB,
    settings JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    CONSTRAINT tenants_tenant_code_check CHECK (tenant_code ~ '^[a-z0-9_-]+$')
);

-- Tenant domains table
CREATE TABLE tutor.tenant_domains (
    domain_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tutor.tenants(tenant_id) ON DELETE CASCADE,
    domain VARCHAR(255) UNIQUE NOT NULL,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    status tutor.domain_status NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    CONSTRAINT tenant_domains_domain_check CHECK (domain ~ '^[a-z0-9.-]+$')
);

-- ============================================================================
-- SUBJECT MANAGEMENT TABLES
-- ============================================================================

-- Subjects table
CREATE TABLE tutor.subjects (
    subject_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subject_code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type tutor.subject_type NOT NULL,
    grade_levels INTEGER[],
    status tutor.subject_status NOT NULL DEFAULT 'active',
    supported_question_types tutor.question_type[] NOT NULL,
    answer_validation_method tutor.validation_method NOT NULL,
    settings JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    CONSTRAINT subjects_subject_code_check CHECK (subject_code ~ '^[a-z0-9_-]+$')
);

-- ============================================================================
-- USER ACCOUNT TABLES
-- ============================================================================

-- User Account (Parent Table) - for tenant-scoped users (students, tutors, tenant admins)
CREATE TABLE tutor.user_accounts (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tutor.tenants(tenant_id) ON DELETE RESTRICT,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    account_status tutor.account_status NOT NULL DEFAULT 'pending_activation',
    requires_password_change BOOLEAN NOT NULL DEFAULT TRUE,
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    created_by UUID,
    CONSTRAINT user_accounts_username_tenant_unique UNIQUE (username, tenant_id),
    CONSTRAINT user_accounts_email_tenant_unique UNIQUE (email, tenant_id)
);

-- User Subject Role Assignment - manages subject-level roles (student or tutor per subject)
CREATE TABLE tutor.user_subject_roles (
    assignment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES tutor.user_accounts(user_id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tutor.tenants(tenant_id) ON DELETE RESTRICT,
    subject_id UUID NOT NULL REFERENCES tutor.subjects(subject_id) ON DELETE RESTRICT,
    role tutor.user_role NOT NULL,
    status tutor.assignment_status NOT NULL DEFAULT 'active',
    assigned_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    assigned_by UUID NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID,
    notes TEXT,
    CONSTRAINT user_subject_roles_role_check CHECK (role IN ('student', 'tutor')),
    CONSTRAINT user_subject_roles_unique UNIQUE (user_id, subject_id, role)
    -- Note: Preventing a user from having both 'student' and 'tutor' roles for the same subject
    -- is enforced by application logic. PostgreSQL CHECK constraints cannot use subqueries.
);

-- Student Subject Profile - student-specific data per subject
CREATE TABLE tutor.student_subject_profiles (
    profile_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES tutor.user_accounts(user_id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES tutor.subjects(subject_id) ON DELETE RESTRICT,
    tenant_id UUID NOT NULL REFERENCES tutor.tenants(tenant_id) ON DELETE RESTRICT,
    grade_level INTEGER,
    assigned_tutor_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT student_subject_profiles_unique UNIQUE (user_id, subject_id),
    CONSTRAINT student_subject_profiles_grade_level_check CHECK (grade_level IS NULL OR (grade_level >= 1 AND grade_level <= 12))
);

-- Tutor Subject Profile - tutor-specific data per subject
CREATE TABLE tutor.tutor_subject_profiles (
    profile_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES tutor.user_accounts(user_id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES tutor.subjects(subject_id) ON DELETE RESTRICT,
    tenant_id UUID NOT NULL REFERENCES tutor.tenants(tenant_id) ON DELETE RESTRICT,
    name VARCHAR(255),
    profile JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT tutor_subject_profiles_unique UNIQUE (user_id, subject_id)
);

-- Tenant Administrator Account - extends user_accounts for tenant admins
CREATE TABLE tutor.tenant_admin_accounts (
    tenant_admin_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES tutor.user_accounts(user_id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tutor.tenants(tenant_id) ON DELETE RESTRICT,
    name VARCHAR(255) NOT NULL,
    permissions TEXT[],
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- System Administrator Account - separate table, not tenant-scoped
CREATE TABLE tutor.system_admin_accounts (
    admin_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role tutor.user_role NOT NULL DEFAULT 'system_admin',
    account_status tutor.account_status NOT NULL DEFAULT 'pending_activation',
    requires_password_change BOOLEAN NOT NULL DEFAULT TRUE,
    permissions TEXT[],
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES tutor.system_admin_accounts(admin_id),
    CONSTRAINT system_admin_accounts_role_check CHECK (role = 'system_admin')
);

-- Add foreign key for assigned_tutor_id in student_subject_profiles
ALTER TABLE tutor.student_subject_profiles 
    ADD CONSTRAINT student_subject_profiles_assigned_tutor_fk 
    FOREIGN KEY (assigned_tutor_id) 
    REFERENCES tutor.user_accounts(user_id) 
    ON DELETE SET NULL;

-- ============================================================================
-- AUTHENTICATION TABLES
-- ============================================================================

-- Password reset OTP table
CREATE TABLE tutor.password_reset_otp (
    otp_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES tutor.user_accounts(user_id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    otp_code_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP WITH TIME ZONE
);

-- Authentication tokens table
CREATE TYPE tutor.user_type AS ENUM ('tenant_user', 'system_admin');

CREATE TABLE tutor.authentication_tokens (
    token_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    user_type tutor.user_type NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT authentication_tokens_user_check CHECK (
        (user_type = 'tenant_user' AND user_id IS NOT NULL) OR
        (user_type = 'system_admin' AND user_id IS NOT NULL)
    )
);

-- ============================================================================
-- QUESTION AND QUIZ TABLES
-- ============================================================================

-- Questions table
CREATE TABLE tutor.questions (
    question_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tutor.tenants(tenant_id) ON DELETE RESTRICT,
    subject_id UUID NOT NULL REFERENCES tutor.subjects(subject_id) ON DELETE RESTRICT,
    subject_code VARCHAR(100) NOT NULL,
    grade_level INTEGER,
    difficulty tutor.question_difficulty NOT NULL,
    question_type tutor.question_type NOT NULL,
    question_text TEXT NOT NULL,
    options JSONB,
    correct_answer JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ai_model_version VARCHAR(50),
    CONSTRAINT questions_grade_level_check CHECK (grade_level IS NULL OR (grade_level >= 1 AND grade_level <= 12))
);

-- Quiz sessions table
CREATE TABLE tutor.quiz_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tutor.tenants(tenant_id) ON DELETE RESTRICT,
    student_id UUID NOT NULL REFERENCES tutor.user_accounts(user_id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES tutor.subjects(subject_id) ON DELETE RESTRICT,
    subject_code VARCHAR(100) NOT NULL,
    grade_level INTEGER,
    difficulty tutor.question_difficulty,
    questions UUID[] NOT NULL,
    status tutor.session_status NOT NULL DEFAULT 'in_progress',
    score DECIMAL(10, 2) NOT NULL DEFAULT 0,
    max_score DECIMAL(10, 2) NOT NULL DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    time_limit INTEGER,
    CONSTRAINT quiz_sessions_grade_level_check CHECK (grade_level IS NULL OR (grade_level >= 1 AND grade_level <= 12))
);

-- Answer submissions table
CREATE TABLE tutor.answer_submissions (
    submission_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tutor.tenants(tenant_id) ON DELETE RESTRICT,
    question_id UUID NOT NULL REFERENCES tutor.questions(question_id) ON DELETE RESTRICT,
    student_id UUID NOT NULL REFERENCES tutor.user_accounts(user_id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES tutor.quiz_sessions(session_id) ON DELETE CASCADE,
    answer JSONB NOT NULL,
    is_correct BOOLEAN NOT NULL,
    score DECIMAL(10, 2) NOT NULL DEFAULT 0,
    max_score DECIMAL(10, 2) NOT NULL DEFAULT 0,
    feedback TEXT,
    hints_used UUID[],
    time_spent INTEGER NOT NULL DEFAULT 0,
    submitted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Hints table
CREATE TABLE tutor.hints (
    hint_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tutor.tenants(tenant_id) ON DELETE RESTRICT,
    question_id UUID NOT NULL REFERENCES tutor.questions(question_id) ON DELETE CASCADE,
    hint_level INTEGER NOT NULL,
    hint_text TEXT NOT NULL,
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT hints_hint_level_check CHECK (hint_level >= 1 AND hint_level <= 4)
);

-- Student progress table
CREATE TABLE tutor.student_progress (
    student_id UUID PRIMARY KEY REFERENCES tutor.user_accounts(user_id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tutor.tenants(tenant_id) ON DELETE RESTRICT,
    subject_stats JSONB NOT NULL DEFAULT '{}',
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TUTOR-STUDENT RELATIONSHIPS
-- ============================================================================

-- Student-tutor assignments table
CREATE TABLE tutor.student_tutor_assignments (
    assignment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tutor.tenants(tenant_id) ON DELETE RESTRICT,
    subject_id UUID NOT NULL REFERENCES tutor.subjects(subject_id) ON DELETE RESTRICT,
    student_id UUID NOT NULL REFERENCES tutor.user_accounts(user_id) ON DELETE CASCADE,
    tutor_id UUID NOT NULL REFERENCES tutor.user_accounts(user_id) ON DELETE CASCADE,
    status tutor.assignment_status NOT NULL DEFAULT 'active',
    assigned_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    assigned_by UUID NOT NULL,
    deactivated_at TIMESTAMP WITH TIME ZONE,
    deactivated_by UUID,
    notes TEXT,
    CONSTRAINT student_tutor_assignments_unique UNIQUE (student_id, tutor_id, subject_id, tenant_id)
);

-- ============================================================================
-- MESSAGING TABLES
-- ============================================================================

-- Messages table
CREATE TABLE tutor.messages (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tutor.tenants(tenant_id) ON DELETE RESTRICT,
    sender_id UUID NOT NULL,
    sender_role tutor.user_role NOT NULL,
    recipient_id UUID NOT NULL,
    recipient_role tutor.user_role NOT NULL,
    content TEXT NOT NULL,
    status tutor.message_status NOT NULL DEFAULT 'sent',
    email_sent BOOLEAN NOT NULL DEFAULT FALSE,
    email_sent_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    subject_reference UUID REFERENCES tutor.subjects(subject_id) ON DELETE SET NULL,
    question_reference UUID REFERENCES tutor.questions(question_id) ON DELETE SET NULL,
    conversation_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT messages_sender_role_check CHECK (sender_role IN ('student', 'tutor', 'tenant_admin')),
    CONSTRAINT messages_recipient_role_check CHECK (recipient_role IN ('student', 'tutor', 'tenant_admin'))
);

-- ============================================================================
-- COMPETITION TABLES
-- ============================================================================

-- Competitions table
CREATE TABLE tutor.competitions (
    competition_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tutor.tenants(tenant_id) ON DELETE RESTRICT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    subject_id UUID NOT NULL REFERENCES tutor.subjects(subject_id) ON DELETE RESTRICT,
    subject_code VARCHAR(100) NOT NULL,
    status tutor.competition_status NOT NULL DEFAULT 'upcoming',
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    registration_start TIMESTAMP WITH TIME ZONE NOT NULL,
    registration_end TIMESTAMP WITH TIME ZONE NOT NULL,
    rules JSONB NOT NULL,
    eligibility JSONB,
    visibility tutor.visibility_type NOT NULL DEFAULT 'public',
    max_participants INTEGER,
    participant_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    cancelled_by UUID,
    cancellation_reason TEXT,
    CONSTRAINT competitions_date_check CHECK (start_date < end_date),
    CONSTRAINT competitions_registration_check CHECK (registration_start < registration_end AND registration_end <= start_date),
    CONSTRAINT competitions_max_participants_check CHECK (max_participants IS NULL OR max_participants > 0)
);

-- Competition registrations table
CREATE TABLE tutor.competition_registrations (
    registration_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competition_id UUID NOT NULL REFERENCES tutor.competitions(competition_id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tutor.tenants(tenant_id) ON DELETE RESTRICT,
    student_id UUID NOT NULL REFERENCES tutor.user_accounts(user_id) ON DELETE CASCADE,
    status tutor.registration_status NOT NULL DEFAULT 'registered',
    registered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    cancelled_by UUID,
    waitlist_position INTEGER,
    notes TEXT,
    CONSTRAINT competition_registrations_unique UNIQUE (competition_id, student_id)
);

-- Competition sessions table
CREATE TABLE tutor.competition_sessions (
    competition_session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competition_id UUID NOT NULL REFERENCES tutor.competitions(competition_id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tutor.tenants(tenant_id) ON DELETE RESTRICT,
    student_id UUID NOT NULL REFERENCES tutor.user_accounts(user_id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES tutor.quiz_sessions(session_id) ON DELETE CASCADE,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    time_limit INTEGER,
    score DECIMAL(10, 2) NOT NULL DEFAULT 0,
    max_score DECIMAL(10, 2) NOT NULL DEFAULT 0,
    accuracy DECIMAL(5, 2),
    completion_time INTEGER,
    questions_answered INTEGER NOT NULL DEFAULT 0,
    status tutor.competition_session_status NOT NULL DEFAULT 'in_progress',
    CONSTRAINT competition_sessions_unique UNIQUE (competition_id, student_id)
);

-- ============================================================================
-- AUDIT LOG TABLE
-- ============================================================================

-- Audit logs table
CREATE TABLE tutor.audit_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tutor.tenants(tenant_id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    performed_by UUID NOT NULL,
    performed_by_role tutor.user_role NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    target_id UUID NOT NULL,
    details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT audit_logs_performed_by_role_check CHECK (performed_by_role IN ('tenant_admin', 'system_admin'))
);

-- ============================================================================
-- COLUMN COMMENTS
-- ============================================================================

-- Tenants table columns
COMMENT ON COLUMN tutor.tenants.tenant_id IS 'Unique identifier for the tenant';
COMMENT ON COLUMN tutor.tenants.tenant_code IS 'Unique slug identifier for the tenant (lowercase, alphanumeric, underscores, hyphens only)';
COMMENT ON COLUMN tutor.tenants.name IS 'Display name of the educational institution';
COMMENT ON COLUMN tutor.tenants.description IS 'Description of the tenant/institution';
COMMENT ON COLUMN tutor.tenants.status IS 'Current status of the tenant: active, inactive, or suspended';
COMMENT ON COLUMN tutor.tenants.primary_domain IS 'Primary domain identifier for this tenant';
COMMENT ON COLUMN tutor.tenants.contact_info IS 'JSON object containing contact information (email, phone, address)';
COMMENT ON COLUMN tutor.tenants.settings IS 'JSON object containing tenant-specific settings (branding, features, subscription)';
COMMENT ON COLUMN tutor.tenants.created_at IS 'Timestamp when the tenant was created';
COMMENT ON COLUMN tutor.tenants.updated_at IS 'Timestamp when the tenant was last updated (auto-updated by trigger)';
COMMENT ON COLUMN tutor.tenants.created_by IS 'UUID of the system admin who created this tenant';

-- Tenant domains table columns
COMMENT ON COLUMN tutor.tenant_domains.domain_id IS 'Unique identifier for the domain';
COMMENT ON COLUMN tutor.tenant_domains.tenant_id IS 'Reference to the tenant this domain belongs to';
COMMENT ON COLUMN tutor.tenant_domains.domain IS 'Domain name (e.g., example.com, www.example.com) - must be unique across all tenants';
COMMENT ON COLUMN tutor.tenant_domains.is_primary IS 'Whether this is the primary domain for the tenant';
COMMENT ON COLUMN tutor.tenant_domains.status IS 'Status of the domain: active or inactive';
COMMENT ON COLUMN tutor.tenant_domains.created_at IS 'Timestamp when the domain was created';
COMMENT ON COLUMN tutor.tenant_domains.updated_at IS 'Timestamp when the domain was last updated (auto-updated by trigger)';
COMMENT ON COLUMN tutor.tenant_domains.created_by IS 'UUID of the system admin who created this domain';

-- Subjects table columns
COMMENT ON COLUMN tutor.subjects.subject_id IS 'Unique identifier for the subject';
COMMENT ON COLUMN tutor.subjects.subject_code IS 'Unique slug identifier for the subject (lowercase, alphanumeric, underscores, hyphens only)';
COMMENT ON COLUMN tutor.subjects.name IS 'Display name of the subject';
COMMENT ON COLUMN tutor.subjects.description IS 'Description of the subject/course';
COMMENT ON COLUMN tutor.subjects.type IS 'Type of subject: academic, programming, language, science, or other';
COMMENT ON COLUMN tutor.subjects.grade_levels IS 'Array of grade levels this subject supports (e.g., [6,7,8,9,10,11,12]) or NULL for all levels';
COMMENT ON COLUMN tutor.subjects.status IS 'Status of the subject: active, inactive, or archived';
COMMENT ON COLUMN tutor.subjects.supported_question_types IS 'Array of question types supported by this subject';
COMMENT ON COLUMN tutor.subjects.answer_validation_method IS 'Method used to validate answers: ai_semantic, code_execution, exact_match, or ai_structured';
COMMENT ON COLUMN tutor.subjects.settings IS 'JSON object containing subject-specific settings (AI prompts, validation rules, hint strategies)';
COMMENT ON COLUMN tutor.subjects.metadata IS 'JSON object containing metadata (curriculum, learning objectives, icon, category, tags)';
COMMENT ON COLUMN tutor.subjects.created_at IS 'Timestamp when the subject was created';
COMMENT ON COLUMN tutor.subjects.updated_at IS 'Timestamp when the subject was last updated (auto-updated by trigger)';
COMMENT ON COLUMN tutor.subjects.created_by IS 'UUID of the admin who created this subject';

-- User accounts table columns
COMMENT ON COLUMN tutor.user_accounts.user_id IS 'Unique identifier for the user account (parent table for tenant-scoped users)';
COMMENT ON COLUMN tutor.user_accounts.tenant_id IS 'Reference to the tenant this user belongs to (required for tenant isolation)';
COMMENT ON COLUMN tutor.user_accounts.username IS 'Unique username within the tenant';
COMMENT ON COLUMN tutor.user_accounts.email IS 'Unique email address within the tenant';
COMMENT ON COLUMN tutor.user_accounts.password_hash IS 'Cryptographically hashed password (bcrypt/Argon2) - never store plain text';
COMMENT ON COLUMN tutor.user_accounts.account_status IS 'Current status: pending_activation, active, inactive, or locked';
COMMENT ON COLUMN tutor.user_accounts.requires_password_change IS 'Whether the user must change password on next login (true for preset accounts)';
COMMENT ON COLUMN tutor.user_accounts.failed_login_attempts IS 'Number of consecutive failed login attempts (used for account lockout)';
COMMENT ON COLUMN tutor.user_accounts.locked_until IS 'Timestamp when account lockout expires (NULL if not locked)';
COMMENT ON COLUMN tutor.user_accounts.created_at IS 'Timestamp when the account was created';
COMMENT ON COLUMN tutor.user_accounts.updated_at IS 'Timestamp when the account was last updated (auto-updated by trigger)';
COMMENT ON COLUMN tutor.user_accounts.last_login IS 'Timestamp of the last successful login';
COMMENT ON COLUMN tutor.user_accounts.created_by IS 'UUID of the admin who created this account (tenant admin or system admin)';

-- User subject roles table columns
COMMENT ON COLUMN tutor.user_subject_roles.assignment_id IS 'Unique identifier for the role assignment';
COMMENT ON COLUMN tutor.user_subject_roles.user_id IS 'Reference to user_accounts.user_id';
COMMENT ON COLUMN tutor.user_subject_roles.tenant_id IS 'Denormalized from user_accounts for convenience';
COMMENT ON COLUMN tutor.user_subject_roles.subject_id IS 'Reference to subjects.subject_id';
COMMENT ON COLUMN tutor.user_subject_roles.role IS 'Role for this specific subject: student or tutor';
COMMENT ON COLUMN tutor.user_subject_roles.status IS 'Status of the assignment: active or inactive';
COMMENT ON COLUMN tutor.user_subject_roles.assigned_at IS 'Timestamp when the role was assigned';
COMMENT ON COLUMN tutor.user_subject_roles.assigned_by IS 'UUID of tenant admin or system admin who assigned this role';
COMMENT ON COLUMN tutor.user_subject_roles.updated_at IS 'Timestamp when the assignment was last updated';
COMMENT ON COLUMN tutor.user_subject_roles.updated_by IS 'UUID of tenant admin or system admin who updated this assignment';
COMMENT ON COLUMN tutor.user_subject_roles.notes IS 'Optional notes about the assignment';

-- Student subject profiles table columns
COMMENT ON COLUMN tutor.student_subject_profiles.profile_id IS 'Unique identifier for the student subject profile';
COMMENT ON COLUMN tutor.student_subject_profiles.user_id IS 'Reference to user_accounts.user_id';
COMMENT ON COLUMN tutor.student_subject_profiles.subject_id IS 'Reference to subjects.subject_id';
COMMENT ON COLUMN tutor.student_subject_profiles.tenant_id IS 'Denormalized from user_accounts for convenience';
COMMENT ON COLUMN tutor.student_subject_profiles.grade_level IS 'Grade level for this subject (1-12) or NULL if not applicable';
COMMENT ON COLUMN tutor.student_subject_profiles.assigned_tutor_id IS 'Reference to user_accounts.user_id (tutor must have tutor role for this subject)';
COMMENT ON COLUMN tutor.student_subject_profiles.created_at IS 'Timestamp when the profile was created';
COMMENT ON COLUMN tutor.student_subject_profiles.updated_at IS 'Timestamp when the profile was last updated';

-- Tutor subject profiles table columns
COMMENT ON COLUMN tutor.tutor_subject_profiles.profile_id IS 'Unique identifier for the tutor subject profile';
COMMENT ON COLUMN tutor.tutor_subject_profiles.user_id IS 'Reference to user_accounts.user_id';
COMMENT ON COLUMN tutor.tutor_subject_profiles.subject_id IS 'Reference to subjects.subject_id';
COMMENT ON COLUMN tutor.tutor_subject_profiles.tenant_id IS 'Denormalized from user_accounts for convenience';
COMMENT ON COLUMN tutor.tutor_subject_profiles.name IS 'Optional subject-specific tutor name/alias';
COMMENT ON COLUMN tutor.tutor_subject_profiles.profile IS 'JSON object containing subject-specific profile (bio, specializations, qualifications)';
COMMENT ON COLUMN tutor.tutor_subject_profiles.created_at IS 'Timestamp when the profile was created';
COMMENT ON COLUMN tutor.tutor_subject_profiles.updated_at IS 'Timestamp when the profile was last updated';

-- Tenant admin accounts table columns
COMMENT ON COLUMN tutor.tenant_admin_accounts.tenant_admin_id IS 'Unique identifier for the tenant admin account';
COMMENT ON COLUMN tutor.tenant_admin_accounts.user_id IS 'Foreign key to user_accounts.user_id (one-to-one relationship)';
COMMENT ON COLUMN tutor.tenant_admin_accounts.tenant_id IS 'Denormalized from user_accounts for convenience';
COMMENT ON COLUMN tutor.tenant_admin_accounts.name IS 'Full name of the tenant administrator';
COMMENT ON COLUMN tutor.tenant_admin_accounts.permissions IS 'Array of specific permissions (optional, for fine-grained access control)';
COMMENT ON COLUMN tutor.tenant_admin_accounts.created_at IS 'Timestamp when the account was created';
COMMENT ON COLUMN tutor.tenant_admin_accounts.updated_at IS 'Timestamp when the account was last updated';

-- System admin accounts table columns
COMMENT ON COLUMN tutor.system_admin_accounts.admin_id IS 'Unique identifier for the system administrator account (separate from user_accounts)';
COMMENT ON COLUMN tutor.system_admin_accounts.username IS 'Unique username across all system admins';
COMMENT ON COLUMN tutor.system_admin_accounts.email IS 'Unique email address across all system admins';
COMMENT ON COLUMN tutor.system_admin_accounts.password_hash IS 'Cryptographically hashed password (bcrypt/Argon2) - never store plain text';
COMMENT ON COLUMN tutor.system_admin_accounts.name IS 'Full name of the system administrator';
COMMENT ON COLUMN tutor.system_admin_accounts.role IS 'Always system_admin';
COMMENT ON COLUMN tutor.system_admin_accounts.account_status IS 'Current status: pending_activation, active, inactive, suspended, or locked';
COMMENT ON COLUMN tutor.system_admin_accounts.requires_password_change IS 'Whether the admin must change password on next login (true for preset accounts)';
COMMENT ON COLUMN tutor.system_admin_accounts.permissions IS 'Array of specific permissions (optional, for fine-grained access control)';
COMMENT ON COLUMN tutor.system_admin_accounts.failed_login_attempts IS 'Number of consecutive failed login attempts (used for account lockout)';
COMMENT ON COLUMN tutor.system_admin_accounts.locked_until IS 'Timestamp when account lockout expires (NULL if not locked)';
COMMENT ON COLUMN tutor.system_admin_accounts.created_at IS 'Timestamp when the account was created';
COMMENT ON COLUMN tutor.system_admin_accounts.updated_at IS 'Timestamp when the account was last updated (auto-updated by trigger)';
COMMENT ON COLUMN tutor.system_admin_accounts.last_login IS 'Timestamp of the last successful login';
COMMENT ON COLUMN tutor.system_admin_accounts.created_by IS 'UUID of system admin who created this account';

-- Password reset OTP table columns
COMMENT ON COLUMN tutor.password_reset_otp.otp_id IS 'Unique identifier for the OTP record';
COMMENT ON COLUMN tutor.password_reset_otp.user_id IS 'Reference to user_accounts.user_id (for tenant-scoped users)';
COMMENT ON COLUMN tutor.password_reset_otp.email IS 'Email address the OTP was sent to';
COMMENT ON COLUMN tutor.password_reset_otp.otp_code_hash IS 'Hashed one-time passcode (never store plain text)';
COMMENT ON COLUMN tutor.password_reset_otp.expires_at IS 'Timestamp when the OTP expires (typically 15 minutes from creation)';
COMMENT ON COLUMN tutor.password_reset_otp.used IS 'Whether this OTP has been used (single-use only)';
COMMENT ON COLUMN tutor.password_reset_otp.created_at IS 'Timestamp when the OTP was created';
COMMENT ON COLUMN tutor.password_reset_otp.used_at IS 'Timestamp when the OTP was used (NULL if not used)';

-- Authentication tokens table columns
COMMENT ON COLUMN tutor.authentication_tokens.token_id IS 'Unique identifier for the token record';
COMMENT ON COLUMN tutor.authentication_tokens.user_id IS 'Reference to user_accounts.user_id (for tenant_user) or system_admin_accounts.admin_id (for system_admin)';
COMMENT ON COLUMN tutor.authentication_tokens.user_type IS 'Type of user: tenant_user or system_admin (indicates which table to reference)';
COMMENT ON COLUMN tutor.authentication_tokens.access_token IS 'JWT access token (includes subject roles in claims for tenant users)';
COMMENT ON COLUMN tutor.authentication_tokens.refresh_token IS 'JWT refresh token (optional, for token refresh flow)';
COMMENT ON COLUMN tutor.authentication_tokens.expires_at IS 'Timestamp when the token expires';
COMMENT ON COLUMN tutor.authentication_tokens.created_at IS 'Timestamp when the token was created';
COMMENT ON COLUMN tutor.authentication_tokens.revoked IS 'Whether this token has been revoked (e.g., on logout)';

-- Questions table columns
COMMENT ON COLUMN tutor.questions.question_id IS 'Unique identifier for the question';
COMMENT ON COLUMN tutor.questions.tenant_id IS 'Reference to tenant (NULL for system-wide questions, UUID for tenant-specific questions)';
COMMENT ON COLUMN tutor.questions.subject_id IS 'Reference to the subject this question belongs to';
COMMENT ON COLUMN tutor.questions.subject_code IS 'Denormalized subject code for quick access (denormalized from subjects table)';
COMMENT ON COLUMN tutor.questions.grade_level IS 'Grade level this question is appropriate for (1-12) or NULL if not grade-specific';
COMMENT ON COLUMN tutor.questions.difficulty IS 'Difficulty level: beginner, intermediate, or advanced';
COMMENT ON COLUMN tutor.questions.question_type IS 'Type of question: multiple_choice, short_answer, code_completion, code_writing, fill_blank, or true_false';
COMMENT ON COLUMN tutor.questions.question_text IS 'The question text/prompt';
COMMENT ON COLUMN tutor.questions.options IS 'JSON array of options for multiple choice questions';
COMMENT ON COLUMN tutor.questions.correct_answer IS 'JSON object containing the correct answer(s)';
COMMENT ON COLUMN tutor.questions.metadata IS 'JSON object containing metadata (topic, learning_objectives, estimated_time, points)';
COMMENT ON COLUMN tutor.questions.created_at IS 'Timestamp when the question was generated';
COMMENT ON COLUMN tutor.questions.ai_model_version IS 'Version of the AI model used to generate this question';

-- Quiz sessions table columns
COMMENT ON COLUMN tutor.quiz_sessions.session_id IS 'Unique identifier for the quiz session';
COMMENT ON COLUMN tutor.quiz_sessions.tenant_id IS 'Reference to the tenant (required for tenant isolation)';
COMMENT ON COLUMN tutor.quiz_sessions.student_id IS 'Reference to user_accounts.user_id (user must have student role for this subject)';
COMMENT ON COLUMN tutor.quiz_sessions.subject_id IS 'Reference to the subject for this quiz';
COMMENT ON COLUMN tutor.quiz_sessions.subject_code IS 'Denormalized subject code for quick access';
COMMENT ON COLUMN tutor.quiz_sessions.grade_level IS 'Grade level for this quiz session (1-12) or NULL if not grade-specific';
COMMENT ON COLUMN tutor.quiz_sessions.difficulty IS 'Difficulty level of the quiz';
COMMENT ON COLUMN tutor.quiz_sessions.questions IS 'Array of question UUIDs in this quiz session';
COMMENT ON COLUMN tutor.quiz_sessions.status IS 'Current status: in_progress, completed, expired, or abandoned';
COMMENT ON COLUMN tutor.quiz_sessions.score IS 'Total score achieved in this session';
COMMENT ON COLUMN tutor.quiz_sessions.max_score IS 'Maximum possible score for this session';
COMMENT ON COLUMN tutor.quiz_sessions.started_at IS 'Timestamp when the session was started';
COMMENT ON COLUMN tutor.quiz_sessions.completed_at IS 'Timestamp when the session was completed (NULL if not completed)';
COMMENT ON COLUMN tutor.quiz_sessions.time_limit IS 'Time limit in seconds (NULL if no time limit)';

-- Answer submissions table columns
COMMENT ON COLUMN tutor.answer_submissions.submission_id IS 'Unique identifier for the answer submission';
COMMENT ON COLUMN tutor.answer_submissions.tenant_id IS 'Reference to the tenant (required for tenant isolation)';
COMMENT ON COLUMN tutor.answer_submissions.question_id IS 'Reference to the question being answered';
COMMENT ON COLUMN tutor.answer_submissions.student_id IS 'Reference to user_accounts.user_id (user must have student role for the session subject)';
COMMENT ON COLUMN tutor.answer_submissions.session_id IS 'Reference to the quiz session this answer belongs to';
COMMENT ON COLUMN tutor.answer_submissions.answer IS 'JSON object containing the student answer (text, code, or selected options)';
COMMENT ON COLUMN tutor.answer_submissions.is_correct IS 'Whether the answer is correct (boolean)';
COMMENT ON COLUMN tutor.answer_submissions.score IS 'Points awarded for this answer';
COMMENT ON COLUMN tutor.answer_submissions.max_score IS 'Maximum points possible for this question';
COMMENT ON COLUMN tutor.answer_submissions.feedback IS 'Feedback message provided to the student';
COMMENT ON COLUMN tutor.answer_submissions.hints_used IS 'Array of hint UUIDs that were used before submitting this answer';
COMMENT ON COLUMN tutor.answer_submissions.time_spent IS 'Time spent on this question in seconds';
COMMENT ON COLUMN tutor.answer_submissions.submitted_at IS 'Timestamp when the answer was submitted';

-- Hints table columns
COMMENT ON COLUMN tutor.hints.hint_id IS 'Unique identifier for the hint';
COMMENT ON COLUMN tutor.hints.tenant_id IS 'Reference to the tenant (required for tenant isolation)';
COMMENT ON COLUMN tutor.hints.question_id IS 'Reference to the question this hint is for';
COMMENT ON COLUMN tutor.hints.hint_level IS 'Level of the hint (1-4, where 1 is most subtle, 4 is most explicit)';
COMMENT ON COLUMN tutor.hints.hint_text IS 'The hint text content';
COMMENT ON COLUMN tutor.hints.generated_at IS 'Timestamp when the hint was generated';

-- Student progress table columns
COMMENT ON COLUMN tutor.student_progress.student_id IS 'Reference to user_accounts.user_id (user must have student role for tracked subjects)';
COMMENT ON COLUMN tutor.student_progress.tenant_id IS 'Reference to the tenant (required for tenant isolation)';
COMMENT ON COLUMN tutor.student_progress.subject_stats IS 'JSON object containing aggregated statistics per subject (total_questions, correct, accuracy, average_score, topics)';
COMMENT ON COLUMN tutor.student_progress.last_updated IS 'Timestamp when the progress was last updated';

-- Student-tutor assignments table columns
COMMENT ON COLUMN tutor.student_tutor_assignments.assignment_id IS 'Unique identifier for the assignment';
COMMENT ON COLUMN tutor.student_tutor_assignments.tenant_id IS 'Reference to the tenant (required for tenant isolation)';
COMMENT ON COLUMN tutor.student_tutor_assignments.subject_id IS 'Subject for which the assignment applies (assignment is subject-specific)';
COMMENT ON COLUMN tutor.student_tutor_assignments.student_id IS 'Reference to user_accounts.user_id (user must have student role for this subject)';
COMMENT ON COLUMN tutor.student_tutor_assignments.tutor_id IS 'Reference to user_accounts.user_id (user must have tutor role for this subject)';
COMMENT ON COLUMN tutor.student_tutor_assignments.status IS 'Status of the assignment: active or inactive';
COMMENT ON COLUMN tutor.student_tutor_assignments.assigned_at IS 'Timestamp when the assignment was created';
COMMENT ON COLUMN tutor.student_tutor_assignments.assigned_by IS 'UUID of tenant admin (user_accounts.user_id) or system admin (system_admin_accounts.admin_id)';
COMMENT ON COLUMN tutor.student_tutor_assignments.deactivated_at IS 'Timestamp when the assignment was deactivated (NULL if active)';
COMMENT ON COLUMN tutor.student_tutor_assignments.deactivated_by IS 'UUID of the admin who deactivated this assignment (NULL if self-deactivated)';
COMMENT ON COLUMN tutor.student_tutor_assignments.notes IS 'Optional notes about the assignment';

-- Messages table columns
COMMENT ON COLUMN tutor.messages.message_id IS 'Unique identifier for the message';
COMMENT ON COLUMN tutor.messages.tenant_id IS 'Reference to the tenant (required for tenant isolation)';
COMMENT ON COLUMN tutor.messages.sender_id IS 'Reference to user_accounts.user_id (for student, tutor, tenant_admin)';
COMMENT ON COLUMN tutor.messages.sender_role IS 'Role of the sender: student, tutor, or tenant_admin';
COMMENT ON COLUMN tutor.messages.recipient_id IS 'Reference to user_accounts.user_id (for student, tutor, tenant_admin)';
COMMENT ON COLUMN tutor.messages.recipient_role IS 'Role of the recipient: student, tutor, or tenant_admin';
COMMENT ON COLUMN tutor.messages.content IS 'Text content of the message';
COMMENT ON COLUMN tutor.messages.status IS 'Status of the message: sent, delivered, read, or deleted';
COMMENT ON COLUMN tutor.messages.email_sent IS 'Whether an email copy was sent to the recipient';
COMMENT ON COLUMN tutor.messages.email_sent_at IS 'Timestamp when the email was sent (NULL if not sent)';
COMMENT ON COLUMN tutor.messages.read_at IS 'Timestamp when the message was read (NULL if not read)';
COMMENT ON COLUMN tutor.messages.subject_reference IS 'Optional reference to a subject (for context)';
COMMENT ON COLUMN tutor.messages.question_reference IS 'Optional reference to a question (for context)';
COMMENT ON COLUMN tutor.messages.conversation_id IS 'UUID grouping messages in the same conversation thread';
COMMENT ON COLUMN tutor.messages.created_at IS 'Timestamp when the message was created';
COMMENT ON COLUMN tutor.messages.updated_at IS 'Timestamp when the message was last updated (auto-updated by trigger)';
COMMENT ON COLUMN tutor.messages.deleted_at IS 'Timestamp when the message was soft-deleted (NULL if not deleted)';

-- Competitions table columns
COMMENT ON COLUMN tutor.competitions.competition_id IS 'Unique identifier for the competition';
COMMENT ON COLUMN tutor.competitions.tenant_id IS 'Reference to the tenant (NULL for system-wide competitions, UUID for tenant-specific)';
COMMENT ON COLUMN tutor.competitions.name IS 'Name of the competition';
COMMENT ON COLUMN tutor.competitions.description IS 'Description of the competition';
COMMENT ON COLUMN tutor.competitions.subject_id IS 'Reference to the subject this competition is for';
COMMENT ON COLUMN tutor.competitions.subject_code IS 'Denormalized subject code for quick access';
COMMENT ON COLUMN tutor.competitions.status IS 'Current status: upcoming, active, ended, or cancelled';
COMMENT ON COLUMN tutor.competitions.start_date IS 'Timestamp when the competition starts';
COMMENT ON COLUMN tutor.competitions.end_date IS 'Timestamp when the competition ends';
COMMENT ON COLUMN tutor.competitions.registration_start IS 'Timestamp when registration opens';
COMMENT ON COLUMN tutor.competitions.registration_end IS 'Timestamp when registration closes';
COMMENT ON COLUMN tutor.competitions.rules IS 'JSON object containing competition rules (time_limit, num_questions, difficulty, allowed_question_types, max_attempts, scoring_rules, hints_allowed, narratives_allowed)';
COMMENT ON COLUMN tutor.competitions.eligibility IS 'JSON object containing eligibility criteria (grade_levels, tenant_restrictions, minimum_requirements)';
COMMENT ON COLUMN tutor.competitions.visibility IS 'Visibility level: public, private, or tenant_specific';
COMMENT ON COLUMN tutor.competitions.max_participants IS 'Maximum number of participants allowed (NULL for unlimited)';
COMMENT ON COLUMN tutor.competitions.participant_count IS 'Current number of registered participants';
COMMENT ON COLUMN tutor.competitions.created_at IS 'Timestamp when the competition was created';
COMMENT ON COLUMN tutor.competitions.updated_at IS 'Timestamp when the competition was last updated (auto-updated by trigger)';
COMMENT ON COLUMN tutor.competitions.created_by IS 'UUID of the admin who created this competition';
COMMENT ON COLUMN tutor.competitions.cancelled_at IS 'Timestamp when the competition was cancelled (NULL if not cancelled)';
COMMENT ON COLUMN tutor.competitions.cancelled_by IS 'UUID of the admin who cancelled this competition (NULL if not cancelled)';
COMMENT ON COLUMN tutor.competitions.cancellation_reason IS 'Reason for cancellation (NULL if not cancelled)';

-- Competition registrations table columns
COMMENT ON COLUMN tutor.competition_registrations.registration_id IS 'Unique identifier for the registration';
COMMENT ON COLUMN tutor.competition_registrations.competition_id IS 'Reference to the competition';
COMMENT ON COLUMN tutor.competition_registrations.tenant_id IS 'Reference to the tenant (required for tenant isolation)';
COMMENT ON COLUMN tutor.competition_registrations.student_id IS 'Reference to user_accounts.user_id (user must have student role for competition subject)';
COMMENT ON COLUMN tutor.competition_registrations.status IS 'Status of the registration: registered, confirmed, or cancelled';
COMMENT ON COLUMN tutor.competition_registrations.registered_at IS 'Timestamp when the student registered';
COMMENT ON COLUMN tutor.competition_registrations.confirmed_at IS 'Timestamp when the registration was confirmed (NULL if not confirmed)';
COMMENT ON COLUMN tutor.competition_registrations.cancelled_at IS 'Timestamp when the registration was cancelled (NULL if not cancelled)';
COMMENT ON COLUMN tutor.competition_registrations.cancelled_by IS 'UUID of who cancelled (student_id if self-cancelled, admin_id if admin-cancelled)';
COMMENT ON COLUMN tutor.competition_registrations.waitlist_position IS 'Position in waitlist if max participants reached (NULL if not waitlisted)';
COMMENT ON COLUMN tutor.competition_registrations.notes IS 'Optional notes about the registration';

-- Competition sessions table columns
COMMENT ON COLUMN tutor.competition_sessions.competition_session_id IS 'Unique identifier for the competition session';
COMMENT ON COLUMN tutor.competition_sessions.competition_id IS 'Reference to the competition';
COMMENT ON COLUMN tutor.competition_sessions.tenant_id IS 'Reference to the tenant (required for tenant isolation)';
COMMENT ON COLUMN tutor.competition_sessions.student_id IS 'Reference to user_accounts.user_id (user must have student role for competition subject)';
COMMENT ON COLUMN tutor.competition_sessions.session_id IS 'Reference to the quiz session used for this competition';
COMMENT ON COLUMN tutor.competition_sessions.started_at IS 'Timestamp when the competition session was started';
COMMENT ON COLUMN tutor.competition_sessions.completed_at IS 'Timestamp when the competition session was completed (NULL if not completed)';
COMMENT ON COLUMN tutor.competition_sessions.time_limit IS 'Time limit in seconds for this competition session';
COMMENT ON COLUMN tutor.competition_sessions.score IS 'Total score achieved in this competition session';
COMMENT ON COLUMN tutor.competition_sessions.max_score IS 'Maximum possible score for this competition session';
COMMENT ON COLUMN tutor.competition_sessions.accuracy IS 'Accuracy percentage (correct answers / total questions)';
COMMENT ON COLUMN tutor.competition_sessions.completion_time IS 'Time taken to complete the competition in seconds';
COMMENT ON COLUMN tutor.competition_sessions.questions_answered IS 'Number of questions answered';
COMMENT ON COLUMN tutor.competition_sessions.status IS 'Status of the session: in_progress, completed, expired, or abandoned';

-- Audit logs table columns
COMMENT ON COLUMN tutor.audit_logs.log_id IS 'Unique identifier for the audit log entry';
COMMENT ON COLUMN tutor.audit_logs.tenant_id IS 'Reference to the tenant (NULL for system-level actions)';
COMMENT ON COLUMN tutor.audit_logs.action IS 'Action performed (e.g., create_account, disable_account, assign_tutor)';
COMMENT ON COLUMN tutor.audit_logs.performed_by IS 'UUID of tenant admin (user_accounts.user_id) or system admin (system_admin_accounts.admin_id)';
COMMENT ON COLUMN tutor.audit_logs.performed_by_role IS 'Role of the user who performed the action (tenant_admin or system_admin)';
COMMENT ON COLUMN tutor.audit_logs.target_type IS 'Type of target entity (account, subject, assignment, message, tenant, etc.)';
COMMENT ON COLUMN tutor.audit_logs.target_id IS 'UUID of the target entity that was acted upon';
COMMENT ON COLUMN tutor.audit_logs.details IS 'JSON object containing action-specific details';
COMMENT ON COLUMN tutor.audit_logs.ip_address IS 'IP address of the user who performed the action';
COMMENT ON COLUMN tutor.audit_logs.user_agent IS 'User agent string of the client that performed the action';
COMMENT ON COLUMN tutor.audit_logs.timestamp IS 'Timestamp when the action was performed';

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION tutor.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tutor.tenants
    FOR EACH ROW EXECUTE FUNCTION tutor.update_updated_at_column();

CREATE TRIGGER update_tenant_domains_updated_at BEFORE UPDATE ON tutor.tenant_domains
    FOR EACH ROW EXECUTE FUNCTION tutor.update_updated_at_column();

CREATE TRIGGER update_subjects_updated_at BEFORE UPDATE ON tutor.subjects
    FOR EACH ROW EXECUTE FUNCTION tutor.update_updated_at_column();

CREATE TRIGGER update_user_accounts_updated_at BEFORE UPDATE ON tutor.user_accounts
    FOR EACH ROW EXECUTE FUNCTION tutor.update_updated_at_column();

CREATE TRIGGER update_user_subject_roles_updated_at BEFORE UPDATE ON tutor.user_subject_roles
    FOR EACH ROW EXECUTE FUNCTION tutor.update_updated_at_column();

CREATE TRIGGER update_student_subject_profiles_updated_at BEFORE UPDATE ON tutor.student_subject_profiles
    FOR EACH ROW EXECUTE FUNCTION tutor.update_updated_at_column();

CREATE TRIGGER update_tutor_subject_profiles_updated_at BEFORE UPDATE ON tutor.tutor_subject_profiles
    FOR EACH ROW EXECUTE FUNCTION tutor.update_updated_at_column();

CREATE TRIGGER update_tenant_admin_accounts_updated_at BEFORE UPDATE ON tutor.tenant_admin_accounts
    FOR EACH ROW EXECUTE FUNCTION tutor.update_updated_at_column();

CREATE TRIGGER update_system_admin_accounts_updated_at BEFORE UPDATE ON tutor.system_admin_accounts
    FOR EACH ROW EXECUTE FUNCTION tutor.update_updated_at_column();

CREATE TRIGGER update_messages_updated_at BEFORE UPDATE ON tutor.messages
    FOR EACH ROW EXECUTE FUNCTION tutor.update_updated_at_column();

CREATE TRIGGER update_competitions_updated_at BEFORE UPDATE ON tutor.competitions
    FOR EACH ROW EXECUTE FUNCTION tutor.update_updated_at_column();

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE tutor.tenants IS 'Multi-tenant educational institutions';
COMMENT ON TABLE tutor.tenant_domains IS 'Domain mappings for tenant resolution';
COMMENT ON TABLE tutor.subjects IS 'Subjects/courses available in the system';
COMMENT ON TABLE tutor.user_accounts IS 'Parent table for tenant-scoped user accounts (students, tutors, tenant admins)';
COMMENT ON TABLE tutor.user_subject_roles IS 'Subject-level role assignments (student or tutor per subject)';
COMMENT ON TABLE tutor.student_subject_profiles IS 'Student-specific data per subject';
COMMENT ON TABLE tutor.tutor_subject_profiles IS 'Tutor-specific data per subject';
COMMENT ON TABLE tutor.tenant_admin_accounts IS 'Tenant administrator accounts (extends user_accounts)';
COMMENT ON TABLE tutor.system_admin_accounts IS 'System administrator accounts (separate table, not tenant-scoped)';
COMMENT ON TABLE tutor.questions IS 'AI-generated quiz questions';
COMMENT ON TABLE tutor.quiz_sessions IS 'Quiz session tracking';
COMMENT ON TABLE tutor.answer_submissions IS 'Student answer submissions with validation results';
COMMENT ON TABLE tutor.hints IS 'AI-generated hints for questions';
COMMENT ON TABLE tutor.student_progress IS 'Aggregated student progress statistics';
COMMENT ON TABLE tutor.student_tutor_assignments IS 'Student-tutor assignment relationships';
COMMENT ON TABLE tutor.messages IS 'Student-tutor messaging system';
COMMENT ON TABLE tutor.competitions IS 'One-time competitions per subject';
COMMENT ON TABLE tutor.competition_registrations IS 'Student registrations for competitions';
COMMENT ON TABLE tutor.competition_sessions IS 'Competition-specific quiz sessions';
COMMENT ON TABLE tutor.audit_logs IS 'Audit trail for administrative actions';

