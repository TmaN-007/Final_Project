"""
Campus Resource Hub - User Data Access Layer
============================================
MVC Role: Data access for user management
MCP Role: User data queries for AI-assisted authentication

This module handles all database operations for users including:
- User CRUD operations
- Authentication queries
- Email verification
- Password reset
- Session management

All queries use parameterized statements for SQL injection prevention.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import secrets
from werkzeug.security import generate_password_hash, check_password_hash

from src.data_access.base_dal import BaseDAL


class UserDAL(BaseDAL):
    """
    User Data Access Layer.

    Handles all database operations for the users table and related authentication tables.
    """

    @classmethod
    def create_user(cls, name: str, email: str, password: str, role: str = 'student',
                    department_id: Optional[int] = None, profile_image: Optional[str] = None) -> int:
        """
        Create a new user.

        Args:
            name (str): User's full name
            email (str): User's email address (must be unique)
            password (str): Plain text password (will be hashed)
            role (str): User role ('student', 'staff', 'admin')
            department_id (Optional[int]): Department ID
            profile_image (Optional[str]): Path to profile image

        Returns:
            int: New user's ID

        Raises:
            sqlite3.IntegrityError: If email already exists

        Example:
            >>> user_id = UserDAL.create_user(
            ...     name='John Doe',
            ...     email='john@iu.edu',
            ...     password='SecurePass123',
            ...     role='student'
            ... )
        """
        password_hash = generate_password_hash(password)
        verification_token = secrets.token_urlsafe(32)
        verification_expires = datetime.now() + timedelta(days=1)

        query = """
            INSERT INTO users (
                name, email, password_hash, role, department_id, profile_image,
                email_verified, verification_token, verification_token_expires, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, datetime('now'))
        """

        return cls.execute_update(query, (
            name, email, password_hash, role, department_id, profile_image,
            verification_token, verification_expires.isoformat()
        ))

    @classmethod
    def get_user_by_id(cls, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.

        Args:
            user_id (int): User ID

        Returns:
            Optional[Dict]: User data or None if not found

        Example:
            >>> user = UserDAL.get_user_by_id(123)
            >>> print(user['name'])
        """
        return cls.get_by_id('users', 'user_id', user_id)

    @classmethod
    def get_user_by_email(cls, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email address.

        Args:
            email (str): User's email address

        Returns:
            Optional[Dict]: User data or None if not found

        Example:
            >>> user = UserDAL.get_user_by_email('john@iu.edu')
        """
        query = "SELECT * FROM users WHERE email = ?"
        results = cls.execute_query(query, (email,))
        return results[0] if results else None

    @classmethod
    def verify_password(cls, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Verify user credentials.

        Args:
            email (str): User's email
            password (str): Plain text password

        Returns:
            Optional[Dict]: User data if credentials valid and not banned, None otherwise

        Example:
            >>> user = UserDAL.verify_password('john@iu.edu', 'password123')
            >>> if user:
            ...     print("Login successful")
        """
        user = cls.get_user_by_email(email)

        if user and check_password_hash(user['password_hash'], password):
            # Check if user is banned
            if user.get('is_banned', False):
                return None
            return user

        return None

    @classmethod
    def update_user(cls, user_id: int, **kwargs) -> bool:
        """
        Update user fields.

        Args:
            user_id (int): User ID
            **kwargs: Fields to update (name, department_id, profile_image, etc.)

        Returns:
            bool: True if user was updated, False otherwise

        Example:
            >>> UserDAL.update_user(
            ...     user_id=123,
            ...     name='Jane Doe',
            ...     department_id=5
            ... )
        """
        # Filter out None values and build SET clause
        updates = {k: v for k, v in kwargs.items() if v is not None}

        if not updates:
            return False

        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values())
        values.append(user_id)

        query = f"UPDATE users SET {set_clause}, updated_at = datetime('now') WHERE user_id = ?"

        rows_affected = cls.execute_update(query, tuple(values))
        return rows_affected > 0

    @classmethod
    def verify_email(cls, verification_token: str) -> bool:
        """
        Verify user's email address.

        Args:
            verification_token (str): Email verification token

        Returns:
            bool: True if email was verified, False if token invalid/expired

        Example:
            >>> if UserDAL.verify_email(token):
            ...     flash('Email verified successfully')
        """
        query = """
            UPDATE users
            SET email_verified = 1,
                verification_token = NULL,
                verification_token_expires = NULL,
                updated_at = datetime('now')
            WHERE verification_token = ?
              AND verification_token_expires > datetime('now')
        """

        rows_affected = cls.execute_update(query, (verification_token,))
        return rows_affected > 0

    @classmethod
    def generate_reset_token(cls, email: str) -> Optional[str]:
        """
        Generate password reset token for user.

        Args:
            email (str): User's email address

        Returns:
            Optional[str]: Reset token if user exists, None otherwise

        Example:
            >>> token = UserDAL.generate_reset_token('john@iu.edu')
            >>> # Send token in email to user
        """
        user = cls.get_user_by_email(email)

        if not user:
            return None

        reset_token = secrets.token_urlsafe(32)
        reset_expires = datetime.now() + timedelta(hours=1)

        query = """
            UPDATE users
            SET reset_password_token = ?,
                reset_password_expires = ?,
                updated_at = datetime('now')
            WHERE user_id = ?
        """

        cls.execute_update(query, (reset_token, reset_expires.isoformat(), user['user_id']))

        return reset_token

    @classmethod
    def reset_password(cls, reset_token: str, new_password: str) -> bool:
        """
        Reset user password with token.

        Args:
            reset_token (str): Password reset token
            new_password (str): New password (will be hashed)

        Returns:
            bool: True if password was reset, False if token invalid/expired

        Example:
            >>> if UserDAL.reset_password(token, 'NewPass123'):
            ...     flash('Password reset successful')
        """
        password_hash = generate_password_hash(new_password)

        query = """
            UPDATE users
            SET password_hash = ?,
                reset_password_token = NULL,
                reset_password_expires = NULL,
                updated_at = datetime('now')
            WHERE reset_password_token = ?
              AND reset_password_expires > datetime('now')
        """

        rows_affected = cls.execute_update(query, (password_hash, reset_token))
        return rows_affected > 0

    @classmethod
    def get_users_by_role(cls, role: str) -> List[Dict[str, Any]]:
        """
        Get all users with a specific role.

        Args:
            role (str): User role ('student', 'staff', 'admin')

        Returns:
            List[Dict]: List of users

        Example:
            >>> admins = UserDAL.get_users_by_role('admin')
        """
        query = "SELECT * FROM users WHERE role = ? ORDER BY name"
        return cls.execute_query(query, (role,))

    @classmethod
    def email_exists(cls, email: str) -> bool:
        """
        Check if email already exists in database.

        Args:
            email (str): Email address to check

        Returns:
            bool: True if email exists, False otherwise

        Example:
            >>> if UserDAL.email_exists('john@iu.edu'):
            ...     flash('Email already registered')
        """
        query = "SELECT COUNT(*) as count FROM users WHERE email = ?"
        results = cls.execute_query(query, (email,))
        return results[0]['count'] > 0 if results else False

    @classmethod
    def update_user_role(cls, user_id: int, new_role: str) -> int:
        """
        Update user's role (admin-only operation).

        Args:
            user_id (int): User ID to update
            new_role (str): New role ('student', 'staff', 'admin')

        Returns:
            int: Number of rows affected

        Security Note:
            This method should only be called by admin users.
            Always verify admin permissions before calling this method.

        Example:
            >>> # In admin controller:
            >>> if current_user.is_admin:
            ...     UserDAL.update_user_role(user_id=5, new_role='staff')
        """
        if new_role not in ('student', 'staff', 'admin'):
            raise ValueError(f"Invalid role: {new_role}. Must be 'student', 'staff', or 'admin'")

        query = """
            UPDATE users
            SET role = ?,
                updated_at = datetime('now')
            WHERE user_id = ?
        """
        return cls.execute_update(query, (new_role, user_id))

    @classmethod
    def get_all_users(cls, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all users with pagination (admin-only).

        Args:
            limit (int): Maximum number of users to return
            offset (int): Pagination offset

        Returns:
            List[Dict]: List of users with department info

        Example:
            >>> users = UserDAL.get_all_users(limit=50, offset=0)
        """
        query = """
            SELECT
                u.user_id,
                u.name,
                u.email,
                u.role,
                u.profile_image,
                u.email_verified,
                u.created_at,
                u.updated_at,
                d.name as department_name
            FROM users u
            LEFT JOIN departments d ON u.department_id = d.department_id
            ORDER BY u.created_at DESC
            LIMIT ? OFFSET ?
        """
        return cls.execute_query(query, (limit, offset))

    # =============================================================================
    # ADMIN PANEL METHODS
    # =============================================================================

    @classmethod
    def count_all_users(cls) -> int:
        """Count total number of users."""
        query = "SELECT COUNT(*) as count FROM users"
        result = cls.execute_query(query)
        return result[0]['count'] if result else 0

    @classmethod
    def count_active_users(cls) -> int:
        """Count users with verified email (active)."""
        query = "SELECT COUNT(*) as count FROM users WHERE email_verified = 1"
        result = cls.execute_query(query)
        return result[0]['count'] if result else 0

    @classmethod
    def count_pending_users(cls) -> int:
        """Count users with unverified email (pending)."""
        query = "SELECT COUNT(*) as count FROM users WHERE email_verified = 0"
        result = cls.execute_query(query)
        return result[0]['count'] if result else 0

    @classmethod
    def get_recent_users(cls, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recently registered users."""
        query = """
            SELECT user_id, name, email, role, email_verified, is_banned,
                   datetime(last_login, 'localtime') as last_login,
                   datetime(created_at, 'localtime') as created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT ?
        """
        results = cls.execute_query(query, (limit,))
        # Add computed 'status' field for template compatibility
        for user in results:
            if user.get('is_banned'):
                user['status'] = 'banned'
            else:
                user['status'] = 'active'
        return results

    @classmethod
    def get_all_users_paginated(cls, page: int = 1, per_page: int = 20,
                                 role_filter: str = '', status_filter: str = '',
                                 search_query: str = '') -> Dict[str, Any]:
        """
        Get paginated list of users with optional filters.

        Args:
            page: Page number (1-indexed)
            per_page: Number of items per page
            role_filter: Filter by role ('student', 'staff', 'admin')
            status_filter: Filter by email verification ('active'=verified, 'pending'=unverified, 'inactive'=unverified)
            search_query: Search in name or email

        Returns:
            Dict with 'users' list and 'pagination' info
        """
        offset = (page - 1) * per_page

        # Build WHERE clause dynamically
        where_clauses = []
        params = []

        if role_filter:
            where_clauses.append("role = ?")
            params.append(role_filter)

        if status_filter:
            # Map status filter to is_banned
            if status_filter == 'active':
                where_clauses.append("is_banned = 0")
            elif status_filter == 'banned':
                where_clauses.append("is_banned = 1")

        if search_query:
            where_clauses.append("(name LIKE ? OR email LIKE ?)")
            search_pattern = f'%{search_query}%'
            params.extend([search_pattern, search_pattern])

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        # Get total count
        count_query = f"SELECT COUNT(*) as count FROM users WHERE {where_sql}"
        total_result = cls.execute_query(count_query, tuple(params))
        total_count = total_result[0]['count'] if total_result else 0

        # Get users
        query = f"""
            SELECT user_id, name, email, role, email_verified, is_banned,
                   datetime(last_login, 'localtime') as last_login,
                   datetime(created_at, 'localtime') as created_at
            FROM users
            WHERE {where_sql}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([per_page, offset])
        users = cls.execute_query(query, tuple(params))

        # Add computed 'status' field for template compatibility
        for user in users:
            if user.get('is_banned'):
                user['status'] = 'banned'
            else:
                user['status'] = 'active'

        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page

        return {
            'users': users,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_prev': page > 1,
                'has_next': page < total_pages
            }
        }

    @classmethod
    def update_user_status(cls, user_id: int, status: str) -> bool:
        """
        Update user email verification status (active, inactive, pending).

        Args:
            user_id: User ID
            status: New status ('active'=verified, 'inactive'/'pending'=unverified)

        Returns:
            bool: True if successful
        """
        # Map status to email_verified boolean
        email_verified = 1 if status == 'active' else 0

        query = """
            UPDATE users
            SET email_verified = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """
        cls.execute_update(query, (email_verified, user_id))
        return True

    @classmethod
    def update_user_role(cls, user_id: int, role: str) -> bool:
        """
        Update user role.

        Args:
            user_id: User ID
            role: New role ('student', 'staff', 'admin')

        Returns:
            bool: True if successful
        """
        query = """
            UPDATE users
            SET role = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """
        cls.execute_update(query, (role, user_id))
        return True

    @classmethod
    def ban_user(cls, user_id: int) -> bool:
        """
        Ban a user from accessing the system.

        Args:
            user_id: User ID to ban

        Returns:
            bool: True if successful
        """
        query = """
            UPDATE users
            SET is_banned = 1, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """
        cls.execute_update(query, (user_id,))
        return True

    @classmethod
    def unban_user(cls, user_id: int) -> bool:
        """
        Unban a user, allowing them to access the system again.

        Args:
            user_id: User ID to unban

        Returns:
            bool: True if successful
        """
        query = """
            UPDATE users
            SET is_banned = 0, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """
        cls.execute_update(query, (user_id,))
        return True

    @classmethod
    def update_last_login(cls, user_id: int) -> bool:
        """
        Update user's last login timestamp.

        Args:
            user_id: User ID

        Returns:
            bool: True if successful
        """
        query = """
            UPDATE users
            SET last_login = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """
        cls.execute_update(query, (user_id,))
        return True
