"""
Campus Resource Hub - Booking Controller
==========================================
MVC Role: Controller for booking management
MCP Role: Booking request handling for AI-assisted scheduling

Handles:
- Booking calendar views
- Creating new bookings
- Approving/rejecting bookings
- Cancelling bookings
- Viewing user bookings
- Waitlist management
"""

import sys
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from src.data_access.booking_dal import BookingDAL
from src.data_access.resource_dal import ResourceDAL
from src.data_access.message_dal import MessageDAL
from src.data_access.review_dal import ReviewDAL
from src.models.booking import Booking
from src.forms.booking_forms import BookingForm, BookingApprovalForm, BookingCancellationForm, WaitlistForm
from src.utils.decorators import role_required
from src.utils import system_messaging

# Create blueprint
booking_bp = Blueprint('booking', __name__, url_prefix='/bookings')


@booking_bp.route('/')
@login_required
def index():
    """
    View all bookings for current user.

    Returns:
        HTML: User's booking list
    """
    # Auto-complete past bookings
    BookingDAL.auto_complete_past_bookings()

    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    upcoming_only = request.args.get('upcoming', 'true') == 'true'
    page = int(request.args.get('page', 1))
    per_page = 20

    # Build status filter
    status = None if status_filter == 'all' else status_filter

    # Get total count for pagination
    total_count = BookingDAL.count_bookings_by_user(
        user_id=current_user.user_id,
        status=status,
        upcoming_only=upcoming_only
    )

    # Calculate pagination info
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1

    # Get bookings
    bookings_data = BookingDAL.get_bookings_by_user(
        user_id=current_user.user_id,
        status=status,
        upcoming_only=upcoming_only,
        limit=per_page,
        offset=(page - 1) * per_page
    )

    # Convert to Booking objects
    bookings = [Booking(b) for b in bookings_data]

    # Check review status for completed bookings
    booking_review_status = {}
    for booking in bookings:
        if booking.status == 'completed':
            has_reviewed = ReviewDAL.has_user_reviewed_booking(
                booking.booking_id,
                current_user.user_id
            )
            booking_review_status[booking.booking_id] = has_reviewed

    # Build pagination object
    pagination = {
        'page': page,
        'per_page': per_page,
        'total_count': total_count,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages
    }

    return render_template(
        'bookings/index.html',
        bookings=bookings,
        booking_review_status=booking_review_status,
        pagination=pagination,
        status_filter=status_filter,
        upcoming_only=upcoming_only,
        title='My Bookings',
        page_name='bookings'
    )


@booking_bp.route('/<int:booking_id>')
@login_required
def detail(booking_id):
    """
    View booking details.

    Args:
        booking_id (int): Booking ID

    Returns:
        HTML: Booking detail page
    """
    booking_data = BookingDAL.get_booking_by_id(booking_id)

    if not booking_data:
        flash('Booking not found.', 'error')
        return redirect(url_for('booking.index'))

    booking = Booking(booking_data)

    # Check if user has permission to view this booking
    resource = ResourceDAL.get_resource_by_id(booking.resource_id)
    is_owner = (resource and resource.get('owner_type') == 'user'
                and resource.get('owner_id') == current_user.user_id)
    is_requester = booking.requester_id == current_user.user_id
    is_admin = current_user.role == 'admin'

    if not (is_requester or is_owner or is_admin):
        flash('You do not have permission to view this booking.', 'error')
        return redirect(url_for('booking.index'))

    # Create cancellation form if applicable
    cancel_form = BookingCancellationForm() if booking.can_be_cancelled(current_user.user_id) else None

    # Create approval form if applicable
    approval_form = None
    if is_owner and booking.can_be_approved():
        approval_form = BookingApprovalForm()
        approval_form.booking_id.data = booking_id

    return render_template(
        'bookings/detail.html',
        booking=booking,
        cancel_form=cancel_form,
        approval_form=approval_form,
        is_owner=is_owner,
        is_requester=is_requester,
        title=f'Booking Details',
        page_name='bookings'
    )


