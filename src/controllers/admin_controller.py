"""
Campus Resource Hub - Admin Controller
========================================
MVC Role: Controller (Admin Panel)
MCP Role: Provides context for admin panel operations and management

This controller handles:
1. Admin dashboard with statistics
2. User management (view, activate/deactivate)
3. Resource management (approve, reject, archive)
4. Booking management (view, cancel)
5. Review moderation (approve, delete)
"""

import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from src.utils.decorators import role_required
from src.data_access.user_dal import UserDAL
from src.data_access.resource_dal import ResourceDAL
from src.data_access.booking_dal import BookingDAL
from src.data_access.review_dal import ReviewDAL
from src.utils import system_messaging

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    """
    Admin dashboard with overview statistics.

    Shows key metrics and recent activity across the platform.
    """
    try:
        # Get statistics
        stats = {
            'total_users': UserDAL.count_all_users(),
            'active_users': UserDAL.count_active_users(),
            'pending_users': UserDAL.count_pending_users(),
            'total_resources': ResourceDAL.count_all_resources(),
            'pending_resources': ResourceDAL.count_pending_resources(),
            'total_bookings': BookingDAL.count_all_bookings(),
            'pending_bookings': BookingDAL.count_pending_bookings(),
            'total_reviews': ReviewDAL.count_all_reviews(),
            'pending_reviews': ReviewDAL.count_pending_reviews()
        }

        # Get recent activity
        recent_users = UserDAL.get_recent_users(limit=5)
        recent_resources = ResourceDAL.get_recent_resources(limit=5)
        recent_bookings = BookingDAL.get_recent_bookings(limit=5)

        return render_template(
            'admin/dashboard.html',
            stats=stats,
            recent_users=recent_users,
            recent_resources=recent_resources,
            recent_bookings=recent_bookings
        )

    except Exception as e:
        logger.error(f"Error loading admin dashboard: {str(e)}", exc_info=True)
        flash('Error loading dashboard.', 'danger')
        return redirect(url_for('main.index'))


# =============================================================================
# USER MANAGEMENT
# =============================================================================

@admin_bp.route('/users')
@login_required
@role_required('admin')
def users():
    """
    List all users with filtering and pagination.
    """
    try:
        # Get filters from query params
        role_filter = request.args.get('role', '')
        status_filter = request.args.get('status', '')
        search_query = request.args.get('search', '')
        page = request.args.get('page', 1, type=int)
        per_page = 20

        # Get users
        users_data = UserDAL.get_all_users_paginated(
            page=page,
            per_page=per_page,
            role_filter=role_filter,
            status_filter=status_filter,
            search_query=search_query
        )

        return render_template(
            'admin/users.html',
            result=users_data,
            role_filter=role_filter,
            status_filter=status_filter,
            search_query=search_query
        )

    except Exception as e:
        logger.error(f"Error loading users: {str(e)}", exc_info=True)
        flash('Error loading users.', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/users/<int:user_id>')
@login_required
@role_required('admin')
def user_detail(user_id):
    """
    View detailed information about a specific user.
    """
    try:
        user = UserDAL.get_user_by_id(user_id)
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('admin.users'))

        # Compute status for display
        if user.get('is_banned'):
            user['status'] = 'banned'
        else:
            user['status'] = 'active'

        # Get pagination parameters for each section
        resources_page = request.args.get('resources_page', 1, type=int)
        bookings_page = request.args.get('bookings_page', 1, type=int)
        reviews_page = request.args.get('reviews_page', 1, type=int)

        # Get user's resources (owned by this user) - fetch ALL
        user_resources = ResourceDAL.get_all_resources(
            owner_type='user',
            owner_id=user_id,
            limit=1000  # Fetch all resources
        )

        # Get user's bookings - fetch ALL
        user_bookings = BookingDAL.get_bookings_by_user(user_id, limit=1000)

        # Get user's reviews - fetch ALL
        user_reviews = ReviewDAL.get_reviews_by_user(user_id, limit=1000)

        return render_template(
            'admin/user_detail.html',
            user=user,
            user_resources=user_resources,
            user_bookings=user_bookings,
            user_reviews=user_reviews,
            resources_page=resources_page,
            bookings_page=bookings_page,
            reviews_page=reviews_page
        )

    except Exception as e:
        logger.error(f"Error loading user detail: {str(e)}", exc_info=True)
        flash('Error loading user details.', 'danger')
        return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/change-role', methods=['POST'])
