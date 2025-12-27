# Creating the First System Admin Account

This guide explains how to create the first system administrator account in the database.

## Prerequisites

- Database migrations have been run (all migration files from `db/migration/`):
  - `0.0.10__initial_schema.sql`
  - `0.0.20__indexes_and_constraints.sql`
  - `0.0.30__rls_policies.sql`
  - `0.0.40__roles_and_permissions.sql`
- PostgreSQL database is accessible
- `DATABASE_URL` is configured in your `.env` file

## Method 1: Using Environment Variables (Recommended)

**This is the easiest and most secure method.**

### Quick Start

1. **Add variables to your `.env` file**:
   ```bash
   SYSTEM_ADMIN_USERNAME=psingh
   SYSTEM_ADMIN_EMAIL=psingh@atduty.com
   SYSTEM_ADMIN_NAME=System Administrator
   SYSTEM_ADMIN_PASSWORD=your_temporary_password
   ```

2. **Run the Python script**:
   ```bash
   python scripts/create_system_admin_from_env.py
   ```

The script will automatically:
- Read values from `.env` file
- Generate password hash using bcrypt
- Create or update the account in `tutor.system_admin_accounts` table
- Display account details

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SYSTEM_ADMIN_USERNAME` | Yes | Username for the system admin account |
| `SYSTEM_ADMIN_EMAIL` | Yes | Email address for the system admin |
| `SYSTEM_ADMIN_NAME` | No | Full name (defaults to "System Administrator") |
| `SYSTEM_ADMIN_PASSWORD` | Yes | Temporary password (will be changed on first login) |

### Example `.env` Entry

```bash
# System Admin Account Creation
SYSTEM_ADMIN_USERNAME=admin
SYSTEM_ADMIN_EMAIL=admin@example.com
SYSTEM_ADMIN_NAME=System Administrator
SYSTEM_ADMIN_PASSWORD=TempPassword123!
```

### Alternative: Set Variables Inline

You can also set variables inline without modifying `.env`:

```bash
SYSTEM_ADMIN_USERNAME=admin \
SYSTEM_ADMIN_EMAIL=admin@example.com \
SYSTEM_ADMIN_PASSWORD=TempPassword123! \
python scripts/create_system_admin_from_env.py
```

### What the Script Does

1. Loads environment variables from `.env` file
2. Validates that required variables are set
3. Generates bcrypt password hash (using bcrypt directly or passlib as fallback)
4. Sets database search path to `tutor` schema
5. Checks if account already exists (by username or email in `tutor.system_admin_accounts`)
6. Creates new account or updates existing one
7. Displays account details and temporary password

## First Login

After creating the account:

1. **Login via UI or API**:
   - Username: The username you set
   - Password: The temporary password
   - Domain: Use any valid tenant domain (system admin can use any domain)

2. **Change password**: The system will require you to change the password on first login.

3. **Account activation**: After changing password, the account status will automatically change from `pending_activation` to `active`.

## Important Notes

- **System admins are not tenant-scoped**: They have `tenant_id = NULL` and don't belong to any tenant
- **Table location**: Accounts are stored in `tutor.system_admin_accounts` table
- **Schema**: The script automatically sets the search path to the `tutor` schema
- **Domain requirement**: Even though system admins don't have a tenant, the login endpoint currently requires a domain parameter. Use any valid tenant domain.
- **Security**: 
  - Use a strong temporary password
  - Change password immediately after first login
  - Delete any credential files after use
  - Never commit passwords or hashes to version control
  - Never commit `.env` file to version control

## Troubleshooting

### Error: "Database table 'tutor.system_admin_accounts' does not exist"

**Cause**: Database migrations haven't been run yet.

**Solution**: Run migrations first:
```bash
# Option 1: Using Alembic
alembic upgrade head

# Option 2: Run SQL files manually (in order)
psql -U your_db_user -d your_database -f db/migration/0.0.10__initial_schema.sql
psql -U your_db_user -d your_database -f db/migration/0.0.20__indexes_and_constraints.sql
psql -U your_db_user -d your_database -f db/migration/0.0.30__rls_policies.sql
psql -U your_db_user -d your_database -f db/migration/0.0.40__roles_and_permissions.sql
```

### Error: "SYSTEM_ADMIN_USERNAME environment variable is required"

**Cause**: Required environment variable is not set.

**Solution**: 
- Add the variable to your `.env` file
- Or set it inline when running the script (see "Alternative: Set Variables Inline" above)

### Error: "Account exists but is not a system_admin"

**Cause**: An account with that username/email exists but has a different role.

**Solution**: 
- Delete the existing account first, or use different credentials
- Check existing accounts: 
  ```sql
  SELECT * FROM tutor.system_admin_accounts WHERE username = 'your_username' OR email = 'your_email';
  ```

### Error: Database connection failed

**Cause**: Database connection issues.

**Solution**:
- Check your `DATABASE_URL` in `.env` file
- Ensure the database is running and accessible
- Verify database credentials are correct
- Check network connectivity to the database server

### Error: "role does not exist" or enum type errors

**Cause**: The `user_role` or `account_status` enum types don't exist.

**Solution**:
- Make sure migrations have been run (especially `0.0.10__initial_schema.sql`)
- Check that the `tutor.user_role` enum includes `'system_admin'`
- Check that the `tutor.account_status` enum exists

### Error: Permission denied or RLS policy errors

**Cause**: The database user doesn't have proper permissions or RLS is blocking access.

**Solution**:
- Ensure you're using a database user with appropriate permissions (e.g., `app_migrator` role)
- According to migration `0.0.30__rls_policies.sql`, the `app_migrator` role can insert/update system admin accounts
- For initial setup, you may need to connect as a superuser or temporarily disable RLS

### Login fails with "Domain is required"

**Cause**: The authentication service requires a domain parameter.

**Solution**:
- Use any valid tenant domain from your database
- This is a known limitation - system admins should be able to login without domain
- Check available domains: 
  ```sql
  SELECT domain FROM tutor.tenant_domains WHERE status = 'active';
  ```

## Database Schema Reference

The system admin account is stored in the `tutor.system_admin_accounts` table with the following structure:

- `admin_id` (UUID, primary key)
- `username` (VARCHAR(100), unique, not null)
- `email` (VARCHAR(255), unique, not null)
- `password_hash` (VARCHAR(255), not null)
- `name` (VARCHAR(255), not null)
- `role` (tutor.user_role enum, default: 'system_admin')
- `account_status` (tutor.account_status enum, default: 'pending_activation')
- `requires_password_change` (BOOLEAN, default: TRUE)
- `permissions` (TEXT[])
- `failed_login_attempts` (INTEGER, default: 0)
- `locked_until` (TIMESTAMP WITH TIME ZONE)
- `created_at` (TIMESTAMP WITH TIME ZONE)
- `updated_at` (TIMESTAMP WITH TIME ZONE)
- `last_login` (TIMESTAMP WITH TIME ZONE)
- `created_by` (UUID, references system_admin_accounts.admin_id)

**Note**: System admins do NOT have a `tenant_id` column - they are not tenant-scoped.

## Security Best Practices

1. **Use strong temporary passwords**: At least 12 characters with mixed case, numbers, and symbols
2. **Change password immediately**: After first login, change the password to something secure
3. **Protect credentials**: Never commit `.env` files or passwords to version control
4. **Rotate credentials**: Periodically review and update system admin accounts
5. **Audit access**: Monitor system admin account usage and login attempts
6. **Limit accounts**: Only create system admin accounts for users who truly need system-level access
