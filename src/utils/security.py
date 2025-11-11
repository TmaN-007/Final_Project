"""
Campus Resource Hub - Security Utilities
========================================
MVC Role: Security layer utilities
MCP Role: Security boundary for AI-assisted operations

Implements security features required by project brief:
- XSS protection (input sanitization)
- File upload validation
- Path traversal prevention
- Input validation helpers
"""

import os
import re
from typing import Optional, Tuple
from werkzeug.utils import secure_filename
import bleach


# Allowed HTML tags for rich text (if needed)
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}


def sanitize_html(html_content: str) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.

    Args:
        html_content (str): Raw HTML content

    Returns:
        str: Sanitized HTML with only allowed tags

    Example:
        >>> sanitize_html('<script>alert("XSS")</script><p>Safe content</p>')
        '<p>Safe content</p>'
    """
    return bleach.clean(
        html_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )


def sanitize_input(text: str) -> str:
    """
    Sanitize plain text input (strip all HTML).

    Args:
        text (str): Raw text input

    Returns:
        str: Sanitized text with HTML removed

    Example:
        >>> sanitize_input('<b>Username</b>')
        'Username'
    """
    return bleach.clean(text, tags=[], strip=True)


def is_safe_filename(filename: str) -> bool:
    """
    Check if filename is safe (no path traversal).

    Args:
        filename (str): Filename to check

    Returns:
        bool: True if safe, False otherwise

    Example:
        >>> is_safe_filename('document.pdf')
        True
        >>> is_safe_filename('../../../etc/passwd')
        False
    """
    # Check for path traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        return False

    # Check for null bytes
    if '\x00' in filename:
        return False

    return True


def validate_file_upload(filename: str, allowed_extensions: set, max_size: int = None) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file.

    Args:
        filename (str): Original filename
        allowed_extensions (set): Set of allowed extensions (e.g., {'jpg', 'png', 'pdf'})
        max_size (int): Maximum file size in bytes (optional)

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)

    Example:
        >>> valid, error = validate_file_upload('document.pdf', {'pdf', 'doc'})
        >>> if not valid:
        ...     flash(error, 'danger')
    """
    # Check if filename is provided
    if not filename:
        return False, "No file selected"

    # Check for safe filename
    if not is_safe_filename(filename):
        return False, "Invalid filename"

    # Check file extension
    if '.' not in filename:
        return False, "File must have an extension"

    extension = filename.rsplit('.', 1)[1].lower()
    if extension not in allowed_extensions:
        return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"

    return True, None


def secure_upload_filename(filename: str) -> str:
    """
    Generate secure filename for upload.

    Args:
        filename (str): Original filename

    Returns:
        str: Secure filename

    Example:
        >>> secure_upload_filename('My Document (1).pdf')
        'My_Document_1.pdf'
    """
    return secure_filename(filename)


def is_valid_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email (str): Email address

    Returns:
        bool: True if valid, False otherwise

    Example:
        >>> is_valid_email('user@iu.edu')
        True
        >>> is_valid_email('invalid-email')
        False
    """
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_strong_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    Check if password meets strength requirements.

    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character

    Args:
        password (str): Password to check

    Returns:
        Tuple[bool, Optional[str]]: (is_strong, error_message)

    Example:
        >>> strong, error = is_strong_password('SecurePass123!')
        >>> if not strong:
        ...     flash(error, 'danger')
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"

    return True, None


def generate_safe_redirect_url(next_url: str, default_url: str = '/') -> str:
    """
    Generate safe redirect URL (prevent open redirect vulnerability).

    Args:
        next_url (str): Requested redirect URL
        default_url (str): Default URL if next_url is unsafe

    Returns:
        str: Safe redirect URL

    Example:
        >>> generate_safe_redirect_url('http://evil.com', '/dashboard')
        '/dashboard'
        >>> generate_safe_redirect_url('/dashboard', '/dashboard')
        '/dashboard'
    """
    if not next_url:
        return default_url

    # Only allow relative URLs (no external redirects)
    if next_url.startswith('/') and not next_url.startswith('//'):
        return next_url

    return default_url
