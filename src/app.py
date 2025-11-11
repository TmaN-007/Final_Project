"""
Campus Resource Hub - Flask Application Factory
===============================================
MVC Role: Application Initialization & Configuration
MCP Role: Central coordination point for AI-assisted development context

This module implements the Flask application factory pattern, which:
1. Creates and configures the Flask app
2. Registers blueprints (controllers)
3. Initializes extensions (security, database connections)
4. Sets up error handlers
5. Configures logging

Factory Pattern Benefits:
- Multiple app instances for testing
- Cleaner configuration management
- Easier extension initialization
"""

import os
import logging
from flask import Flask, render_template, jsonify
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from pathlib import Path

# Import configuration
from config import get_config

# Initialize extensions (configured later in create_app)
csrf = CSRFProtect()
login_manager = LoginManager()


def create_app(config_name=None):
    """
    Application Factory Function.

    Creates and configures a Flask application instance using the factory pattern.
    This allows for multiple app configurations (dev, test, production) and
    makes testing easier.

    Args:
        config_name (str): Configuration name ('development', 'testing', 'production')
                          If None, uses FLASK_ENV environment variable

    Returns:
        Flask: Configured Flask application instance

    Example:
        >>> app = create_app('development')
        >>> app.run(debug=True)
    """

    # Create Flask app instance
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    config_class.init_app(app)

    # Initialize Flask extensions
    init_extensions(app)

    # Register blueprints (controllers)
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Setup logging
    setup_logging(app)

    # Context processors (make variables available to all templates)
    register_template_context(app)

    # Application shell context (for flask shell command)
    register_shell_context(app)

    return app


def init_extensions(app):
    """
    Initialize Flask extensions.

    Extensions are initialized here to avoid circular imports and to
    keep the application factory clean.

    Args:
        app (Flask): Flask application instance
    """

    # CSRF Protection (Flask-WTF)
    csrf.init_app(app)

    # Login Manager (Flask-Login)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Redirect to login page if not authenticated
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # User loader callback for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        """
        Load user by ID for Flask-Login.
        Returns a User object, not a dict.
        """
        from src.data_access.user_dal import UserDAL
        from src.models.user import User

        user_data = UserDAL.get_user_by_id(int(user_id))
        if user_data:
            return User(user_data)
        return None

    # TODO: Initialize Flask-Mail when email notifications are implemented
    # mail.init_app(app)


def register_blueprints(app):
    """
    Register Flask blueprints (controllers).

    Blueprints organize routes into logical modules (auth, resources, bookings, etc.)
    This is the "Controller" part of MVC.

    Args:
        app (Flask): Flask application instance
    """

    # Main/Home blueprint
    from src.controllers.main_controller import main_bp
    app.register_blueprint(main_bp)

    # Authentication blueprint
    from src.controllers.auth_controller import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # TODO: Register other blueprints as they are implemented
    # from src.controllers.resource_controller import resource_bp
    # app.register_blueprint(resource_bp, url_prefix='/resources')

    # from src.controllers.booking_controller import booking_bp
    # app.register_blueprint(booking_bp, url_prefix='/bookings')


def register_error_handlers(app):
    """
    Register custom error handlers.

    Provides user-friendly error pages for common HTTP errors.

    Args:
        app (Flask): Flask application instance
    """

    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        if app.config['DEBUG']:
            return jsonify({'error': 'Not found', 'message': str(error)}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        app.logger.error(f'Server Error: {error}')
        if app.config['DEBUG']:
            return jsonify({'error': 'Internal server error', 'message': str(error)}), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 errors."""
        return render_template('errors/403.html'), 403


def setup_logging(app):
    """
    Configure application logging.

    Sets up logging to both file and console based on configuration.

    Args:
        app (Flask): Flask application instance
    """

    if not app.debug and not app.testing:
        # File logging
        log_file = app.config.get('LOG_FILE')
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            app.logger.addHandler(file_handler)

        # Console logging
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        app.logger.addHandler(console_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Campus Resource Hub startup')


def register_template_context(app):
    """
    Register template context processors.

    Makes certain variables/functions available to all templates automatically.

    Args:
        app (Flask): Flask application instance
    """

    @app.context_processor
    def utility_processor():
        """Make utility functions available in templates."""
        return {
            'app_name': 'Campus Resource Hub',
            'app_version': '1.0.0',
            'current_year': 2025
        }


def register_shell_context(app):
    """
    Register shell context for 'flask shell' command.

    Makes objects available in the Flask shell without importing.

    Args:
        app (Flask): Flask application instance

    Usage:
        $ flask shell
        >>> app
        >>> db
        >>> User
    """

    @app.shell_context_processor
    def make_shell_context():
        """Add models and utilities to flask shell context."""
        # TODO: Add models and DAL classes here as they are implemented
        return {
            'app': app,
            'config': app.config
        }
