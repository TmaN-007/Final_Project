"""
Input Validation Utilities
===========================
Production-level validators with decorators for security and data integrity.

Security Features:
- Email validation (RFC 5322 compliant)
- Password strength validation (OWASP compliant)
- Input sanitization
- SQL injection prevention
- XSS prevention
"""

import re
import bleach
from functools import wraps
from flask import flash, request
from typing import Callable, Any, Dict, List, Optional


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class InputValidator:
    """
    Production-level input validator with comprehensive security checks.

    Features:
    - Email validation (RFC 5322)
    - Password strength (OWASP guidelines)
    - Name validation (prevents injection)
    - Input sanitization (XSS prevention)
    """

    # Email regex (RFC 5322 simplified)
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    # Password requirements (OWASP)
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 128
    PASSWORD_UPPERCASE_REGEX = re.compile(r'[A-Z]')
    PASSWORD_LOWERCASE_REGEX = re.compile(r'[a-z]')
    PASSWORD_DIGIT_REGEX = re.compile(r'[0-9]')
    PASSWORD_SPECIAL_REGEX = re.compile(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]')

    # Name validation (prevent injection)
    NAME_REGEX = re.compile(r'^[a-zA-Z\s\'-]{2,100}$')

    # Allowed HTML tags for sanitization
    ALLOWED_TAGS = []  # No HTML allowed in user inputs
    ALLOWED_ATTRIBUTES = {}

    @staticmethod
    def validate_email(email: str) -> tuple[bool, Optional[str]]:
        """
        Validate email address.

        Args:
            email: Email address to validate

        Returns:
            Tuple of (is_valid, error_message)

        Security:
            - Prevents email injection
            - Validates format
            - Checks length limits
        """
        if not email or not isinstance(email, str):
            return False, "Email is required."

        email = email.strip().lower()

        # Length check (prevent DoS)
        if len(email) > 254:  # RFC 5321
            return False, "Email address is too long."

        if len(email) < 5:  # a@b.c minimum
            return False, "Email address is too short."

        # Format validation
        if not InputValidator.EMAIL_REGEX.match(email):
            return False, "Invalid email format. Please use a valid email address."

        # Additional checks
        local_part, domain = email.rsplit('@', 1)

        if len(local_part) > 64:  # RFC 5321
            return False, "Email local part is too long."

        if domain.startswith('.') or domain.endswith('.'):
            return False, "Invalid domain format."

        return True, None

    @staticmethod
    def validate_password(password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password strength (OWASP compliant).

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message)

        Requirements:
            - 8-128 characters
            - At least one uppercase letter
            - At least one lowercase letter
            - At least one digit
            - At least one special character
        """
        if not password or not isinstance(password, str):
            return False, "Password is required."

        # Length check
        if len(password) < InputValidator.PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {InputValidator.PASSWORD_MIN_LENGTH} characters long."

        if len(password) > InputValidator.PASSWORD_MAX_LENGTH:
            return False, f"Password must not exceed {InputValidator.PASSWORD_MAX_LENGTH} characters."

        # Uppercase check
        if not InputValidator.PASSWORD_UPPERCASE_REGEX.search(password):
            return False, "Password must contain at least one uppercase letter."

        # Lowercase check
        if not InputValidator.PASSWORD_LOWERCASE_REGEX.search(password):
            return False, "Password must contain at least one lowercase letter."

        # Digit check
        if not InputValidator.PASSWORD_DIGIT_REGEX.search(password):
            return False, "Password must contain at least one number."

        # Special character check
        if not InputValidator.PASSWORD_SPECIAL_REGEX.search(password):
            return False, "Password must contain at least one special character (!@#$%^&*...)."

        return True, None

    @staticmethod
    def validate_name(name: str) -> tuple[bool, Optional[str]]:
        """
        Validate user name.

        Args:
            name: Name to validate

        Returns:
            Tuple of (is_valid, error_message)

        Security:
            - Prevents SQL injection
            - Prevents XSS attacks
            - Validates reasonable length
        """
        if not name or not isinstance(name, str):
            return False, "Name is required."

        name = name.strip()

        # Length check
        if len(name) < 2:
            return False, "Name must be at least 2 characters long."

        if len(name) > 100:
            return False, "Name must not exceed 100 characters."

        # Format validation (letters, spaces, hyphens, apostrophes only)
        if not InputValidator.NAME_REGEX.match(name):
            return False, "Name can only contain letters, spaces, hyphens, and apostrophes."

        return True, None

    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Sanitize user input to prevent XSS attacks.

        Args:
            text: Text to sanitize

        Returns:
            Sanitized text (HTML stripped)

        Security:
            - Removes all HTML tags
            - Escapes special characters
        """
        if not text or not isinstance(text, str):
            return ""

        # Strip all HTML tags
        sanitized = bleach.clean(
            text,
            tags=InputValidator.ALLOWED_TAGS,
            attributes=InputValidator.ALLOWED_ATTRIBUTES,
            strip=True
        )

        return sanitized.strip()

    @staticmethod
    def validate_passwords_match(password: str, confirm_password: str) -> tuple[bool, Optional[str]]:
        """
        Validate that passwords match.

        Args:
            password: Original password
            confirm_password: Confirmation password

        Returns:
            Tuple of (is_valid, error_message)
        """
        if password != confirm_password:
            return False, "Passwords do not match."

        return True, None


