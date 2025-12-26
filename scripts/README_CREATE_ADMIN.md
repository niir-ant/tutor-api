# Creating the First System Admin Account

This guide explains how to create the first system administrator account in the database.

## Prerequisites

- Database migrations have been run
- PostgreSQL database is accessible
- You have database admin privileges

## Method 1: Using Environment Variables (Recommended)

**This is the easiest and most secure method.**

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
- Generate password hash
- Create or update the account
- Display account details

See `README_ENV_ADMIN.md` for more details.

## Method 2: Using SQL Script with pgcrypto

If your PostgreSQL database has the `pgcrypto` extension available:

1. **Enable pgcrypto extension** (if not already enabled):
   ```sql
   CREATE EXTENSION IF NOT EXISTS pgcrypto;
   ```

2. **Edit the SQL script** to set your credentials:
   ```bash
   # Edit scripts/create_first_system_admin.sql
   # Update these variables in the DO block:
   #   - temp_password: Your temporary password
   #   - admin_username: Your desired username
   #   - admin_email: Your email address
   #   - admin_name: Your full name
   ```

3. **Run the SQL script**:
   ```bash
   psql -U your_db_user -d your_database -f scripts/create_first_system_admin.sql
   ```

4. **Note the temporary password** from the output - you'll need it for first login.

## Method 2: Using Python Helper Script

If `pgcrypto` is not available, use the Python script to generate the password hash:

1. **Generate password hash**:
   ```bash
   python scripts/generate_password_hash.py
   ```
   
   Or with a specific password:
   ```bash
   python scripts/generate_password_hash.py "MySecurePassword123!"
   ```

2. **Copy the password hash** from the output.

3. **Edit the SQL script** and use the manual INSERT statement:
   - Uncomment the "Alternative: Manual INSERT" section
   - Replace `PASSWORD_HASH_HERE` with the hash from step 2
   - Update username, email, and name fields

4. **Run the SQL script**:
   ```bash
   psql -U your_db_user -d your_database -f scripts/create_first_system_admin.sql
   ```

## Method 3: Direct Python Script (Alternative)

You can also create a Python script that directly inserts into the database:

```python
from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.models.database import AdministratorAccount
from src.core.security import get_password_hash
from src.models.user import UserRole, AccountStatus
import secrets

def create_system_admin():
    db = SessionLocal()
    try:
        temp_password = secrets.token_urlsafe(16)
        password_hash = get_password_hash(temp_password)
        
        admin = AdministratorAccount(
            tenant_id=None,  # System admin has no tenant
            username='admin',
            email='admin@example.com',
            password_hash=password_hash,
            name='System Administrator',
            role=UserRole.SYSTEM_ADMIN,
            account_status=AccountStatus.PENDING_ACTIVATION,
            requires_password_change=True
        )
        
        db.add(admin)
        db.commit()
        
        print(f"System admin created!")
        print(f"Username: admin")
        print(f"Temporary password: {temp_password}")
        print("Change password on first login!")
        
    finally:
        db.close()

if __name__ == "__main__":
    create_system_admin()
```

## First Login

After creating the account:

1. **Login via UI or API**:
   - Username: The username you set
   - Password: The temporary password
   - Domain: Use any valid tenant domain (system admin can use any domain)

2. **Change password**: The system will require you to change the password on first login.

3. **Account activation**: After changing password, the account status will automatically change from `pending_activation` to `active`.

## Important Notes

- **System admins have `tenant_id = NULL`** - they don't belong to any tenant
- **Domain requirement**: Even though system admins don't have a tenant, the login endpoint currently requires a domain parameter. Use any valid tenant domain.
- **Security**: 
  - Use a strong temporary password
  - Change password immediately after first login
  - Delete any credential files after use
  - Never commit passwords or hashes to version control

## Troubleshooting

### Error: "role does not exist"
- Make sure the `user_role` enum includes `'system_admin'`
- Check that migrations have been run

### Error: "tenant_id constraint violation"
- System admin must have `tenant_id = NULL`
- Make sure you're not setting a tenant_id for system_admin

### Error: "username or email already exists"
- The account may already exist
- Check existing accounts: `SELECT * FROM administrator_accounts WHERE role = 'system_admin';`
- Delete and recreate if needed (be careful!)

### Login fails with "Domain is required"
- The authentication service requires a domain parameter
- Use any valid tenant domain from your database
- This is a known limitation - system admins should be able to login without domain

