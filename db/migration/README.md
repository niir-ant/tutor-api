# Database Migrations

This directory contains PostgreSQL migration scripts for the Quiz API database schema.

## Migration Files

The migrations follow Semantic Versioning (SemVer) naming convention: `major.minor.patch__description.sql`

- `0.0.10__initial_schema.sql` - Initial database schema with all tables, types, and triggers
- `0.0.20__indexes_and_constraints.sql` - Indexes and constraints for performance
- `0.0.30__rls_policies.sql` - Row Level Security (RLS) policies for multi-tenant isolation
- `0.0.40__roles_and_permissions.sql` - Database roles and permissions

## Prerequisites

- PostgreSQL 12 or higher
- `uuid-ossp` extension (for UUID generation)
- `pgcrypto` extension (for cryptographic functions)

## Running Migrations

### Using psql

```bash
# Connect to your database
psql -U postgres -d quiz_api

# Run migrations in order
\i 0.0.10__initial_schema.sql
\i 0.0.20__indexes_and_constraints.sql
\i 0.0.30__rls_policies.sql
\i 0.0.40__roles_and_permissions.sql
```

### Using a Migration Tool

If using a migration tool like `migrate` (golang-migrate), `Flyway`, or `Liquibase`:

```bash
# Example with golang-migrate
migrate -path db/migration -database "postgres://user:password@localhost/quiz_api?sslmode=disable" up
```

## Database Setup

### 1. Create Database

```sql
CREATE DATABASE quiz_api;
\c quiz_api
```

### 2. Run Migrations

Execute all migration files in order.

### 3. Update Passwords

**IMPORTANT**: Change default passwords in `0.0.40__roles_and_permissions.sql`:

```sql
ALTER ROLE app_user WITH PASSWORD 'your_secure_password';
ALTER ROLE app_readonly WITH PASSWORD 'your_secure_password';
ALTER ROLE app_migrator WITH PASSWORD 'your_secure_password';
```

## Row Level Security (RLS)

The database uses Row Level Security to enforce multi-tenant data isolation. The application must set the following session variables for each database connection:

```sql
SET app.current_tenant_id = 'uuid-of-tenant';
SET app.current_user_id = 'uuid-of-user';
SET app.current_user_role = 'student' | 'tutor' | 'tenant_admin' | 'system_admin';
```

### Example Application Code (Python/psycopg2)

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="quiz_api",
    user="app_user",
    password="your_password"
)

cursor = conn.cursor()
cursor.execute("SET app.current_tenant_id = %s", (tenant_id,))
cursor.execute("SET app.current_user_id = %s", (user_id,))
cursor.execute("SET app.current_user_role = %s", (user_role,))
conn.commit()
```

## Database Roles

### app_user
- Primary application role
- Full CRUD access to all tables
- RLS policies enforce tenant isolation
- Used by the API application

### app_readonly
- Read-only access for reporting/analytics
- Can only SELECT from tables
- Useful for BI tools and reporting dashboards

### app_migrator
- Full privileges for running migrations
- Should only be used during deployment
- Not for application runtime

## Schema Overview

### Core Tables

- **tenants** - Multi-tenant educational institutions
- **tenant_domains** - Domain mappings for tenant resolution
- **subjects** - Subjects/courses (system-wide or tenant-specific)
- **student_accounts** - Student user accounts
- **tutor_accounts** - Tutor user accounts
- **administrator_accounts** - Admin accounts (tenant and system level)

### Quiz & Learning Tables

- **questions** - AI-generated quiz questions
- **quiz_sessions** - Quiz session tracking
- **answer_submissions** - Student answer submissions
- **hints** - AI-generated hints
- **student_progress** - Aggregated progress statistics

### Relationship Tables

- **student_tutor_assignments** - Student-tutor relationships
- **messages** - Student-tutor messaging

### Competition Tables

- **competitions** - One-time competitions per subject
- **competition_registrations** - Student registrations
- **competition_sessions** - Competition-specific sessions

### System Tables

- **password_reset_otp** - Password reset tokens
- **authentication_tokens** - JWT token storage
- **audit_logs** - Audit trail for admin actions

## Security Considerations

1. **Tenant Isolation**: RLS policies ensure data isolation between tenants
2. **Role-Based Access**: Different access levels for students, tutors, and admins
3. **Password Security**: All passwords are hashed (bcrypt/Argon2) - never stored in plain text
4. **OTP Security**: OTP codes are hashed before storage
5. **Session Variables**: Application must set tenant/user context for each connection
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
WHERE schemaname = 'public';
```

### Backup

Regular backups are essential:

```bash
pg_dump -U app_migrator -d quiz_api -F c -f backup_$(date +%Y%m%d).dump
```

## Troubleshooting

### RLS Policy Issues

If queries are returning no rows unexpectedly, check:
1. Session variables are set correctly
2. User role matches expected role
3. Tenant ID matches the data's tenant_id

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

