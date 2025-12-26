# Quiz API Requirements Document

## 1. Overview

### 1.1 Purpose
This document outlines the requirements for a Quiz API that provides AI-generated quiz-style questions for multiple subjects, including Math (grades 6-12), English (grades 6-12), and Python programming. The API will support interactive learning through question generation, answer validation, scoring, hints, and educational narratives. The system is designed to be extensible, allowing new subjects to be added dynamically without requiring code changes. The system supports multi-tenancy, where each tenant represents an educational institution with isolated data and tenant-level administration.

### 1.2 Scope
The API will serve as a backend service for educational applications, providing:
- Multi-tenant architecture (each tenant represents an educational institution)
- User management and authentication for students, tutors, and administrators
- Role-based access control (Student, Tutor, Tenant Admin, System Admin)
- Tenant management and isolation
- Tutor management and student-tutor assignment (within tenant)
- Messaging system between students and tutors (within tenant)
- Subject management (create, update, configure subjects dynamically)
- Dynamic question generation using AI
- Answer validation and scoring
- Adaptive learning support (hints, explanations)
- Progress tracking for students
- Multi-subject and multi-grade support
- Extensible architecture for adding new subjects
- Administrative controls for account and course management (tenant-scoped and system-wide)

### 1.3 Target Users
- Students (grades 6-12 for Math/English, all levels for Python) - within their tenant
- Tutors (assigned to teams of students) - within their tenant
- Tenant Administrators (manage accounts and courses within their institution/tenant)
- System Administrators (manage tenants, system-wide settings, and all accounts)
- Educational platforms integrating quiz functionality

---

## 2. Functional Requirements

### 2.1 Question Generation

#### 2.1.1 AI-Generated Questions
- **FR-1.1**: The system shall generate quiz questions using AI for configured subjects. Initial subjects include:
  - Mathematics (grades 6-12)
  - English Language Arts (grades 6-12)
  - Python Programming (all skill levels)
- **FR-1.1a**: The system shall support dynamic subject addition without code changes
- **FR-1.2**: Questions shall be generated dynamically based on:
  - Subject
  - Grade level (for Math/English)
  - Difficulty level (beginner, intermediate, advanced)
  - Topic or curriculum area (optional)
  - Question type (multiple choice, short answer, code completion, etc.)
- **FR-1.3**: Generated questions shall include:
  - Question text/prompt
  - Correct answer(s)
  - Distractor options (for multiple choice)
  - Metadata (difficulty, estimated time, learning objectives)

#### 2.1.2 Question Types
- **FR-1.4**: Support multiple question formats:
  - Multiple choice (single and multiple correct answers)
  - Short answer/text response
  - Code completion (for Python)
  - Code writing (for Python)
  - Fill-in-the-blank
  - True/False

### 2.2 Answer Validation

#### 2.2.1 Answer Checking
- **FR-2.1**: The system shall validate student answers using AI-powered evaluation
- **FR-2.2**: For multiple choice questions, validate against correct answer(s)
- **FR-2.3**: For text-based answers (English, short answers), use AI to evaluate:
  - Semantic correctness
  - Partial credit for partially correct answers
  - Grammar and spelling considerations (configurable)
- **FR-2.4**: For Python code answers, validate:
  - Code correctness (syntax and logic)
  - Output matching expected results
  - Code quality and best practices (optional)
  - Test case execution
- **FR-2.5**: Return validation results including:
  - Correct/incorrect status
  - Score/points awarded
  - Feedback message
  - Specific areas of correctness/incorrectness

### 2.3 Scoring and Progress Tracking

#### 2.3.1 Score Calculation
- **FR-3.1**: Track scores for individual questions and quiz sessions
- **FR-3.2**: Support configurable scoring:
  - Points per question
  - Partial credit for partially correct answers
  - Bonus points for hints used (optional)
- **FR-3.3**: Calculate aggregate metrics:
  - Total score per quiz session
  - Average score per subject/topic
  - Performance trends over time
  - Accuracy percentage

#### 2.3.2 Progress Tracking
- **FR-3.4**: Maintain student progress records:
  - Questions attempted
  - Questions answered correctly/incorrectly
  - Time spent per question
  - Hints requested
  - Topics mastered/struggling
- **FR-3.5**: Provide progress analytics:
  - Performance by subject
  - Performance by grade level
  - Performance by topic
  - Improvement trends
  - Weak areas identification

### 2.4 Hints System

