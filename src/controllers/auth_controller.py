"""
Campus Resource Hub - Authentication Controller
===============================================
MVC Role: Controller for user authentication and registration
MCP Role: Security boundary for user access control

Handles:
- User registration (sign up)
- User login (sign in)
- User logout (sign out)
- Password reset flow
- Email verification

Security Features:
- CSRF protection (Flask-WTF)
- Password hashing (bcrypt)
- Session management (Flask-Login)
- Email verification tokens
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from src.data_access.user_dal import UserDAL
from src.models.user import User
from src.forms.auth_forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from src.utils.validators import validate_registration_input, validate_login_input, rate_limit_check
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
@validate_registration_input
@rate_limit_check(max_attempts=5, window_minutes=15)
def register():
    """
    User registration route (PRODUCTION LEVEL).

    GET: Display registration form
    POST: Process registration submission

    Form Fields:
        - name (str): Full name (2-100 chars, letters only)
        - email (str): Email address (RFC 5322 compliant, must be unique)
        - password (str): Password (8-128 chars, OWASP compliant)
        - confirm_password (str): Password confirmation

    Returns:
        HTML: Registration form or redirect to login on success

    Security:
        - OOP validators with decorators (@validate_registration_input)
        - Input sanitization (XSS prevention)
        - SQL injection prevention (parameterized queries in DAL)
        - Password hashing with bcrypt (12 rounds)
        - CSRF protection (Flask-WTF)
        - Rate limiting (5 attempts per 15 minutes)
        - Comprehensive error logging
    """

    # Redirect if already logged in
    if current_user.is_authenticated:
        logger.info(f"User {current_user.email} already authenticated, redirecting to dashboard")
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # Get validated data from decorator
        validated_data = getattr(request, 'validated_data', None)

        if not validated_data:
            # Validation failed, decorator already flashed error
            return render_template('auth/register.html', title='Register', page='register')

        name = validated_data['name']
        email = validated_data['email']
        password = validated_data['password']

        # Check if email already exists
        try:
            if UserDAL.email_exists(email):
                logger.warning(f"Registration attempt with existing email: {email}")
                flash('Email address already registered. Please login or use a different email.', 'danger')
                return render_template('auth/register.html', title='Register', page='register')

            # Create user (all new registrations default to 'student' role)
            user_id = UserDAL.create_user(
                name=name,
                email=email,
                password=password,
                role='student'  # Hardcoded for security - admins created manually
            )

            logger.info(f"New user registered successfully: {email} (ID: {user_id})")
            flash('Account created successfully! You can now login.', 'success')
            return redirect(url_for('auth.login'))

        except ValueError as e:
            # Validation error from DAL
            logger.error(f"Registration validation error for {email}: {str(e)}")
            flash(str(e), 'danger')
            return render_template('auth/register.html', title='Register', page='register')

        except Exception as e:
            # Unexpected error
            logger.error(f"Registration error for {email}: {str(e)}", exc_info=True)
            flash('An unexpected error occurred. Please try again later.', 'danger')
            return render_template('auth/register.html', title='Register', page='register')

    # GET request - display form
    return render_template('auth/register.html',
                          title='Register',
                          page='register')


@auth_bp.route('/login', methods=['GET', 'POST'])
@validate_login_input
@rate_limit_check(max_attempts=5, window_minutes=15)
def login():
    """
    User login route (PRODUCTION LEVEL).

    GET: Display login form
    POST: Process login submission

    Form Fields:
        - email (str): User email (RFC 5322 compliant)
        - password (str): User password
        - remember_me (bool): Remember me checkbox (optional)

    Returns:
        HTML: Login form or redirect to dashboard on success

    Security:
        - OOP validators with decorators (@validate_login_input)
        - Input sanitization (XSS prevention)
        - Generic error messages (prevents user enumeration)
        - Bcrypt password verification (constant-time comparison)
        - Rate limiting (5 attempts per 15 minutes)
        - CSRF protection (Flask-WTF)
        - Session security (HTTPOnly, Secure flags)
        - Comprehensive audit logging
    """

    # Redirect if already logged in
    if current_user.is_authenticated:
        logger.info(f"User {current_user.email} already authenticated, redirecting to dashboard")
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # Get validated data from decorator
        validated_data = getattr(request, 'validated_data', None)

        if not validated_data:
            # Validation failed, decorator already flashed generic error
            return render_template('auth/login.html', title='Login', page='login')

        email = validated_data['email']
        password = validated_data['password']
        remember_me = validated_data['remember_me']

        try:
            # Verify credentials (constant-time comparison in DAL)
            user_data = UserDAL.verify_password(email, password)

            if not user_data:
                # Generic error message (security best practice - prevents user enumeration)
                logger.warning(f"Failed login attempt for email: {email}")
                flash('Invalid email or password.', 'danger')
                return render_template('auth/login.html', title='Login', page='login')

            # Create User object from database result
            user = User(user_data)

            # Login user with Flask-Login
            login_user(user, remember=remember_me)

            # Update last login timestamp
            UserDAL.update_last_login(user.id)

            logger.info(f"Successful login for user: {email} (ID: {user.id})")
            # Don't show welcome message - removed per user request
            # flash(f'Welcome back, {user.name}!', 'success')

            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                # Validate redirect URL to prevent open redirect vulnerability
                from urllib.parse import urlparse, urljoin
                from flask import url_for as flask_url_for

                # Only allow relative URLs
                if not urlparse(next_page).netloc:
                    return redirect(next_page)

            return redirect(url_for('main.index'))

        except Exception as e:
            # Unexpected error
            logger.error(f"Login error for {email}: {str(e)}", exc_info=True)
            # Generic error message (don't leak implementation details)
            flash('An error occurred. Please try again.', 'danger')
            return render_template('auth/login.html', title='Login', page='login')

    # GET request - display form
    return render_template('auth/login.html',
                          title='Login',
                          page='login')


@auth_bp.route('/logout')
@login_required
def logout():
    """
    User logout route.

    Requires authentication.
    Clears user session and redirects to login page.

    Returns:
        Redirect: Login page with logout message
    """
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    """
    Email verification route.

    Args:
        token (str): Verification token from email link

    Returns:
        Redirect: Login page with verification result message

    Security:
        - Token expiry check (24 hours)
        - One-time use token

    TODO: Implement email verification logic
    """

    # TODO: Implement email verification
    # 1. Validate token format
    # 2. Find user by verification token
    # 3. Check token expiry
    # 4. Mark email as verified
    # 5. Clear verification token
    # 6. Flash success message

    flash('Email verification functionality coming soon!', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Password reset request route.

    GET: Display password reset request form
    POST: Process reset request and send email

    Form Fields:
        - email (str): User email address

    Returns:
        HTML: Password reset request form

    Security:
        - Rate limiting on email sending
        - Time-limited reset tokens (1 hour)

    TODO: Implement password reset request logic
    """

    if request.method == 'POST':
        # TODO: Implement password reset request
        # 1. Validate email format
        # 2. Find user by email
        # 3. Generate reset token
        # 4. Send reset email
        # 5. Flash success message (even if email not found - security)

        flash('Password reset functionality coming soon!', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html',
                          title='Forgot Password',
                          page='forgot_password')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Password reset form route.

    Args:
        token (str): Password reset token from email link

    GET: Display password reset form
    POST: Process password reset

    Form Fields:
        - password (str): New password
        - confirm_password (str): Password confirmation

    Returns:
        HTML: Password reset form or redirect to login on success

    Security:
        - Token expiry check (1 hour)
        - One-time use token
        - Password strength validation

    TODO: Implement password reset logic
    """

    if request.method == 'POST':
        # TODO: Implement password reset
        # 1. Validate token
        # 2. Check token expiry
        # 3. Validate new password strength
        # 4. Hash new password
        # 5. Update user password
        # 6. Clear reset token
        # 7. Send confirmation email
        # 8. Flash success and redirect to login

        flash('Password reset functionality coming soon!', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html',
                          title='Reset Password',
                          token=token,
                          page='reset_password')


@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    Edit user profile route.

    GET: Display profile edit form with current user data
    POST: Process profile update

    Form Fields:
        - name (str): Full name
        - email (str): Email address

    Returns:
        HTML: Profile edit form or redirect to same page on success

    Security:
        - Login required
        - CSRF protection
        - Input validation and sanitization
    """
    from src.utils.security import sanitize_html

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()

        # Validate inputs
        if not name or len(name) < 2:
            flash('Name must be at least 2 characters long.', 'danger')
            return render_template('auth/edit_profile.html',
                                 title='Edit Profile',
                                 page='edit_profile')

        if not email or '@' not in email:
            flash('Please provide a valid email address.', 'danger')
            return render_template('auth/edit_profile.html',
                                 title='Edit Profile',
                                 page='edit_profile')

        # Sanitize inputs
        name = sanitize_html(name)
        email = sanitize_html(email)

        # Check if email is already taken by another user
        if email != current_user.email:
            if UserDAL.email_exists(email):
                flash('Email address is already in use by another user.', 'danger')
                return render_template('auth/edit_profile.html',
                                     title='Edit Profile',
                                     page='edit_profile')

        # Update user profile
        try:
            success = UserDAL.update_user(
                user_id=current_user.user_id,
                name=name,
                email=email
            )

            if success:
                # Update the current_user object
                current_user.name = name
                current_user.email = email

                logger.info(f"User {current_user.user_id} updated profile")
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('main.index'))
            else:
                flash('Failed to update profile. Please try again.', 'danger')

        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            flash('An error occurred while updating your profile.', 'danger')

    return render_template('auth/edit_profile.html',
                         title='Edit Profile',
                         page='edit_profile')