@booking_bp.route('/resource/<int:resource_id>/calendar')
@login_required
def calendar(resource_id):
    """
    View booking calendar for a resource.

    Args:
        resource_id (int): Resource ID

    Returns:
        HTML: Calendar view with existing bookings
    """
    # Get resource
    resource_data = ResourceDAL.get_resource_by_id(resource_id)
    if not resource_data:
        flash('Resource not found.', 'error')
        return redirect(url_for('resource.index'))

    # Get date range (default: current month)
    try:
        year = int(request.args.get('year', datetime.now().year))
        month = int(request.args.get('month', datetime.now().month))
    except ValueError:
        year = datetime.now().year
        month = datetime.now().month

    # Calculate start and end of month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    # Get all bookings for this resource in the date range
    bookings_data = BookingDAL.get_bookings_by_resource(
        resource_id=resource_id,
        start_date=start_date,
        end_date=end_date,
        status='approved'  # Only show approved bookings on calendar
    )

    # Convert to Booking objects
    bookings = [Booking(b) for b in bookings_data]

    # Check if user is owner
    is_owner = (resource_data.get('owner_type') == 'user'
                and resource_data.get('owner_id') == current_user.user_id)

    return render_template(
        'bookings/calendar.html',
        resource=resource_data,
        bookings=bookings,
        year=year,
        month=month,
        is_owner=is_owner,
        title=f'Calendar - {resource_data["title"]}',
        page_name='bookings'
    )


@booking_bp.route('/resource/<int:resource_id>/create', methods=['GET', 'POST'])
@login_required
def create(resource_id):
    """
    Create a new booking.

    Args:
        resource_id (int): Resource ID

    Returns:
        HTML: Booking creation form or redirect on success
    """
    # Get resource
    resource_data = ResourceDAL.get_resource_by_id(resource_id)
    if not resource_data:
        flash('Resource not found.', 'error')
        return redirect(url_for('resource.index'))

    # Check if resource is published
    if resource_data.get('status') != 'published':
        flash('This resource is not available for booking.', 'error')
        return redirect(url_for('resource.detail', resource_id=resource_id))

    form = BookingForm()
    form.resource_id.data = resource_id

    if form.validate_on_submit():
        try:
            # Calculate booking duration in minutes
            booking_duration = (form.end_datetime.data - form.start_datetime.data).total_seconds() / 60

            # Validate against max duration if availability_rules exist
            if resource_data.get('availability_rules'):
                import json
                try:
                    availability_rules = json.loads(resource_data['availability_rules'])
                    max_duration = availability_rules.get('booking_duration_max')

                    if max_duration and booking_duration > max_duration:
                        hours = max_duration / 60 if max_duration >= 60 else None
                        if hours and hours == int(hours):
                            max_str = f"{int(hours)} hour{'s' if hours != 1 else ''}"
                        elif hours:
                            max_str = f"{hours:.1f} hours"
                        else:
                            max_str = f"{int(max_duration)} minutes"

                        flash(f'Booking duration exceeds the maximum allowed time of {max_str}.', 'error')
                        return render_template(
                            'bookings/create.html',
                            form=form,
                            resource=resource_data,
                            title=f'Book {resource_data["title"]}',
                            page_name='bookings'
                        )
                except (json.JSONDecodeError, KeyError):
                    pass  # If availability_rules is malformed, skip validation

            # Check if user is the resource owner - owners don't need approval for their own resources
            is_owner = (
                resource_data.get('owner_type') == 'user' and
                resource_data.get('owner_id') == current_user.user_id
            )

            # Create booking
            # Owners skip approval even if requires_approval is True
            booking_id = BookingDAL.create_booking(
                resource_id=resource_id,
                requester_id=current_user.user_id,
                start_datetime=form.start_datetime.data,
                end_datetime=form.end_datetime.data,
                notes=form.notes.data,
                approval_required=bool(resource_data.get('requires_approval')) and not is_owner
            )

            if booking_id:
                # Send system notification
                print(f"[BOOKING DEBUG] Booking {booking_id} created successfully", file=sys.stderr, flush=True)
                print(f"[BOOKING DEBUG] requires_approval={resource_data.get('requires_approval')}, is_owner={is_owner}", file=sys.stderr, flush=True)
                print(f"[BOOKING DEBUG] About to send system notification", file=sys.stderr, flush=True)
                try:
                    if resource_data.get('requires_approval') and not is_owner:
                        # Booking needs approval - send "awaiting approval" notification
                        print(f"[BOOKING DEBUG] Sending awaiting approval notification", file=sys.stderr, flush=True)
                        result = system_messaging.send_system_message(
                            recipient_id=current_user.user_id,
                            subject=f"Booking Request Submitted - {resource_data.get('title', 'Resource')}",
                            content=f"""Your booking request has been submitted and is awaiting approval from the resource owner.

Resource: {resource_data.get('title', 'Resource')}
Booking ID: {booking_id}
Date: {form.start_datetime.data.strftime('%B %d, %Y')}
Time: {form.start_datetime.data.strftime('%I:%M %p')} - {form.end_datetime.data.strftime('%I:%M %p')}

You will receive another notification once your booking is reviewed. You can check the status in your bookings page."""
                        )
                        print(f"[BOOKING DEBUG] Awaiting approval notification result: {result}", file=sys.stderr, flush=True)
                    else:
                        # Booking is auto-approved - send approval notification
                        print(f"[BOOKING DEBUG] Sending auto-approved notification", file=sys.stderr, flush=True)
                        result = system_messaging.notify_booking_approved(
                            booking_id=booking_id,
                            user_id=current_user.user_id,
                            resource_title=resource_data.get('title', 'Resource'),
                            start_datetime=form.start_datetime.data,
                            end_datetime=form.end_datetime.data
                        )
                        print(f"[BOOKING DEBUG] Auto-approved notification result: {result}", file=sys.stderr, flush=True)
                    print(f"[BOOKING DEBUG] System notification sent successfully", file=sys.stderr, flush=True)
                except Exception as e:
                    # Log error but don't fail the booking
                    print(f"[BOOKING DEBUG] EXCEPTION sending system notification: {e}", file=sys.stderr, flush=True)
                    import traceback
                    traceback.print_exc(file=sys.stderr)

                if resource_data.get('requires_approval') and not is_owner:
                    flash('Booking request submitted! Awaiting approval from resource owner.', 'success')
                else:
                    flash('Booking confirmed! You can view it in your bookings.', 'success')

                return redirect(url_for('booking.detail', booking_id=booking_id))
            else:
                # Booking conflict
                flash('This time slot is not available. Please choose a different time or join the waitlist.', 'error')

        except ValueError as e:
            flash(f'Error creating booking: {str(e)}', 'error')
        except Exception as e:
            print(f"ERROR creating booking: {e}", file=sys.stderr, flush=True)
            flash('An error occurred while creating the booking. Please try again.', 'error')

    # Pre-populate form with query parameters if provided
    if request.method == 'GET':
        start_param = request.args.get('start')
        end_param = request.args.get('end')
        if start_param:
            try:
                form.start_datetime.data = datetime.fromisoformat(start_param)
            except ValueError:
                pass
        if end_param:
            try:
                form.end_datetime.data = datetime.fromisoformat(end_param)
            except ValueError:
                pass

    return render_template(
        'bookings/create.html',
        form=form,
        resource=resource_data,
        title=f'Book {resource_data["title"]}',
        page_name='bookings'
    )


