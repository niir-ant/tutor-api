-- Migration: 0.0.10__initial_schema.sql
-- Description: Initial database schema for Quiz API with multi-tenancy support
-- Created: 2025

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom types/enums
CREATE TYPE account_status AS ENUM ('pending_activation', 'active', 'inactive', 'locked', 'suspended');
CREATE TYPE tenant_status AS ENUM ('active', 'inactive', 'suspended');
CREATE TYPE domain_status AS ENUM ('active', 'inactive');
CREATE TYPE subject_status AS ENUM ('active', 'inactive', 'archived');
CREATE TYPE question_difficulty AS ENUM ('beginner', 'intermediate', 'advanced');
CREATE TYPE question_type AS ENUM ('multiple_choice', 'short_answer', 'code_completion', 'code_writing', 'fill_blank', 'true_false');
CREATE TYPE subject_type AS ENUM ('academic', 'programming', 'language', 'science', 'other');
CREATE TYPE validation_method AS ENUM ('ai_semantic', 'code_execution', 'exact_match', 'ai_structured');
CREATE TYPE session_status AS ENUM ('in_progress', 'completed', 'expired', 'abandoned');
CREATE TYPE competition_status AS ENUM ('upcoming', 'active', 'ended', 'cancelled');
CREATE TYPE registration_status AS ENUM ('registered', 'confirmed', 'cancelled');
CREATE TYPE message_status AS ENUM ('sent', 'delivered', 'read', 'deleted');
CREATE TYPE user_role AS ENUM ('student', 'tutor', 'tenant_admin', 'system_admin');
CREATE TYPE assignment_status AS ENUM ('active', 'inactive');
CREATE TYPE competition_session_status AS ENUM ('in_progress', 'completed', 'expired', 'abandoned');
CREATE TYPE visibility_type AS ENUM ('public', 'private', 'tenant_specific');

-- ============================================================================
-- TENANT MANAGEMENT TABLES
-- ============================================================================

-- Tenants table
CREATE TABLE tenants (
    tenant_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status tenant_status NOT NULL DEFAULT 'active',
    primary_domain VARCHAR(255),
    contact_info JSONB,
    settings JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    CONSTRAINT tenants_tenant_code_check CHECK (tenant_code ~ '^[a-z0-9_-]+$')
);

-- Tenant domains table
CREATE TABLE tenant_domains (
    domain_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    domain VARCHAR(255) UNIQUE NOT NULL,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    status domain_status NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    CONSTRAINT tenant_domains_domain_check CHECK (domain ~ '^[a-z0-9.-]+$')
);

-- ============================================================================
-- SUBJECT MANAGEMENT TABLES
-- ============================================================================

