# Quiz API Source Code

This directory contains the FastAPI application source code generated from the OpenAPI specification.

## Project Structure

```
src/
├── __init__.py
├── main.py                 # FastAPI application entry point
├── core/                   # Core application modules
│   ├── __init__.py
│   ├── config.py          # Configuration settings (Pydantic Settings)
│   ├── database.py        # Database setup, session management, and RLS context
│   ├── security.py        # Security utilities (JWT, password hashing with bcrypt)
│   ├── exceptions.py      # Custom exceptions (NotFoundError, BadRequestError, etc.)
│   └── dependencies.py    # FastAPI dependencies (auth, role checking, tenant resolution)
├── models/                # Database models (SQLAlchemy ORM)
│   ├── __init__.py
│   ├── user.py           # User-related enums (UserRole, AccountStatus, etc.)
│   └── database.py       # SQLAlchemy ORM models matching PostgreSQL schema
├── schemas/               # Pydantic schemas for request/response validation
│   ├── __init__.py
│   ├── auth.py           # Authentication schemas
│   ├── common.py         # Common schemas (pagination, responses)
│   ├── answer.py         # Answer submission schemas
│   ├── competition.py    # Competition schemas
│   ├── hint.py           # Hint schemas
│   ├── message.py        # Messaging schemas
│   ├── progress.py       # Student progress schemas
│   ├── question.py       # Question schemas
│   ├── session.py        # Quiz session schemas
│   ├── subject.py        # Subject management schemas
│   └── tenant.py         # Tenant management schemas
├── api/                   # API routes
│   └── v1/
│       ├── __init__.py
│       ├── router.py     # Main API router with all endpoint registrations
│       └── endpoints/    # Endpoint modules
│           ├── auth.py              # Authentication (login, logout, password management)
│           ├── questions.py         # Question generation and retrieval
│           ├── answers.py           # Answer submission and validation
│           ├── hints.py             # Hint generation
│           ├── sessions.py          # Quiz session management
│           ├── progress.py          # Student progress tracking
│           ├── students.py           # Student data endpoints
│           ├── tutors.py            # Tutor data endpoints
│           ├── messages.py          # Student-tutor messaging
│           ├── subjects.py          # Subject management
│           ├── competitions.py       # Competition management
│           ├── tenants.py           # Tenant resolution
│           ├── system_admin.py       # System admin endpoints
│           └── tenant_admin.py      # Tenant admin endpoints
└── services/              # Business logic layer
    ├── __init__.py
    ├── auth.py           # Authentication service (login, password management, OTP)
    ├── tenant.py         # Tenant resolution and management
    ├── subject.py        # Subject management
    ├── question.py       # Question generation and retrieval
    ├── answer.py         # Answer validation and scoring
    ├── hint.py           # Hint generation
    ├── session.py        # Quiz session management
    ├── progress.py       # Student progress tracking and analytics
    ├── student.py        # Student management
    ├── tutor.py          # Tutor management and student assignments
    ├── message.py        # Messaging service
    └── competition.py    # Competition management
```

## Getting Started

### 1. Set Up Virtual Environment