@booking_bp.route('/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel(booking_id):
    """
    Cancel a booking.

    Args:
        booking_id (int): Booking ID

    Returns:
        Redirect to booking list
    """
    booking_data = BookingDAL.get_booking_by_id(booking_id)

    if not booking_data:
        flash('Booking not found.', 'error')
        return redirect(url_for('booking.index'))

    booking = Booking(booking_data)

    # Check permission
    if not booking.can_be_cancelled(current_user.user_id):
        flash('You cannot cancel this booking.', 'error')
        return redirect(url_for('booking.detail', booking_id=booking_id))

    # Cancel booking
    if BookingDAL.cancel_booking(booking_id):
        # Send system notification
        try:
            resource_data = ResourceDAL.get_resource_by_id(booking.resource_id)
            if resource_data:
                cancelled_by = "user" if booking.requester_id == current_user.user_id else "admin"
                system_messaging.notify_booking_cancelled(
                    booking_id=booking_id,
                    user_id=booking.requester_id,
                    resource_title=resource_data.get('title', 'Resource'),
                    reason="Cancelled by user request" if cancelled_by == "user" else "Cancelled by administrator",
                    cancelled_by=cancelled_by
                )
        except Exception as e:
            print(f"Failed to send system notification: {e}")

        flash('Booking cancelled successfully.', 'success')
    else:
        flash('Failed to cancel booking.', 'error')

    return redirect(url_for('booking.index'))


@booking_bp.route('/<int:booking_id>/approve', methods=['POST'])
@login_required
@role_required('staff', 'admin')
def approve(booking_id):
    """
    Approve or reject a booking.

    Args:
        booking_id (int): Booking ID

    Returns:
        Redirect to bookings pending approval
    """
    booking_data = BookingDAL.get_booking_by_id(booking_id)

    if not booking_data:
        flash('Booking not found.', 'error')
        return redirect(url_for('booking.pending_approvals'))

    booking = Booking(booking_data)
    resource = ResourceDAL.get_resource_by_id(booking.resource_id)

    # Check if user is resource owner
    is_owner = (resource and resource.get('owner_type') == 'user'
                and resource.get('owner_id') == current_user.user_id)
    is_admin = current_user.role == 'admin'

    if not (is_owner or is_admin):
        flash('You do not have permission to approve this booking.', 'error')
        return redirect(url_for('booking.pending_approvals'))

    # Check if booking can be approved
    if not booking.can_be_approved():
        flash('This booking cannot be approved.', 'error')
        return redirect(url_for('booking.pending_approvals'))

    # Get form data
    form = BookingApprovalForm()

    if form.validate_on_submit():
        action = form.action.data
        comment = form.comment.data

        # Update booking status
        success = BookingDAL.update_booking_status(
            booking_id=booking_id,
            new_status=action,
            approver_id=current_user.user_id,
            comment=comment
        )

        if success:
            # Send system notification
            try:
                if action == 'approved':
                    system_messaging.notify_booking_approved(
                        booking_id=booking_id,
                        user_id=booking.requester_id,
                        resource_title=resource.get('title', 'Resource') if resource else 'Resource',
                        start_datetime=booking.start_datetime if hasattr(booking.start_datetime, 'strftime') else datetime.fromisoformat(str(booking.start_datetime)),
                        end_datetime=booking.end_datetime if hasattr(booking.end_datetime, 'strftime') else datetime.fromisoformat(str(booking.end_datetime))
                    )
                else:
                    system_messaging.notify_booking_rejected(
                        booking_id=booking_id,
                        user_id=booking.requester_id,
                        resource_title=resource.get('title', 'Resource') if resource else 'Resource',
                        rejection_reason=comment
                    )
            except Exception as e:
                print(f"Failed to send system notification: {e}")

            if action == 'approved':
                flash('Booking approved successfully!', 'success')
            else:
                flash('Booking rejected.', 'info')
        else:
            flash('Failed to process booking approval.', 'error')
    else:
        flash('Invalid form submission.', 'error')

    return redirect(url_for('booking.pending_approvals'))


@booking_bp.route('/pending')
@login_required
@role_required('staff', 'admin')
def pending_approvals():
    """
    View bookings pending approval for resources owned by current user.

    Returns:
        HTML: List of pending bookings
    """
    page = int(request.args.get('page', 1))
    per_page = 20

    # Get pending bookings for user's resources
    bookings_data = BookingDAL.get_pending_approvals(
        resource_owner_id=current_user.user_id,
        owner_type='user',
        limit=per_page,
        offset=(page - 1) * per_page
    )

    # Convert to Booking objects
    bookings = [Booking(b) for b in bookings_data]

    # Create approval forms for each booking
    forms = {}
    for booking in bookings:
        form = BookingApprovalForm()
        form.booking_id.data = booking.booking_id
        forms[booking.booking_id] = form

    return render_template(
        'bookings/pending_approvals.html',
        bookings=bookings,
        forms=forms,
        page=page,
        title='Pending Approvals',
        page_name='bookings'
    )


@booking_bp.route('/resource/<int:resource_id>/available-slots')
@login_required
def available_slots(resource_id):
    """
    Get available time slots for a resource (AJAX endpoint).

    Args:
        resource_id (int): Resource ID

    Returns:
        JSON: List of available slots
    """
    try:
        # Get date range from query parameters
        start_str = request.args.get('start')
        end_str = request.args.get('end')
        duration = int(request.args.get('duration', 60))  # Default 1 hour

        if not start_str or not end_str:
            return jsonify({'error': 'Missing start or end date'}), 400

        start_date = datetime.fromisoformat(start_str)
        end_date = datetime.fromisoformat(end_str)

        # Get available slots
        slots = BookingDAL.get_available_slots(
            resource_id=resource_id,
            start_date=start_date,
            end_date=end_date,
            slot_duration_minutes=duration
        )

        # Convert to JSON-serializable format
        slots_json = [
            {
                'start': slot['start_datetime'].isoformat(),
                'end': slot['end_datetime'].isoformat()
            }
            for slot in slots
        ]

        return jsonify({'slots': slots_json})

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"ERROR getting available slots: {e}", file=sys.stderr, flush=True)
        return jsonify({'error': 'Internal server error'}), 500