-- Subjects table
CREATE TABLE subjects (
    subject_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subject_code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type subject_type NOT NULL,
    grade_levels INTEGER[],
    status subject_status NOT NULL DEFAULT 'active',
    supported_question_types question_type[] NOT NULL,
    answer_validation_method validation_method NOT NULL,
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

-- Student accounts table
CREATE TABLE student_accounts (
    student_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE RESTRICT,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'student',
    grade_level INTEGER,
    account_status account_status NOT NULL DEFAULT 'pending_activation',
    requires_password_change BOOLEAN NOT NULL DEFAULT TRUE,
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    assigned_tutor_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    created_by UUID,
    CONSTRAINT student_accounts_username_tenant_unique UNIQUE (username, tenant_id),
    CONSTRAINT student_accounts_email_tenant_unique UNIQUE (email, tenant_id),
    CONSTRAINT student_accounts_grade_level_check CHECK (grade_level IS NULL OR (grade_level >= 1 AND grade_level <= 12))
);

-- Tutor accounts table
CREATE TABLE tutor_accounts (
    tutor_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE RESTRICT,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    status account_status NOT NULL DEFAULT 'pending_activation',
    requires_password_change BOOLEAN NOT NULL DEFAULT TRUE,
    profile JSONB,
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    created_by UUID,
    CONSTRAINT tutor_accounts_username_tenant_unique UNIQUE (username, tenant_id),
    CONSTRAINT tutor_accounts_email_tenant_unique UNIQUE (email, tenant_id)
);

-- Administrator accounts table
CREATE TABLE administrator_accounts (
    admin_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(tenant_id) ON DELETE RESTRICT,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    status account_status NOT NULL DEFAULT 'pending_activation',
    requires_password_change BOOLEAN NOT NULL DEFAULT TRUE,
    permissions TEXT[],
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    created_by UUID,
    CONSTRAINT administrator_accounts_username_unique UNIQUE (username),
    CONSTRAINT administrator_accounts_email_unique UNIQUE (email),
    CONSTRAINT administrator_accounts_role_check CHECK (role IN ('tenant_admin', 'system_admin')),
    CONSTRAINT administrator_accounts_tenant_check CHECK (
        (role = 'system_admin' AND tenant_id IS NULL) OR
        (role = 'tenant_admin' AND tenant_id IS NOT NULL)
    )
);

-- Add foreign key for assigned_tutor_id in student_accounts
ALTER TABLE student_accounts 
    ADD CONSTRAINT student_accounts_assigned_tutor_fk 
    FOREIGN KEY (assigned_tutor_id) 
    REFERENCES tutor_accounts(tutor_id) 
    ON DELETE SET NULL;

-- ============================================================================
-- AUTHENTICATION TABLES
-- ============================================================================

-- Password reset OTP table
CREATE TABLE password_reset_otp (
    otp_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES student_accounts(student_id) ON DELETE CASCADE,
    tutor_id UUID REFERENCES tutor_accounts(tutor_id) ON DELETE CASCADE,
    admin_id UUID REFERENCES administrator_accounts(admin_id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    otp_code_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT password_reset_otp_user_check CHECK (
        (student_id IS NOT NULL AND tutor_id IS NULL AND admin_id IS NULL) OR
        (student_id IS NULL AND tutor_id IS NOT NULL AND admin_id IS NULL) OR
        (student_id IS NULL AND tutor_id IS NULL AND admin_id IS NOT NULL)
    )
);

-- Authentication tokens table
CREATE TABLE authentication_tokens (
    token_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES student_accounts(student_id) ON DELETE CASCADE,
    tutor_id UUID REFERENCES tutor_accounts(tutor_id) ON DELETE CASCADE,
    admin_id UUID REFERENCES administrator_accounts(admin_id) ON DELETE CASCADE,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT authentication_tokens_user_check CHECK (
        (student_id IS NOT NULL AND tutor_id IS NULL AND admin_id IS NULL) OR
        (student_id IS NULL AND tutor_id IS NOT NULL AND admin_id IS NULL) OR
        (student_id IS NULL AND tutor_id IS NULL AND admin_id IS NOT NULL)
    )
);

-- ============================================================================
-- QUESTION AND QUIZ TABLES
-- ============================================================================

-- Questions table
CREATE TABLE questions (
    question_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(tenant_id) ON DELETE RESTRICT,
    subject_id UUID NOT NULL REFERENCES subjects(subject_id) ON DELETE RESTRICT,
    subject_code VARCHAR(100) NOT NULL,
    grade_level INTEGER,
    difficulty question_difficulty NOT NULL,
    question_type question_type NOT NULL,
    question_text TEXT NOT NULL,
    options JSONB,
    correct_answer JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ai_model_version VARCHAR(50),
    CONSTRAINT questions_grade_level_check CHECK (grade_level IS NULL OR (grade_level >= 1 AND grade_level <= 12))
);

-- Quiz sessions table
CREATE TABLE quiz_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE RESTRICT,
    student_id UUID NOT NULL REFERENCES student_accounts(student_id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES subjects(subject_id) ON DELETE RESTRICT,
    subject_code VARCHAR(100) NOT NULL,
    grade_level INTEGER,
    difficulty question_difficulty,
    questions UUID[] NOT NULL,
    status session_status NOT NULL DEFAULT 'in_progress',
    score DECIMAL(10, 2) NOT NULL DEFAULT 0,
    max_score DECIMAL(10, 2) NOT NULL DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    time_limit INTEGER,
    CONSTRAINT quiz_sessions_grade_level_check CHECK (grade_level IS NULL OR (grade_level >= 1 AND grade_level <= 12))
);

-- Answer submissions table
CREATE TABLE answer_submissions (
    submission_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE RESTRICT,
    question_id UUID NOT NULL REFERENCES questions(question_id) ON DELETE RESTRICT,
    student_id UUID NOT NULL REFERENCES student_accounts(student_id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES quiz_sessions(session_id) ON DELETE CASCADE,
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
CREATE TABLE hints (
    hint_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE RESTRICT,
    question_id UUID NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    hint_level INTEGER NOT NULL,
    hint_text TEXT NOT NULL,
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT hints_hint_level_check CHECK (hint_level >= 1 AND hint_level <= 4)
);

-- Student progress table
CREATE TABLE student_progress (
    student_id UUID PRIMARY KEY REFERENCES student_accounts(student_id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE RESTRICT,
    subject_stats JSONB NOT NULL DEFAULT '{}',
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TUTOR-STUDENT RELATIONSHIPS
-- ============================================================================

-- Student-tutor assignments table
CREATE TABLE student_tutor_assignments (
    assignment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE RESTRICT,
    student_id UUID NOT NULL REFERENCES student_accounts(student_id) ON DELETE CASCADE,
    tutor_id UUID NOT NULL REFERENCES tutor_accounts(tutor_id) ON DELETE CASCADE,
    status assignment_status NOT NULL DEFAULT 'active',
    assigned_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    assigned_by UUID NOT NULL,
    deactivated_at TIMESTAMP WITH TIME ZONE,
    deactivated_by UUID,
    notes TEXT,
    CONSTRAINT student_tutor_assignments_unique UNIQUE (student_id, tutor_id, tenant_id)
);

-- ============================================================================
-- MESSAGING TABLES
-- ============================================================================

-- Messages table
CREATE TABLE messages (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE RESTRICT,
    sender_id UUID NOT NULL,
    sender_role user_role NOT NULL,
    recipient_id UUID NOT NULL,
    recipient_role user_role NOT NULL,
    content TEXT NOT NULL,
    status message_status NOT NULL DEFAULT 'sent',
    email_sent BOOLEAN NOT NULL DEFAULT FALSE,
    email_sent_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    subject_reference UUID REFERENCES subjects(subject_id) ON DELETE SET NULL,
    question_reference UUID REFERENCES questions(question_id) ON DELETE SET NULL,
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
CREATE TABLE competitions (
    competition_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(tenant_id) ON DELETE RESTRICT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    subject_id UUID NOT NULL REFERENCES subjects(subject_id) ON DELETE RESTRICT,
    subject_code VARCHAR(100) NOT NULL,
    status competition_status NOT NULL DEFAULT 'upcoming',
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    registration_start TIMESTAMP WITH TIME ZONE NOT NULL,
    registration_end TIMESTAMP WITH TIME ZONE NOT NULL,
    rules JSONB NOT NULL,
    eligibility JSONB,
    visibility visibility_type NOT NULL DEFAULT 'public',
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
CREATE TABLE competition_registrations (
    registration_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competition_id UUID NOT NULL REFERENCES competitions(competition_id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE RESTRICT,
    student_id UUID NOT NULL REFERENCES student_accounts(student_id) ON DELETE CASCADE,
    status registration_status NOT NULL DEFAULT 'registered',
    registered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    cancelled_by UUID,
    waitlist_position INTEGER,
    notes TEXT,
    CONSTRAINT competition_registrations_unique UNIQUE (competition_id, student_id)
);

-- Competition sessions table
CREATE TABLE competition_sessions (
    competition_session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competition_id UUID NOT NULL REFERENCES competitions(competition_id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE RESTRICT,
    student_id UUID NOT NULL REFERENCES student_accounts(student_id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES quiz_sessions(session_id) ON DELETE CASCADE,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    time_limit INTEGER,
    score DECIMAL(10, 2) NOT NULL DEFAULT 0,
    max_score DECIMAL(10, 2) NOT NULL DEFAULT 0,
    accuracy DECIMAL(5, 2),
    completion_time INTEGER,
    questions_answered INTEGER NOT NULL DEFAULT 0,
    status competition_session_status NOT NULL DEFAULT 'in_progress',
    CONSTRAINT competition_sessions_unique UNIQUE (competition_id, student_id)
);

-- ============================================================================
-- AUDIT LOG TABLE
-- ============================================================================

-- Audit logs table
CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(tenant_id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    performed_by UUID NOT NULL,
    performed_by_role user_role NOT NULL,
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
COMMENT ON COLUMN tenants.tenant_id IS 'Unique identifier for the tenant';
COMMENT ON COLUMN tenants.tenant_code IS 'Unique slug identifier for the tenant (lowercase, alphanumeric, underscores, hyphens only)';
COMMENT ON COLUMN tenants.name IS 'Display name of the educational institution';
COMMENT ON COLUMN tenants.description IS 'Description of the tenant/institution';
COMMENT ON COLUMN tenants.status IS 'Current status of the tenant: active, inactive, or suspended';
COMMENT ON COLUMN tenants.primary_domain IS 'Primary domain identifier for this tenant';
COMMENT ON COLUMN tenants.contact_info IS 'JSON object containing contact information (email, phone, address)';
COMMENT ON COLUMN tenants.settings IS 'JSON object containing tenant-specific settings (branding, features, subscription)';
COMMENT ON COLUMN tenants.created_at IS 'Timestamp when the tenant was created';
COMMENT ON COLUMN tenants.updated_at IS 'Timestamp when the tenant was last updated (auto-updated by trigger)';
COMMENT ON COLUMN tenants.created_by IS 'UUID of the system admin who created this tenant';

-- Tenant domains table columns
COMMENT ON COLUMN tenant_domains.domain_id IS 'Unique identifier for the domain';
COMMENT ON COLUMN tenant_domains.tenant_id IS 'Reference to the tenant this domain belongs to';
COMMENT ON COLUMN tenant_domains.domain IS 'Domain name (e.g., example.com, www.example.com) - must be unique across all tenants';
COMMENT ON COLUMN tenant_domains.is_primary IS 'Whether this is the primary domain for the tenant';
COMMENT ON COLUMN tenant_domains.status IS 'Status of the domain: active or inactive';
COMMENT ON COLUMN tenant_domains.created_at IS 'Timestamp when the domain was created';
COMMENT ON COLUMN tenant_domains.updated_at IS 'Timestamp when the domain was last updated (auto-updated by trigger)';
COMMENT ON COLUMN tenant_domains.created_by IS 'UUID of the system admin who created this domain';

-- Subjects table columns
COMMENT ON COLUMN subjects.subject_id IS 'Unique identifier for the subject';
COMMENT ON COLUMN subjects.subject_code IS 'Unique slug identifier for the subject (lowercase, alphanumeric, underscores, hyphens only)';
COMMENT ON COLUMN subjects.name IS 'Display name of the subject';
COMMENT ON COLUMN subjects.description IS 'Description of the subject/course';
COMMENT ON COLUMN subjects.type IS 'Type of subject: academic, programming, language, science, or other';
COMMENT ON COLUMN subjects.grade_levels IS 'Array of grade levels this subject supports (e.g., [6,7,8,9,10,11,12]) or NULL for all levels';
COMMENT ON COLUMN subjects.status IS 'Status of the subject: active, inactive, or archived';
COMMENT ON COLUMN subjects.supported_question_types IS 'Array of question types supported by this subject';
COMMENT ON COLUMN subjects.answer_validation_method IS 'Method used to validate answers: ai_semantic, code_execution, exact_match, or ai_structured';
COMMENT ON COLUMN subjects.settings IS 'JSON object containing subject-specific settings (AI prompts, validation rules, hint strategies)';
COMMENT ON COLUMN subjects.metadata IS 'JSON object containing metadata (curriculum, learning objectives, icon, category, tags)';
COMMENT ON COLUMN subjects.created_at IS 'Timestamp when the subject was created';
COMMENT ON COLUMN subjects.updated_at IS 'Timestamp when the subject was last updated (auto-updated by trigger)';
COMMENT ON COLUMN subjects.created_by IS 'UUID of the admin who created this subject';

-- Student accounts table columns
COMMENT ON COLUMN student_accounts.student_id IS 'Unique identifier for the student account';
COMMENT ON COLUMN student_accounts.tenant_id IS 'Reference to the tenant this student belongs to (required for tenant isolation)';
COMMENT ON COLUMN student_accounts.username IS 'Unique username within the tenant';
COMMENT ON COLUMN student_accounts.email IS 'Unique email address within the tenant';
COMMENT ON COLUMN student_accounts.password_hash IS 'Cryptographically hashed password (bcrypt/Argon2) - never store plain text';
COMMENT ON COLUMN student_accounts.role IS 'User role - always "student" for this table';
COMMENT ON COLUMN student_accounts.grade_level IS 'Grade level of the student (1-12) or NULL if not applicable';
COMMENT ON COLUMN student_accounts.account_status IS 'Current status: pending_activation, active, inactive, or locked';
COMMENT ON COLUMN student_accounts.requires_password_change IS 'Whether the student must change password on next login (true for preset accounts)';
COMMENT ON COLUMN student_accounts.failed_login_attempts IS 'Number of consecutive failed login attempts (used for account lockout)';
COMMENT ON COLUMN student_accounts.locked_until IS 'Timestamp when account lockout expires (NULL if not locked)';
COMMENT ON COLUMN student_accounts.assigned_tutor_id IS 'Reference to the tutor assigned to this student (optional)';
COMMENT ON COLUMN student_accounts.created_at IS 'Timestamp when the account was created';
COMMENT ON COLUMN student_accounts.updated_at IS 'Timestamp when the account was last updated (auto-updated by trigger)';
COMMENT ON COLUMN student_accounts.last_login IS 'Timestamp of the last successful login';
COMMENT ON COLUMN student_accounts.created_by IS 'UUID of the admin who created this account';

-- Tutor accounts table columns
COMMENT ON COLUMN tutor_accounts.tutor_id IS 'Unique identifier for the tutor account';
COMMENT ON COLUMN tutor_accounts.tenant_id IS 'Reference to the tenant this tutor belongs to (required for tenant isolation)';
COMMENT ON COLUMN tutor_accounts.username IS 'Unique username within the tenant';
COMMENT ON COLUMN tutor_accounts.email IS 'Unique email address within the tenant';
COMMENT ON COLUMN tutor_accounts.password_hash IS 'Cryptographically hashed password (bcrypt/Argon2) - never store plain text';
COMMENT ON COLUMN tutor_accounts.name IS 'Full name of the tutor';
COMMENT ON COLUMN tutor_accounts.status IS 'Current status: pending_activation, active, inactive, suspended, or locked';
COMMENT ON COLUMN tutor_accounts.requires_password_change IS 'Whether the tutor must change password on next login (true for preset accounts)';
COMMENT ON COLUMN tutor_accounts.profile IS 'JSON object containing tutor profile (bio, specializations, contact_info, qualifications)';
COMMENT ON COLUMN tutor_accounts.failed_login_attempts IS 'Number of consecutive failed login attempts (used for account lockout)';
COMMENT ON COLUMN tutor_accounts.locked_until IS 'Timestamp when account lockout expires (NULL if not locked)';
COMMENT ON COLUMN tutor_accounts.created_at IS 'Timestamp when the account was created';
COMMENT ON COLUMN tutor_accounts.updated_at IS 'Timestamp when the account was last updated (auto-updated by trigger)';
COMMENT ON COLUMN tutor_accounts.last_login IS 'Timestamp of the last successful login';
COMMENT ON COLUMN tutor_accounts.created_by IS 'UUID of the admin who created this account';

-- Administrator accounts table columns
COMMENT ON COLUMN administrator_accounts.admin_id IS 'Unique identifier for the administrator account';
COMMENT ON COLUMN administrator_accounts.tenant_id IS 'Reference to the tenant (NULL for system_admin, required for tenant_admin)';
COMMENT ON COLUMN administrator_accounts.username IS 'Unique username (globally unique)';
COMMENT ON COLUMN administrator_accounts.email IS 'Unique email address (globally unique)';
COMMENT ON COLUMN administrator_accounts.password_hash IS 'Cryptographically hashed password (bcrypt/Argon2) - never store plain text';
COMMENT ON COLUMN administrator_accounts.name IS 'Full name of the administrator';
COMMENT ON COLUMN administrator_accounts.role IS 'Administrator role: tenant_admin or system_admin';
COMMENT ON COLUMN administrator_accounts.status IS 'Current status: pending_activation, active, inactive, suspended, or locked';
COMMENT ON COLUMN administrator_accounts.requires_password_change IS 'Whether the admin must change password on next login (true for preset accounts)';
COMMENT ON COLUMN administrator_accounts.permissions IS 'Array of specific permissions (optional, for fine-grained access control)';
COMMENT ON COLUMN administrator_accounts.failed_login_attempts IS 'Number of consecutive failed login attempts (used for account lockout)';
COMMENT ON COLUMN administrator_accounts.locked_until IS 'Timestamp when account lockout expires (NULL if not locked)';
COMMENT ON COLUMN administrator_accounts.created_at IS 'Timestamp when the account was created';
COMMENT ON COLUMN administrator_accounts.updated_at IS 'Timestamp when the account was last updated (auto-updated by trigger)';
COMMENT ON COLUMN administrator_accounts.last_login IS 'Timestamp of the last successful login';
COMMENT ON COLUMN administrator_accounts.created_by IS 'UUID of the admin who created this account (system admin for tenant_admin, super admin for system_admin)';

-- Password reset OTP table columns
COMMENT ON COLUMN password_reset_otp.otp_id IS 'Unique identifier for the OTP record';
COMMENT ON COLUMN password_reset_otp.student_id IS 'Reference to student account (mutually exclusive with tutor_id and admin_id)';
COMMENT ON COLUMN password_reset_otp.tutor_id IS 'Reference to tutor account (mutually exclusive with student_id and admin_id)';
COMMENT ON COLUMN password_reset_otp.admin_id IS 'Reference to admin account (mutually exclusive with student_id and tutor_id)';
COMMENT ON COLUMN password_reset_otp.email IS 'Email address the OTP was sent to';
COMMENT ON COLUMN password_reset_otp.otp_code_hash IS 'Hashed one-time passcode (never store plain text)';
COMMENT ON COLUMN password_reset_otp.expires_at IS 'Timestamp when the OTP expires (typically 15 minutes from creation)';
COMMENT ON COLUMN password_reset_otp.used IS 'Whether this OTP has been used (single-use only)';
COMMENT ON COLUMN password_reset_otp.created_at IS 'Timestamp when the OTP was created';
COMMENT ON COLUMN password_reset_otp.used_at IS 'Timestamp when the OTP was used (NULL if not used)';

-- Authentication tokens table columns
COMMENT ON COLUMN authentication_tokens.token_id IS 'Unique identifier for the token record';
COMMENT ON COLUMN authentication_tokens.student_id IS 'Reference to student account (mutually exclusive with tutor_id and admin_id)';
COMMENT ON COLUMN authentication_tokens.tutor_id IS 'Reference to tutor account (mutually exclusive with student_id and admin_id)';
COMMENT ON COLUMN authentication_tokens.admin_id IS 'Reference to admin account (mutually exclusive with student_id and tutor_id)';
COMMENT ON COLUMN authentication_tokens.access_token IS 'JWT access token (stored for revocation purposes)';
COMMENT ON COLUMN authentication_tokens.refresh_token IS 'JWT refresh token (optional, for token refresh flow)';
COMMENT ON COLUMN authentication_tokens.expires_at IS 'Timestamp when the token expires';
COMMENT ON COLUMN authentication_tokens.created_at IS 'Timestamp when the token was created';
COMMENT ON COLUMN authentication_tokens.revoked IS 'Whether this token has been revoked (e.g., on logout)';

-- Questions table columns
COMMENT ON COLUMN questions.question_id IS 'Unique identifier for the question';
COMMENT ON COLUMN questions.tenant_id IS 'Reference to tenant (NULL for system-wide questions, UUID for tenant-specific questions)';
COMMENT ON COLUMN questions.subject_id IS 'Reference to the subject this question belongs to';
COMMENT ON COLUMN questions.subject_code IS 'Denormalized subject code for quick access (denormalized from subjects table)';
COMMENT ON COLUMN questions.grade_level IS 'Grade level this question is appropriate for (1-12) or NULL if not grade-specific';
COMMENT ON COLUMN questions.difficulty IS 'Difficulty level: beginner, intermediate, or advanced';
COMMENT ON COLUMN questions.question_type IS 'Type of question: multiple_choice, short_answer, code_completion, code_writing, fill_blank, or true_false';
COMMENT ON COLUMN questions.question_text IS 'The question text/prompt';
COMMENT ON COLUMN questions.options IS 'JSON array of options for multiple choice questions';
COMMENT ON COLUMN questions.correct_answer IS 'JSON object containing the correct answer(s)';
COMMENT ON COLUMN questions.metadata IS 'JSON object containing metadata (topic, learning_objectives, estimated_time, points)';
COMMENT ON COLUMN questions.created_at IS 'Timestamp when the question was generated';
COMMENT ON COLUMN questions.ai_model_version IS 'Version of the AI model used to generate this question';

-- Quiz sessions table columns
COMMENT ON COLUMN quiz_sessions.session_id IS 'Unique identifier for the quiz session';
COMMENT ON COLUMN quiz_sessions.tenant_id IS 'Reference to the tenant (required for tenant isolation)';
COMMENT ON COLUMN quiz_sessions.student_id IS 'Reference to the student taking the quiz';
COMMENT ON COLUMN quiz_sessions.subject_id IS 'Reference to the subject for this quiz';
COMMENT ON COLUMN quiz_sessions.subject_code IS 'Denormalized subject code for quick access';
COMMENT ON COLUMN quiz_sessions.grade_level IS 'Grade level for this quiz session (1-12) or NULL if not grade-specific';
COMMENT ON COLUMN quiz_sessions.difficulty IS 'Difficulty level of the quiz';
COMMENT ON COLUMN quiz_sessions.questions IS 'Array of question UUIDs in this quiz session';
COMMENT ON COLUMN quiz_sessions.status IS 'Current status: in_progress, completed, expired, or abandoned';
COMMENT ON COLUMN quiz_sessions.score IS 'Total score achieved in this session';
COMMENT ON COLUMN quiz_sessions.max_score IS 'Maximum possible score for this session';
COMMENT ON COLUMN quiz_sessions.started_at IS 'Timestamp when the session was started';
COMMENT ON COLUMN quiz_sessions.completed_at IS 'Timestamp when the session was completed (NULL if not completed)';
COMMENT ON COLUMN quiz_sessions.time_limit IS 'Time limit in seconds (NULL if no time limit)';

-- Answer submissions table columns
COMMENT ON COLUMN answer_submissions.submission_id IS 'Unique identifier for the answer submission';
COMMENT ON COLUMN answer_submissions.tenant_id IS 'Reference to the tenant (required for tenant isolation)';
COMMENT ON COLUMN answer_submissions.question_id IS 'Reference to the question being answered';
COMMENT ON COLUMN answer_submissions.student_id IS 'Reference to the student who submitted the answer';
COMMENT ON COLUMN answer_submissions.session_id IS 'Reference to the quiz session this answer belongs to';
COMMENT ON COLUMN answer_submissions.answer IS 'JSON object containing the student answer (text, code, or selected options)';
COMMENT ON COLUMN answer_submissions.is_correct IS 'Whether the answer is correct (boolean)';
COMMENT ON COLUMN answer_submissions.score IS 'Points awarded for this answer';
COMMENT ON COLUMN answer_submissions.max_score IS 'Maximum points possible for this question';
COMMENT ON COLUMN answer_submissions.feedback IS 'Feedback message provided to the student';
COMMENT ON COLUMN answer_submissions.hints_used IS 'Array of hint UUIDs that were used before submitting this answer';
COMMENT ON COLUMN answer_submissions.time_spent IS 'Time spent on this question in seconds';
COMMENT ON COLUMN answer_submissions.submitted_at IS 'Timestamp when the answer was submitted';

-- Hints table columns
COMMENT ON COLUMN hints.hint_id IS 'Unique identifier for the hint';
COMMENT ON COLUMN hints.tenant_id IS 'Reference to the tenant (required for tenant isolation)';
COMMENT ON COLUMN hints.question_id IS 'Reference to the question this hint is for';
COMMENT ON COLUMN hints.hint_level IS 'Level of the hint (1-4, where 1 is most subtle, 4 is most explicit)';
COMMENT ON COLUMN hints.hint_text IS 'The hint text content';
COMMENT ON COLUMN hints.generated_at IS 'Timestamp when the hint was generated';

-- Student progress table columns
COMMENT ON COLUMN student_progress.student_id IS 'Reference to the student (primary key)';
COMMENT ON COLUMN student_progress.tenant_id IS 'Reference to the tenant (required for tenant isolation)';
COMMENT ON COLUMN student_progress.subject_stats IS 'JSON object containing aggregated statistics per subject (total_questions, correct, accuracy, average_score, topics)';
COMMENT ON COLUMN student_progress.last_updated IS 'Timestamp when the progress was last updated';

-- Student-tutor assignments table columns
COMMENT ON COLUMN student_tutor_assignments.assignment_id IS 'Unique identifier for the assignment';
COMMENT ON COLUMN student_tutor_assignments.tenant_id IS 'Reference to the tenant (required for tenant isolation)';
COMMENT ON COLUMN student_tutor_assignments.student_id IS 'Reference to the student being assigned';
COMMENT ON COLUMN student_tutor_assignments.tutor_id IS 'Reference to the tutor being assigned';
COMMENT ON COLUMN student_tutor_assignments.status IS 'Status of the assignment: active or inactive';
COMMENT ON COLUMN student_tutor_assignments.assigned_at IS 'Timestamp when the assignment was created';
COMMENT ON COLUMN student_tutor_assignments.assigned_by IS 'UUID of the admin who created this assignment';
COMMENT ON COLUMN student_tutor_assignments.deactivated_at IS 'Timestamp when the assignment was deactivated (NULL if active)';
COMMENT ON COLUMN student_tutor_assignments.deactivated_by IS 'UUID of the admin who deactivated this assignment (NULL if self-deactivated)';
COMMENT ON COLUMN student_tutor_assignments.notes IS 'Optional notes about the assignment';

-- Messages table columns
COMMENT ON COLUMN messages.message_id IS 'Unique identifier for the message';
COMMENT ON COLUMN messages.tenant_id IS 'Reference to the tenant (required for tenant isolation)';
COMMENT ON COLUMN messages.sender_id IS 'UUID of the user who sent the message (student, tutor, or tenant_admin)';
COMMENT ON COLUMN messages.sender_role IS 'Role of the sender: student, tutor, or tenant_admin';
COMMENT ON COLUMN messages.recipient_id IS 'UUID of the user who receives the message';
COMMENT ON COLUMN messages.recipient_role IS 'Role of the recipient: student, tutor, or tenant_admin';
COMMENT ON COLUMN messages.content IS 'Text content of the message';
COMMENT ON COLUMN messages.status IS 'Status of the message: sent, delivered, read, or deleted';
COMMENT ON COLUMN messages.email_sent IS 'Whether an email copy was sent to the recipient';
COMMENT ON COLUMN messages.email_sent_at IS 'Timestamp when the email was sent (NULL if not sent)';
COMMENT ON COLUMN messages.read_at IS 'Timestamp when the message was read (NULL if not read)';
COMMENT ON COLUMN messages.subject_reference IS 'Optional reference to a subject (for context)';
COMMENT ON COLUMN messages.question_reference IS 'Optional reference to a question (for context)';
COMMENT ON COLUMN messages.conversation_id IS 'UUID grouping messages in the same conversation thread';
COMMENT ON COLUMN messages.created_at IS 'Timestamp when the message was created';
COMMENT ON COLUMN messages.updated_at IS 'Timestamp when the message was last updated (auto-updated by trigger)';
COMMENT ON COLUMN messages.deleted_at IS 'Timestamp when the message was soft-deleted (NULL if not deleted)';

-- Competitions table columns
COMMENT ON COLUMN competitions.competition_id IS 'Unique identifier for the competition';
COMMENT ON COLUMN competitions.tenant_id IS 'Reference to the tenant (NULL for system-wide competitions, UUID for tenant-specific)';
COMMENT ON COLUMN competitions.name IS 'Name of the competition';
COMMENT ON COLUMN competitions.description IS 'Description of the competition';
COMMENT ON COLUMN competitions.subject_id IS 'Reference to the subject this competition is for';
COMMENT ON COLUMN competitions.subject_code IS 'Denormalized subject code for quick access';
COMMENT ON COLUMN competitions.status IS 'Current status: upcoming, active, ended, or cancelled';
COMMENT ON COLUMN competitions.start_date IS 'Timestamp when the competition starts';
COMMENT ON COLUMN competitions.end_date IS 'Timestamp when the competition ends';
COMMENT ON COLUMN competitions.registration_start IS 'Timestamp when registration opens';
COMMENT ON COLUMN competitions.registration_end IS 'Timestamp when registration closes';
COMMENT ON COLUMN competitions.rules IS 'JSON object containing competition rules (time_limit, num_questions, difficulty, allowed_question_types, max_attempts, scoring_rules, hints_allowed, narratives_allowed)';
COMMENT ON COLUMN competitions.eligibility IS 'JSON object containing eligibility criteria (grade_levels, tenant_restrictions, minimum_requirements)';
COMMENT ON COLUMN competitions.visibility IS 'Visibility level: public, private, or tenant_specific';
COMMENT ON COLUMN competitions.max_participants IS 'Maximum number of participants allowed (NULL for unlimited)';
COMMENT ON COLUMN competitions.participant_count IS 'Current number of registered participants';
COMMENT ON COLUMN competitions.created_at IS 'Timestamp when the competition was created';
COMMENT ON COLUMN competitions.updated_at IS 'Timestamp when the competition was last updated (auto-updated by trigger)';
COMMENT ON COLUMN competitions.created_by IS 'UUID of the admin who created this competition';
COMMENT ON COLUMN competitions.cancelled_at IS 'Timestamp when the competition was cancelled (NULL if not cancelled)';
COMMENT ON COLUMN competitions.cancelled_by IS 'UUID of the admin who cancelled this competition (NULL if not cancelled)';
COMMENT ON COLUMN competitions.cancellation_reason IS 'Reason for cancellation (NULL if not cancelled)';

-- Competition registrations table columns
COMMENT ON COLUMN competition_registrations.registration_id IS 'Unique identifier for the registration';
COMMENT ON COLUMN competition_registrations.competition_id IS 'Reference to the competition';
COMMENT ON COLUMN competition_registrations.tenant_id IS 'Reference to the tenant (required for tenant isolation)';
COMMENT ON COLUMN competition_registrations.student_id IS 'Reference to the student registering';
COMMENT ON COLUMN competition_registrations.status IS 'Status of the registration: registered, confirmed, or cancelled';
COMMENT ON COLUMN competition_registrations.registered_at IS 'Timestamp when the student registered';
COMMENT ON COLUMN competition_registrations.confirmed_at IS 'Timestamp when the registration was confirmed (NULL if not confirmed)';
COMMENT ON COLUMN competition_registrations.cancelled_at IS 'Timestamp when the registration was cancelled (NULL if not cancelled)';
COMMENT ON COLUMN competition_registrations.cancelled_by IS 'UUID of who cancelled (student_id if self-cancelled, admin_id if admin-cancelled)';
COMMENT ON COLUMN competition_registrations.waitlist_position IS 'Position in waitlist if max participants reached (NULL if not waitlisted)';
COMMENT ON COLUMN competition_registrations.notes IS 'Optional notes about the registration';

-- Competition sessions table columns
COMMENT ON COLUMN competition_sessions.competition_session_id IS 'Unique identifier for the competition session';
COMMENT ON COLUMN competition_sessions.competition_id IS 'Reference to the competition';
COMMENT ON COLUMN competition_sessions.tenant_id IS 'Reference to the tenant (required for tenant isolation)';
COMMENT ON COLUMN competition_sessions.student_id IS 'Reference to the student participating';
COMMENT ON COLUMN competition_sessions.session_id IS 'Reference to the quiz session used for this competition';
COMMENT ON COLUMN competition_sessions.started_at IS 'Timestamp when the competition session was started';
COMMENT ON COLUMN competition_sessions.completed_at IS 'Timestamp when the competition session was completed (NULL if not completed)';
COMMENT ON COLUMN competition_sessions.time_limit IS 'Time limit in seconds for this competition session';
COMMENT ON COLUMN competition_sessions.score IS 'Total score achieved in this competition session';
COMMENT ON COLUMN competition_sessions.max_score IS 'Maximum possible score for this competition session';
COMMENT ON COLUMN competition_sessions.accuracy IS 'Accuracy percentage (correct answers / total questions)';
COMMENT ON COLUMN competition_sessions.completion_time IS 'Time taken to complete the competition in seconds';
COMMENT ON COLUMN competition_sessions.questions_answered IS 'Number of questions answered';
COMMENT ON COLUMN competition_sessions.status IS 'Status of the session: in_progress, completed, expired, or abandoned';

-- Audit logs table columns
COMMENT ON COLUMN audit_logs.log_id IS 'Unique identifier for the audit log entry';
COMMENT ON COLUMN audit_logs.tenant_id IS 'Reference to the tenant (NULL for system-level actions)';
COMMENT ON COLUMN audit_logs.action IS 'Action performed (e.g., create_account, disable_account, assign_tutor)';
COMMENT ON COLUMN audit_logs.performed_by IS 'UUID of the user who performed the action';
COMMENT ON COLUMN audit_logs.performed_by_role IS 'Role of the user who performed the action (tenant_admin or system_admin)';
COMMENT ON COLUMN audit_logs.target_type IS 'Type of target entity (account, subject, assignment, message, tenant, etc.)';
COMMENT ON COLUMN audit_logs.target_id IS 'UUID of the target entity that was acted upon';
COMMENT ON COLUMN audit_logs.details IS 'JSON object containing action-specific details';
COMMENT ON COLUMN audit_logs.ip_address IS 'IP address of the user who performed the action';
COMMENT ON COLUMN audit_logs.user_agent IS 'User agent string of the client that performed the action';
COMMENT ON COLUMN audit_logs.timestamp IS 'Timestamp when the action was performed';

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tenant_domains_updated_at BEFORE UPDATE ON tenant_domains
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subjects_updated_at BEFORE UPDATE ON subjects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_student_accounts_updated_at BEFORE UPDATE ON student_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tutor_accounts_updated_at BEFORE UPDATE ON tutor_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_administrator_accounts_updated_at BEFORE UPDATE ON administrator_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_messages_updated_at BEFORE UPDATE ON messages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_competitions_updated_at BEFORE UPDATE ON competitions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE tenants IS 'Multi-tenant educational institutions';
COMMENT ON TABLE tenant_domains IS 'Domain mappings for tenant resolution';
COMMENT ON TABLE subjects IS 'Subjects/courses available in the system';
COMMENT ON TABLE student_accounts IS 'Student user accounts with tenant isolation';
COMMENT ON TABLE tutor_accounts IS 'Tutor user accounts with tenant isolation';
COMMENT ON TABLE administrator_accounts IS 'Administrator accounts (tenant and system level)';
COMMENT ON TABLE questions IS 'AI-generated quiz questions';
COMMENT ON TABLE quiz_sessions IS 'Quiz session tracking';
COMMENT ON TABLE answer_submissions IS 'Student answer submissions with validation results';
COMMENT ON TABLE hints IS 'AI-generated hints for questions';
COMMENT ON TABLE student_progress IS 'Aggregated student progress statistics';
COMMENT ON TABLE student_tutor_assignments IS 'Student-tutor assignment relationships';
COMMENT ON TABLE messages IS 'Student-tutor messaging system';
COMMENT ON TABLE competitions IS 'One-time competitions per subject';
COMMENT ON TABLE competition_registrations IS 'Student registrations for competitions';
COMMENT ON TABLE competition_sessions IS 'Competition-specific quiz sessions';
COMMENT ON TABLE audit_logs IS 'Audit trail for administrative actions';

