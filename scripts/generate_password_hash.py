#!/usr/bin/env python3
"""
Helper script to generate bcrypt password hash for system admin account creation.

Usage:
    python scripts/generate_password_hash.py
    
    Or with a specific password:
    python scripts/generate_password_hash.py "MySecurePassword123!"
"""
import sys
import secrets
from passlib.context import CryptContext

# Initialize password hashing context (same as in the application)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_password_hash(password: str = None) -> str:
    """
    Generate a bcrypt hash for a password.
    
    Args:
        password: Plain text password. If None, generates a random secure password.
    
    Returns:
        Tuple of (password, password_hash)
    """
    if password is None:
        # Generate a secure random password
        password = secrets.token_urlsafe(16)
    
    # Generate bcrypt hash
    password_hash = pwd_context.hash(password)
    
    return password, password_hash


def main():
    """Main function"""
    print("=" * 60)
    print("System Admin Password Hash Generator")
    print("=" * 60)
    print()
    
    # Get password from command line or generate one
    if len(sys.argv) > 1:
        password = sys.argv[1]
        print(f"Using provided password...")
    else:
        password, _ = generate_password_hash()
        print("Generated secure random password...")
    
    # Generate hash
    _, password_hash = generate_password_hash(password)
    
    print()
    print("=" * 60)
    print("Password Hash Generated Successfully!")
    print("=" * 60)
    print()
    print("Temporary Password (for first login):")
    print(f"  {password}")
    print()
    print("Password Hash (use in SQL script):")
    print(f"  {password_hash}")
    print()
    print("=" * 60)
    print("Instructions:")
    print("=" * 60)
    print("1. Copy the password hash above")
    print("2. Use it in the SQL script: scripts/create_first_system_admin.sql")
    print("3. Replace 'PASSWORD_HASH_HERE' with the hash above")
    print("4. Or use the DO block version which generates it automatically")
    print("5. Save the temporary password - you'll need it for first login")
    print("6. Change password immediately after first login!")
    print("=" * 60)
    
    # Also write to a file for convenience
    output_file = "scripts/system_admin_credentials.txt"
    try:
        with open(output_file, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("System Admin Credentials\n")
            f.write("=" * 60 + "\n")
            f.write(f"Temporary Password: {password}\n")
            f.write(f"Password Hash: {password_hash}\n")
            f.write("=" * 60 + "\n")
            f.write("IMPORTANT: Keep this file secure and delete after use!\n")
            f.write("=" * 60 + "\n")
        print(f"\nCredentials also saved to: {output_file}")
        print("⚠️  Remember to delete this file after use!")
    except Exception as e:
        print(f"\nWarning: Could not write to file: {e}")


if __name__ == "__main__":
    main()