@booking_bp.route('/resource/<int:resource_id>/waitlist', methods=['GET', 'POST'])
@login_required
def waitlist(resource_id):
    """
    Join waitlist for a resource.

    Args:
        resource_id (int): Resource ID

    Returns:
        HTML: Waitlist form or redirect on success
    """
    # Get resource
    resource_data = ResourceDAL.get_resource_by_id(resource_id)
    if not resource_data:
        flash('Resource not found.', 'error')
        return redirect(url_for('resource.index'))

    form = WaitlistForm()
    form.resource_id.data = resource_id

    if form.validate_on_submit():
        try:
            waitlist_id = BookingDAL.add_to_waitlist(
                resource_id=resource_id,
                user_id=current_user.user_id,
                desired_start_datetime=form.desired_start_datetime.data,
                desired_end_datetime=form.desired_end_datetime.data
            )

            if waitlist_id:
                flash('You have been added to the waitlist! We will notify you when a slot becomes available.', 'success')
                return redirect(url_for('resource.detail', resource_id=resource_id))
            else:
                flash('Failed to join waitlist. Please try again.', 'error')

        except Exception as e:
            print(f"ERROR adding to waitlist: {e}", file=sys.stderr, flush=True)
            flash('An error occurred. Please try again.', 'error')

    return render_template(
        'bookings/waitlist.html',
        form=form,
        resource=resource_data,
        title=f'Join Waitlist - {resource_data["title"]}',
        page_name='bookings'
    )


