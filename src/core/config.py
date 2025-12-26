"""
Application configuration
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator
from typing import List, Optional
import os
from pathlib import Path
import json

# #region agent log
log_path = "/Users/pavnitbhatia/atduty/github/code/tutor-api/.cursor/debug.log"
def _log(hypothesis_id, location, message, data):
    try:
        with open(log_path, "a") as f:
            f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": hypothesis_id, "location": location, "message": message, "data": data, "timestamp": int(__import__("time").time() * 1000)}) + "\n")
    except: pass
# #endregion


class Settings(BaseSettings):
    """Application settings"""
    
    # Project
    PROJECT_NAME: str = "Quiz API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for AI-generated quiz questions for educational institutions"
    API_V1_PREFIX: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database - make optional to allow construction from components
    DATABASE_URL: Optional[str] = None
    
    # Individual DB components (for constructing DATABASE_URL if not provided)
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    
    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password
    PASSWORD_MIN_LENGTH: int = 8
    OTP_EXPIRATION_SECONDS: int = 900  # 15 minutes
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: Optional[List[str]] = None
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"
    
    # Email
    EMAIL_PROVIDER: Optional[str] = None  # sendgrid, ses, mailgun, smtp
    SENDGRID_API_KEY: Optional[str] = None
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    
    # Redis (optional)
    REDIS_URL: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_REQUESTS_PER_HOUR: int = 1000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    # Database role passwords (for migrations, not used by app)
    DB_APP_USER_PASSWORD: Optional[str] = None
    DB_APP_READONLY_PASSWORD: Optional[str] = None
    DB_APP_MIGRATOR_PASSWORD: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields instead of rejecting them
    
    # #region agent log
    @model_validator(mode='after')
    def construct_database_url(self):
        _log("A", "config.py:construct_database_url", "Validator called", {"has_database_url": bool(self.DATABASE_URL), "has_db_components": all([self.DB_HOST, self.DB_PORT, self.DB_NAME, self.DB_USER, self.DB_PASSWORD])})
        # #endregion
        # If DATABASE_URL is not provided, construct it from individual components
        if not self.DATABASE_URL:
            # #region agent log
            _log("B", "config.py:construct_database_url", "DATABASE_URL missing, checking components", {"db_host": bool(self.DB_HOST), "db_port": bool(self.DB_PORT), "db_name": bool(self.DB_NAME), "db_user": bool(self.DB_USER), "db_password": bool(self.DB_PASSWORD)})
            # #endregion
            if all([self.DB_HOST, self.DB_PORT, self.DB_NAME, self.DB_USER, self.DB_PASSWORD]):
                # #region agent log
                _log("B", "config.py:construct_database_url", "Constructing DATABASE_URL from components", {})
                # #endregion
                # URL-encode password to handle special characters
                from urllib.parse import quote_plus
                encoded_password = quote_plus(self.DB_PASSWORD)
                self.DATABASE_URL = f"postgresql://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
                # #region agent log
                _log("B", "config.py:construct_database_url", "DATABASE_URL constructed", {"database_url_set": bool(self.DATABASE_URL)})
                # #endregion
            else:
                # #region agent log
                _log("A", "config.py:construct_database_url", "Missing required DB components", {"missing": [k for k, v in {"DB_HOST": self.DB_HOST, "DB_PORT": self.DB_PORT, "DB_NAME": self.DB_NAME, "DB_USER": self.DB_USER, "DB_PASSWORD": self.DB_PASSWORD}.items() if not v]})
                # #endregion
                raise ValueError("Either DATABASE_URL or all of (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD) must be provided")
        
        # Final validation: DATABASE_URL must be set at this point
        if not self.DATABASE_URL:
            # #region agent log
            _log("A", "config.py:construct_database_url", "DATABASE_URL still None after validation", {})
            # #endregion
            raise ValueError("DATABASE_URL is required but was not provided and could not be constructed from components")
        
        # #region agent log
        _log("A", "config.py:construct_database_url", "Validator complete", {"database_url_set": bool(self.DATABASE_URL), "database_url_preview": self.DATABASE_URL[:50] + "..." if self.DATABASE_URL and len(self.DATABASE_URL) > 50 else self.DATABASE_URL})
        # #endregion
        return self


# #region agent log
_log("C", "config.py:before_settings", "About to load Settings", {"cwd": os.getcwd(), "env_file_exists": os.path.exists(".env")})
try:
    with open(".env", "r") as f:
        env_lines = f.readlines()
        _log("C", "config.py:before_settings", "Read .env file", {"line_count": len(env_lines), "line_12_preview": env_lines[11][:50] if len(env_lines) > 11 else "N/A"})
except Exception as e:
    _log("C", "config.py:before_settings", "Error reading .env", {"error": str(e)})
# #endregion

# Load settings
try:
    # #region agent log
    _log("A", "config.py:settings", "Creating Settings instance", {})
    # #endregion
    settings = Settings()
    # #region agent log
    _log("A", "config.py:settings", "Settings created successfully", {"database_url_set": bool(settings.DATABASE_URL)})
    # #endregion
except Exception as e:
    # #region agent log
    _log("A", "config.py:settings", "Settings creation failed", {"error": str(e), "error_type": type(e).__name__})
    # #endregion
    raise

