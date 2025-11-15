"""
Campus Resource Hub - Resource Controller
==========================================
MVC Role: Controller for resource management (CRUD operations)

Handles:
- Browse/search resources
- View resource details
- Create new resources (staff/admin only)
- Edit resources (owner/admin only)
- Deactivate resources (owner/admin only)

Security:
- Role-based access control (RBAC)
- Ownership verification
- CSRF protection
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_required, current_user
from src.data_access.resource_dal import ResourceDAL
from src.data_access.booking_dal import BookingDAL
from src.data_access.message_dal import MessageDAL
from src.data_access.review_dal import ReviewDAL
from src.models.resource import Resource
from src.models.review import Review
from src.utils.decorators import role_required, owner_required
from src.utils.security import sanitize_html
from src.utils import system_messaging
from werkzeug.utils import secure_filename
import logging
import os
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Create blueprint
resource_bp = Blueprint('resource', __name__, url_prefix='/resources')


@resource_bp.route('/')
@resource_bp.route('/browse')
def index():
    """
    Browse/search resources (PUBLIC - no login required).

    Query Parameters:
        - q: Search query
        - category: Category ID filter
        - status: Status filter (default: 'published')
        - sort: Sort by ('title', 'created_at', 'rating')
        - page: Page number (default: 1)

    Returns:
        HTML: Resource browse page with search results
    """
    # Get query parameters
    search_query = request.args.get('q', '').strip()
    category_id = request.args.get('category', type=int)
    location = request.args.get('location', '').strip()
    min_capacity = request.args.get('capacity', type=int)
    availability_date = request.args.get('availability_date', '').strip()
    availability_time = request.args.get('availability_time', '').strip()
    status = request.args.get('status', 'published')
    sort_by = request.args.get('sort', 'recent')
    page = request.args.get('page', 1, type=int)
    per_page = 12

    offset = (page - 1) * per_page

    try:
        # Get all categories for filter dropdown
        categories = ResourceDAL.get_all_categories()

        # Get total count for pagination FIRST (using same filters)
        total_count = ResourceDAL.count_search_resources(
            search_query=search_query if search_query else None,
            category_id=category_id,
            location=location if location else None,
            min_capacity=min_capacity,
            availability_date=availability_date if availability_date else None,
            availability_time=availability_time if availability_time else None
        )

        # Then get paginated resources
        resources_data = ResourceDAL.search_resources(
            search_query=search_query if search_query else None,
            category_id=category_id,
            location=location if location else None,
            min_capacity=min_capacity,
            availability_date=availability_date if availability_date else None,
            availability_time=availability_time if availability_time else None,
            sort_by=sort_by,
            limit=per_page,
            offset=offset
        )

        # Convert to Resource objects
        resources = [Resource(r) for r in resources_data]

        logger.info(f"Resource browse: query='{search_query}', category={category_id}, found {len(resources)} resources")

        return render_template(
            'resources/index.html',
            title='Browse Resources',
            resources=resources,
            categories=categories,
            search_query=search_query,
            selected_category=category_id,
            selected_location=location,
            selected_capacity=min_capacity,
            selected_date=availability_date,
            selected_time=availability_time,
            selected_sort=sort_by,
            page=page,
            per_page=per_page,
            total_count=total_count,
            total_pages=max(1, (total_count + per_page - 1) // per_page)
        )

    except Exception as e:
        logger.error(f"Error browsing resources: {str(e)}", exc_info=True)
        flash('An error occurred while loading resources. Please try again.', 'danger')
        return render_template('resources/index.html', resources=[], categories=[])


@resource_bp.route('/<int:resource_id>', methods=['GET', 'POST'])
def detail(resource_id):
    """
    View resource detail page and handle booking submissions.

    Args:
        resource_id: Resource ID

    Returns:
        HTML: Resource detail page with booking option
    """
    try:
        resource_data = ResourceDAL.get_resource_by_id(resource_id)

        if not resource_data:
            logger.warning(f"Resource not found: {resource_id}")
            flash('Resource not found.', 'warning')
            return redirect(url_for('resource.index'))

        resource = Resource(resource_data)

        # Only show published resources to non-owners
        if resource.status != 'published':
            if not current_user.is_authenticated:
                flash('This resource is not available.', 'warning')
                return redirect(url_for('resource.index'))

            # Check if user can view (owner or admin)
            is_owner = (resource.owner_type == 'user' and resource.owner_id == current_user.user_id)
            is_admin = current_user.role == 'admin'

            if not (is_owner or is_admin):
                flash('This resource is not available.', 'warning')
                return redirect(url_for('resource.index'))

        # Handle booking submission
        if request.method == 'POST':
            if not current_user.is_authenticated:
                flash('You must be logged in to book a resource.', 'warning')
                return redirect(url_for('auth.login'))

            try:
                # Get form data
                start_datetime_str = request.form.get('start_datetime')
                end_datetime_str = request.form.get('end_datetime')
                purpose = request.form.get('purpose', '').strip()

                # Parse datetime strings
                start_datetime = datetime.fromisoformat(start_datetime_str)
                end_datetime = datetime.fromisoformat(end_datetime_str)

                # Create booking
                booking_id = BookingDAL.create_booking(
                    resource_id=resource_id,
                    requester_id=current_user.user_id,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    notes=purpose if purpose else None,
                    approval_required=resource.requires_approval
                )

                if booking_id:
                    # Send system notification
                    print(f"DEBUG: Booking {booking_id} created, attempting to send system notification...")
                    try:
                        print(f"DEBUG: resource.requires_approval = {resource.requires_approval}")
                        if resource.requires_approval:
                            # Booking needs approval - send "awaiting approval" notification
                            print(f"DEBUG: Sending awaiting approval message to user {current_user.user_id}")
                            result = system_messaging.send_system_message(
                                recipient_id=current_user.user_id,
                                subject=f"Booking Request Submitted - {resource.title}",
                                content=f"""Your booking request has been submitted and is awaiting approval from the resource owner.

