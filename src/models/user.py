"""
Campus Resource Hub - User Model
=================================
MVC Role: Model representing User entity
MCP Role: User object structure for AI-assisted user management

Integrates with Flask-Login for authentication.
"""

from flask_login import UserMixin
from typing import Optional
from src.data_access.user_dal import UserDAL


class User(UserMixin):
    """
    User model class.

    Integrates with Flask-Login to provide:
    - is_authenticated: True if user is logged in
    - is_active: True if account is active
    - is_anonymous: False for real users
    - get_id(): Returns user ID as string

    Attributes:
        user_id (int): Primary key
        name (str): Full name
        email (str): Email address
        role (str): User role ('student', 'staff', 'admin')
        department_id (int): Department affiliation
        profile_image (str): Profile image path
        email_verified (bool): Email verification status
        created_at (datetime): Account creation timestamp
    """

    def __init__(self, user_data: dict):
        """
        Initialize User from database row.

        Args:
            user_data (dict): User data from database
        """
        self._user_id = user_data['user_id']
        self._id = user_data['user_id']  # Flask-Login compatibility
        self._name = user_data['name']
        self._email = user_data['email']
        self._role = user_data['role']
        self._department_id = user_data.get('department_id')
        self._profile_image = user_data.get('profile_image')
        self._email_verified = bool(user_data['email_verified'])
        self._created_at = user_data.get('created_at')

    # Property getters and setters
    @property
    def user_id(self) -> int:
        """Get user ID."""
        return self._user_id

    @user_id.setter
    def user_id(self, value: int):
        """Set user ID."""
        if not isinstance(value, int) or value <= 0:
            raise ValueError("User ID must be a positive integer")
        self._user_id = value

    @property
    def id(self) -> int:
        """Get ID (Flask-Login compatibility)."""
        return self._id

    @id.setter
    def id(self, value: int):
        """Set ID (Flask-Login compatibility)."""
        if not isinstance(value, int) or value <= 0:
            raise ValueError("ID must be a positive integer")
        self._id = value

    @property
    def name(self) -> str:
        """Get user name."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Set user name with validation."""
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        self._name = value.strip()

    @property
    def email(self) -> str:
        """Get user email."""
        return self._email

    @email.setter
    def email(self, value: str):
        """Set user email with validation."""
        if not value or not value.strip():
            raise ValueError("Email cannot be empty")
        if '@' not in value:
            raise ValueError("Invalid email format")
        self._email = value.strip().lower()

    @property
    def role(self) -> str:
        """Get user role."""
        return self._role

    @role.setter
    def role(self, value: str):
        """Set user role with validation."""
        valid_roles = ('student', 'staff', 'admin')
        if value not in valid_roles:
            raise ValueError(f"Role must be one of {valid_roles}")
        self._role = value

    @property
    def department_id(self) -> Optional[int]:
        """Get department ID."""
        return self._department_id

    @department_id.setter
    def department_id(self, value: Optional[int]):
        """Set department ID."""
        self._department_id = value

    @property
    def profile_image(self) -> Optional[str]:
        """Get profile image path."""
        return self._profile_image

    @profile_image.setter
    def profile_image(self, value: Optional[str]):
        """Set profile image path."""
        self._profile_image = value

    @property
    def email_verified(self) -> bool:
        """Get email verification status."""
        return self._email_verified

    @email_verified.setter
    def email_verified(self, value: bool):
        """Set email verification status."""
        self._email_verified = bool(value)

    @property
    def created_at(self):
        """Get creation timestamp."""
        return self._created_at

    @created_at.setter
    def created_at(self, value):
        """Set creation timestamp."""
        self._created_at = value

    def get_id(self) -> str:
        """
        Required by Flask-Login.

        Returns:
            str: User ID as string
        """
        return str(self._user_id)

    @property
    def is_active(self) -> bool:
        """
        Check if user account is active.

        Returns:
            bool: True for all users (email verification not yet implemented)

        TODO: Once email verification is implemented, return self.email_verified
        """
        return True  # Temporarily allow all users until email verification is implemented

    def is_student(self) -> bool:
        """Check if user is a student."""
        return self.role == 'student'

    def is_staff(self) -> bool:
        """Check if user is staff."""
        return self.role == 'staff'

    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == 'admin'

    def can_approve_bookings(self) -> bool:
        """Check if user can approve bookings."""
        return self.role in ('staff', 'admin')

    def can_manage_resources(self) -> bool:
        """Check if user can manage all resources."""
        return self.role == 'admin'

    @staticmethod
    def get_by_id(user_id: int) -> Optional['User']:
        """
        Get user by ID.

        Args:
            user_id (int): User ID

        Returns:
            Optional[User]: User object or None
        """
        user_data = UserDAL.get_user_by_id(user_id)
        return User(user_data) if user_data else None

    @staticmethod
    def get_by_email(email: str) -> Optional['User']:
        """
        Get user by email.

        Args:
            email (str): Email address

        Returns:
            Optional[User]: User object or None
        """
        user_data = UserDAL.get_user_by_email(email)
        return User(user_data) if user_data else None

    def __repr__(self) -> str:
        """String representation."""
        return f"<User {self.user_id}: {self.name} ({self.email})>"