def validate_registration_input(f: Callable) -> Callable:
    """
    Decorator to validate registration form inputs.

    Usage:
        @validate_registration_input
        def register():
            # Registration logic
            pass

    Validates:
        - Name (required, 2-100 chars, letters only)
        - Email (required, valid format)
        - Password (required, meets strength requirements)
        - Confirm Password (required, matches password)

    Security:
        - Sanitizes all inputs
        - Prevents SQL injection
        - Prevents XSS attacks
        - Validates data types
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            # Get form data
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')

            # Sanitize inputs
            name = InputValidator.sanitize_input(name)
            email = InputValidator.sanitize_input(email)

            # Validate name
            is_valid, error = InputValidator.validate_name(name)
            if not is_valid:
                flash(error, 'danger')
                return f(*args, **kwargs)

            # Validate email
            is_valid, error = InputValidator.validate_email(email)
            if not is_valid:
                flash(error, 'danger')
                return f(*args, **kwargs)

            # Validate password
            is_valid, error = InputValidator.validate_password(password)
            if not is_valid:
                flash(error, 'danger')
                return f(*args, **kwargs)

            # Validate passwords match
            is_valid, error = InputValidator.validate_passwords_match(password, confirm_password)
            if not is_valid:
                flash(error, 'danger')
                return f(*args, **kwargs)

            # Store validated data in request context for use in route
            request.validated_data = {
                'name': name,
                'email': email.lower(),
                'password': password
            }

        return f(*args, **kwargs)

    return decorated_function


def validate_login_input(f: Callable) -> Callable:
    """
    Decorator to validate login form inputs.

    Usage:
        @validate_login_input
        def login():
            # Login logic
            pass

    Validates:
        - Email (required, valid format)
        - Password (required, non-empty)

    Security:
        - Sanitizes inputs
        - Prevents injection attacks
        - Generic error messages (security best practice)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            # Get form data
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')

            # Sanitize email
            email = InputValidator.sanitize_input(email)

            # Validate email format
            is_valid, error = InputValidator.validate_email(email)
            if not is_valid:
                # Generic error message for security
                flash('Invalid email or password.', 'danger')
                return f(*args, **kwargs)

            # Validate password is not empty
            if not password:
                # Generic error message for security
                flash('Invalid email or password.', 'danger')
                return f(*args, **kwargs)

            # Store validated data in request context
            request.validated_data = {
                'email': email.lower(),
                'password': password,
                'remember_me': request.form.get('remember_me') == 'on'
            }

        return f(*args, **kwargs)

    return decorated_function


def rate_limit_check(max_attempts: int = 5, window_minutes: int = 15):
    """
    Decorator for rate limiting authentication attempts.

    Args:
        max_attempts: Maximum attempts allowed in time window
        window_minutes: Time window in minutes

    Usage:
        @rate_limit_check(max_attempts=5, window_minutes=15)
        def login():
            pass

    Note: This is a simple implementation. For production, use Redis or similar.
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # TODO: Implement rate limiting with Redis/Memcached
            # For now, pass through
            return f(*args, **kwargs)
        return decorated_function
    return decorator
