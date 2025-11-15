"""
Role-Based Access Control (RBAC) Decorators for Campus Resource Hub.

Provides decorators for enforcing authorization rules based on user roles
and resource ownership.
"""

from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user
from src.data_access.resource_dal import ResourceDAL
import logging

logger = logging.getLogger(__name__)


def role_required(*roles):
    """
    Decorator to restrict access based on user role.

    Usage:
        @role_required('staff', 'admin')
        def create_resource():
            # Only staff and admin can access
            pass

    Args:
        *roles: Variable number of allowed roles ('student', 'staff', 'admin')

    Returns:
        Decorator function

    Example:
        @app.route('/admin/dashboard')
        @login_required
        @role_required('admin')
        def admin_dashboard():
            return render_template('admin/dashboard.html')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                logger.warning(f"Unauthenticated user attempted to access {f.__name__}")
                flash('Please login to access this page.', 'warning')
                return redirect(url_for('auth.login'))

            if current_user.role not in roles:
                logger.warning(
                    f"User {current_user.email} (role: {current_user.role}) "
                    f"attempted unauthorized access to {f.__name__} (requires: {roles})"
                )
                flash('You do not have permission to access this page.', 'danger')
                abort(403)  # Forbidden

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def owner_required(resource_type='resource'):
    """
    Decorator to restrict access to resource owners or admins.

    Checks if the current user owns the resource being accessed.
    Admins bypass this check (they can access any resource).

    Usage:
        @owner_required('resource')
        def edit_resource(resource_id):
            # Only resource owner or admin can access
            pass

    Args:
        resource_type: Type of resource ('resource', 'booking', etc.)

    Returns:
        Decorator function

    Example:
        @app.route('/resources/<int:resource_id>/edit')
        @login_required
        @owner_required('resource')
        def edit_resource(resource_id):
            return render_template('resources/edit.html')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                logger.warning(f"Unauthenticated user attempted to access {f.__name__}")
                flash('Please login to access this page.', 'warning')
                return redirect(url_for('auth.login'))

            # Admin can access everything
            if current_user.role == 'admin':
                return f(*args, **kwargs)

            # Get resource_id from kwargs
            resource_id = kwargs.get('resource_id')

            if not resource_id:
                logger.error(f"owner_required decorator used on {f.__name__} but no resource_id in kwargs")
                abort(500)  # Internal server error

            # Check ownership based on resource type
            if resource_type == 'resource':
                resource = ResourceDAL.get_resource_by_id(resource_id)

                if not resource:
                    logger.warning(f"User {current_user.email} attempted to access non-existent resource {resource_id}")
                    flash('Resource not found.', 'danger')
                    abort(404)  # Not found

                # Check if user is the owner
                if resource['owner_type'] == 'user' and resource['owner_id'] == current_user.user_id:
                    return f(*args, **kwargs)

                # User is not the owner
                logger.warning(
                    f"User {current_user.email} (ID: {current_user.user_id}) "
                    f"attempted unauthorized access to resource {resource_id} "
                    f"(owner: {resource['owner_type']}:{resource['owner_id']})"
                )
                flash('You do not have permission to modify this resource.', 'danger')
                abort(403)  # Forbidden

            # Add other resource types here as needed (bookings, reviews, etc.)
            else:
                logger.error(f"Unknown resource_type '{resource_type}' in owner_required decorator")
                abort(500)

        return decorated_function
    return decorator


def staff_or_owner_required(resource_type='resource'):
    """
    Decorator to restrict access to staff members or resource owners.

    Similar to owner_required, but also allows any staff member to access.
    Useful for approval workflows where staff can approve any booking.

    Usage:
        @staff_or_owner_required('booking')
        def approve_booking(booking_id):
            # Staff or booking owner can access
            pass

    Args:
        resource_type: Type of resource ('resource', 'booking', etc.)

    Returns:
        Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please login to access this page.', 'warning')
                return redirect(url_for('auth.login'))

            # Admin and staff can access
            if current_user.role in ['admin', 'staff']:
                return f(*args, **kwargs)

            # For students, check ownership (same logic as owner_required)
            # This allows students to manage their own bookings
            resource_id = kwargs.get('resource_id') or kwargs.get('booking_id')

            if not resource_id:
                abort(500)

            # Ownership check logic would go here
            # For now, deny access to students
            flash('You do not have permission to access this page.', 'danger')
            abort(403)

        return decorated_function
    return decorator
