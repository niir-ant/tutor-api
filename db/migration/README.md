# Database Migrations

This directory contains PostgreSQL migration scripts for the Quiz API database schema.

## Migration Files

The migrations follow Semantic Versioning (SemVer) naming convention: `major.minor.patch__description.sql`

- `0.0.10__initial_schema.sql` - Initial database schema with all tables, types, and triggers
- `0.0.20__indexes_and_constraints.sql` - Indexes and constraints for performance
- `0.0.30__rls_policies.sql` - Row Level Security (RLS) policies for multi-tenant isolation
- `0.0.40__roles_and_permissions.sql` - Database roles and permissions
- `0.0.50__auth_rls_fix.sql` - RLS policy fix to allow system admin authentication
- `0.0.60__add_name_to_user_accounts.sql` - Add name column to user_accounts table

## Prerequisites

- PostgreSQL 12 or higher
- `uuid-ossp` extension (for UUID generation)
- `pgcrypto` extension (for cryptographic functions)

## Running Migrations

### Using psql

```bash
# Connect to your database
psql -U postgres -d tutor

# Run migrations in order
\i 0.0.10__initial_schema.sql
\i 0.0.20__indexes_and_constraints.sql
\i 0.0.30__rls_policies.sql
\i 0.0.40__roles_and_permissions.sql
\i 0.0.50__auth_rls_fix.sql
\i 0.0.60__add_name_to_user_accounts.sql
```

### Using a Migration Tool

If using a migration tool like `migrate` (golang-migrate), `Flyway`, or `Liquibase`:

```bash
# Example with golang-migrate
migrate -path db/migration -database "postgres://user:password@localhost/tutor?sslmode=disable" up
```

## Database Setup

### 1. Create Database

```sql
CREATE DATABASE tutor;
\c tutor
```

### 2. Run Migrations

Execute all migration files in order.

### 3. Configure Environment Variables

**IMPORTANT**: Create a `.env` file from `env.example` and configure:

1. **DATABASE_URL** (required) - Your PostgreSQL connection string
2. **Database role passwords** - Set in `.env`:
   - `DB_APP_USER_PASSWORD`
   - `DB_APP_READONLY_PASSWORD`
   - `DB_APP_MIGRATOR_PASSWORD`

Then either:
- Manually update `0.0.40__roles_and_permissions.sql` with your passwords, OR
- Use the helper script: `python scripts/prepare_migration_with_env.py`

After running migrations, update passwords:
```sql
ALTER ROLE app_user WITH PASSWORD 'your_secure_password';
ALTER ROLE app_readonly WITH PASSWORD 'your_secure_password';
ALTER ROLE app_migrator WITH PASSWORD 'your_secure_password';
```

## Row Level Security (RLS)

The database uses Row Level Security to enforce multi-tenant data isolation. **The application MUST use the `tutor.set_context()` function to set context - DO NOT use SET commands directly.**

```sql
-- Correct way to set context (use this function)
SELECT tutor.set_context(
    'uuid-of-tenant'::UUID,
    'uuid-of-user'::UUID,
    'student'::tutor.user_role
);

-- WRONG - Do not use SET commands directly
-- SET app.current_tenant_id = 'uuid-of-tenant';  ❌
```

### Documentation

For detailed instructions on setting context, see **[README_CONTEXT.md](README_CONTEXT.md)**.

### Quick Example (Python/SQLAlchemy)

```python
from sqlalchemy.orm import Session
from sqlalchemy import text

def set_db_context(db: Session, tenant_id: UUID, user_id: UUID, user_role: str):
    """Set transaction-local context for RLS using tutor.set_context()"""
    db.execute(
        text("SELECT tutor.set_context(:tenant_id, :user_id, :role::tutor.user_role)"),
        {
            "tenant_id": str(tenant_id) if tenant_id else None,
            "user_id": str(user_id),
            "role": user_role
        }
    )
```

## Database Roles

### app_user
- Primary application role
- Full CRUD access to all tables
- RLS policies enforce tenant isolation
- Used by the API application
- Has EXECUTE permission on all functions in the `tutor` schema

### app_readonly
- Read-only access for reporting/analytics
- Can only SELECT from tables and views
- Useful for BI tools and reporting dashboards
- No write permissions

### app_migrator
- Full privileges for running migrations
- Should only be used during deployment
- Not for application runtime
- Can bypass RLS for migration operations

## Schema Overview

### Core Tables