#### 2.4.1 Hint Generation
- **FR-4.1**: Generate contextual hints when a student requests help
- **FR-4.2**: Hints shall be AI-generated and adaptive:
  - Progressive hints (first hint is subtle, subsequent hints more explicit)
  - Context-aware (consider student's previous attempts)
  - Subject-appropriate (different strategies for Math vs English vs Python)
- **FR-4.3**: Support multiple hint levels:
  - Level 1: Subtle guidance (e.g., "Consider the order of operations")
  - Level 2: More specific direction (e.g., "Remember PEMDAS")
  - Level 3: Direct approach (e.g., "Start by solving parentheses first")
  - Level 4: Step-by-step guidance (optional)

#### 2.4.2 Hint Tracking
- **FR-4.4**: Track hint usage:
  - Number of hints requested per question
  - Which hint level was used
  - Impact on answer correctness
  - Adjust scoring if hints are used (configurable)

### 2.5 Educational Narratives

#### 2.5.1 Narrative Generation
- **FR-5.1**: Generate educational narratives/explanations for questions when requested
- **FR-5.2**: Narratives shall include:
  - Conceptual explanation of the topic
  - Step-by-step solution approach
  - Why the answer is correct
  - Common mistakes to avoid
  - Related concepts and connections
  - Real-world applications (where applicable)
- **FR-5.3**: Narratives shall be:
  - Grade-level appropriate
  - Clear and engaging
  - Comprehensive yet concise
  - AI-generated and contextually relevant

#### 2.5.2 Narrative Delivery
- **FR-5.4**: Provide narratives in multiple formats:
  - Text-based explanation
  - Structured format (steps, bullet points)
  - Optional: Markdown formatting for rich text

### 2.6 Session Management

#### 2.6.1 Quiz Sessions
- **FR-6.1**: Support quiz session creation and management
- **FR-6.2**: Session parameters:
  - Subject selection
  - Grade level (for Math/English)
  - Number of questions
  - Difficulty level
  - Time limits (optional)
- **FR-6.3**: Track session state:
  - Current question
  - Questions answered
  - Time elapsed
  - Session completion status

### 2.7 User Management

#### 2.7.1 Student Account Management
- **FR-7.1**: Support preset student account creation by administrators
- **FR-7.2**: Preset accounts shall include:
  - Student identifier (username or email)
  - Email address
  - Initial temporary password or password reset token
  - Grade level (optional)
  - Account status (pending_activation, active, inactive)
- **FR-7.3**: Link student accounts to progress tracking:
  - All quiz sessions associated with student_id
  - All answer submissions tracked per student
  - Progress analytics per student
  - Performance history per student

#### 2.7.2 Authentication
- **FR-7.4**: Support student login with:
  - Username/email and password
  - Session token generation upon successful login
  - Token expiration and refresh mechanisms
- **FR-7.5**: Password security requirements:
  - Passwords must be stored as cryptographic hashes (bcrypt, Argon2, or similar)
  - Never store plain text passwords
  - Support password strength requirements (configurable)
- **FR-7.6**: First-time login handling:
  - Detect first-time login for preset accounts
  - Require password change on first login
  - Prevent access to quiz features until password is changed
  - Mark account as activated after first password change

#### 2.7.3 Password Management
- **FR-7.7**: Password change functionality:
  - Allow authenticated students to change their password
  - Require current password verification
  - Validate new password meets strength requirements
  - Update password hash in database
- **FR-7.8**: Forgot password functionality:
  - Generate one-time passcode (OTP) for password reset
  - Send OTP to student's registered email address
  - OTP validity period (e.g., 15 minutes)
  - Single-use OTP (invalidated after use)
  - Allow password reset using valid OTP
  - Rate limiting on OTP requests (prevent abuse)

#### 2.7.4 Email Integration
- **FR-7.9**: Email service integration for:
  - Sending one-time passcodes for password reset
  - Sending account activation notifications
  - Sending password change confirmations
- **FR-7.10**: Email requirements:
  - Secure email delivery
  - Email templates for different scenarios
  - Support for email service providers (SendGrid, AWS SES, etc.)

#### 2.7.5 Account Status Management
- **FR-7.11**: Track and manage account status:
  - Pending activation (preset account, not yet logged in)
  - Active (password set, can access all features)
  - Inactive (administratively disabled)
  - Locked (temporary lockout after failed login attempts)
- **FR-7.12**: Account lockout protection:
  - Track failed login attempts
  - Lock account after N failed attempts (configurable)
  - Temporary lockout duration (configurable)
  - Admin unlock capability

### 2.8 Subject Management

#### 2.8.1 Subject Configuration
- **FR-8.1**: Support dynamic subject creation and management
- **FR-8.2**: Subject configuration shall include:
  - Subject identifier (unique code/slug)
  - Subject name (display name)
  - Subject description
  - Grade level support (which grades are applicable, if any)
  - Subject type (academic, programming, language, etc.)
  - Active/inactive status
  - Subject-specific settings:
    - Default difficulty levels
    - Supported question types
    - Answer validation method (AI-based, code execution, etc.)
    - Special requirements (e.g., code execution for programming subjects)
- **FR-8.3**: Support subject metadata:
  - Curriculum alignment
  - Learning objectives
  - Subject icon/image (optional)
  - Category/tags

#### 2.8.2 Subject Lifecycle
- **FR-8.4**: Support subject states:
  - Active: Available for question generation and student use
  - Inactive: Hidden from students but data preserved
  - Archived: Historical data only, no new questions
- **FR-8.5**: Prevent deletion of subjects with existing:
  - Questions
  - Student progress data
  - Quiz sessions
  - Instead, mark as inactive or archived

#### 2.8.3 Subject Extensibility
- **FR-8.6**: Design system to be extensible for new subjects:
  - Subject configuration stored in database (not hardcoded)
  - Question generation adapts to subject configuration
  - Answer validation adapts to subject type
  - Progress tracking works for any subject
  - No code changes required to add new subjects
- **FR-8.7**: Support subject-specific customizations:
  - Custom AI prompts for question generation per subject
  - Subject-specific answer validation rules
  - Subject-specific hint strategies
  - Subject-specific narrative templates

#### 2.8.4 Subject Validation
- **FR-8.8**: Validate subject configuration:
  - Unique subject identifier
  - Required fields present
  - Valid grade level ranges (if applicable)
  - Valid question types for subject
  - Valid answer validation method

### 2.9 Competition Management

#### 2.9.1 Competition Concept
- **FR-9.1**: Support one-time competitions per subject
- **FR-9.2**: Competition characteristics:
  - Each competition is associated with a single subject
  - One-time event (not recurring)
  - Time-bound with start and end dates/times
  - Multiple students can participate
  - Competitive scoring and leaderboards
  - Winners/rankings based on performance
- **FR-9.3**: Competition lifecycle:
  - Upcoming: Competition created but not yet started
  - Active: Competition is currently running (between start and end time)
  - Ended: Competition has completed, results finalized
  - Cancelled: Competition cancelled before or during execution

#### 2.9.2 Competition Configuration
- **FR-9.4**: Competition configuration shall include:
  - Competition name and description
  - Subject association (one subject per competition)
  - Start date and time
  - End date and time
  - Registration period (registration start/end times)
  - Competition rules:
    - Time limit per question or total time limit
    - Number of questions
    - Difficulty level(s)
    - Allowed question types
    - Maximum attempts (typically 1 for competitions)
    - Scoring rules (points per question, bonus points, penalties)
  - Eligibility criteria:
    - Grade level restrictions (optional)
    - Tenant restrictions (tenant-specific or system-wide)
    - Minimum requirements (optional)
- **FR-9.5**: Competition visibility and access:
  - Public (visible to all eligible students)
  - Private (invitation-only)
  - Tenant-specific (only students in specific tenant)
  - Grade-level specific (only students in specific grades)

#### 2.9.3 Competition Registration
- **FR-9.6**: Student registration for competitions:
  - Students can register for competitions during registration period
  - Registration validation:
    - Check eligibility (grade level, tenant, etc.)
    - Verify competition is accepting registrations
    - Prevent duplicate registrations
    - Check maximum participant limits (if set)
  - Track registration status (registered, confirmed, cancelled)
- **FR-9.7**: Registration management:
  - View registered participants
  - Cancel registrations (by student or admin)
  - Waitlist support (optional, if participant limit reached)
  - Send registration confirmations

#### 2.9.4 Competition Sessions
- **FR-9.8**: Competition-specific quiz sessions:
  - Competition sessions are separate from regular quiz sessions
  - Students can start competition session only during active period
  - One attempt per student (or configurable max attempts)
  - Competition sessions use competition-specific rules
  - Questions generated based on competition configuration
  - Time tracking for competition sessions
- **FR-9.9**: Competition session constraints:
  - Cannot start session before competition start time
  - Cannot start session after competition end time
  - Session must be completed within competition time window
  - No hints allowed (configurable)
  - No narrative access during competition (configurable)
  - Strict time limits enforced

#### 2.9.5 Competition Leaderboards
- **FR-9.10**: Real-time and final leaderboards:
  - Real-time leaderboard updates during active competition
  - Final leaderboard after competition ends
  - Ranking based on:
    - Total score (primary)
    - Accuracy percentage (tie-breaker)
    - Completion time (tie-breaker, if applicable)
  - Leaderboard visibility:
    - Public (visible to all)
    - Participants only
    - Private (admin only)
- **FR-9.11**: Leaderboard features:
  - Top N participants display
  - Student's own rank and position
  - Filter by grade level (if applicable)
  - Pagination for large competitions
  - Export leaderboard data (admin)

#### 2.9.6 Competition Results and Winners
- **FR-9.12**: Competition results:
  - Final rankings after competition ends
  - Winner determination (top N participants)
  - Prize/recognition assignment (optional)
  - Individual student results
  - Competition statistics (participation rate, average score, etc.)
- **FR-9.13**: Results distribution:
  - Automatic results announcement after competition ends
  - Email notifications to participants (optional)
  - Results available for viewing
  - Certificate generation (optional, future enhancement)

#### 2.9.7 Competition Administration
- **FR-9.14**: Admin capabilities for competitions:
  - Create competitions (tenant admin or system admin)
  - Update competition configuration (before start)
  - Cancel competitions
  - View all registrations
  - Monitor active competitions
  - View competition analytics and statistics
  - Export competition data
- **FR-9.15**: Competition management constraints:
  - Cannot modify competition after it has started
  - Cannot delete competitions with existing participants
  - Archive completed competitions (preserve data)

### 2.10 Tutor Management

#### 2.10.1 Tutor Account Management
- **FR-9.1**: Support tutor account creation and management
- **FR-9.2**: Tutor accounts shall have:
  - Unique tutor identifier
  - Authentication credentials (username/email, password)
  - Tutor profile information (name, email, contact details)
  - Account status (active, inactive, suspended)
  - Assigned students (team of students)
- **FR-10.3**: Tutor account creation:
  - Can be created by administrators
  - Can be converted from existing student account (by admin)
  - Requires password setup (similar to student accounts)
  - Can have preset account creation with first-time password change

#### 2.10.2 Student-Tutor Assignment
- **FR-10.4**: Support assignment of students to tutors:
  - One tutor can have multiple students (team)
  - One student can be assigned to one tutor (or optionally multiple tutors)
  - Assignment managed by administrators
  - Track assignment history (when assigned, by whom)
- **FR-10.5**: Tutor team management:
  - View all assigned students
  - View student progress and performance
  - Filter and search students in team
  - Get team statistics and analytics

#### 2.10.3 Tutor Capabilities
- **FR-10.6**: Tutors shall be able to:
  - View assigned students' progress and performance
  - View student quiz history and results
  - Access student analytics and reports
  - Send messages to assigned students
  - Receive and respond to messages from assigned students
  - View messaging history with students

### 2.11 Messaging System

#### 2.11.1 Student-Tutor Messaging
- **FR-11.1**: Support bidirectional messaging between students and tutors
- **FR-11.2**: Message requirements:
  - Student can send messages to their assigned tutor
  - Tutor can send messages to any assigned student
  - Messages include: sender, recipient, content, timestamp
  - Message status (sent, delivered, read)
  - Thread/conversation grouping
- **FR-10.3**: Message content:
  - Text content (required)
  - Optional attachments (files, images) - future enhancement
  - Message metadata (subject/topic reference, question reference)
- **FR-10.4**: Message delivery:
  - Real-time or near-real-time delivery
  - Message persistence in database
  - Message history and conversation threads

#### 2.11.2 Email Integration for Messages
- **FR-10.5**: Support email copy option for messages:
  - Sender can choose to send email copy when sending message
  - Email copy sent to recipient's registered email address
  - Email includes message content and context
  - Email notifications for new messages (optional, configurable)
- **FR-10.6**: Email notification preferences:
  - Per-user email notification settings
  - Options: immediate, digest, disabled
  - Email templates for different message types

#### 2.11.3 Message Management
- **FR-11.7**: Message operations:
  - Mark messages as read/unread
  - Delete messages (soft delete, preserve history)
  - Search messages by content, sender, date
  - Filter messages by conversation thread
  - Archive conversations

### 2.12 Administrator Management

#### 2.12.1 Admin Account Management
- **FR-11.1**: Support administrator account creation and management
- **FR-11.2**: Admin accounts shall have:
  - Unique admin identifier
  - Authentication credentials (username/email, password)
  - Admin profile information
  - Account status (active, inactive)
  - Permission levels (super admin, admin, limited admin)
- **FR-11.3**: Admin account creation:
  - Created by existing super administrators
  - Requires secure setup process
  - Can be preset with first-time password change

#### 2.12.2 Account Management Capabilities
- **FR-11.4**: Administrators shall be able to:
  - Create student accounts (preset accounts)
  - Create tutor accounts
  - Convert existing accounts to tutor accounts
  - Enable/disable any account (student, tutor, or admin)
  - Reset passwords for any account
  - View account details and activity
  - Manage account roles and permissions
- **FR-11.5**: Account enable/disable functionality:
  - Disable account: prevents login and access
  - Enable account: restores access
  - Track enable/disable history (who, when, why)
  - Preserve account data when disabled

#### 2.12.3 Course/Subject Management Capabilities
- **FR-11.6**: Administrators shall be able to:
  - Create new subjects/courses
  - Update subject configurations
  - Enable/disable subjects/courses
  - View subject statistics and usage
  - Manage subject settings and metadata
- **FR-11.7**: Subject enable/disable functionality:
  - Disable subject: hides from students, preserves data
  - Enable subject: makes available to students
  - Track enable/disable history
  - Prevent deletion of subjects with existing data

#### 2.12.4 Student-Tutor Assignment Management
- **FR-12.8**: Administrators shall be able to:
  - Assign students to tutors
  - Reassign students to different tutors
  - Remove student-tutor assignments
  - View all assignments and team compositions
  - Bulk assignment operations

#### 2.12.5 Application Management
- **FR-12.9**: Administrators shall have access to:
  - System-wide statistics and analytics
  - User activity monitoring
  - System configuration settings
  - Audit logs and activity history
  - Backup and maintenance operations

### 2.13 Tenant Management

#### 2.13.1 Tenant Concept
- **FR-13.1**: Support multi-tenant architecture where each tenant represents an educational institution
- **FR-13.2**: Tenant isolation requirements:
  - Each tenant has isolated data (students, tutors, sessions, progress)
  - Students and tutors belong to a single tenant
  - Data access is scoped to tenant (tenant isolation)
  - Cross-tenant data access is prevented
- **FR-13.3**: Tenant identification:
  - Each tenant has unique identifier (tenant_id)
  - Tenant code/name for display
  - Domain-based tenant resolution (primary method)
- **FR-13.4**: Domain-based tenant identification:
  - Each tenant can be associated with one or more domains
  - Domain is passed as parameter in initial API call (e.g., login, registration)
  - Tenant is resolved based on the domain parameter
  - All tenant-related content is presented based on the resolved tenant
  - Domain must be validated and mapped to a tenant before processing requests
  - Invalid or unmapped domains result in error response

#### 2.13.2 Tenant Configuration
- **FR-13.5**: Tenant configuration shall include:
  - Tenant name (institution name)
  - Tenant code (unique identifier)
  - One or more associated domains (required)
  - Primary domain (default domain for the tenant)
  - Contact information
  - Status (active, inactive, suspended)
  - Settings (customizations, branding, features)
  - Subscription/license information
- **FR-13.6**: Domain management:
  - Each tenant must have at least one domain
  - Domains must be unique across all tenants
  - Primary domain is used as default when multiple domains exist
  - Additional domains can be added/removed by system admin
  - Domain format validation (e.g., example.com, subdomain.example.com)
  - Domain status (active, inactive)
- **FR-13.7**: Domain-to-tenant mapping:
  - System maintains domain-to-tenant mapping
  - Fast lookup mechanism for domain resolution
  - Cache domain mappings for performance
  - Support wildcard domains (optional, future enhancement)
- **FR-13.8**: Tenant lifecycle:
  - Create tenant (by system admin) with at least one domain
  - Activate/deactivate tenant
  - Suspend tenant (preserve data, restrict access)
  - Archive tenant (historical data only)
  - Add/remove domains for existing tenants

#### 2.13.3 Domain-Based Tenant Resolution
- **FR-13.9**: Domain parameter handling:
  - Domain parameter required in initial/unauthenticated API calls:
    - Login
    - Registration
    - Password reset
    - Public endpoints
    - Tenant resolution
  - Domain optional for authenticated requests (tenant_id in JWT token)
  - Domain can be passed as:
    - Query parameter: `?domain=example.com`
    - Header: `X-Tenant-Domain: example.com`
    - Path parameter: `/api/v1/{domain}/...` (optional pattern)
  - Domain is validated against tenant domain mappings
  - Invalid or inactive domains return appropriate error
- **FR-13.10**: Tenant resolution process:
  - Extract domain from request (parameter, header, or path)
  - Lookup tenant_id from domain-to-tenant mapping
  - Validate tenant is active
  - Set tenant context for the request
  - All subsequent operations use resolved tenant_id
  - Tenant context persists for the session/request
  - For authenticated requests, tenant_id from JWT token takes precedence over domain parameter
- **FR-13.11**: Domain validation:
  - Validate domain format (DNS-compliant)
  - Check domain exists in system
  - Verify domain is active and associated with active tenant
  - Return clear error messages for invalid domains
  - Support domain aliases (optional)
- **FR-13.12**: Authenticated request handling:
  - Authenticated requests include tenant_id in JWT token
  - Domain parameter is optional for authenticated requests
  - If domain is provided in authenticated request, validate it matches token's tenant_id
  - Tenant context from token is used for all data operations

#### 2.13.4 Tenant-Level Administration
- **FR-13.13**: Support tenant-level administrators:
  - Tenant admins belong to a specific tenant
  - Tenant admins can only manage resources within their tenant
  - Tenant admins can create/manage student and tutor accounts (within tenant)
  - Tenant admins cannot access other tenants' data
  - Tenant admins cannot manage system-level settings
- **FR-13.14**: Tenant admin capabilities:
  - Create student accounts (within tenant)
  - Create tutor accounts (within tenant)
  - Assign students to tutors (within tenant)
  - Enable/disable student and tutor accounts (within tenant)
  - View tenant-level statistics and reports
  - Manage tenant-specific settings

#### 2.13.5 System-Level Administration
- **FR-13.15**: Support system-level administrators:
  - System admins have access across all tenants
  - System admins can create/manage tenants
  - System admins can create tenant admin accounts
  - System admins can manage all accounts (students, tutors, tenant admins)
  - System admins can manage system-wide subjects/courses
  - System admins can view system-wide statistics

### 2.14 Role-Based Access Control

#### 2.14.1 User Roles
- **FR-14.1**: Support four primary roles:
  - Student: Can take quizzes, view own progress, message tutor (within tenant)
  - Tutor: Can view assigned students' progress, message students, respond to messages (within tenant)
  - Tenant Admin: Manage accounts and courses within their tenant only
  - System Admin: Full system access, manage tenants, all accounts, system-wide courses
- **FR-14.2**: Role-based permissions:
  - Each role has specific API endpoint access
  - Role validation on all protected endpoints
  - Hierarchical permissions (system admin > tenant admin > tutor > student)
  - Tenant-scoped permissions for tenant admin, tutor, and student

#### 2.14.2 Access Control
- **FR-14.3**: Enforce access control:
  - Students can only access their own data within their tenant
  - Tutors can only access their assigned students' data within their tenant
  - Tenant admins can only access data within their tenant
  - System admins can access all data across all tenants
  - Prevent unauthorized cross-tenant data access
  - Audit access attempts with tenant context
- **FR-14.4**: Tenant isolation enforcement:
  - All data queries must include tenant_id filter
  - API responses must only include tenant-scoped data
  - Prevent tenant_id manipulation in API requests
  - Validate tenant membership for all operations

---

## 3. API Endpoints

### 3.1 Question Endpoints

#### 3.1.1 Generate Question
```
POST /api/v1/questions/generate
```
**Request Body:**
```json
{
  "subject_id": "uuid",  // Or use subject_code: "string"
  "grade_level": 6-12,  // Required if subject supports grade levels, optional otherwise
  "difficulty": "beginner|intermediate|advanced",
  "topic": "string",  // Optional: specific topic/curriculum area
  "question_type": "multiple_choice|short_answer|code_completion|code_writing|fill_blank|true_false",
  "session_id": "string"  // Optional: link to quiz session
}
```

**Response:**
```json
{
  "question_id": "uuid",
  "question_text": "string",
  "question_type": "string",
  "options": ["array"],  // For multiple choice
  "metadata": {
    "difficulty": "string",
    "estimated_time": "integer",
    "learning_objectives": ["array"],
    "topic": "string"
  },
  "session_id": "string"
}
```

#### 3.1.2 Get Question
```
GET /api/v1/questions/{question_id}
```

#### 3.1.3 Get Question Narrative
```
GET /api/v1/questions/{question_id}/narrative
```

**Response:**
```json
{
  "question_id": "uuid",
  "narrative": "string",
  "explanation": {
    "concept": "string",
    "steps": ["array"],
    "why_correct": "string",
    "common_mistakes": ["array"],
    "related_concepts": ["array"]
  }
}
```

### 3.2 Answer Endpoints

#### 3.2.1 Submit Answer
```
POST /api/v1/questions/{question_id}/answer
```

**Request Body:**
```json
{
  "answer": "string|object",  // Text, code, or selected option(s)
  "student_id": "string",
  "session_id": "string",
  "time_spent": "integer",  // seconds
  "hints_used": ["array"]  // Optional: list of hint IDs used
}
```

**Response:**
```json
{
  "question_id": "uuid",
  "correct": "boolean",
  "score": "float",
  "max_score": "float",
  "feedback": "string",
  "correct_answer": "string",  // Revealed after submission
  "explanation": "string",  // Optional detailed explanation
  "areas_correct": ["array"],  // For partial credit
  "areas_incorrect": ["array"]
}
```

#### 3.2.2 Validate Answer (Pre-submission)
```
POST /api/v1/questions/{question_id}/validate
```
Similar to submit answer but doesn't record the attempt (for practice mode).

### 3.3 Hint Endpoints

#### 3.3.1 Get Hint
```
POST /api/v1/questions/{question_id}/hint
```

**Request Body:**
```json
{
  "hint_level": "integer",  // 1-4, optional (defaults to next available)
  "student_id": "string",
  "previous_attempts": ["array"],  // Optional: previous answer attempts
  "hints_already_shown": ["array"]  // Optional: previously shown hints
}
```

**Response:**
```json
{
  "hint_id": "uuid",
  "hint_level": "integer",
  "hint_text": "string",
  "remaining_hints": "integer"
}
```

### 3.4 Session Endpoints

#### 3.4.1 Create Quiz Session
```
POST /api/v1/sessions
```

**Request Body:**
```json
{
  "student_id": "string",
  "subject_id": "uuid",  // Or use subject_code: "string"
  "grade_level": "integer",  // Required if subject supports grade levels
  "difficulty": "string",
  "num_questions": "integer",
  "topics": ["array"],  // Optional
  "time_limit": "integer"  // Optional: seconds
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "questions": ["array"],  // Array of question IDs
  "created_at": "timestamp",
  "expires_at": "timestamp"
}
```

#### 3.4.2 Get Session Status
```
GET /api/v1/sessions/{session_id}
```

**Response:**
```json
{
  "session_id": "uuid",
  "status": "in_progress|completed|expired",
  "current_question": "integer",
  "total_questions": "integer",
  "score": "float",
  "max_score": "float",
  "time_elapsed": "integer",
  "questions_answered": "integer"
}
```

#### 3.4.3 Get Session Results
```
GET /api/v1/sessions/{session_id}/results
```

### 3.5 Progress Endpoints

#### 3.5.1 Get Student Progress
```
GET /api/v1/students/{student_id}/progress
```

**Query Parameters:**
- `subject` (optional)
- `grade_level` (optional)
- `time_range` (optional: last_week, last_month, all_time)

**Response:**
```json
{
  "student_id": "string",
  "overall_stats": {
    "total_questions": "integer",
    "correct_answers": "integer",
    "accuracy": "float",
    "average_score": "float"
  },
  "by_subject": {
    "math": { /* stats */ },
    "english": { /* stats */ },
    "python": { /* stats */ }
  },
  "by_topic": { /* topic-level stats */ },
  "trends": {
    "improvement_rate": "float",
    "weak_areas": ["array"],
    "strong_areas": ["array"]
  }
}
```

#### 3.5.2 Get Performance Analytics
```
GET /api/v1/students/{student_id}/analytics
```

### 3.6 Authentication Endpoints

#### 3.6.1 Student Login
```
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "username": "string",  // Username or email
  "password": "string",
  "domain": "string"  // Required: domain to identify tenant
}
```

**Alternative (Domain as Query Parameter):**
```
POST /api/v1/auth/login?domain=example.com
```

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Alternative (Domain as Header):**
```
POST /api/v1/auth/login
Headers:
  X-Tenant-Domain: example.com
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "Bearer",
  "expires_in": "integer",  // seconds
  "refresh_token": "string",  // Optional
  "user": {
    "user_id": "uuid",
    "username": "string",
    "email": "string",
    "role": "student|tutor|tenant_admin|system_admin",
    "tenant_id": "uuid",  // Null for system_admin
    "grade_level": "integer",  // For students
    "requires_password_change": "boolean",  // True for first-time login
    "account_status": "pending_activation|active|inactive|locked"
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid credentials
- `403 Forbidden`: Account locked or inactive
- `400 Bad Request`: Account requires password change

#### 3.6.2 Student Logout
```
POST /api/v1/auth/logout
```

**Headers:**
- `Authorization: Bearer {token}`

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

#### 3.6.3 Refresh Token
```
POST /api/v1/auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "Bearer",
  "expires_in": "integer"
}
```

### 3.7 User Management Endpoints

#### 3.7.1 Create Preset Student Account
```
POST /api/v1/admin/students
```

**Headers:**
- `Authorization: Bearer {admin_token}`

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "grade_level": "integer",  // Optional
  "send_activation_email": "boolean"  // Optional: send email with temp password
}
```

