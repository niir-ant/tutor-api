# Creating System Admin from Environment Variables

The easiest way to create a system admin account is using environment variables with the Python script.

## Quick Start

1. **Add variables to your `.env` file**:

```bash
SYSTEM_ADMIN_USERNAME=psingh
SYSTEM_ADMIN_EMAIL=psingh@atduty.com
SYSTEM_ADMIN_NAME=System Administrator
SYSTEM_ADMIN_PASSWORD=your_temporary_password_here
```

2. **Run the Python script**:

```bash
python scripts/create_system_admin_from_env.py
```

That's it! The script will:
- Read values from `.env` file
- Generate password hash automatically
- Create or update the system admin account
- Display the account details

## Environment Variables

Add these to your `.env` file:

| Variable | Required | Description |
|----------|----------|-------------|
| `SYSTEM_ADMIN_USERNAME` | Yes | Username for the system admin account |
| `SYSTEM_ADMIN_EMAIL` | Yes | Email address for the system admin |
| `SYSTEM_ADMIN_NAME` | No | Full name (defaults to "System Administrator") |
| `SYSTEM_ADMIN_PASSWORD` | Yes | Temporary password (will be changed on first login) |

## Example `.env` Entry

```bash
# System Admin Account Creation
SYSTEM_ADMIN_USERNAME=admin
SYSTEM_ADMIN_EMAIL=admin@example.com
SYSTEM_ADMIN_NAME=System Administrator
SYSTEM_ADMIN_PASSWORD=TempPassword123!
```

## Alternative: Set Variables Inline

You can also set variables inline without modifying `.env`:

```bash
SYSTEM_ADMIN_USERNAME=admin \
SYSTEM_ADMIN_EMAIL=admin@example.com \
SYSTEM_ADMIN_PASSWORD=TempPassword123! \
python scripts/create_system_admin_from_env.py
```

## What the Script Does

1. Loads environment variables from `.env` file
2. Validates that required variables are set
3. Generates bcrypt password hash
4. Checks if account already exists (by username or email)
5. Creates new account or updates existing one
6. Displays account details and temporary password

## Security Notes

- The temporary password is displayed in the output - save it securely
- Change the password immediately after first login
- Never commit `.env` file to version control
- Use strong temporary passwords
- Delete credential files after use

## Troubleshooting

### Error: "SYSTEM_ADMIN_USERNAME environment variable is required"
- Make sure the variable is set in your `.env` file
- Or set it inline when running the script

### Error: "Account exists but is not a system_admin"
- An account with that username/email exists but has a different role
- Delete the existing account first, or use different credentials

### Error: Database connection failed
- Check your `DATABASE_URL` in `.env` file
- Ensure the database is running and accessible

