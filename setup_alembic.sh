#!/bin/bash
# Setup script for Alembic local environment

set -e

echo "🚀 Setting up Alembic for local environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "⚠️  Please edit .env and set your DATABASE_URL and other configuration"
    else
        echo "DATABASE_URL=postgresql://postgres:password@localhost:5432/tutor" > .env
        echo "⚠️  Created .env file. Please update with your database credentials"
    fi
fi

# Check database connection
echo "🔍 Checking database connection..."
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL client found"
else
    echo "⚠️  PostgreSQL client not found. Make sure PostgreSQL is installed."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and set your DATABASE_URL (REQUIRED)"
echo "2. Optionally configure other settings in .env (JWT, AI keys, etc.)"
echo "3. Create database: createdb tutor (or via psql)"
echo "4. Run migrations: alembic upgrade head"
echo ""
echo "To activate virtual environment in the future:"
echo "  source venv/bin/activate"