@login_required
@role_required('admin')
def change_user_role(user_id):
    """
    Change a user's role.
    """
    try:
        new_role = request.form.get('role', '').strip().lower()

        if new_role not in ['student', 'staff', 'admin']:
            flash('Invalid role.', 'danger')
            return redirect(url_for('admin.users'))

        # Prevent admin from changing their own role
        if user_id == current_user.user_id:
            flash('Cannot change your own role.', 'danger')
            return redirect(url_for('admin.users'))

        user = UserDAL.get_user_by_id(user_id)
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('admin.users'))

        UserDAL.update_user_role(user_id, new_role)

        logger.info(f"Admin {current_user.email} changed user {user['email']} role to {new_role}")
        flash(f"User role changed to {new_role}.", 'success')

        # Redirect back to user detail if coming from there, otherwise to users list
        return redirect(request.referrer or url_for('admin.users'))

    except Exception as e:
        logger.error(f"Error changing user role: {str(e)}", exc_info=True)
        flash('Error changing user role.', 'danger')
        return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/ban', methods=['POST'])
@login_required
@role_required('admin')
def ban_user(user_id):
    """
    Ban a user from accessing the system and cancel all their active bookings.
    """
    try:
        # Prevent admin from banning themselves
        if user_id == current_user.user_id:
            flash('Cannot ban your own account.', 'danger')
            return redirect(url_for('admin.users'))

        user = UserDAL.get_user_by_id(user_id)
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('admin.users'))

        # Ban the user
        UserDAL.ban_user(user_id)

        # Cancel all active bookings for this user
        cancelled_count = BookingDAL.cancel_bookings_by_user(user_id)
        if cancelled_count > 0:
            logger.info(f"Admin {current_user.email} cancelled {cancelled_count} bookings for banned user {user['email']}")

        # Send system notification
        try:
            system_messaging.notify_user_banned(
                user_id=user_id,
                cancelled_bookings_count=cancelled_count
            )
        except Exception as e:
            logger.error(f"Failed to send ban notification: {e}")

        logger.info(f"Admin {current_user.email} banned user {user['email']}")
        flash(f"User {user['name']} has been banned.", 'success')
        return redirect(request.referrer or url_for('admin.users'))

    except Exception as e:
        logger.error(f"Error banning user: {str(e)}", exc_info=True)
        flash('Error banning user.', 'danger')
        return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/unban', methods=['POST'])
@login_required
@role_required('admin')
def unban_user(user_id):
    """
    Unban a user, allowing them to access the system again.
    """
    try:
        user = UserDAL.get_user_by_id(user_id)
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('admin.users'))

        UserDAL.unban_user(user_id)

        logger.info(f"Admin {current_user.email} unbanned user {user['email']}")
        flash(f"User {user['name']} has been unbanned.", 'success')
        return redirect(request.referrer or url_for('admin.users'))

    except Exception as e:
        logger.error(f"Error unbanning user: {str(e)}", exc_info=True)
        flash('Error unbanning user.', 'danger')
        return redirect(url_for('admin.users'))


# =============================================================================
# RESOURCE MANAGEMENT
# =============================================================================