Create and activate a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `env.example` to `.env` and configure:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/tutor
JWT_SECRET_KEY=your-secret-key-here
```

### 4. Run Database Migrations

```bash
alembic upgrade head
```

### 5. Run the Application

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000/api/v1
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Implementation Status

### ✅ Completed

#### Core Infrastructure
- ✅ Project structure and organization
- ✅ Core configuration (Pydantic Settings with environment variable support)
- ✅ Database setup with SQLAlchemy ORM models matching PostgreSQL schema
- ✅ Security utilities (JWT token generation/validation, bcrypt password hashing)
- ✅ Custom exception handling
- ✅ FastAPI dependencies for authentication and authorization
- ✅ Multi-tenant support with Row Level Security (RLS) context management

#### Database Models
- ✅ Complete SQLAlchemy ORM models matching `0.0.10__initial_schema.sql`
- ✅ Multi-tenant user account structure (`UserAccount`, `SystemAdminAccount`, `TenantAdminAccount`)
- ✅ Subject-level role assignments (`UserSubjectRole`, `StudentSubjectProfile`, `TutorSubjectProfile`)
- ✅ Quiz and question models (`Question`, `QuizSession`, `AnswerSubmission`, `Hint`)
- ✅ Messaging models (`Message`)
- ✅ Competition models (`Competition`, `CompetitionRegistration`, `CompetitionSession`)
- ✅ Progress tracking (`StudentProgress`)
- ✅ Student-tutor assignments (`StudentTutorAssignment`)
- ✅ Audit logging (`AuditLog`)
- ✅ **Fixed**: SQLAlchemy `metadata` reserved name conflict (using `extra_metadata` with column mapping)
- ✅ **Fixed**: Ambiguous foreign key relationships (explicit `primaryjoin` and `foreign_keys`)

#### Services (Business Logic)
- ✅ Authentication service (login, logout, password change, password reset with OTP)
- ✅ Tenant service (domain resolution, tenant statistics)
- ✅ Subject service (CRUD operations, statistics)
- ✅ Question service (generation, retrieval, metadata handling)
- ✅ Answer service (submission, validation, scoring)
- ✅ Hint service (generation with levels 1-4)
- ✅ Session service (quiz session creation and management)
- ✅ Progress service (student progress tracking and analytics)
- ✅ Student service (student account management)
- ✅ Tutor service (tutor management, student assignments)
- ✅ Message service (messaging between students and tutors)
- ✅ Competition service (competition management, registration, leaderboards)

#### API Endpoints
- ✅ Authentication endpoints (`/auth/login`, `/auth/logout`, `/auth/change-password`, `/auth/forgot-password`, `/auth/reset-password`)
- ✅ Question endpoints (`/questions/generate`, `/questions/{question_id}`, `/questions/{question_id}/narrative`)
- ✅ Answer endpoints (`/answers/{question_id}/answer`, `/answers/{question_id}/validate`)
- ✅ Hint endpoints (`/hints/{question_id}/hint`)
- ✅ Session endpoints (`/sessions`, `/sessions/{session_id}`, `/sessions/{session_id}/results`)
- ✅ Progress endpoints (`/progress/{student_id}/progress`, `/progress/{student_id}/analytics`)
- ✅ Student endpoints (`/students/{student_id}`)
- ✅ Tutor endpoints (`/tutors`, `/tutors/{tutor_id}`, `/tutors/{tutor_id}/students`, `/tutors/{tutor_id}/students/{student_id}/progress`)
- ✅ Message endpoints (`/messages`, `/messages/conversations/{user_id}`, `/messages/{message_id}/read`)
- ✅ Subject endpoints (`/subjects`, `/subjects/{subject_id}`, admin CRUD operations)
- ✅ Competition endpoints (`/competitions`, `/competitions/{competition_id}`, registration, leaderboards, results)
- ✅ Tenant endpoints (`/tenants/resolve`)
- ✅ Tenant admin endpoints (`/tenant/accounts`, `/tenant/students`, `/tenant/tutors`, assignments, statistics)
- ✅ System admin endpoints (`/system/tenants`, `/system/accounts`, `/system/statistics`, audit logs)
- ✅ **Fixed**: Removed duplicate TODO placeholder endpoints causing Operation ID conflicts

#### Schemas
- ✅ Complete Pydantic schemas for all request/response models
- ✅ Request validation and response serialization
- ✅ Common schemas (pagination, error responses)

### 🚧 Partially Implemented / TODO

#### AI Integration
- 🚧 AI service integration for question generation (placeholder implementation)
- 🚧 AI service integration for answer validation (semantic matching)
- 🚧 AI service integration for hint generation (contextual hints)
- 🚧 AI service integration for question narratives/explanations

#### Email Service
- 🚧 Email service for OTP delivery (password reset)
- 🚧 Email notifications for messages
- 🚧 Email notifications for competition updates

#### Advanced Features
- 🚧 Real-time competition leaderboard updates
- 🚧 Advanced analytics and reporting
- 🚧 Bulk operations for student-tutor assignments
- 🚧 Competition statistics calculation (placeholder exists)
- 🚧 Subject statistics calculation (placeholder exists)

#### Infrastructure
- 🚧 Rate limiting
- 🚧 Comprehensive logging and monitoring
- 🚧 Caching layer (Redis integration)
- 🚧 Background job processing
- 🚧 Unit and integration tests

## Development Notes

### Database Models

1. **SQLAlchemy Models**: The models in `src/models/database.py` fully match the PostgreSQL schema defined in `db/migration/0.0.10__initial_schema.sql`.

2. **Reserved Name Handling**: The `metadata` column in `Subject` and `Question` tables is mapped to `extra_metadata` in Python to avoid SQLAlchemy's reserved `metadata` attribute conflict.

3. **Foreign Key Relationships**: When a table has multiple foreign keys to the same parent table (e.g., `StudentSubjectProfile` has both `user_id` and `assigned_tutor_id` pointing to `UserAccount`), relationships must explicitly specify `foreign_keys` and `primaryjoin` to avoid ambiguity.

4. **Enum Types**: PostgreSQL native enums are used with a custom `StrEnumType` decorator to ensure proper Python enum ↔ PostgreSQL enum conversion.

### Services

1. **Service Layer Pattern**: All business logic is implemented in the `services/` directory. Services handle database operations, validation, and business rules.

2. **Multi-tenancy**: All services respect tenant isolation. Tenant ID is extracted from the authenticated user context.

3. **Subject-Level Roles**: Users can have different roles (student/tutor) per subject, managed through `UserSubjectRole` and profile tables.

### API Endpoints

1. **Authentication**: JWT-based authentication is fully implemented with access/refresh tokens. The `get_current_user` dependency extracts user information including subject-level roles.

2. **Role-Based Access Control**: Endpoints use dependency injection (`require_role`, `require_system_admin`, `require_tenant_admin`, `require_tutor_or_admin`) to enforce access control.

3. **Request/Response Validation**: All endpoints use Pydantic schemas for request validation and response serialization.

4. **Error Handling**: Custom exceptions (`NotFoundError`, `BadRequestError`, etc.) are used consistently and return appropriate HTTP status codes.

### Multi-Tenancy and RLS

1. **Row Level Security**: The database uses PostgreSQL RLS policies for data isolation. The application must call `tutor.set_context()` at the start of each transaction to set tenant/user context.

2. **Tenant Resolution**: The `/tenants/resolve` endpoint resolves tenant from domain. System admins can access all tenants.

3. **Context Management**: Database sessions should set RLS context using the `tutor.set_context()` function before executing queries.

### Security

1. **Password Hashing**: Uses bcrypt with 12 rounds for password hashing.

2. **JWT Tokens**: Access tokens include user information and subject roles. Refresh tokens are supported.

3. **OTP System**: Password reset uses one-time passcodes (OTP) with expiration and single-use enforcement.

4. **Account Lockout**: Failed login attempts are tracked and can trigger account lockout.

### Recent Fixes

1. **SQLAlchemy Metadata Conflict**: Fixed reserved name conflict by mapping `metadata` database column to `extra_metadata` Python attribute.

2. **Ambiguous Foreign Keys**: Fixed relationship ambiguity by explicitly specifying `foreign_keys` and `primaryjoin` for `UserAccount.student_profiles` relationship.

3. **Duplicate Operation IDs**: Removed duplicate TODO placeholder endpoints that were causing FastAPI OpenAPI schema warnings.

## Next Steps

### High Priority
1. **AI Integration**: Integrate OpenAI/Anthropic API for:
   - Question generation with context and difficulty levels
   - Semantic answer validation
   - Contextual hint generation
   - Question narrative/explanation generation

2. **Email Service**: Implement email delivery for:
   - Password reset OTP codes
   - Message notifications
   - Competition updates and reminders

3. **Testing**: Write comprehensive test suite:
   - Unit tests for services
   - Integration tests for endpoints
   - Database migration tests
   - Authentication and authorization tests

### Medium Priority
4. **Advanced Features**:
   - Real-time competition leaderboard (WebSocket support)
   - Advanced analytics and reporting dashboards
   - Bulk operations for administrative tasks
   - Competition and subject statistics calculation

5. **Performance**:
   - Implement Redis caching layer
   - Database query optimization
   - Background job processing for heavy operations
   - Rate limiting implementation

6. **Monitoring & Logging**:
   - Structured logging with correlation IDs
   - Application performance monitoring (APM)
   - Error tracking and alerting
   - Audit log analysis tools

### Low Priority
7. **Documentation**:
   - API documentation improvements
   - Developer guides
   - Deployment documentation
   - Architecture decision records (ADRs)

8. **DevOps**:
   - CI/CD pipeline setup
   - Docker containerization
   - Kubernetes deployment manifests
   - Database backup and recovery procedures

## Architecture Highlights

### Multi-Tenancy
- **Tenant Isolation**: Each tenant (educational institution) has isolated data
- **Domain-Based Resolution**: Tenants are identified by domain name
- **RLS Enforcement**: PostgreSQL Row Level Security enforces data isolation at the database level

### Role-Based Access Control
- **System Admin**: Full system access, manages tenants
- **Tenant Admin**: Manages users and settings within their tenant
- **Tutor**: Subject-specific role, manages assigned students
- **Student**: Subject-specific role, takes quizzes and tracks progress

### Subject-Level Roles
- Users can have different roles per subject (e.g., student in Math, tutor in English)
- Roles are managed through `UserSubjectProfile` and `TutorSubjectProfile` tables
- Student-tutor assignments are subject-specific

### Data Model
- **Unified User Account**: `UserAccount` table for all tenant-scoped users (students, tutors, tenant admins)
- **Separate System Admin**: `SystemAdminAccount` table for system administrators (not tenant-scoped)
- **Subject Profiles**: Separate profile tables for subject-specific data (grade level, tutor assignments, etc.)

