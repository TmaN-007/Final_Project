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
from datetime import datetime
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

    # Resource blueprint
    from src.controllers.resource_controller import resource_bp
    app.register_blueprint(resource_bp, url_prefix='/resources')

    # Booking blueprint
    from src.controllers.booking_controller import booking_bp
    app.register_blueprint(booking_bp, url_prefix='/bookings')

    # Message blueprint
    from src.controllers.message_controller import message_bp
    app.register_blueprint(message_bp, url_prefix='/messages')

    # Review blueprint
    from src.controllers.review_controller import review_bp
    app.register_blueprint(review_bp, url_prefix='/reviews')

    # Admin blueprint
    from src.controllers.admin_controller import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')


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
        from flask_login import current_user

        # Get unread message count for authenticated users
        unread_messages = 0
        pending_approvals = 0

        if current_user.is_authenticated:
            try:
                from src.data_access.message_dal import MessageDAL
                unread_messages = MessageDAL.get_unread_message_count(current_user.user_id)
            except Exception:
                # Fail silently if there's an error getting unread count
                unread_messages = 0

            # Get pending approval count for staff/admin users
            if current_user.role in ['staff', 'admin']:
                try:
                    from src.data_access.booking_dal import BookingDAL
                    # Get bookings pending approval for resources owned by current user
                    pending_bookings = BookingDAL.get_pending_approvals(
                        resource_owner_id=current_user.user_id,
                        owner_type='user',
                        limit=1000,  # High limit to get all pending
                        offset=0
                    )
                    pending_approvals = len(pending_bookings)
                except Exception:
                    # Fail silently if there's an error getting pending count
                    pending_approvals = 0

        return {
            'app_name': 'Campus Resource Hub',
            'app_version': '1.0.0',
            'current_year': 2025,
            'now': datetime.now,
            'unread_messages': unread_messages,
            'pending_approvals': pending_approvals
        }

    @app.template_filter('localtime')
    def localtime_filter(utc_time_str, format_str='%Y-%m-%d %H:%M:%S'):
        """
        Convert UTC time string to local time for display.

        Args:
            utc_time_str: UTC datetime string from database
            format_str: Output format string

        Returns:
            Formatted local time string
        """
        if not utc_time_str:
            return ''

        try:
            from datetime import datetime

            # Parse the UTC time string
            if isinstance(utc_time_str, str):
                # Try common datetime formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                    try:
                        dt = datetime.strptime(utc_time_str, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    return utc_time_str  # Return original if parsing fails
            elif isinstance(utc_time_str, datetime):
                dt = utc_time_str
            else:
                return str(utc_time_str)

            # Return formatted time (browser will handle local timezone conversion via JavaScript)
            return dt.strftime(format_str)

        except Exception as e:
            # Return original value if conversion fails
            return str(utc_time_str)


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
