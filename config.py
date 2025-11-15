"""
Campus Resource Hub - Configuration Management
==============================================
MVC Role: Configuration Layer (supports all layers)
MCP Role: Provides context for AI-driven environment awareness

This module handles all application configuration including:
- Flask settings
- Database connections
- Security parameters
- Feature flags
- Environment-specific configurations
"""

import os
from datetime import timedelta
from pathlib import Path

# Base directory of the application
BASE_DIR = Path(__file__).parent.absolute()


class Config:
    """
    Base configuration class.
    Contains settings common to all environments.
    """

    # Flask Core Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database Configuration
    # Allow DATABASE env variable to override the database file (useful for testing)
    DATABASE_FILE = os.environ.get('DATABASE', 'campus_resource_hub.db')
    DATABASE_URL = os.environ.get('DATABASE_URL') or f'sqlite:///{BASE_DIR}/{DATABASE_FILE}'
    DATABASE_PATH = os.path.join(BASE_DIR, DATABASE_FILE)

    # Security Settings
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

    # CSRF Protection (Flask-WTF)
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # No time limit for CSRF tokens

    # File Upload Settings
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'src', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx'}

    # Email Configuration (Flask-Mail)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@campusresourcehub.edu')

    # Pagination
    ITEMS_PER_PAGE = 20

    # AI Features
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    AI_CONCIERGE_ENABLED = bool(OPENAI_API_KEY or ANTHROPIC_API_KEY)

    # Google Calendar Integration
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    CALENDAR_SYNC_ENABLED = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)

    # Rate Limiting
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'True').lower() == 'true'
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '100 per hour')
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')

    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(BASE_DIR, 'logs', 'app.log')

    @staticmethod
    def init_app(app):
        """
        Initialize application with this configuration.
        Can be overridden in subclasses for environment-specific initialization.
        """
        # Create upload folder if it doesn't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Create logs folder if it doesn't exist
        os.makedirs(os.path.dirname(app.config['LOG_FILE']), exist_ok=True)


class DevelopmentConfig(Config):
    """
    Development environment configuration.
    Enables debugging and relaxed security for local development.
    """
    DEBUG = True
    TESTING = False

    # Relaxed security for development
    SESSION_COOKIE_SECURE = False

    # More verbose logging
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """
    Testing environment configuration.
    Uses in-memory database and disables CSRF for testing.
    """
    DEBUG = True
    TESTING = True

    # In-memory SQLite database for tests
    DATABASE_URL = 'sqlite:///:memory:'
    DATABASE_PATH = ':memory:'

    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False

    # Fast password hashing for tests
    BCRYPT_LOG_ROUNDS = 4


class ProductionConfig(Config):
    """
    Production environment configuration.
    Enforces strict security and uses production database.
    """
    DEBUG = False
    TESTING = False

    # Strict security in production
    SESSION_COOKIE_SECURE = True

    # Production database (PostgreSQL recommended)
    DATABASE_URL = os.environ.get('DATABASE_URL') or Config.DATABASE_URL

    # Stricter rate limiting
    RATELIMIT_DEFAULT = '50 per hour'

    @classmethod
    def init_app(cls, app):
        """Production-specific initialization."""
        Config.init_app(app)

        # Log to syslog or external service in production
        import logging
        from logging.handlers import SysLogHandler

        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """
    Get configuration object by name.

    Args:
        config_name (str): Name of configuration ('development', 'testing', 'production')
                          If None, uses FLASK_ENV environment variable or 'default'

    Returns:
        Config: Configuration class
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    return config.get(config_name, config['default'])
