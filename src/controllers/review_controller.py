"""
Campus Resource Hub - Review Controller
========================================
MVC Role: Controller for review management
MCP Role: Review request handling for AI-assisted content moderation

Handles:
- Submitting reviews after completed bookings
- Viewing reviews
- Editing reviews
- Host responses
- Rating aggregation
- Top-rated badges
"""

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from src.data_access.review_dal import ReviewDAL
from src.data_access.booking_dal import BookingDAL
from src.data_access.resource_dal import ResourceDAL
from src.models.review import Review
from src.forms.review_forms import ReviewForm, HostResponseForm

# Create blueprint
review_bp = Blueprint('review', __name__, url_prefix='/reviews')


@review_bp.route('/create/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def create(booking_id):
    """
    Create a review for a completed booking.

    Args:
        booking_id (int): Booking ID

    Returns:
        HTML: Review form or redirect after submission
    """
    # Get the booking
    booking_data = BookingDAL.get_booking_by_id(booking_id)

    if not booking_data:
        flash('Booking not found.', 'error')
        return redirect(url_for('booking.index'))

    # Verify user is the requester
    if booking_data['requester_id'] != current_user.user_id:
        flash('You can only review your own bookings.', 'error')
        return redirect(url_for('booking.index'))

    # Check if booking is completed
    if booking_data['status'] != 'completed':
        flash('You can only review completed bookings.', 'error')
        return redirect(url_for('booking.detail', booking_id=booking_id))

    # Check if already reviewed
    existing_reviews = ReviewDAL.get_reviews_by_user(current_user.user_id)
    for review in existing_reviews:
        if review['booking_id'] == booking_id:
            flash('You have already reviewed this booking.', 'info')
            return redirect(url_for('resource.detail', resource_id=booking_data['resource_id']))

    form = ReviewForm()

    if form.validate_on_submit():
        # Create the review
        review_id = ReviewDAL.create_review(
            booking_id=booking_id,
            resource_id=booking_data['resource_id'],
            reviewer_id=current_user.user_id,
            rating=form.rating.data,
            comment=form.comment.data
        )

        if review_id:
            flash('Thank you for your review!', 'success')
            return redirect(url_for('resource.detail', resource_id=booking_data['resource_id']))
        else:
            flash('Failed to submit review. Please try again.', 'error')

    # Pre-fill form
    form.booking_id.data = booking_id
    form.resource_id.data = booking_data['resource_id']

    # Get resource details
    resource = ResourceDAL.get_resource_by_id(booking_data['resource_id'])

    return render_template(
        'reviews/create.html',
        form=form,
        booking=booking_data,
        resource=resource,
        title='Write Review',
        page_name='reviews'
    )


@review_bp.route('/<int:review_id>')
@login_required
def detail(review_id):
    """
    View review details.

    Args:
        review_id (int): Review ID

    Returns:
        HTML: Review detail page
    """
    review_data = ReviewDAL.get_review_by_id(review_id)

    if not review_data:
        flash('Review not found.', 'error')
        return redirect(url_for('home.index'))

    review = Review(review_data)

    return render_template(
        'reviews/detail.html',
        review=review,
        title='Review Details',
        page_name='reviews'
    )


@review_bp.route('/<int:review_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(review_id):
    """
    Edit a review.

    Args:
        review_id (int): Review ID

    Returns:
        HTML: Edit form or redirect after update
    """
    review_data = ReviewDAL.get_review_by_id(review_id)

    if not review_data:
        flash('Review not found.', 'error')
        return redirect(url_for('home.index'))

    # Verify user is the reviewer
    if review_data['reviewer_id'] != current_user.user_id:
        flash('You can only edit your own reviews.', 'error')
        return redirect(url_for('review.detail', review_id=review_id))

    form = ReviewForm()

    if form.validate_on_submit():
        success = ReviewDAL.update_review(
            review_id=review_id,
            rating=form.rating.data,
            comment=form.comment.data
        )

        if success:
            flash('Review updated successfully!', 'success')
            return redirect(url_for('resource.detail', resource_id=review_data['resource_id']))
        else:
            flash('Failed to update review. Please try again.', 'error')

    # Pre-fill form
    form.booking_id.data = review_data['booking_id']
    form.resource_id.data = review_data['resource_id']
    form.rating.data = review_data['rating']
    form.comment.data = review_data['comment']

    return render_template(
        'reviews/edit.html',
        form=form,
        review=review_data,
        title='Edit Review',
        page_name='reviews'
    )


@review_bp.route('/<int:review_id>/delete', methods=['POST'])
@login_required
def delete(review_id):
    """
    Delete a review.

    Args:
        review_id (int): Review ID

    Returns:
        Redirect to resource page
    """
    review_data = ReviewDAL.get_review_by_id(review_id)

    if not review_data:
        flash('Review not found.', 'error')
        return redirect(url_for('home.index'))

    # Verify user is the reviewer or admin
    if review_data['reviewer_id'] != current_user.user_id and current_user.role != 'admin':
        flash('You do not have permission to delete this review.', 'error')
        return redirect(url_for('review.detail', review_id=review_id))

    resource_id = review_data['resource_id']
    success = ReviewDAL.delete_review(review_id)

    if success:
        flash('Review deleted successfully.', 'success')
    else:
        flash('Failed to delete review.', 'error')

    return redirect(url_for('resource.detail', resource_id=resource_id))


@review_bp.route('/<int:review_id>/respond', methods=['POST'])
@login_required
def respond(review_id):
    """
    Add host response to a review.

    Args:
        review_id (int): Review ID

    Returns:
        JSON response or redirect
    """
    review_data = ReviewDAL.get_review_by_id(review_id)

    if not review_data:
        return jsonify({'success': False, 'message': 'Review not found'}), 404

    # Get resource to verify ownership
    resource = ResourceDAL.get_resource_by_id(review_data['resource_id'])

    if not resource:
        return jsonify({'success': False, 'message': 'Resource not found'}), 404

    # Verify user is resource owner
    is_owner = (resource.get('owner_type') == 'user' and
                resource.get('owner_id') == current_user.user_id)

    if not is_owner:
        return jsonify({'success': False, 'message': 'Only resource owner can respond'}), 403

    # Check if already responded
    if review_data.get('host_response'):
        return jsonify({'success': False, 'message': 'You have already responded to this review'}), 400

    # Get response from form
    response_text = request.form.get('host_response', '').strip()

    if not response_text or len(response_text) < 10:
        return jsonify({'success': False, 'message': 'Response must be at least 10 characters'}), 400

    success = ReviewDAL.add_host_response(review_id, response_text)

    if success:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': 'Response posted successfully'
            })
        else:
            flash('Response posted successfully!', 'success')
            return redirect(url_for('resource.detail', resource_id=review_data['resource_id']))
    else:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Failed to post response'}), 500
        else:
            flash('Failed to post response. Please try again.', 'error')
            return redirect(url_for('resource.detail', resource_id=review_data['resource_id']))


