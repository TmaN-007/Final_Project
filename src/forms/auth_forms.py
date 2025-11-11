"""
Authentication Forms for Campus Resource Hub.

Forms for login, registration, and password management with validation.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from src.data_access.user_dal import UserDAL
from src.utils.security import is_strong_password


class LoginForm(FlaskForm):
    """User login form."""

    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message='Email is required'),
            Email(message='Invalid email address'),
            Length(max=255)
        ],
        render_kw={'placeholder': 'your.email@iu.edu', 'autocomplete': 'email'}
    )

    password = PasswordField(
        'Password',
        validators=[DataRequired(message='Password is required')],
        render_kw={'placeholder': 'Enter your password', 'autocomplete': 'current-password'}
    )

    remember_me = BooleanField('Remember Me')

    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    """User registration form."""

    name = StringField(
        'Full Name',
        validators=[
            DataRequired(message='Name is required'),
            Length(min=2, max=100, message='Name must be between 2 and 100 characters')
        ],
        render_kw={'placeholder': 'John Doe', 'autocomplete': 'name'}
    )

    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message='Email is required'),
            Email(message='Invalid email address'),
            Length(max=255)
        ],
        render_kw={'placeholder': 'your.email@iu.edu', 'autocomplete': 'email'}
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required'),
            Length(min=8, message='Password must be at least 8 characters long')
        ],
        render_kw={
            'placeholder': 'Create a strong password',
            'autocomplete': 'new-password'
        }
    )

    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Please confirm your password'),
            EqualTo('password', message='Passwords must match')
        ],
        render_kw={'placeholder': 'Re-enter your password', 'autocomplete': 'new-password'}
    )

    department_id = SelectField(
        'Department (Optional)',
        coerce=int,
        choices=[],  # Will be populated dynamically
        validators=[]
    )

    submit = SubmitField('Register')

    # Note: role field removed - all new registrations default to 'student'
    # Only admins can promote users to 'staff' or 'admin' via admin panel

    def validate_email(self, field):
        """Check if email already exists."""
        user = UserDAL.get_user_by_email(field.data)
        if user:
            raise ValidationError('This email is already registered. Please use a different email or login.')

    def validate_password(self, field):
        """Check password strength."""
        is_strong, error_message = is_strong_password(field.data)
        if not is_strong:
            raise ValidationError(error_message)


class ForgotPasswordForm(FlaskForm):
    """Password reset request form."""

    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message='Email is required'),
            Email(message='Invalid email address')
        ],
        render_kw={'placeholder': 'your.email@iu.edu', 'autocomplete': 'email'}
    )

    submit = SubmitField('Send Reset Link')

    def validate_email(self, field):
        """Check if email exists."""
        user = UserDAL.get_user_by_email(field.data)
        if not user:
            raise ValidationError('No account found with this email address.')


class ResetPasswordForm(FlaskForm):
    """Password reset form (with token)."""

    password = PasswordField(
        'New Password',
        validators=[
            DataRequired(message='Password is required'),
            Length(min=8, message='Password must be at least 8 characters long')
        ],
        render_kw={'placeholder': 'Enter new password', 'autocomplete': 'new-password'}
    )

    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[
            DataRequired(message='Please confirm your password'),
            EqualTo('password', message='Passwords must match')
        ],
        render_kw={'placeholder': 'Re-enter new password', 'autocomplete': 'new-password'}
    )

    submit = SubmitField('Reset Password')

    def validate_password(self, field):
        """Check password strength."""
        is_strong, error_message = is_strong_password(field.data)
        if not is_strong:
            raise ValidationError(error_message)
