#!/usr/bin/env python3
"""
Create system admin account in the database from environment variables.

This script reads admin account details from environment variables and creates
or updates the system admin account directly in the database.

Environment variables required:
    SYSTEM_ADMIN_USERNAME - Username for the system admin
    SYSTEM_ADMIN_EMAIL - Email address for the system admin
    SYSTEM_ADMIN_NAME - Full name of the system admin (optional, defaults to "System Administrator")
    SYSTEM_ADMIN_PASSWORD - Temporary password (will be hashed)

Usage:
    python scripts/create_system_admin_from_env.py

Or set variables inline:
    SYSTEM_ADMIN_USERNAME=admin SYSTEM_ADMIN_EMAIL=admin@example.com SYSTEM_ADMIN_PASSWORD=temp123 python scripts/create_system_admin_from_env.py
"""
import os
import sys
import uuid
from pathlib import Path

# Try to use bcrypt directly first (more reliable)
try:
    import bcrypt
    USE_BCRYPT_DIRECT = True
except ImportError:
    USE_BCRYPT_DIRECT = False
    # Fallback to passlib if bcrypt not available
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    except ImportError:
        print("Error: Neither bcrypt nor passlib is available.")
        print("Please install: pip install bcrypt")
        sys.exit(1)

# Load .env file (with error handling)
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path, verbose=False)  # verbose=False to suppress parsing warnings
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")
    print("Continuing with environment variables from system...")

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import database modules
try:
    from src.core.database import SessionLocal
    from src.models.user import UserRole, AccountStatus
    from sqlalchemy import text
    DB_AVAILABLE = True
except ImportError as e:
    DB_AVAILABLE = False
    print(f"Warning: Could not import database modules: {e}")
    print("Make sure database migrations have been run and dependencies are installed.")


def get_password_hash_safe(password: str) -> str:
    """
    Generate password hash using bcrypt directly (more reliable than passlib).
    Falls back to passlib if bcrypt is not available.
    """
    # Ensure password is bytes (bcrypt requirement)
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = password
    
    # Truncate password if longer than 72 bytes (bcrypt limit)
    if len(password_bytes) > 72:
        print(f"Warning: Password is longer than 72 bytes, truncating...")
        password_bytes = password_bytes[:72]
    
    # Generate bcrypt hash
    if USE_BCRYPT_DIRECT:
        # Use bcrypt directly (more reliable)
        salt = bcrypt.gensalt(rounds=12)
        password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    else:
        # Fallback to passlib
        password_hash = pwd_context.hash(password)
    
    return password_hash