Resource: {resource.title}
Booking ID: {booking_id}
Date: {start_datetime.strftime('%B %d, %Y')}
Time: {start_datetime.strftime('%I:%M %p')} - {end_datetime.strftime('%I:%M %p')}

You will receive another notification once your booking is reviewed. You can check the status in your bookings page."""
                            )
                            print(f"DEBUG: Awaiting approval message result = {result}")
                            flash('Your booking request has been submitted and is pending approval.', 'success')
                        else:
                            # Booking is auto-approved - send approval notification
                            print(f"DEBUG: Sending auto-approved message to user {current_user.user_id}")
                            result = system_messaging.notify_booking_approved(
                                booking_id=booking_id,
                                user_id=current_user.user_id,
                                resource_title=resource.title,
                                start_datetime=start_datetime,
                                end_datetime=end_datetime
                            )
                            print(f"DEBUG: Auto-approved message result = {result}")
                            flash('Your booking has been confirmed!', 'success')
                    except Exception as e:
                        # Log error but don't fail the booking
                        print(f"DEBUG ERROR: Failed to send system notification: {e}")
                        logger.error(f"Failed to send system notification: {e}", exc_info=True)
                        # Still show success message to user
                        if resource.requires_approval:
                            flash('Your booking request has been submitted and is pending approval.', 'success')
                        else:
                            flash('Your booking has been confirmed!', 'success')
                else:
                    flash('This time slot is not available. Please choose a different time.', 'danger')
                    logger.warning(f"Booking conflict for resource {resource_id}")

                return redirect(url_for('resource.detail', resource_id=resource_id))

            except ValueError as e:
                flash(f'Invalid booking data: {str(e)}', 'danger')
                logger.error(f"Booking validation error: {str(e)}")
            except Exception as e:
                flash('An error occurred while creating your booking. Please try again.', 'danger')
                logger.error(f"Error creating booking: {str(e)}", exc_info=True)

        # Get reviews and rating summary
        reviews_data = ReviewDAL.get_reviews_by_resource(resource_id, visible_only=True, limit=10)
        reviews = [Review(r) for r in reviews_data]
        rating_summary = ReviewDAL.get_resource_rating_summary(resource_id)

        # Check if current user is the resource owner (for host response functionality)
        is_owner = False
        eligible_booking_id = None
        if current_user.is_authenticated:
            is_owner = (resource.owner_type == 'user' and resource.owner_id == current_user.user_id)

            # Check if user has a completed booking without a review
            user_bookings = BookingDAL.get_bookings_by_user(current_user.user_id)
            for booking in user_bookings:
                if booking['resource_id'] == resource_id and booking['status'] == 'completed':
                    # Check if this booking already has a review
                    existing_reviews = ReviewDAL.get_reviews_by_user(current_user.user_id)
                    has_review = any(r['booking_id'] == booking['booking_id'] for r in existing_reviews)
                    if not has_review:
                        eligible_booking_id = booking['booking_id']
                        break

        # Get availability (TODO: implement when booking is done)
        # availability = ResourceDAL.get_availability(resource_id)

        # Calculate available quantity for equipment/lab instruments (categories 2, 3)
        available_quantity = None
        if resource.capacity and resource.category_id in [2, 3]:
            # Get current bookings for this resource
            now = datetime.now()
            current_bookings = BookingDAL.get_bookings_by_resource(
                resource_id=resource_id,
                start_date=now,
                end_date=now,
                status='approved'
            )
            # Calculate how many items are currently booked
            booked_count = len(current_bookings)
            available_quantity = max(0, resource.capacity - booked_count)

        logger.info(f"Resource detail viewed: {resource_id} ({resource.title})")

        return render_template(
            'resources/detail.html',
            title=resource.title,
            resource=resource,
            available_quantity=available_quantity,
            reviews=reviews,
            rating_summary=rating_summary,
            is_owner=is_owner,
            eligible_booking_id=eligible_booking_id
        )

    except Exception as e:
        logger.error(f"Error loading resource {resource_id}: {str(e)}", exc_info=True)
        flash('An error occurred while loading the resource. Please try again.', 'danger')
        return redirect(url_for('resource.index'))


@resource_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('staff', 'admin')
def create():
    """
    Create new resource - STEP 1: Resource Details (STAFF/ADMIN ONLY).

    GET: Display resource details form
    POST: Save resource details to session and redirect to availability configuration

    Returns:
        HTML: Resource creation form or redirect to availability configuration
    """
    if request.method == 'GET':
        # Get categories for dropdown
        categories = ResourceDAL.get_all_categories()

        return render_template(
            'resources/create.html',
            title='Create Resource',
            categories=categories
        )

    # POST - Process form submission
    try:
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category_id', type=int)
        location = request.form.get('location', '').strip()
        location_details = request.form.get('location_details', '').strip()
        # Combine location and details with dash separator
        if location_details:
            location = f"{location} - {location_details}"
        capacity = request.form.get('capacity', type=int)
        requires_approval = request.form.get('requires_approval') == 'on'

        # Handle image upload
        images = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                # Create unique filename
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                name, ext = os.path.splitext(filename)
                unique_filename = f"{name}_{timestamp}{ext}"

                # Save file
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, unique_filename)
                file.save(file_path)

                # Store relative path
                images = f"/static/uploads/{unique_filename}"

        # Validate required fields
        if not title or not category_id or not location:
            flash('Please fill in all required fields.', 'warning')
            categories = ResourceDAL.get_all_categories()
            return render_template('resources/create.html', categories=categories)

        # Sanitize HTML input
        title = sanitize_html(title)
        description = sanitize_html(description)
        location = sanitize_html(location)

        # Store resource details in session
        session['resource_details'] = {
            'title': title,
            'description': description,
            'category_id': category_id,
            'location': location,
            'capacity': capacity,
            'requires_approval': requires_approval,
            'images': images
        }

        logger.info(f"Resource details saved by {current_user.email}, proceeding to availability configuration")

        # Redirect to availability configuration
        return redirect(url_for('resource.configure_availability'))

    except Exception as e:
        logger.error(f"Error saving resource details: {str(e)}", exc_info=True)
        flash('An error occurred while saving resource details. Please try again.', 'danger')
        categories = ResourceDAL.get_all_categories()
        return render_template('resources/create.html', categories=categories)


@resource_bp.route('/configure-availability', methods=['GET', 'POST'])
@login_required
@role_required('staff', 'admin')
def configure_availability():
    """
    Configure availability rules - STEP 2 of resource creation or editing.

    Requires resource details to be filled first (stored in session).
    - For creation: uses 'resource_details' from session
    - For editing: uses 'resource_edit' from session

    GET: Display availability configuration form
    POST: Create or update resource with availability rules

    Returns:
        HTML: Availability configuration form or redirect to resource detail on success
    """
    # Determine if we're in edit mode or create mode
    edit_mode = 'resource_edit' in session
    create_mode = 'resource_details' in session

    # Check if resource details are in session (either mode)
    if not edit_mode and not create_mode:
        flash('Please fill in resource details first.', 'warning')
        return redirect(url_for('resource.create'))

    if request.method == 'GET':
        # Get existing availability rules if in edit mode
        existing_rules = None
        if edit_mode:
            resource_data = session.get('resource_edit')
            resource_id = resource_data.get('resource_id')
            resource = ResourceDAL.get_resource_by_id(resource_id)
            if resource and resource.get('availability_rules'):
                try:
                    existing_rules = json.loads(resource['availability_rules'])

                    # Normalize weekly_schedule to array format if it's in object format
                    # Old format: {"monday": [["09:00 AM", "05:00 PM"]], ...}
                    # New format: [{day: "monday", slots: [{start_time: "09:00", end_time: "17:00"}]}]
                    if existing_rules and 'weekly_schedule' in existing_rules:
                        weekly_schedule = existing_rules['weekly_schedule']

                        # Check if it's in old object format
                        if isinstance(weekly_schedule, dict):
                            # Convert to new array format
                            normalized_schedule = []
                            for day, slots in weekly_schedule.items():
                                if slots and len(slots) > 0:  # Only include days with slots
                                    day_slots = []
                                    for slot in slots:
                                        if isinstance(slot, list) and len(slot) == 2:
                                            # Convert from ["09:00 AM", "05:00 PM"] to {start_time: "09:00", end_time: "17:00"}
                                            day_slots.append({
                                                'start_time': slot[0],
                                                'end_time': slot[1]
                                            })
                                    if day_slots:
                                        normalized_schedule.append({
                                            'day': day,
                                            'slots': day_slots
                                        })
                            existing_rules['weekly_schedule'] = normalized_schedule

                except json.JSONDecodeError:
                    existing_rules = None

        return render_template(
            'resources/configure_availability.html',
            title='Configure Availability',
            edit_mode=edit_mode,
            existing_rules=existing_rules
        )

    # POST - Process availability rules and create/update resource
    try:
        # Get booking duration constraints
        min_duration = request.form.get('min_duration', type=int)
        max_duration = request.form.get('max_duration', type=int)
        advance_days = request.form.get('advance_days', type=int)
        buffer_time = request.form.get('buffer_time', type=int, default=0)

        # Get listing lifecycle status
        status = request.form.get('status', 'published').strip()
        # Validate status value
        if status not in ['draft', 'published', 'archived']:
            status = 'published'

        # Build weekly schedule from form data
        weekly_schedule = []
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        for day in days:
            # Check if day is enabled
            day_enabled = request.form.get(f'{day}_enabled') == 'on'

            if day_enabled:
                # Collect all time slots for this day
                slots = []
                slot_num = 1
                while True:
                    start_time = request.form.get(f'{day}_start_{slot_num}')
                    end_time = request.form.get(f'{day}_end_{slot_num}')

                    if not start_time or not end_time:
                        break

                    slots.append({
                        'start_time': start_time,
                        'end_time': end_time
                    })
                    slot_num += 1

                if slots:
                    weekly_schedule.append({
                        'day': day,
                        'slots': slots
                    })

        # Build availability rules JSON
        availability_rules = {
            'weekly_schedule': weekly_schedule,
            'booking_duration_min': min_duration,
            'booking_duration_max': max_duration,
            'advance_booking_days': advance_days,
            'buffer_time_minutes': buffer_time
        }

        # Determine edit vs create mode
        if edit_mode:
            # EDIT MODE: Update existing resource
            resource_data = session.get('resource_edit')
            resource_id = resource_data['resource_id']

            # Update resource with new details and availability rules
            ResourceDAL.update_resource(
                resource_id=resource_id,
                title=resource_data['title'],
                description=resource_data['description'],
                category_id=resource_data['category_id'],
                location=resource_data['location'],
                capacity=resource_data['capacity'],
                status=status,
                requires_approval=resource_data['requires_approval'],
                images=resource_data['images'],
                availability_rules=json.dumps(availability_rules)
            )

            # Clear resource edit data from session
            session.pop('resource_edit', None)

            logger.info(
                f"Resource updated: ID={resource_id}, title='{resource_data['title']}', "
                f"owner={current_user.email} (ID:{current_user.user_id})"
            )

            flash(f'Resource "{resource_data["title"]}" updated successfully!', 'success')
            return redirect(url_for('resource.detail', resource_id=resource_id))

        else:
            # CREATE MODE: Create new resource
            resource_details = session.get('resource_details')

            # Create resource with both details and availability rules
            resource_id = ResourceDAL.create_resource(
                owner_type='user',
                owner_id=current_user.user_id,
                title=resource_details['title'],
                description=resource_details['description'],
                category_id=resource_details['category_id'],
                location=resource_details['location'],
                capacity=resource_details['capacity'],
                status=status,  # Use status from form
                availability_mode='rules',  # Default to rules-based
                requires_approval=resource_details['requires_approval'],
                images=resource_details['images'],
                availability_rules=json.dumps(availability_rules)
            )

            # Clear resource details from session
            session.pop('resource_details', None)

            logger.info(
                f"Resource created: ID={resource_id}, title='{resource_details['title']}', "
                f"owner={current_user.email} (ID:{current_user.user_id})"
            )

            flash(f'Resource "{resource_details["title"]}" created successfully!', 'success')
            return redirect(url_for('resource.detail', resource_id=resource_id))

    except Exception as e:
        logger.error(f"Error {'updating' if edit_mode else 'creating'} resource: {str(e)}", exc_info=True)
        flash(f'An error occurred while {"updating" if edit_mode else "creating"} the resource. Please try again.', 'danger')
        return render_template('resources/configure_availability.html')


@resource_bp.route('/<int:resource_id>/edit', methods=['GET', 'POST'])
@login_required
@owner_required('resource')
def edit(resource_id):
    """
    Edit resource (OWNER/ADMIN ONLY).

    Args:
        resource_id: Resource ID

    Returns:
        HTML: Resource edit form or redirect to detail on success
    """
    try:
        resource_data = ResourceDAL.get_resource_by_id(resource_id)

        if not resource_data:
            flash('Resource not found.', 'warning')
            return redirect(url_for('resource.index'))

        resource = Resource(resource_data)

        if request.method == 'GET':
            # Get categories for dropdown
            categories = ResourceDAL.get_all_categories()

            # Split location into building and location_details for the form
            location = resource.location or ''
            location_details = ''
            if ' - ' in location:
                parts = location.split(' - ', 1)
                location = parts[0]
                location_details = parts[1]

            return render_template(
                'resources/edit.html',
                title=f'Edit {resource.title}',
                resource=resource,
                categories=categories,
                location=location,
                location_details=location_details
            )

        # POST - Process form submission
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category_id', type=int)
        location = request.form.get('location', '').strip()
        location_details = request.form.get('location_details', '').strip()
        # Combine location and details with dash separator
        if location_details:
            location = f"{location} - {location_details}"
        capacity = request.form.get('capacity', type=int)
        requires_approval = request.form.get('requires_approval') == 'on'
        status = request.form.get('status', 'published')

        # Handle image upload (keep existing image if no new one uploaded)
        images = resource.images  # Keep existing
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                # Create unique filename
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                name, ext = os.path.splitext(filename)
                unique_filename = f"{name}_{timestamp}{ext}"

                # Save file
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, unique_filename)
                file.save(file_path)

                # Store relative path
                images = f"/static/uploads/{unique_filename}"

        # Validate required fields
        if not title or not category_id or not location:
            flash('Please fill in all required fields.', 'warning')
            categories = ResourceDAL.get_all_categories()
            return render_template('resources/edit.html', resource=resource, categories=categories)

        # Sanitize HTML input
        title = sanitize_html(title)
        description = sanitize_html(description)
        location = sanitize_html(location)

        # Store resource details in session for step 2 (availability rules)
        session['resource_edit'] = {
            'resource_id': resource_id,
            'title': title,
            'description': description,
            'category_id': category_id,
            'location': location,
            'capacity': capacity,
            'status': status,
            'requires_approval': requires_approval,
            'images': images
        }

        # Redirect to configure availability (Step 2)
        return redirect(url_for('resource.configure_availability', edit_mode='true'))

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error updating resource {resource_id}: {str(e)}\n{error_details}")
        flash(f'An error occurred while updating the resource: {str(e)}', 'danger')
        categories = ResourceDAL.get_all_categories()
        return render_template('resources/edit.html',
                             resource=Resource(resource_data),
                             categories=categories,
                             title=f'Edit {resource_data["title"]}')


@resource_bp.route('/<int:resource_id>/delete', methods=['POST'])
@login_required
@owner_required('resource')
def delete(resource_id):
    """
    Soft delete (archive) resource (OWNER/ADMIN ONLY).

    Args:
        resource_id: Resource ID

    Returns:
        Redirect: To resources index
    """
    try:
        resource_data = ResourceDAL.get_resource_by_id(resource_id)

        if not resource_data:
            flash('Resource not found.', 'warning')
            return redirect(url_for('resource.index'))

        resource = Resource(resource_data)

        # Get all active bookings for this resource
        from src.data_access.booking_dal import BookingDAL
        active_bookings = BookingDAL.get_bookings_by_resource(
            resource_id=resource_id,
            status='approved'
        )

        # Also get pending bookings
        pending_bookings = BookingDAL.get_bookings_by_resource(
            resource_id=resource_id,
            status='pending'
        )

        all_bookings = active_bookings + pending_bookings
        cancelled_count = 0

        # Track affected users and their booking counts for notifications
        affected_users = {}  # {user_id: booking_count}

        # Cancel all active and pending bookings
        for booking in all_bookings:
            if BookingDAL.cancel_booking(booking['booking_id']):
                cancelled_count += 1
                # Track this user's cancelled bookings
                user_id = booking['requester_id']
                affected_users[user_id] = affected_users.get(user_id, 0) + 1

                # Send individual cancellation notification for each booking
                try:
                    system_messaging.notify_booking_cancelled(
                        booking_id=booking['booking_id'],
                        user_id=user_id,
                        resource_title=resource.title,
                        reason=f"The resource '{resource.title}' has been archived and is no longer available.",
                        cancelled_by="system"
                    )
                    logger.info(
                        f"Sent cancellation notification for booking {booking['booking_id']} to user {user_id}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to send cancellation notification for booking {booking['booking_id']}: {str(e)}",
                        exc_info=True
                    )

                logger.info(
                    f"Auto-cancelled booking {booking['booking_id']} due to resource archival"
                )

        # Soft delete by changing status to 'archived'
        ResourceDAL.update_resource(
            resource_id=resource_id,
            status='archived'
        )

        logger.info(
            f"Resource archived: ID={resource_id}, title='{resource.title}', "
            f"by_user={current_user.email} (ID:{current_user.user_id}), "
            f"cancelled_bookings={cancelled_count}"
        )

        # Send system notifications to affected users
        for user_id, booking_count in affected_users.items():
            try:
                system_messaging.notify_resource_archived(
                    user_id=user_id,
                    resource_title=resource.title,
                    affected_bookings_count=booking_count
                )
                logger.info(
                    f"Sent archival notification to user {user_id} "
                    f"({booking_count} booking(s) cancelled)"
                )
            except Exception as e:
                # Log error but don't fail the archival
                logger.error(
                    f"Failed to send archival notification to user {user_id}: {str(e)}",
                    exc_info=True
                )

        if cancelled_count > 0:
            flash(f'Resource "{resource.title}" has been archived. {cancelled_count} booking(s) were automatically cancelled.', 'success')
        else:
            flash(f'Resource "{resource.title}" has been archived.', 'success')

        return redirect(url_for('resource.index'))

    except Exception as e:
        logger.error(f"Error deleting resource {resource_id}: {str(e)}", exc_info=True)
        flash('An error occurred while deleting the resource. Please try again.', 'danger')
        return redirect(url_for('resource.detail', resource_id=resource_id))


@resource_bp.route('/my-resources')
@login_required
@role_required('staff', 'admin')
def my_resources():
    """
    View current user's resources (STAFF/ADMIN ONLY).

    Returns:
        HTML: User's resources list
    """
    try:
        # Get user's resources (all statuses)
        logger.info(f"Fetching resources for user: email={current_user.email}, user_id={current_user.user_id}, role={current_user.role}")

        resources_data = ResourceDAL.get_all_resources(
            owner_type='user',
            owner_id=current_user.user_id,
            status=None,  # Get all statuses
            limit=100
        )

        logger.info(f"Query returned {len(resources_data)} resources")
        if resources_data:
            logger.info(f"Sample resource: {resources_data[0].get('title', 'N/A')} (owner_id={resources_data[0].get('owner_id', 'N/A')})")

        resources = [Resource(r) for r in resources_data]

        logger.info(f"User {current_user.email} viewing their resources: {len(resources)} found")

        return render_template(
            'resources/my_resources.html',
            title='My Resources',
            resources=resources
        )

    except Exception as e:
        logger.error(f"Error loading user resources: {str(e)}", exc_info=True)
        flash('An error occurred while loading your resources. Please try again.', 'danger')
        return render_template('resources/my_resources.html', resources=[])