@admin_bp.route('/resources')
@login_required
@role_required('admin')
def resources():
    """
    List all resources with filtering and pagination.
    """
    try:
        # Get filters from query params
        status_filter = request.args.get('status', '')
        category_filter = request.args.get('category', '')
        search_query = request.args.get('search', '')
        owner_filter = request.args.get('owner', '')
        page = request.args.get('page', 1, type=int)
        per_page = 20

        # Get resources
        resources_data = ResourceDAL.get_all_resources_paginated(
            page=page,
            per_page=per_page,
            status_filter=status_filter,
            category_filter=category_filter,
            search_query=search_query,
            owner_filter=owner_filter
        )

        # Get categories for filter dropdown
        categories = ResourceDAL.get_all_categories()

        return render_template(
            'admin/resources.html',
            result=resources_data,
            categories=categories,
            status_filter=status_filter,
            category_filter=category_filter,
            search_query=search_query,
            owner_filter=owner_filter
        )

    except Exception as e:
        logger.error(f"Error loading resources: {str(e)}", exc_info=True)
        flash('Error loading resources.', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/resources/<int:resource_id>/update-status', methods=['POST'])
@login_required
@role_required('admin')
def update_resource_status(resource_id):
    """
    Update resource status (draft, published, archived).
    If archiving, cancels all active bookings and hides reviews.
    If publishing/unarchiving, shows hidden reviews.
    """
    try:
        new_status = request.form.get('status', '').strip().lower()

        if new_status not in ['draft', 'published', 'archived']:
            flash('Invalid status.', 'error')
            return redirect(url_for('admin.resources'))

        resource = ResourceDAL.get_resource_by_id(resource_id)
        if not resource:
            flash('Resource not found.', 'error')
            return redirect(url_for('admin.resources'))

        # If archiving, cancel all active bookings and hide reviews
        if new_status == 'archived':
            cancelled_count = BookingDAL.cancel_bookings_by_resource(resource_id)
            if cancelled_count > 0:
                logger.info(f"Admin {current_user.email} cancelled {cancelled_count} bookings for resource {resource['title']}")

            hidden_count = ReviewDAL.hide_reviews_by_resource(resource_id)
            if hidden_count > 0:
                logger.info(f"Admin {current_user.email} hid {hidden_count} reviews for archived resource {resource['title']}")

        # If publishing, show previously hidden reviews
        elif new_status == 'published':
            shown_count = ReviewDAL.show_reviews_by_resource(resource_id)
            if shown_count > 0:
                logger.info(f"Admin {current_user.email} showed {shown_count} reviews for published resource {resource['title']}")

        ResourceDAL.update_resource_status(resource_id, new_status)

        logger.info(f"Admin {current_user.email} changed resource {resource['title']} status to {new_status}")

        flash(f'Resource status changed to {new_status}.', 'success')
        return redirect(url_for('admin.resources'))

    except Exception as e:
        logger.error(f"Error updating resource status: {str(e)}", exc_info=True)
        flash('Error updating resource status.', 'error')
        return redirect(url_for('admin.resources'))


@admin_bp.route('/resources/<int:resource_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_resource(resource_id):
    """
    Delete a resource (admin only).
    Automatically cancels all active bookings before deletion.
    """
    try:
        resource = ResourceDAL.get_resource_by_id(resource_id)
        if not resource:
            flash('Resource not found.', 'error')
            return redirect(url_for('admin.resources'))

        # Cancel all active bookings before deleting
        cancelled_count = BookingDAL.cancel_bookings_by_resource(resource_id)
        if cancelled_count > 0:
            logger.info(f"Admin {current_user.email} cancelled {cancelled_count} bookings before deleting resource {resource['title']}")

        ResourceDAL.delete_resource(resource_id)

        logger.info(f"Admin {current_user.email} deleted resource {resource['title']}")

        flash('Resource deleted successfully.', 'success')
        return redirect(url_for('admin.resources'))

    except Exception as e:
        logger.error(f"Error deleting resource: {str(e)}", exc_info=True)
        flash('Error deleting resource.', 'error')
        return redirect(url_for('admin.resources'))


# =============================================================================
# BOOKING MANAGEMENT
# =============================================================================

@admin_bp.route('/bookings')
@login_required
@role_required('admin')
def bookings():
    """
    List all bookings with filtering and pagination.
    """
    try:
        # Auto-complete past bookings
        BookingDAL.auto_complete_past_bookings()

        # Get filters from query params
        status_filter = request.args.get('status', '')
        search_query = request.args.get('search', '')
        booking_id = request.args.get('booking_id', '', type=str)
        page = request.args.get('page', 1, type=int)
        per_page = 20

        # Get bookings
        bookings_data = BookingDAL.get_all_bookings_paginated(
            page=page,
            per_page=per_page,
            status_filter=status_filter,
            search_query=search_query,
            booking_id=booking_id
        )

        return render_template(
            'admin/bookings.html',
            result=bookings_data,
            status_filter=status_filter,
            search_query=search_query
        )

    except Exception as e:
        logger.error(f"Error loading bookings: {str(e)}", exc_info=True)
        flash('Error loading bookings.', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
@login_required
@role_required('admin')
def cancel_booking(booking_id):
    """
    Cancel a booking (admin override).
    """
    try:
        booking = BookingDAL.get_booking_by_id(booking_id)
        if not booking:
            flash('Booking not found.', 'danger')
            return redirect(url_for('admin.bookings'))

        if booking['status'] == 'cancelled':
            flash('Booking is already cancelled.', 'warning')
            return redirect(url_for('admin.bookings'))

        if booking['status'] == 'completed':
            flash('Cannot cancel a completed booking.', 'warning')
            return redirect(url_for('admin.bookings'))

        # Cancel the booking
        BookingDAL.cancel_booking(booking_id)

        # Send system notification to the user
        try:
            system_messaging.notify_booking_cancelled_by_admin(
                user_id=booking['requester_id'],
                booking_id=booking_id,
                resource_title=booking.get('resource_title', 'Resource')
            )
        except Exception as e:
            logger.error(f"Failed to send cancellation notification: {e}")

        logger.info(f"Admin {current_user.email} cancelled booking {booking_id}")
        flash('Booking cancelled successfully.', 'success')
        return redirect(url_for('admin.bookings'))

    except Exception as e:
        logger.error(f"Error cancelling booking: {str(e)}", exc_info=True)
        flash('Error cancelling booking.', 'danger')
        return redirect(url_for('admin.bookings'))


# =============================================================================
# REVIEW MODERATION
# =============================================================================

@admin_bp.route('/reviews')
@login_required
@role_required('admin')
def reviews():
    """
    List all reviews with filtering and pagination.
    """
    try:
        # Get filters from query params
        status_filter = request.args.get('status', '')
        search_query = request.args.get('q', '')
        page = request.args.get('page', 1, type=int)
        per_page = 20

        # Get reviews
        reviews_data = ReviewDAL.get_all_reviews_paginated(
            page=page,
            per_page=per_page,
            visibility_filter=status_filter
        )

        return render_template(
            'admin/reviews.html',
            result=reviews_data,
            status_filter=status_filter,
            search_query=search_query
        )

    except Exception as e:
        logger.error(f"Error loading reviews: {str(e)}", exc_info=True)
        flash('Error loading reviews.', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/reviews/<int:review_id>/approve', methods=['POST'])
@login_required
@role_required('admin')
def approve_review(review_id):
    """
    Approve a pending review (make it visible).
    """
    try:
        review = ReviewDAL.get_review_by_id(review_id)
        if not review:
            flash('Review not found.', 'danger')
            return redirect(url_for('admin.reviews'))

        ReviewDAL.approve_review(review_id)

        logger.info(f"Admin {current_user.email} approved review {review_id}")
        flash('Review approved successfully.', 'success')
        return redirect(url_for('admin.reviews'))

    except Exception as e:
        logger.error(f"Error approving review: {str(e)}", exc_info=True)
        flash('Error approving review.', 'danger')
        return redirect(url_for('admin.reviews'))


@admin_bp.route('/reviews/<int:review_id>/hide', methods=['POST'])
@login_required
@role_required('admin')
def hide_review(review_id):
    """
    Hide a review (make it invisible to users).
    """
    try:
        review = ReviewDAL.get_review_by_id(review_id)
        if not review:
            flash('Review not found.', 'danger')
            return redirect(url_for('admin.reviews'))

        ReviewDAL.hide_review(review_id)

        logger.info(f"Admin {current_user.email} hid review {review_id}")
        flash('Review hidden successfully.', 'success')
        return redirect(url_for('admin.reviews'))

    except Exception as e:
        logger.error(f"Error hiding review: {str(e)}", exc_info=True)
        flash('Error hiding review.', 'danger')
        return redirect(url_for('admin.reviews'))


@admin_bp.route('/reviews/<int:review_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_review(review_id):
    """
    Delete a review (moderation).
    """
    try:
        reason = request.form.get('reason', 'Removed by administrator')

        review = ReviewDAL.get_review_by_id(review_id)
        if not review:
            flash('Review not found.', 'danger')
            return redirect(url_for('admin.reviews'))

        # Get resource_id before deleting for redirect
        resource_id = review.get('resource_id')

        ReviewDAL.delete_review(review_id)

        logger.info(f"Admin {current_user.email} deleted review {review_id}: {reason}")
        flash('Review deleted successfully by moderator.', 'success')

        # Check if there's a redirect parameter (when called from resource page)
        redirect_to = request.form.get('redirect_to', '')
        if redirect_to == 'resource' and resource_id:
            return redirect(url_for('resources.view_resource', resource_id=resource_id))

        return redirect(url_for('admin.reviews'))

    except Exception as e:
        logger.error(f"Error deleting review: {str(e)}", exc_info=True)
        flash('Error deleting review.', 'danger')
        return redirect(url_for('admin.reviews'))