@review_bp.route('/my-reviews')
@login_required
def my_reviews():
    """
    View all reviews written by current user.

    Returns:
        HTML: User's review list
    """
    page = int(request.args.get('page', 1))
    per_page = 20

    reviews_data = ReviewDAL.get_reviews_by_user(
        user_id=current_user.user_id,
        limit=per_page,
        offset=(page - 1) * per_page
    )

    reviews = [Review(r) for r in reviews_data]

    return render_template(
        'reviews/my_reviews.html',
        reviews=reviews,
        page=page,
        title='My Reviews',
        page_name='reviews'
    )


@review_bp.route('/resource/<int:resource_id>')
def resource_reviews(resource_id):
    """
    View all reviews for a resource (API endpoint).

    Args:
        resource_id (int): Resource ID

    Returns:
        JSON: Reviews data with statistics
    """
    # Get filter parameters
    min_rating = request.args.get('min_rating', type=int)
    sort_by = request.args.get('sort_by', 'recent')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    # Get reviews
    reviews_data = ReviewDAL.get_reviews_by_resource(
        resource_id=resource_id,
        visible_only=True,
        min_rating=min_rating,
        sort_by=sort_by,
        limit=per_page,
        offset=(page - 1) * per_page
    )

    # Get rating summary
    rating_summary = ReviewDAL.get_resource_rating_summary(resource_id)

    reviews = [Review(r) for r in reviews_data]

    return jsonify({
        'reviews': [r.to_dict() for r in reviews],
        'rating_summary': rating_summary,
        'page': page,
        'per_page': per_page
    })