def create_system_admin_from_env():
    """
    Create system admin account in database from environment variables.
    
    Note: This script creates accounts in the tutor.system_admin_accounts table.
    System admins are not tenant-scoped (no tenant_id).
    
    RLS Note: According to migration 0.0.30__rls_policies.sql, the app_migrator
    role can insert/update system admin accounts. For initial setup, ensure the
    DATABASE_URL uses a user with appropriate permissions (app_migrator or app_user
    with proper context set).
    """
    # Get values from environment
    username = os.getenv("SYSTEM_ADMIN_USERNAME")
    email = os.getenv("SYSTEM_ADMIN_EMAIL")
    name = os.getenv("SYSTEM_ADMIN_NAME", "System Administrator")
    password = os.getenv("SYSTEM_ADMIN_PASSWORD")
    
    # Validate required variables
    if not username:
        print("Error: SYSTEM_ADMIN_USERNAME environment variable is required")
        print("Add it to your .env file or set it as an environment variable")
        sys.exit(1)
    
    if not email:
        print("Error: SYSTEM_ADMIN_EMAIL environment variable is required")
        print("Add it to your .env file or set it as an environment variable")
        sys.exit(1)
    
    if not password:
        print("Error: SYSTEM_ADMIN_PASSWORD environment variable is required")
        print("Set a temporary password that will be changed on first login")
        print("Add it to your .env file or set it as an environment variable")
        sys.exit(1)
    
    # Check if database modules are available
    if not DB_AVAILABLE:
        print("Error: Database modules are not available.")
        print("Make sure database migrations have been run and dependencies are installed.")
        sys.exit(1)
    
    # Generate password hash
    print("Generating password hash...")
    password_hash = get_password_hash_safe(password)
    
    # Create database session
    db = SessionLocal()
    try:
        # Set search path to tutor schema (as per migration files)
        # This ensures we can find tables in the tutor schema
        db.execute(text("SET search_path TO tutor, public"))
        db.commit()
        
        # Check if account already exists by username or email
        # Use raw SQL to query tutor.system_admin_accounts directly
        existing_by_username = db.execute(
            text("""
                SELECT admin_id, username, email, name, role, account_status, requires_password_change
                FROM tutor.system_admin_accounts
                WHERE username = :username
                LIMIT 1
            """),
            {"username": username}
        ).fetchone()
        
        existing_by_email = db.execute(
            text("""
                SELECT admin_id, username, email, name, role, account_status, requires_password_change
                FROM tutor.system_admin_accounts
                WHERE email = :email
                LIMIT 1
            """),
            {"email": email}
        ).fetchone()
        
        existing = existing_by_username or existing_by_email
        
        if existing:
            # Update existing account
            admin_id = existing[0]
            existing_role = existing[4]  # role is at index 4
            
            # Verify it's a system_admin before updating
            if existing_role != 'system_admin':
                print(f"❌ Error: Account with username '{existing[1]}' or email '{existing[2]}' exists but is not a system_admin")
                print(f"   Current role: {existing_role}")
                sys.exit(1)
            
            # Update the account
            db.execute(
                text("""
                    UPDATE tutor.system_admin_accounts
                    SET email = :email,
                        username = :username,
                        password_hash = :password_hash,
                        name = :name,
                        role = 'system_admin'::tutor.user_role,
                        account_status = 'pending_activation'::tutor.account_status,
                        requires_password_change = TRUE,
                        updated_at = NOW()
                    WHERE admin_id = CAST(:admin_id AS uuid)::uuid
                """),
                {
                    "admin_id": str(admin_id),
                    "email": email,
                    "username": username,
                    "password_hash": password_hash,
                    "name": name
                }
            )
            db.commit()
            
            print("\n" + "=" * 60)
            print("✅ Updated existing system admin account!")
            print("=" * 60)
            print(f"Admin ID: {admin_id}")
            print(f"Username: {username}")
            print(f"Email: {email}")
            print(f"Name: {name}")
            print(f"Role: system_admin")
            print(f"Status: pending_activation")
            print("=" * 60)
            print(f"Temporary Password: {password}")
            print("⚠️  IMPORTANT: Change password on first login!")
            print("=" * 60)
        else:
            # Create new account
            admin_id = uuid.uuid4()
            
            db.execute(
                text("""
                    INSERT INTO tutor.system_admin_accounts (
                        admin_id,
                        username,
                        email,
                        password_hash,
                        name,
                        role,
                        account_status,
                        requires_password_change,
                        created_at,
                        updated_at
                    ) VALUES (
                        CAST(:admin_id AS uuid),
                        :username,
                        :email,
                        :password_hash,
                        :name,
                        'system_admin'::tutor.user_role,
                        'pending_activation'::tutor.account_status,
                        TRUE,
                        NOW(),
                        NOW()
                    )
                """),
                {
                    "admin_id": str(admin_id),
                    "username": username,
                    "email": email,
                    "password_hash": password_hash,
                    "name": name
                }
            )
            db.commit()
            
            print("\n" + "=" * 60)
            print("✅ Created new system admin account!")
            print("=" * 60)
            print(f"Admin ID: {admin_id}")
            print(f"Username: {username}")
            print(f"Email: {email}")
            print(f"Name: {name}")
            print(f"Role: system_admin")
            print(f"Status: pending_activation")
            print("=" * 60)
            print(f"Temporary Password: {password}")
            print("⚠️  IMPORTANT: Change password on first login!")
            print("=" * 60)
            
    except Exception as e:
        db.rollback()
        
        # Check for specific database errors (table doesn't exist)
        error_str = str(e).lower()
        is_table_missing = (
            "does not exist" in error_str or 
            "undefinedtable" in error_str or 
            ("relation" in error_str and (
                "administrator_accounts" in error_str or 
                "system_admin_accounts" in error_str
            ))
        )
        
        if is_table_missing:
            print("\n❌ Error: Database table 'tutor.system_admin_accounts' does not exist.")
            print("\n💡 This usually means database migrations haven't been run yet.")
            print("   Please run migrations first:")
            print("   1. alembic upgrade head")
            print("   OR")
            print("   2. Run the SQL migration files from db/migration/ in order:")
            print("      - 0.0.10__initial_schema.sql")
            print("      - 0.0.20__indexes_and_constraints.sql")
            print("      - 0.0.30__rls_policies.sql")
            print("      - 0.0.40__roles_and_permissions.sql")
            print("\n   After migrations are complete, run this script again.")
        else:
            print(f"\n❌ Error creating system admin account: {e}")
            import traceback
            traceback.print_exc()
        
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    create_system_admin_from_env()