**Response:**
```json
{
  "student_id": "uuid",
  "username": "string",
  "email": "string",
  "account_status": "pending_activation",
  "temporary_password": "string",  // Only if send_activation_email is false
  "created_at": "timestamp"
}
```

#### 3.7.2 Get Student Account
```
GET /api/v1/students/{student_id}
```

**Headers:**
- `Authorization: Bearer {token}` (student's own token or admin token)

**Response:**
```json
{
  "student_id": "uuid",
  "username": "string",
  "email": "string",
  "grade_level": "integer",
  "account_status": "string",
  "created_at": "timestamp",
  "last_login": "timestamp",
  "requires_password_change": "boolean"
}
```

#### 3.7.3 Change Password (First Login)
```
POST /api/v1/auth/change-password
```

**Headers:**
- `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "current_password": "string",  // Required for existing passwords, optional for first-time
  "new_password": "string",
  "confirm_password": "string"
}
```

**Response:**
```json
{
  "message": "Password changed successfully",
  "requires_password_change": "false"
}
```

**Error Responses:**
- `400 Bad Request`: Password doesn't meet requirements or doesn't match
- `401 Unauthorized`: Current password incorrect
- `403 Forbidden`: Token expired or invalid

#### 3.7.4 Update Password
```
POST /api/v1/auth/update-password
```

**Headers:**
- `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "current_password": "string",
  "new_password": "string",
  "confirm_password": "string"
}
```

**Response:**
```json
{
  "message": "Password updated successfully"
}
```

#### 3.7.5 Request Password Reset (Forgot Password)
```
POST /api/v1/auth/forgot-password
```

**Request Body:**
```json
{
  "email": "string"
}
```

**Response:**
```json
{
  "message": "If the email exists, a one-time passcode has been sent",
  "otp_expires_in": "integer"  // seconds
}
```

**Note:** Always return success message (even if email doesn't exist) to prevent email enumeration attacks.

#### 3.7.6 Verify OTP and Reset Password
```
POST /api/v1/auth/reset-password
```

**Request Body:**
```json
{
  "email": "string",
  "otp": "string",  // One-time passcode
  "new_password": "string",
  "confirm_password": "string"
}
```

**Response:**
```json
{
  "message": "Password reset successfully",
  "access_token": "string",  // Optional: auto-login after reset
  "token_type": "Bearer"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid or expired OTP
- `404 Not Found`: Email not found
- `429 Too Many Requests`: Too many OTP requests

#### 3.7.7 Resend OTP
```
POST /api/v1/auth/resend-otp
```

**Request Body:**
```json
{
  "email": "string"
}
```

**Response:**
```json
{
  "message": "One-time passcode resent",
  "otp_expires_in": "integer"
}
```

**Note:** Rate limited to prevent abuse.

### 3.8 Subject Management Endpoints

#### 3.8.1 List Subjects
```
GET /api/v1/subjects
```

**Query Parameters:**
- `status` (optional: active, inactive, all)
- `grade_level` (optional: filter by grade level support)
- `type` (optional: filter by subject type)

**Response:**
```json
{
  "subjects": [
    {
      "subject_id": "uuid",
      "subject_code": "string",
      "name": "string",
      "description": "string",
      "type": "string",
      "grade_levels": ["array"],  // [6, 7, 8, 9, 10, 11, 12] or null for all
      "status": "active|inactive|archived",
      "supported_question_types": ["array"],
      "answer_validation_method": "string",
      "created_at": "timestamp",
      "updated_at": "timestamp"
    }
  ],
  "total": "integer"
}
```

#### 3.8.2 Get Subject
```
GET /api/v1/subjects/{subject_id}
```

**Response:**
```json
{
  "subject_id": "uuid",
  "subject_code": "string",
  "name": "string",
  "description": "string",
  "type": "string",
  "grade_levels": ["array"],
  "status": "string",
  "supported_question_types": ["array"],
  "answer_validation_method": "string",
  "settings": {
    "default_difficulty": "string",
    "ai_prompt_template": "string",  // Optional
    "validation_rules": "object",  // Optional
    "hint_strategy": "string"  // Optional
  },
  "metadata": {
    "curriculum": "string",
    "learning_objectives": ["array"],
    "icon_url": "string",  // Optional
    "category": "string"
  },
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

#### 3.8.3 Create Subject
```
POST /api/v1/admin/subjects
```

**Headers:**
- `Authorization: Bearer {admin_token}`

**Request Body:**
```json
{
  "subject_code": "string",  // Unique identifier (e.g., "chemistry", "history")
  "name": "string",  // Display name
  "description": "string",
  "type": "academic|programming|language|science|other",
  "grade_levels": ["array"],  // [6, 7, 8, ...] or null for all levels
  "supported_question_types": ["array"],  // ["multiple_choice", "short_answer", ...]
  "answer_validation_method": "ai_semantic|code_execution|exact_match|ai_structured",
  "settings": {
    "default_difficulty": "beginner|intermediate|advanced",
    "ai_prompt_template": "string",  // Optional: custom prompt for question generation
    "validation_rules": "object",  // Optional: subject-specific validation rules
    "hint_strategy": "progressive|direct|contextual"  // Optional
  },
  "metadata": {
    "curriculum": "string",  // Optional
    "learning_objectives": ["array"],  // Optional
    "icon_url": "string",  // Optional
    "category": "string"  // Optional
  }
}
```

**Response:**
```json
{
  "subject_id": "uuid",
  "subject_code": "string",
  "name": "string",
  "status": "active",
  "created_at": "timestamp"
}
```

#### 3.8.4 Update Subject
```
PUT /api/v1/admin/subjects/{subject_id}
```

**Headers:**
- `Authorization: Bearer {admin_token}`

**Request Body:**
```json
{
  "name": "string",  // Optional
  "description": "string",  // Optional
  "grade_levels": ["array"],  // Optional
  "status": "active|inactive|archived",  // Optional
  "supported_question_types": ["array"],  // Optional
  "settings": "object",  // Optional
  "metadata": "object"  // Optional
}
```

**Response:**
```json
{
  "subject_id": "uuid",
  "subject_code": "string",
  "name": "string",
  "updated_at": "timestamp"
}
```

#### 3.8.5 Deactivate Subject
```
POST /api/v1/admin/subjects/{subject_id}/deactivate
```

**Headers:**
- `Authorization: Bearer {admin_token}`

**Response:**
```json
{
  "subject_id": "uuid",
  "status": "inactive",
  "message": "Subject deactivated. Existing data preserved."
}
```

**Note:** Cannot deactivate if subject has active quiz sessions.

#### 3.8.6 Get Subject Statistics
```
GET /api/v1/admin/subjects/{subject_id}/statistics
```

**Headers:**
- `Authorization: Bearer {admin_token}`

**Response:**
```json
{
  "subject_id": "uuid",
  "subject_code": "string",
  "total_questions": "integer",
  "total_sessions": "integer",
  "total_students": "integer",
  "average_score": "float",
  "questions_by_difficulty": {
    "beginner": "integer",
    "intermediate": "integer",
    "advanced": "integer"
  }
}
```

### 3.9 Competition Endpoints

#### 3.9.1 List Competitions
```
GET /api/v1/competitions
```

**Query Parameters:**
- `subject_id` (optional: filter by subject)
- `status` (optional: upcoming, active, ended, cancelled, all)
- `tenant_id` (optional: filter by tenant, for system admin)

**Response:**
```json
{
  "competitions": [
    {
      "competition_id": "uuid",
      "name": "string",
      "subject_id": "uuid",
      "subject_code": "string",
      "status": "upcoming|active|ended|cancelled",
      "start_date": "timestamp",
      "end_date": "timestamp",
      "registration_start": "timestamp",
      "registration_end": "timestamp",
      "participant_count": "integer",
      "created_at": "timestamp"
    }
  ],
  "total": "integer"
}
```

#### 3.9.2 Get Competition
```
GET /api/v1/competitions/{competition_id}
```

**Response:**
```json
{
  "competition_id": "uuid",
  "tenant_id": "uuid",
  "name": "string",
  "description": "string",
  "subject_id": "uuid",
  "subject_code": "string",
  "status": "upcoming|active|ended|cancelled",
  "start_date": "timestamp",
  "end_date": "timestamp",
  "registration_start": "timestamp",
  "registration_end": "timestamp",
  "rules": {
    "time_limit": "integer",
    "num_questions": "integer",
    "difficulty": "string",
    "allowed_question_types": ["array"],
    "max_attempts": "integer",
    "scoring_rules": "object",
    "hints_allowed": "boolean",
    "narratives_allowed": "boolean"
  },
  "eligibility": {
    "grade_levels": ["array"],
    "tenant_restrictions": ["array"],
    "minimum_requirements": "object"
  },
  "visibility": "public|private|tenant_specific",
  "participant_count": "integer",
  "max_participants": "integer",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

#### 3.9.3 Create Competition
```
POST /api/v1/admin/competitions
```

**Headers:**
- `Authorization: Bearer {admin_token}`

**Request Body:**
```json
{
  "name": "string",
  "description": "string",
  "subject_id": "uuid",
  "start_date": "timestamp",
  "end_date": "timestamp",
  "registration_start": "timestamp",
  "registration_end": "timestamp",
  "rules": {
    "time_limit": "integer",
    "num_questions": "integer",
    "difficulty": "beginner|intermediate|advanced",
    "allowed_question_types": ["array"],
    "max_attempts": "integer",
    "scoring_rules": "object",
    "hints_allowed": "boolean",
    "narratives_allowed": "boolean"
  },
  "eligibility": {
    "grade_levels": ["array"],
    "tenant_restrictions": ["array"],
    "minimum_requirements": "object"
  },
  "visibility": "public|private|tenant_specific",
  "max_participants": "integer"
}
```

**Response:**
```json
{
  "competition_id": "uuid",
  "name": "string",
  "status": "upcoming",
  "created_at": "timestamp"
}
```

#### 3.9.4 Update Competition
```
PUT /api/v1/admin/competitions/{competition_id}
```

**Headers:**
- `Authorization: Bearer {admin_token}`

**Request Body:**
```json
{
  "name": "string",
  "description": "string",
  "start_date": "timestamp",
  "end_date": "timestamp",
  "registration_start": "timestamp",
  "registration_end": "timestamp",
  "rules": "object",
  "eligibility": "object",
  "visibility": "string",
  "max_participants": "integer"
}
```

**Note:** Cannot update competition after it has started.

#### 3.9.5 Cancel Competition
```
POST /api/v1/admin/competitions/{competition_id}/cancel
```

**Headers:**
- `Authorization: Bearer {admin_token}`

**Request Body:**
```json
{
  "reason": "string"
}
```

**Response:**
```json
{
  "competition_id": "uuid",
  "status": "cancelled",
  "cancelled_at": "timestamp",
  "reason": "string"
}
```

#### 3.9.6 Register for Competition
```
POST /api/v1/competitions/{competition_id}/register
```

**Request Body:**
```json
{}
```

**Response:**
```json
{
  "registration_id": "uuid",
  "competition_id": "uuid",
  "student_id": "uuid",
  "status": "registered",
  "registered_at": "timestamp"
}
```

**Error Responses:**
- `400 Bad Request`: Registration period closed, already registered, not eligible
- `403 Forbidden`: Maximum participants reached

#### 3.9.7 Cancel Registration
```
DELETE /api/v1/competitions/{competition_id}/register
```

**Response:**
```json
{
  "registration_id": "uuid",
  "status": "cancelled",
  "cancelled_at": "timestamp"
}
```

#### 3.9.8 Get Competition Leaderboard
```
GET /api/v1/competitions/{competition_id}/leaderboard
```

**Query Parameters:**
- `type` (optional: real_time, final, default: real_time for active, final for ended)
- `limit` (optional: default 100)
- `offset` (optional: default 0)
- `grade_level` (optional: filter by grade level)

**Response:**
```json
{
  "competition_id": "uuid",
  "type": "real_time|final",
  "last_updated": "timestamp",
  "leaderboard": [
    {
      "rank": "integer",
      "student_id": "uuid",
      "student_name": "string",
      "score": "float",
      "max_score": "float",
      "accuracy": "float",
      "completion_time": "integer",
      "questions_answered": "integer",
      "completed_at": "timestamp"
    }
  ],
  "total_participants": "integer",
  "user_rank": "integer",
  "user_position": "object"
}
```

#### 3.9.9 Start Competition Session
```
POST /api/v1/competitions/{competition_id}/start
```

**Request Body:**
```json
{}
```

**Response:**
```json
{
  "competition_session_id": "uuid",
  "competition_id": "uuid",
  "student_id": "uuid",
  "session_id": "uuid",
  "started_at": "timestamp",
  "time_limit": "integer",
  "questions": ["array"]
}
```

**Error Responses:**
- `400 Bad Request`: Competition not active, already started, not registered
- `403 Forbidden`: Competition time window expired

#### 3.9.10 Get Competition Results
```
GET /api/v1/competitions/{competition_id}/results
```

**Response:**
```json
{
  "competition_id": "uuid",
  "name": "string",
  "status": "ended",
  "ended_at": "timestamp",
  "total_participants": "integer",
  "winners": [
    {
      "rank": "integer",
      "student_id": "uuid",
      "student_name": "string",
      "score": "float",
      "max_score": "float",
      "accuracy": "float"
    }
  ],
  "statistics": {
    "average_score": "float",
    "highest_score": "float",
    "participation_rate": "float",
    "completion_rate": "float"
  },
  "leaderboard": ["array"]
}
```

#### 3.9.11 Get Student Competition Result
```
GET /api/v1/competitions/{competition_id}/results/{student_id}
```

**Response:**
```json
{
  "competition_id": "uuid",
  "student_id": "uuid",
  "rank": "integer",
  "score": "float",
  "max_score": "float",
  "accuracy": "float",
  "questions_answered": "integer",
  "completion_time": "integer",
  "completed_at": "timestamp",
  "session_details": "object"
}
```

#### 3.9.12 Get Competition Statistics
```
GET /api/v1/admin/competitions/{competition_id}/statistics
```

**Headers:**
- `Authorization: Bearer {admin_token}`

**Response:**
```json
{
  "competition_id": "uuid",
  "name": "string",
  "status": "string",
  "registrations": {
    "total": "integer",
    "confirmed": "integer",
    "cancelled": "integer"
  },
  "participation": {
    "started": "integer",
    "completed": "integer",
    "completion_rate": "float"
  },
  "performance": {
    "average_score": "float",
    "highest_score": "float",
    "lowest_score": "float",
    "median_score": "float"
  },
  "timing": {
    "average_completion_time": "integer",
    "fastest_completion": "integer",
    "slowest_completion": "integer"
  }
}
```

### 3.10 Tutor Management Endpoints

#### 3.9.1 List Tutors
```
GET /api/v1/tutors
```

**Headers:**
- `Authorization: Bearer {admin_token}`

**Query Parameters:**
- `status` (optional: active, inactive, all)
- `search` (optional: search by name, email)

**Response:**
```json
{
  "tutors": [
    {
      "tutor_id": "uuid",
      "username": "string",
      "email": "string",
      "name": "string",
      "status": "active|inactive|suspended",
      "student_count": "integer",
      "created_at": "timestamp"
    }
  ],
  "total": "integer"
}
```

#### 3.9.2 Get Tutor
```
GET /api/v1/tutors/{tutor_id}
```

**Headers:**
- `Authorization: Bearer {tutor_token|admin_token}`

**Response:**
```json
{
  "tutor_id": "uuid",
  "username": "string",
  "email": "string",
  "name": "string",
  "status": "string",
  "profile": {
    "bio": "string",
    "specializations": ["array"],
    "contact_info": "object"
  },
  "created_at": "timestamp",
  "last_login": "timestamp"
}
```

#### 3.9.3 Create Tutor Account
```
POST /api/v1/admin/tutors
```

**Headers:**
- `Authorization: Bearer {admin_token}`

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "name": "string",
  "send_activation_email": "boolean"
}
```

**Response:**
```json
{
  "tutor_id": "uuid",
  "username": "string",
  "email": "string",
  "status": "pending_activation",
  "temporary_password": "string",  // Only if send_activation_email is false
  "created_at": "timestamp"
}
```

#### 3.9.4 Convert Account to Tutor
```
POST /api/v1/admin/accounts/{account_id}/assign-tutor-role
```

**Headers:**
- `Authorization: Bearer {admin_token}`

**Response:**
```json
{
  "account_id": "uuid",
  "tutor_id": "uuid",
  "role": "tutor",
  "message": "Account successfully assigned tutor role"
}
```

#### 3.9.5 Get Tutor's Students (Team)
```
GET /api/v1/tutors/{tutor_id}/students
```

**Headers:**
- `Authorization: Bearer {tutor_token|admin_token}`

**Response:**
```json
{
  "tutor_id": "uuid",
  "students": [
    {
      "student_id": "uuid",
      "username": "string",
      "name": "string",
      "email": "string",
      "grade_level": "integer",
      "assigned_at": "timestamp",
      "progress_summary": {
        "total_questions": "integer",
        "accuracy": "float",
        "average_score": "float"
      }
    }
  ],
  "total": "integer"
}
```

#### 3.9.6 Get Student Progress (Tutor View)
```
GET /api/v1/tutors/{tutor_id}/students/{student_id}/progress
```

**Headers:**
- `Authorization: Bearer {tutor_token|admin_token}`

**Response:**
```json
{
  "student_id": "uuid",
  "student_name": "string",
  "overall_stats": {
    "total_questions": "integer",
    "correct_answers": "integer",
    "accuracy": "float",
    "average_score": "float"
  },
  "by_subject": {
    "math": { /* stats */ },
    "english": { /* stats */ }
  },
  "recent_sessions": ["array"],
  "weak_areas": ["array"],
  "strong_areas": ["array"]
}
```

### 3.11 Messaging Endpoints

#### 3.10.1 Send Message
```
POST /api/v1/messages
```

**Headers:**
- `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "recipient_id": "uuid",  // Tutor ID if sender is student, Student ID if sender is tutor
  "content": "string",
  "send_email_copy": "boolean",  // Optional: default false
  "subject_reference": "uuid",  // Optional: reference to subject
  "question_reference": "uuid"  // Optional: reference to question
}
```

**Response:**
```json
{
  "message_id": "uuid",
  "sender_id": "uuid",
  "recipient_id": "uuid",
  "content": "string",
  "status": "sent",
  "email_sent": "boolean",
  "created_at": "timestamp"
}
```

#### 3.10.2 Get Messages (Conversation)
```
GET /api/v1/messages
```

**Headers:**
- `Authorization: Bearer {token}`

**Query Parameters:**
- `conversation_with` (optional: user_id to filter conversation)
- `unread_only` (optional: boolean)
- `limit` (optional: default 50)
- `offset` (optional: default 0)

**Response:**
```json
{
  "messages": [
    {
      "message_id": "uuid",
      "sender_id": "uuid",
      "sender_name": "string",
      "sender_role": "student|tutor",
      "recipient_id": "uuid",
      "recipient_name": "string",
      "content": "string",
      "status": "sent|delivered|read",
      "read_at": "timestamp",
      "created_at": "timestamp"
    }
  ],
  "total": "integer",
  "unread_count": "integer"
}
```

#### 3.10.3 Get Conversation Thread
```
GET /api/v1/messages/conversations/{user_id}
```

**Headers:**
- `Authorization: Bearer {token}`

**Query Parameters:**
- `limit` (optional)
- `offset` (optional)

**Response:**
```json
{
  "conversation_with": {
    "user_id": "uuid",
    "name": "string",
    "role": "student|tutor"
  },
  "messages": ["array"],
  "total": "integer"
}
```

#### 3.10.4 Mark Message as Read
```
PUT /api/v1/messages/{message_id}/read
```

**Headers:**
- `Authorization: Bearer {token}`

**Response:**
```json
{
  "message_id": "uuid",
  "status": "read",
  "read_at": "timestamp"
}
```

#### 3.10.5 Mark Conversation as Read
```
PUT /api/v1/messages/conversations/{user_id}/read
```

**Headers:**
- `Authorization: Bearer {token}`

**Response:**
```json
{
  "conversation_with": "uuid",
  "messages_marked_read": "integer"
}
```

#### 3.10.6 Delete Message
```
DELETE /api/v1/messages/{message_id}
```

**Headers:**
- `Authorization: Bearer {token}`

**Response:**
```json
{
  "message_id": "uuid",
  "status": "deleted",
  "deleted_at": "timestamp"
}
```

### 3.12 Tenant Management Endpoints

#### 3.11.1 List Tenants
```
GET /api/v1/system/tenants
```

**Headers:**
- `Authorization: Bearer {system_admin_token}`

**Query Parameters:**
- `status` (optional: active, inactive, suspended, all)
- `search` (optional: search by name, code)

**Response:**
```json
{
  "tenants": [
    {
      "tenant_id": "uuid",
      "tenant_code": "string",
      "name": "string",
      "status": "active|inactive|suspended",
      "student_count": "integer",
      "tutor_count": "integer",
      "created_at": "timestamp"
    }
  ],
  "total": "integer"
}
```

#### 3.11.2 Get Tenant
```
GET /api/v1/system/tenants/{tenant_id}
```

**Headers:**
- `Authorization: Bearer {system_admin_token|tenant_admin_token}`

**Response:**
```json
{
  "tenant_id": "uuid",
  "tenant_code": "string",
  "name": "string",
  "description": "string",
  "status": "active|inactive|suspended",
  "domains": [
    {
      "domain_id": "uuid",
      "domain": "string",
      "is_primary": "boolean",
      "status": "active|inactive"
    }
  ],
  "primary_domain": "string",
  "contact_info": {
    "email": "string",
    "phone": "string",
    "address": "object"
  },
  "settings": {
    "custom_branding": "object",
    "features": ["array"]
  },
  "statistics": {
    "student_count": "integer",
    "tutor_count": "integer",
    "tenant_admin_count": "integer",
    "total_sessions": "integer"
  },
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

#### 3.11.3 Create Tenant
```
POST /api/v1/system/tenants
```

**Headers:**
- `Authorization: Bearer {system_admin_token}`

**Request Body:**
```json
{
  "tenant_code": "string",  // Unique identifier
  "name": "string",  // Institution name
  "description": "string",
  "domains": ["array"],  // Required: at least one domain, e.g., ["example.com", "www.example.com"]
  "primary_domain": "string",  // Required: primary domain (must be in domains array)
  "contact_info": {
    "email": "string",
    "phone": "string",
    "address": "object"
  },
  "settings": {
    "custom_branding": "object",
    "features": ["array"]
  }
}
```

**Response:**
```json
{
  "tenant_id": "uuid",
  "tenant_code": "string",
  "name": "string",
  "status": "active",
  "created_at": "timestamp"
}
```

#### 3.11.4 Update Tenant
```
PUT /api/v1/system/tenants/{tenant_id}
```

**Headers:**
- `Authorization: Bearer {system_admin_token}`

**Request Body:**
```json
{
  "name": "string",  // Optional
  "description": "string",  // Optional
  "contact_info": "object",  // Optional
  "settings": "object"  // Optional
}
```

**Response:**
```json
{
  "tenant_id": "uuid",
  "tenant_code": "string",
  "name": "string",
  "updated_at": "timestamp"
}
```

#### 3.11.5 Enable/Disable Tenant
```
PUT /api/v1/system/tenants/{tenant_id}/status
```

**Headers:**
- `Authorization: Bearer {system_admin_token}`

**Request Body:**
```json
{
  "status": "active|inactive|suspended",
  "reason": "string"  // Optional
}
```

**Response:**
```json
{
  "tenant_id": "uuid",
  "status": "active|inactive|suspended",
  "updated_at": "timestamp",
  "updated_by": "uuid"
}
```

#### 3.11.6 Get Tenant Statistics
```
GET /api/v1/system/tenants/{tenant_id}/statistics
```

**Headers:**
- `Authorization: Bearer {system_admin_token|tenant_admin_token}`

**Response:**
```json
{
  "tenant_id": "uuid",
  "tenant_code": "string",
  "users": {
    "total_students": "integer",
    "total_tutors": "integer",
    "total_tenant_admins": "integer",
    "active_accounts": "integer"
  },
  "activity": {
    "total_sessions": "integer",
    "total_questions": "integer",
    "total_messages": "integer"
  },
  "performance": {
    "average_score": "float",
    "completion_rate": "float"
  }
}
```

#### 3.11.7 Add Domain to Tenant
```
POST /api/v1/system/tenants/{tenant_id}/domains
```

**Headers:**
- `Authorization: Bearer {system_admin_token}`

**Request Body:**
```json
{
  "domain": "string",  // e.g., "newdomain.com"
  "is_primary": "boolean"  // Optional: set as primary domain
}
```

**Response:**
```json
{
  "domain_id": "uuid",
  "tenant_id": "uuid",
  "domain": "string",
  "is_primary": "boolean",
  "status": "active",
  "created_at": "timestamp"
}
```

#### 3.11.8 Remove Domain from Tenant
```
DELETE /api/v1/system/tenants/{tenant_id}/domains/{domain_id}
```

**Headers:**
- `Authorization: Bearer {system_admin_token}`

**Response:**
```json
{
  "domain_id": "uuid",
  "status": "removed",
  "removed_at": "timestamp"
}
```

**Note:** Cannot remove domain if it's the only domain for the tenant. Cannot remove primary domain without setting another as primary first.

#### 3.11.9 Set Primary Domain
```
PUT /api/v1/system/tenants/{tenant_id}/domains/{domain_id}/primary
```

**Headers:**
- `Authorization: Bearer {system_admin_token}`

**Response:**
```json
{
  "domain_id": "uuid",
  "is_primary": "true",
  "updated_at": "timestamp"
}
```

#### 3.11.10 Resolve Tenant from Domain
```
GET /api/v1/tenant/resolve?domain=example.com
```

**Headers:**
- Optional: `Authorization: Bearer {token}` (for authenticated requests)

**Response:**
```json
{
  "domain": "string",
  "tenant_id": "uuid",
  "tenant_code": "string",
  "tenant_name": "string",
  "is_primary": "boolean",
  "tenant_status": "active|inactive|suspended",
  "domain_status": "active|inactive"
}
```

**Error Response (Invalid Domain):**
```json
{
  "error": "domain_not_found",
  "message": "The specified domain is not associated with any tenant",
  "domain": "string"
}
```

### 3.13 System Administrator Endpoints

#### 3.12.1 Create System Admin Account
```
POST /api/v1/system/admins
```

**Headers:**
- `Authorization: Bearer {system_admin_token}`

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "name": "string",
  "role": "system_admin",
  "permissions": ["array"]  // Optional: specific permissions
}
```

**Response:**
```json
{
  "admin_id": "uuid",
  "username": "string",
  "email": "string",
  "role": "string",
  "status": "pending_activation",
  "created_at": "timestamp"
}
```

#### 3.12.2 List All Accounts (System-Wide)
```
GET /api/v1/system/accounts
```

**Headers:**
- `Authorization: Bearer {system_admin_token}`

**Query Parameters:**
- `role` (optional: student, tutor, admin, all)
- `status` (optional: active, inactive, all)
- `search` (optional: search by username, email, name)

**Response:**
```json
{
  "accounts": [
    {
      "account_id": "uuid",
      "username": "string",
      "email": "string",
      "name": "string",
      "role": "student|tutor|admin",
      "status": "active|inactive|locked|pending_activation",
      "created_at": "timestamp",
      "last_login": "timestamp"
    }
  ],
  "total": "integer"
}
```

#### 3.12.3 Get Account Details (System-Wide)
```
GET /api/v1/system/accounts/{account_id}
```

**Headers:**
- `Authorization: Bearer {system_admin_token}`

**Response:**
```json
{
  "account_id": "uuid",
  "username": "string",
  "email": "string",
  "name": "string",
  "role": "string",
  "status": "string",
  "profile": "object",
  "created_at": "timestamp",
  "last_login": "timestamp",
  "activity_history": ["array"]
}
```

#### 3.12.4 Enable/Disable Account (System-Wide)
```
PUT /api/v1/system/accounts/{account_id}/status
```

**Headers:**
- `Authorization: Bearer {system_admin_token}`

**Request Body:**
```json
{
  "status": "active|inactive",
  "reason": "string"  // Optional: reason for status change
}
```

**Response:**
```json
{
  "account_id": "uuid",
  "status": "active|inactive",
  "updated_at": "timestamp",
  "updated_by": "uuid"
}
```

#### 3.12.5 Create Tenant Admin Account
```
POST /api/v1/system/tenants/{tenant_id}/admins
```

**Headers:**
- `Authorization: Bearer {system_admin_token}`

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "name": "string",
  "send_activation_email": "boolean"
}
```

**Response:**
```json
{
  "admin_id": "uuid",
  "tenant_id": "uuid",
  "username": "string",
  "email": "string",
  "role": "tenant_admin",
  "status": "pending_activation",
  "created_at": "timestamp"
}
```

### 3.14 Tenant Administrator Endpoints

#### 3.13.1 List Accounts (Within Tenant)
```
GET /api/v1/tenant/accounts
```

**Headers:**
- `Authorization: Bearer {tenant_admin_token}`

**Query Parameters:**
- `role` (optional: student, tutor, all)
- `status` (optional: active, inactive, all)
- `search` (optional: search by username, email, name)

**Response:**
```json
{
  "accounts": [
    {
      "account_id": "uuid",
      "username": "string",
      "email": "string",
      "name": "string",
      "role": "student|tutor",
      "status": "active|inactive|locked|pending_activation",
      "created_at": "timestamp",
      "last_login": "timestamp"
    }
  ],
  "total": "integer"
}
```

#### 3.13.2 Get Account Details (Within Tenant)
```
GET /api/v1/tenant/accounts/{account_id}
```

**Headers:**
- `Authorization: Bearer {tenant_admin_token}`

**Request Body:**
```json
{
  "student_id": "uuid",
  "tutor_id": "uuid"
}
```

**Response:**
```json
{
  "assignment_id": "uuid",
  "student_id": "uuid",
  "tutor_id": "uuid",
  "assigned_at": "timestamp",
  "assigned_by": "uuid"
}
```

#### 3.13.3 Create Student Account (Within Tenant)
```
POST /api/v1/tenant/students
```

**Headers:**
- `Authorization: Bearer {tenant_admin_token}`

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "grade_level": "integer",
  "send_activation_email": "boolean"
}
```

**Response:**
```json
{
  "student_id": "uuid",
  "tenant_id": "uuid",
  "username": "string",
  "email": "string",
  "status": "pending_activation",
  "created_at": "timestamp"
}
```

#### 3.13.4 Create Tutor Account (Within Tenant)
```
POST /api/v1/tenant/tutors
```

**Headers:**
- `Authorization: Bearer {tenant_admin_token}`

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "name": "string",
  "send_activation_email": "boolean"
}
```

**Response:**
```json
{
  "tutor_id": "uuid",
  "tenant_id": "uuid",
  "username": "string",
  "email": "string",
  "status": "pending_activation",
  "created_at": "timestamp"
}
```

#### 3.13.5 Enable/Disable Account (Within Tenant)
```
PUT /api/v1/tenant/accounts/{account_id}/status
```

**Headers:**
- `Authorization: Bearer {tenant_admin_token}`

**Request Body:**
```json
{
  "status": "active|inactive",
  "reason": "string"  // Optional
}
```

**Response:**
```json
{
  "account_id": "uuid",
  "status": "active|inactive",
  "updated_at": "timestamp",
  "updated_by": "uuid"
}
```

#### 3.13.6 Assign Student to Tutor (Within Tenant)
```
POST /api/v1/tenant/assignments
```

**Headers:**
- `Authorization: Bearer {tenant_admin_token}`

**Response:**
```json
{
  "assignment_id": "uuid",
  "status": "removed",
  "removed_at": "timestamp"
}
```

#### 3.13.7 Remove Student-Tutor Assignment (Within Tenant)
```
DELETE /api/v1/tenant/assignments/{assignment_id}
```

**Headers:**
- `Authorization: Bearer {tenant_admin_token}`

**Response:**
```json
{
  "assignment_id": "uuid",
  "status": "removed",
  "removed_at": "timestamp"
}
```

#### 3.13.8 Bulk Assign Students to Tutor (Within Tenant)
```
POST /api/v1/tenant/assignments/bulk
```

**Headers:**
- `Authorization: Bearer {tenant_admin_token}`

**Request Body:**
```json
{
  "tutor_id": "uuid",
  "student_ids": ["array"]
}
```

**Response:**
```json
{
  "tutor_id": "uuid",
  "assigned_count": "integer",
  "failed_assignments": ["array"],
  "assignments": ["array"]
}
```

#### 3.13.9 Get Tenant Statistics
```
GET /api/v1/tenant/statistics
```

**Headers:**
- `Authorization: Bearer {tenant_admin_token}`

**Response:**
```json
{
  "tenant_id": "uuid",
  "users": {
    "total_students": "integer",
    "total_tutors": "integer",
    "active_accounts": "integer",
    "inactive_accounts": "integer"
  },
  "activity": {
    "total_sessions": "integer",
    "total_questions": "integer",
    "total_messages": "integer",
    "active_sessions": "integer"
  },
  "performance": {
    "average_score": "float",
    "completion_rate": "float"
  }
}
```

### 3.15 System-Wide Administrator Endpoints (Legacy - Updated)

#### 3.14.1 Enable/Disable Subject (System-Wide)
```
PUT /api/v1/system/subjects/{subject_id}/status
```

**Headers:**
- `Authorization: Bearer {system_admin_token}`

**Request Body:**
```json
{
  "status": "active|inactive",
  "reason": "string"  // Optional
}
```

**Response:**
```json
{
  "subject_id": "uuid",
  "subject_code": "string",
  "status": "active|inactive",
  "updated_at": "timestamp",
  "updated_by": "uuid"
}
```

#### 3.14.2 Get System-Wide Statistics
```
GET /api/v1/system/statistics
```

**Headers:**
- `Authorization: Bearer {system_admin_token}`

**Response:**
```json
{
  "users": {
    "total_students": "integer",
    "total_tutors": "integer",
    "total_admins": "integer",
    "active_accounts": "integer",
    "inactive_accounts": "integer"
  },
  "subjects": {
    "total": "integer",
    "active": "integer",
    "inactive": "integer"
  },
  "activity": {
    "total_sessions": "integer",
    "total_questions": "integer",
    "total_messages": "integer",
    "active_sessions": "integer"
  }
}
```

#### 3.14.3 Get Audit Logs (System-Wide)
```
GET /api/v1/system/audit-logs
```

**Headers:**
- `Authorization: Bearer {system_admin_token}`

**Query Parameters:**
- `action` (optional: filter by action type)
- `user_id` (optional: filter by user)
- `date_from` (optional)
- `date_to` (optional)
- `limit` (optional)
- `offset` (optional)

**Response:**
```json
{
  "logs": [
    {
      "log_id": "uuid",
      "action": "string",
      "performed_by": "uuid",
      "target_type": "account|subject|assignment",
      "target_id": "uuid",
      "details": "object",
      "timestamp": "timestamp"
    }
  ],
  "total": "integer"
}
```

---

## 4. Data Models

### 4.1 Tenant
```json
{
  "tenant_id": "uuid",
  "tenant_code": "string",  // Unique identifier (slug)
  "name": "string",  // Institution name
  "description": "string",
  "status": "active|inactive|suspended",
  "primary_domain": "string",  // Primary domain identifier
  "domains": [
    {
      "domain_id": "uuid",
      "domain": "string",  // e.g., "example.com", "www.example.com"
      "is_primary": "boolean",
      "status": "active|inactive",
      "created_at": "timestamp"
    }
  ],
  "contact_info": {
    "email": "string",
    "phone": "string",
    "address": {
      "street": "string",
      "city": "string",
      "state": "string",
      "zip": "string",
      "country": "string"
    }
  },
  "settings": {
    "custom_branding": {
      "logo_url": "string",
      "primary_color": "string",
      "secondary_color": "string"
    },
    "features": ["array"],  // Enabled features
    "subscription": {
      "plan": "string",
      "max_students": "integer",
      "max_tutors": "integer",
      "expires_at": "timestamp"
    }
  },
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "created_by": "uuid"  // System admin user ID
}
```

### 4.1a Tenant Domain
```json
{
  "domain_id": "uuid",
  "tenant_id": "uuid",
  "domain": "string",  // Unique domain name
  "is_primary": "boolean",
  "status": "active|inactive",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "created_by": "uuid"  // System admin user ID
}
```

### 4.2 Question
```json
{
  "question_id": "uuid",
  "tenant_id": "uuid",  // Null for system-wide questions, or tenant_id for tenant-specific
  "subject_id": "uuid",  // Reference to subject
  "subject_code": "string",  // Denormalized for quick access
  "grade_level": "integer",  // Null if subject doesn't use grade levels
  "difficulty": "enum",
  "question_type": "enum",
  "question_text": "string",
  "options": ["array"],  // For multiple choice
  "correct_answer": "string|object",
  "metadata": {
    "topic": "string",
    "learning_objectives": ["array"],
    "estimated_time": "integer",
    "points": "float"
  },
  "created_at": "timestamp",
  "ai_model_version": "string"
}
```

### 4.3 Answer Submission
```json
{
  "submission_id": "uuid",
  "tenant_id": "uuid",  // Required: tenant context
  "question_id": "uuid",
  "student_id": "uuid",  // Must belong to tenant_id
  "session_id": "uuid",
  "answer": "string|object",
  "is_correct": "boolean",
  "score": "float",
  "max_score": "float",
  "feedback": "string",
  "hints_used": ["array"],
  "time_spent": "integer",
  "submitted_at": "timestamp"
}
```

### 4.4 Hint
```json
{
  "hint_id": "uuid",
  "tenant_id": "uuid",  // Required: tenant context
  "question_id": "uuid",
  "hint_level": "integer",
  "hint_text": "string",
  "generated_at": "timestamp"
}
```

### 4.5 Quiz Session
```json
{
  "session_id": "uuid",
  "tenant_id": "uuid",  // Required: tenant context
  "student_id": "uuid",  // Must belong to tenant_id
  "subject_id": "uuid",  // Reference to subject
  "subject_code": "string",  // Denormalized for quick access
  "grade_level": "integer",  // Null if subject doesn't use grade levels
  "difficulty": "enum",
  "questions": ["array"],  // Question IDs
  "status": "enum",
  "score": "float",
  "max_score": "float",
  "started_at": "timestamp",
  "completed_at": "timestamp",
  "time_limit": "integer"
}
```

### 4.6 Student Progress
```json
{
  "student_id": "uuid",
  "tenant_id": "uuid",  // Required: tenant context
  "subject_stats": {
    "math": {
      "total_questions": "integer",
      "correct": "integer",
      "accuracy": "float",
      "average_score": "float",
      "topics": { /* topic-level stats */ }
    },
    "english": { /* similar structure */ },
    "python": { /* similar structure */ }
  },
  "last_updated": "timestamp"
}
```

### 4.7 Student Account
```json
{
  "student_id": "uuid",
  "tenant_id": "uuid",  // Required: tenant membership
  "username": "string",
  "email": "string",
  "password_hash": "string",  // Cryptographic hash, never plain text
  "role": "student",  // User role
  "grade_level": "integer",  // Optional
  "account_status": "pending_activation|active|inactive|locked",
  "requires_password_change": "boolean",
  "failed_login_attempts": "integer",
  "locked_until": "timestamp",  // Null if not locked
  "assigned_tutor_id": "uuid",  // Optional: assigned tutor (must be same tenant)
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "last_login": "timestamp",
  "created_by": "uuid"  // Tenant admin or system admin user ID
}
```

### 4.8 Password Reset OTP
```json
{
  "otp_id": "uuid",
  "student_id": "uuid",
  "email": "string",
  "otp_code": "string",  // Hashed OTP
  "expires_at": "timestamp",
  "used": "boolean",
  "created_at": "timestamp",
  "used_at": "timestamp"
}
```

### 4.9 Authentication Token
```json
{
  "token_id": "uuid",
  "student_id": "uuid",
  "access_token": "string",  // JWT or similar
  "refresh_token": "string",  // Optional
  "expires_at": "timestamp",
  "created_at": "timestamp",
  "revoked": "boolean"
}
```

### 4.10 Subject
```json
{
  "subject_id": "uuid",
  "subject_code": "string",  // Unique identifier (slug)
  "name": "string",  // Display name
  "description": "string",
  "type": "academic|programming|language|science|other",
  "grade_levels": ["array"],  // [6, 7, 8, ...] or null for all levels
  "status": "active|inactive|archived",
  "supported_question_types": ["array"],
  "answer_validation_method": "ai_semantic|code_execution|exact_match|ai_structured",
  "settings": {
    "default_difficulty": "string",
    "ai_prompt_template": "string",  // Optional: custom AI prompt
    "validation_rules": "object",  // Optional: subject-specific rules
    "hint_strategy": "string",  // Optional
    "code_execution_config": "object"  // For programming subjects
  },
  "metadata": {
    "curriculum": "string",
    "learning_objectives": ["array"],
    "icon_url": "string",
    "category": "string",
    "tags": ["array"]
  },
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "created_by": "string"  // Admin user ID
}
```

### 4.11 Competition
```json
{
  "competition_id": "uuid",
  "tenant_id": "uuid",  // Required: tenant context (null for system-wide)
  "name": "string",
  "description": "string",
  "subject_id": "uuid",  // Reference to subject
  "subject_code": "string",  // Denormalized for quick access
  "status": "upcoming|active|ended|cancelled",
  "start_date": "timestamp",
  "end_date": "timestamp",
  "registration_start": "timestamp",
  "registration_end": "timestamp",
  "rules": {
    "time_limit": "integer",  // Total time limit in seconds
    "num_questions": "integer",
    "difficulty": "beginner|intermediate|advanced",
    "allowed_question_types": ["array"],
    "max_attempts": "integer",  // Typically 1 for competitions
    "scoring_rules": {
      "points_per_question": "float",
      "bonus_points": "object",
      "penalties": "object"
    },
    "hints_allowed": "boolean",
    "narratives_allowed": "boolean"
  },
  "eligibility": {
    "grade_levels": ["array"],  // [6, 7, 8, ...] or null for all
    "tenant_restrictions": ["array"],  // Specific tenant IDs or null for all
    "minimum_requirements": {
      "min_accuracy": "float",
      "min_questions_answered": "integer"
    }
  },
  "visibility": "public|private|tenant_specific",
  "max_participants": "integer",  // Null for unlimited
  "participant_count": "integer",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "created_by": "uuid",  // Admin user ID
  "cancelled_at": "timestamp",  // If cancelled
  "cancelled_by": "uuid",  // Admin user ID
  "cancellation_reason": "string"
}
```

### 4.11a Competition Registration
```json
{
  "registration_id": "uuid",
  "competition_id": "uuid",
  "tenant_id": "uuid",  // Required: tenant context
  "student_id": "uuid",  // Must belong to tenant_id
  "status": "registered|confirmed|cancelled",
  "registered_at": "timestamp",
  "confirmed_at": "timestamp",
  "cancelled_at": "timestamp",
  "cancelled_by": "uuid",  // Student ID if self-cancelled, Admin ID if admin-cancelled
  "waitlist_position": "integer",  // If max participants reached
  "notes": "string"  // Optional
}
```

### 4.11b Competition Session
```json
{
  "competition_session_id": "uuid",
  "competition_id": "uuid",
  "tenant_id": "uuid",  // Required: tenant context
  "student_id": "uuid",  // Must belong to tenant_id
  "session_id": "uuid",  // Reference to quiz session
  "started_at": "timestamp",
  "completed_at": "timestamp",
  "time_limit": "integer",
  "score": "float",
  "max_score": "float",
  "accuracy": "float",
  "completion_time": "integer",
  "questions_answered": "integer",
  "status": "in_progress|completed|expired|abandoned"
}
```

### 4.12 Tutor Account
```json
{
  "tutor_id": "uuid",
  "tenant_id": "uuid",  // Required: tenant membership
  "username": "string",
  "email": "string",
  "password_hash": "string",  // Cryptographic hash
  "name": "string",
  "status": "active|inactive|suspended|pending_activation",
  "requires_password_change": "boolean",
  "profile": {
    "bio": "string",
    "specializations": ["array"],
    "contact_info": "object",
    "qualifications": ["array"]
  },
  "failed_login_attempts": "integer",
  "locked_until": "timestamp",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "last_login": "timestamp",
  "created_by": "uuid"  // Tenant admin or system admin user ID
}
```

### 4.13 Administrator Account
```json
{
  "admin_id": "uuid",
  "tenant_id": "uuid",  // Null for system_admin, required for tenant_admin
  "username": "string",
  "email": "string",
  "password_hash": "string",  // Cryptographic hash
  "name": "string",
  "role": "tenant_admin|system_admin",
  "status": "active|inactive|suspended|pending_activation",
  "requires_password_change": "boolean",
  "permissions": ["array"],  // Optional: specific permissions
  "failed_login_attempts": "integer",
  "locked_until": "timestamp",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "last_login": "timestamp",
  "created_by": "uuid"  // System admin user ID (for tenant_admin) or super admin (for system_admin)
}
```

### 4.14 Student-Tutor Assignment
```json
{
  "assignment_id": "uuid",
  "tenant_id": "uuid",  // Required: tenant context
  "student_id": "uuid",  // Must belong to tenant_id
  "tutor_id": "uuid",  // Must belong to tenant_id
  "status": "active|inactive",
  "assigned_at": "timestamp",
  "assigned_by": "uuid",  // Tenant admin or system admin user ID
  "deactivated_at": "timestamp",
  "deactivated_by": "uuid",  // Optional: admin user ID
  "notes": "string"  // Optional: assignment notes
}
```

### 4.15 Message
```json
{
  "message_id": "uuid",
  "tenant_id": "uuid",  // Required: tenant context
  "sender_id": "uuid",  // Must belong to tenant_id
  "sender_role": "student|tutor|tenant_admin",
  "recipient_id": "uuid",  // Must belong to tenant_id
  "recipient_role": "student|tutor|tenant_admin",
  "content": "string",
  "status": "sent|delivered|read|deleted",
  "email_sent": "boolean",
  "email_sent_at": "timestamp",
  "read_at": "timestamp",
  "subject_reference": "uuid",  // Optional: reference to subject
  "question_reference": "uuid",  // Optional: reference to question
  "conversation_id": "uuid",  // Groups messages in conversation
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "deleted_at": "timestamp"  // Soft delete
}
```

### 4.16 Audit Log
```json
{
  "log_id": "uuid",
  "tenant_id": "uuid",  // Null for system-level actions
  "action": "string",  // create_account, disable_account, assign_tutor, etc.
  "performed_by": "uuid",  // User ID who performed action
  "performed_by_role": "tenant_admin|system_admin",
  "target_type": "account|subject|assignment|message|tenant",
  "target_id": "uuid",
  "details": "object",  // Action-specific details
  "ip_address": "string",
  "user_agent": "string",
  "timestamp": "timestamp"
}
```

---

## 5. AI Integration Requirements

### 5.1 Question Generation AI
- **AI-1.1**: Integrate with AI service (OpenAI, Anthropic, or similar) for question generation
- **AI-1.2**: Prompt engineering for:
  - Grade-appropriate language and complexity
  - Subject-specific question formats
  - Curriculum alignment
  - Diverse question types
- **AI-1.3**: Quality assurance:
  - Validate generated questions for accuracy
  - Ensure questions are age-appropriate
  - Check for bias and inclusivity

### 5.2 Answer Validation AI
- **AI-2.1**: Use AI for semantic answer validation (text-based answers)
- **AI-2.2**: Code execution and validation for Python questions
- **AI-2.3**: Partial credit assessment using AI
- **AI-2.4**: Generate contextual feedback

### 5.3 Hint Generation AI
- **AI-3.1**: Generate progressive, contextual hints
- **AI-3.2**: Consider student's answer attempts when generating hints
- **AI-3.3**: Adapt hint style to subject and question type

### 5.4 Narrative Generation AI
- **AI-4.1**: Generate comprehensive educational explanations
- **AI-4.2**: Ensure narratives are pedagogically sound
- **AI-4.3**: Adapt narrative complexity to grade level

### 5.5 AI Configuration
- **AI-5.1**: Configurable AI models per use case
- **AI-5.2**: Token usage tracking and optimization
- **AI-5.3**: Fallback mechanisms if AI service is unavailable
- **AI-5.4**: Rate limiting and cost management

---

## 6. Non-Functional Requirements

### 6.1 Performance
- **NFR-1.1**: Question generation response time: < 5 seconds
- **NFR-1.2**: Answer validation response time: < 3 seconds
- **NFR-1.3**: Hint generation response time: < 3 seconds
- **NFR-1.4**: Narrative generation response time: < 5 seconds
- **NFR-1.5**: Support concurrent users: 1000+ simultaneous sessions

### 6.2 Scalability
- **NFR-2.1**: Horizontal scaling capability
- **NFR-2.2**: Database optimization for large datasets
- **NFR-2.3**: Caching strategy for frequently accessed data
- **NFR-2.4**: Load balancing support

### 6.3 Reliability
- **NFR-3.1**: 99.9% uptime SLA
- **NFR-3.2**: Graceful degradation if AI services are unavailable
- **NFR-3.3**: Data backup and recovery procedures
- **NFR-3.4**: Error handling and logging

### 6.4 Security
- **NFR-4.1**: Authentication and authorization
- **NFR-4.2**: API key management
- **NFR-4.3**: Rate limiting per user/IP
- **NFR-4.4**: Data encryption in transit (HTTPS/TLS)
- **NFR-4.5**: Data encryption at rest
- **NFR-4.6**: PII (Personally Identifiable Information) protection
- **NFR-4.7**: Input validation and sanitization
- **NFR-4.8**: Protection against injection attacks (especially for code execution)
- **NFR-4.9**: Password security:
  - Passwords must be hashed using secure algorithms (bcrypt, Argon2, scrypt)
  - Minimum password strength requirements (configurable)
  - Password hashing with salt
  - Never log or expose passwords in plain text
- **NFR-4.10**: OTP security:
  - OTP codes must be hashed before storage
  - OTP expiration (recommended: 15 minutes)
  - Single-use OTPs
  - Rate limiting on OTP generation (prevent brute force)
  - Secure random OTP generation
- **NFR-4.11**: Session security:
  - Secure token generation (JWT with proper signing)
  - Token expiration and refresh mechanisms
  - Token revocation on logout
  - Protection against token theft (HTTP-only cookies, secure flags)
  - Role information included in token
- **NFR-4.12**: Account protection:
  - Account lockout after failed login attempts
  - Protection against brute force attacks
  - Email enumeration prevention (generic error messages)
- **NFR-4.13**: Role-based access control:
  - Enforce role-based permissions on all endpoints
  - Verify user role in JWT token
  - Prevent privilege escalation
  - Audit role-based access attempts
- **NFR-4.14**: Message security:
  - Verify sender-recipient relationships (student-tutor assignments)
  - Validate message content (prevent XSS, injection)
  - Secure email delivery for message copies
  - Protect message content in transit and at rest
- **NFR-4.15**: Tenant isolation security:
  - Enforce tenant_id in all data queries
  - Prevent cross-tenant data access
  - Validate tenant membership for all operations
  - Tenant-scoped access control for tenant admins
  - System-wide access for system admins only
  - Prevent tenant_id manipulation in API requests
- **NFR-4.16**: Domain-based tenant resolution:
  - Validate domain format (DNS-compliant)
  - Verify domain exists and is active
  - Cache domain-to-tenant mappings for performance
  - Rate limit domain resolution requests
  - Secure domain parameter handling (prevent injection)
  - Validate tenant is active after domain resolution
  - Return appropriate errors for invalid/inactive domains

### 6.5 Usability
- **NFR-5.1**: RESTful API design
- **NFR-5.2**: Comprehensive API documentation (OpenAPI/Swagger)
- **NFR-5.3**: Clear error messages
- **NFR-5.4**: Consistent response formats

### 6.6 Maintainability
- **NFR-6.1**: Modular architecture
- **NFR-6.2**: Comprehensive logging and monitoring
- **NFR-6.3**: Versioning strategy (API versioning)
- **NFR-6.4**: Code documentation

### 6.7 Extensibility
- **NFR-7.1**: Support adding new subjects without code changes
- **NFR-7.2**: Subject configuration stored in database (not hardcoded)
- **NFR-7.3**: Pluggable answer validation methods
- **NFR-7.4**: Configurable AI prompts per subject
- **NFR-7.5**: Backward compatibility when adding new subjects

---

## 7. Technical Constraints

### 7.1 Technology Stack
- **TC-1.1**: Python-based API framework (FastAPI, Flask, or Django REST)
- **TC-1.2**: Database: PostgreSQL or MongoDB for data persistence
- **TC-1.3**: Redis for caching and session management
- **TC-1.4**: AI Integration: OpenAI API, Anthropic Claude, or similar
- **TC-1.5**: Code execution: Secure sandboxed environment for Python code validation

### 7.4 Extensibility Architecture
- **TC-4.1**: Use database-driven subject configuration (not enum/hardcoded)
- **TC-4.2**: Implement strategy pattern for answer validation methods
- **TC-4.3**: Use factory pattern for question generation per subject type
- **TC-4.4**: Support plugin/configuration-based subject extensions
- **TC-4.5**: Maintain subject registry/configuration service

### 7.5 Domain-Based Tenant Resolution
- **TC-5.1**: Implement domain-to-tenant mapping service
- **TC-5.2**: Cache domain mappings (Redis or in-memory cache)
- **TC-5.3**: Support domain resolution from multiple sources:
  - Query parameter
  - HTTP header
  - Path parameter (optional)
- **TC-5.4**: Domain validation middleware/interceptor
- **TC-5.5**: Fast lookup mechanism for domain resolution (O(1) or O(log n))
- **TC-5.6**: Domain format validation (regex or DNS library)

### 7.2 Code Execution Security
- **TC-2.1**: Sandboxed execution environment for Python code
- **TC-2.2**: Resource limits (CPU, memory, execution time)
- **TC-2.3**: Network isolation for code execution
- **TC-2.4**: Input validation and sanitization
- **TC-2.5**: Timeout mechanisms

### 7.3 API Standards
- **TC-3.1**: RESTful API design principles
- **TC-3.2**: JSON request/response format
- **TC-3.3**: HTTP status codes following REST conventions
- **TC-3.4**: API versioning (e.g., /api/v1/)

---

## 8. Integration Requirements

### 8.1 External Services
- **INT-1.1**: AI/LLM service integration (OpenAI, Anthropic, etc.)
- **INT-1.2**: Email service integration (SendGrid, AWS SES, Mailgun, etc.)
  - For sending OTP codes
  - For account activation emails
  - For password change notifications
  - For message email copies
  - For message notifications
- **INT-1.3**: Analytics/monitoring service (optional)

### 8.2 Third-Party Libraries
- **INT-2.1**: Code execution libraries (for Python validation)
- **INT-2.2**: Natural language processing libraries (for text validation)
- **INT-2.3**: Database ORM/ODM
- **INT-2.4**: Password hashing libraries (bcrypt, passlib, argon2-cffi)
- **INT-2.5**: JWT token libraries (PyJWT, python-jose)
- **INT-2.6**: Email libraries (for email service integration)

---

## 9. Testing Requirements

### 9.1 Unit Testing
- **TEST-1.1**: Unit tests for all core functions
- **TEST-1.2**: Mock AI service responses
- **TEST-1.3**: Code coverage: minimum 80%

### 9.2 Integration Testing
- **TEST-2.1**: API endpoint testing
- **TEST-2.2**: Database integration testing
- **TEST-2.3**: AI service integration testing
- **TEST-2.4**: Code execution sandbox testing
- **TEST-2.5**: Subject management testing:
  - Create new subject
  - Update subject configuration
  - Generate questions for new subject
  - Validate answers for new subject
  - Track progress for new subject
- **TEST-2.6**: Role-based access control testing:
  - Student access restrictions
  - Tutor access to assigned students only
  - Admin access to all resources
- **TEST-2.7**: Messaging system testing:
  - Send messages between students and tutors
  - Email copy functionality
  - Message delivery and read status
  - Conversation threading

### 9.3 Security Testing
- **TEST-3.1**: Authentication/authorization testing
- **TEST-3.2**: Input validation testing
- **TEST-3.3**: Code injection prevention testing
- **TEST-3.4**: Rate limiting testing
- **TEST-3.5**: Password security testing:
  - Verify passwords are hashed (never stored in plain text)
  - Test password strength requirements
  - Test password change functionality
  - Test first-time password change requirement
- **TEST-3.6**: OTP security testing:
  - Verify OTP hashing
  - Test OTP expiration
  - Test single-use OTP enforcement
  - Test OTP rate limiting
- **TEST-3.7**: Account lockout testing:
  - Test failed login attempt tracking
  - Test account lockout after threshold
  - Test lockout duration
- **TEST-3.8**: Email enumeration prevention testing
- **TEST-3.9**: Role-based access control testing:
  - Verify students cannot access other students' data
  - Verify tutors can only access assigned students' data
  - Verify admins have full access
  - Test unauthorized access attempts
- **TEST-3.10**: Message security testing:
  - Verify students can only message their assigned tutor
  - Verify tutors can only message assigned students
  - Test message content validation
  - Test email copy security

### 9.4 Performance Testing
- **TEST-4.1**: Load testing
- **TEST-4.2**: Stress testing
- **TEST-4.3**: Response time testing

---

## 10. Deployment Requirements

### 10.1 Environment
- **DEP-1.1**: Development environment
- **DEP-1.2**: Staging environment
- **DEP-1.3**: Production environment

### 10.2 Infrastructure
- **DEP-2.1**: Containerization (Docker)
- **DEP-2.2**: Orchestration (Kubernetes, Docker Compose, or similar)
- **DEP-2.3**: CI/CD pipeline
- **DEP-2.4**: Monitoring and alerting

### 10.3 Configuration Management
- **DEP-3.1**: Environment-specific configuration
- **DEP-3.2**: Secret management
- **DEP-3.3**: Feature flags

---

## 11. Future Enhancements (Out of Scope)

- Multi-language support
- Voice-based questions
- Image-based questions
- Collaborative quiz sessions
- Real-time leaderboards
- Adaptive difficulty adjustment
- Integration with learning management systems (LMS)
- Mobile app SDK

---

## 12. Success Criteria

- Successfully generate accurate, grade-appropriate questions for all subjects
- Validate answers with high accuracy (95%+ for objective questions)
- Provide helpful, contextual hints that improve learning outcomes
- Generate clear, educational narratives
- Track student progress accurately
- Maintain API response times within specified limits
- Achieve 99.9% uptime
- Support 1000+ concurrent users

---

## 13. Assumptions and Dependencies

### 13.1 Assumptions
- AI service (OpenAI, Anthropic, etc.) is available and reliable
- Email service is available and reliable for sending OTP codes
- Students have unique identifiers (username or email)
- Administrators can create preset student accounts
- Curriculum standards are available for grade-level alignment

### 13.2 Dependencies
- AI/LLM service availability
- Email service availability (for OTP delivery)
- Database service
- Caching service (Redis)
- Secure code execution environment
- Network infrastructure

---

## 14. Glossary

- **AI**: Artificial Intelligence
- **LLM**: Large Language Model
- **PII**: Personally Identifiable Information
- **SLA**: Service Level Agreement
- **API**: Application Programming Interface
- **REST**: Representational State Transfer
- **ORM**: Object-Relational Mapping
- **ODM**: Object-Document Mapping

---

## Document Version
- **Version**: 1.6
- **Date**: 2025
- **Author**: Requirements Team
- **Status**: Draft
- **Changes**: 
  - v1.1: Added User Management requirements (Section 2.7), Authentication endpoints (Section 3.6), User Management endpoints (Section 3.7), Student Account data model (Section 4.6), Password Reset OTP model (Section 4.7), Authentication Token model (Section 4.8), and updated Security, Integration, Testing, and Dependencies sections.
  - v1.2: Added Subject Management requirements (Section 2.8), Subject Management endpoints (Section 3.8), Subject data model (Section 4.9), updated Question and Quiz Session models to reference subjects, updated API endpoints to use subject_id/subject_code, added Extensibility requirements (Section 6.7), and added Extensibility Architecture constraints (Section 7.4).
  - v1.3: Added Tutor Management requirements (Section 2.9), Messaging System requirements (Section 2.10), Administrator Management requirements (Section 2.11), Role-Based Access Control requirements (Section 2.12), Tutor Management endpoints (Section 3.9), Messaging endpoints (Section 3.10), Administrator endpoints (Section 3.11), Tutor Account data model (Section 4.10), Administrator Account data model (Section 4.11), Student-Tutor Assignment model (Section 4.12), Message data model (Section 4.13), Audit Log model (Section 4.14), updated Student Account model to include role and assigned_tutor_id, updated authentication to support multiple roles, updated Security, Integration, and Testing sections for role-based access and messaging.
  - v1.4: Added Tenant Management requirements (Section 2.12), updated Role-Based Access Control (Section 2.13) to include tenant_admin role, added Tenant Management endpoints (Section 3.11), separated System Administrator endpoints (Section 3.12) and Tenant Administrator endpoints (Section 3.13), added Tenant data model (Section 4.1), updated all data models to include tenant_id for multi-tenancy support, updated authentication response to include tenant_id, added tenant isolation security requirements (NFR-4.15), and renumbered subsequent data model sections.
  - v1.5: Added domain-based tenant identification (Section 2.12.3), updated Tenant Management to include domain requirements (Section 2.12.2), added domain management endpoints (Sections 3.11.7-3.11.10), added domain resolution endpoint, updated Tenant data model to include domains (Section 4.1), added Tenant Domain data model (Section 4.1a), updated login endpoint to accept domain parameter, added domain-based tenant resolution security requirements (NFR-4.16), and added domain resolution architecture constraints (Section 7.5).
  - v1.6: Added Competition Management requirements (Section 2.9), Competition Endpoints (Section 3.9), Competition data models (Sections 4.11, 4.11a, 4.11b), renumbered subsequent sections (Tutor Management to 2.10, Messaging to 2.11, Administrator to 2.12, Tenant to 2.13, RBAC to 2.14), and renumbered API endpoint sections accordingly.