@booking_bp.route('/calendar-data/<int:resource_id>')
@login_required
def calendar_data(resource_id):
    """
    Get booking data for calendar view (AJAX endpoint).

    Args:
        resource_id (int): Resource ID

    Returns:
        JSON: Booking events for calendar
    """
    try:
        # Get date range from query parameters
        start_str = request.args.get('start')
        end_str = request.args.get('end')

        if not start_str or not end_str:
            return jsonify({'error': 'Missing start or end date'}), 400

        start_date = datetime.fromisoformat(start_str.split('T')[0])
        end_date = datetime.fromisoformat(end_str.split('T')[0])

        # Get bookings
        bookings_data = BookingDAL.get_bookings_by_resource(
            resource_id=resource_id,
            start_date=start_date,
            end_date=end_date
        )

        # Convert to FullCalendar event format
        # Filter out cancelled and rejected bookings from the calendar display
        events = []
        for booking_data in bookings_data:
            booking = Booking(booking_data)

            # Skip cancelled and rejected bookings - they should not block time slots
            if booking.status in ['cancelled', 'rejected']:
                continue

            # Determine color based on status
            color_map = {
                'approved': '#22c55e',
                'pending': '#fbbf24',
                'completed': '#3b82f6'
            }

            events.append({
                'id': booking.booking_id,
                'title': booking.requester_name or f'Booking #{booking.booking_id}',
                'start': booking.start_datetime.isoformat(),
                'end': booking.end_datetime.isoformat(),
                'color': color_map.get(booking.status, '#6b7280'),
                'extendedProps': {
                    'status': booking.status,
                    'notes': booking.notes,
                    'requester_email': booking.requester_email
                }
            })

        return jsonify(events)

    except Exception as e:
        print(f"ERROR getting calendar data: {e}", file=sys.stderr, flush=True)
        return jsonify({'error': 'Internal server error'}), 500


@booking_bp.route('/api/pending_approvals_count')
@login_required
def api_pending_approvals_count():
    """
    API endpoint to get count of pending approvals for current user.
    Used for auto-updating notification badge.

    Returns:
        JSON: {'pending_count': int}
    """
    bookings_data = BookingDAL.get_pending_approvals(
        resource_owner_id=current_user.user_id,
        owner_type='user'
    )

    return jsonify({
        'pending_count': len(bookings_data)
    })