- **tenants** - Multi-tenant educational institutions
- **tenant_domains** - Domain mappings for tenant resolution
- **subjects** - Subjects/courses (system-wide or tenant-specific)
- **user_accounts** - Parent table for tenant-scoped user accounts (students, tutors, tenant admins)
- **user_subject_roles** - Subject-level role assignments (student or tutor per subject)
- **student_subject_profiles** - Student-specific data per subject
- **tutor_subject_profiles** - Tutor-specific data per subject
- **tenant_admin_accounts** - Tenant administrator accounts (extends user_accounts)
- **system_admin_accounts** - System administrator accounts (separate table, not tenant-scoped)

### Quiz & Learning Tables

- **questions** - AI-generated quiz questions (system-wide or tenant-specific)
- **quiz_sessions** - Quiz session tracking
- **answer_submissions** - Student answer submissions with validation results
- **hints** - AI-generated hints for questions
- **student_progress** - Aggregated student progress statistics per subject

### Relationship Tables

- **student_tutor_assignments** - Student-tutor assignment relationships (subject-specific)
- **messages** - Student-tutor messaging system

### Competition Tables

- **competitions** - One-time competitions per subject (system-wide or tenant-specific)
- **competition_registrations** - Student registrations for competitions
- **competition_sessions** - Competition-specific quiz sessions

### System Tables

- **password_reset_otp** - Password reset OTP codes (hashed)
- **authentication_tokens** - JWT token storage (for tenant users and system admins)
- **audit_logs** - Audit trail for administrative actions

### Views

- **v_active_students_with_tutors** - Active students with their tutor assignments (by subject)
- **v_competition_leaderboard** - Competition leaderboards with rankings

### Helper Functions

The migration creates several helper functions for RLS and context management:

**Context Management:**
- `tutor.set_context(tenant_id, user_id, user_role)` - Set transaction-local context (MUST be called at start of each transaction)

**Context Retrieval:**
- `tutor.current_tenant_id()` - Get current tenant ID from context
- `tutor.current_user_id()` - Get current user ID from context
- `tutor.current_user_role()` - Get current user role from context

**Role Checks:**
- `tutor.is_system_admin()` - Check if current user is system admin
- `tutor.is_tenant_admin()` - Check if current user is tenant admin
- `tutor.is_tutor()` - Check if current user is tutor
- `tutor.is_student()` - Check if current user is student
- `tutor.has_student_role_for_subject(subject_id)` - Check if user has student role for a subject
- `tutor.has_tutor_role_for_subject(subject_id)` - Check if user has tutor role for a subject

**Access Control:**
- `tutor.can_access_tenant(tenant_id)` - Check if current user can access a tenant
- `tutor.can_access_student(student_id)` - Check if current user can access a student
- `tutor.can_access_tutor(tutor_id)` - Check if current user can access a tutor

## Security Considerations

1. **Tenant Isolation**: RLS policies ensure data isolation between tenants
2. **Role-Based Access**: Different access levels for students, tutors, and admins
3. **Password Security**: All passwords are hashed (bcrypt/Argon2) - never stored in plain text
4. **OTP Security**: OTP codes are hashed before storage
5. **Context Function**: Application must call `tutor.set_context()` at the start of each transaction (see README_CONTEXT.md)
6. **SSL/TLS**: Use encrypted connections for all database access

## Indexes

The migration includes comprehensive indexes for:
- Foreign key lookups
- Tenant-based queries
- Status filtering
- Date range queries
- Full-text search (questions and messages)
- Composite indexes for common query patterns

## Maintenance

### Vacuum and Analyze

Regular maintenance:

```sql
VACUUM ANALYZE;
```

### Monitor RLS Performance

Check RLS policy usage:

```sql
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE schemaname = 'tutor';
```

### Backup

Regular backups are essential:

```bash
pg_dump -U app_migrator -d tutor -F c -f backup_$(date +%Y%m%d).dump
```

## Troubleshooting

### RLS Policy Issues

If queries are returning no rows unexpectedly, check:
1. `tutor.set_context()` was called at the start of the transaction
2. User role matches expected role
3. Tenant ID matches the data's tenant_id
4. See README_CONTEXT.md for detailed troubleshooting

### Permission Errors

Ensure the application connects as `app_user` role, not as superuser.

### Migration Errors

If a migration fails:
1. Check PostgreSQL version (12+ required)
2. Verify extensions are installed
3. Check for existing objects that might conflict
4. Review error messages for specific issues

## Version History

- **1.0.0** - Initial schema with multi-tenancy, RLS, and competition support

## Support

For issues or questions, contact the development team.

