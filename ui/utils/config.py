"""
Configuration for UI
"""
import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from ui directory
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


def get_api_base_url() -> str:
    """Get API base URL from environment or default"""
    return os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")


def get_app_title() -> str:
    """Get application title"""
    return os.getenv("APP_TITLE", "Quiz API - Educational Platform")

