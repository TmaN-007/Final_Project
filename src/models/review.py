"""
Review Model for Campus Resource Hub.

Represents user reviews and ratings for resources.
"""

from typing import Dict, Any, Optional
from datetime import datetime


class Review:
    """
    Review model representing a user's rating and comment for a resource.

    Attributes:
        review_id: Unique identifier
        booking_id: Associated booking
        resource_id: Resource being reviewed
        reviewer_id: User who wrote the review
        rating: Rating (1-5 stars)
        comment: Review text
        is_visible: Whether review is publicly visible
        flagged_count: Number of times flagged
        host_response: Response from resource owner
        host_responded_at: When host responded
        helpful_count: Number of helpful votes
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    def __init__(self, review_data: Dict[str, Any]):
        """
        Initialize Review from database row.

        Args:
            review_data: Dictionary containing review fields from database
        """
        self._review_id = review_data['review_id']
        self._booking_id = review_data['booking_id']
        self._resource_id = review_data['resource_id']
        self._reviewer_id = review_data['reviewer_id']
        self._rating = review_data['rating']
        self._comment = review_data.get('comment')
        self._is_visible = bool(review_data.get('is_visible', True))
        self._flagged_count = review_data.get('flagged_count', 0)
        self._host_response = review_data.get('host_response')
        self._host_responded_at = review_data.get('host_responded_at')
        self._helpful_count = review_data.get('helpful_count', 0)
        self._created_at = review_data.get('created_at')
        self._updated_at = review_data.get('updated_at')

        # Additional properties from joins
        self._reviewer_name = review_data.get('reviewer_name')
        self._resource_title = review_data.get('resource_title')

    # Property getters and setters
    @property
    def review_id(self) -> int:
        """Get review ID."""
        return self._review_id

    @review_id.setter
    def review_id(self, value: int):
        """Set review ID."""
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Review ID must be a positive integer")
        self._review_id = value

    @property
    def booking_id(self) -> int:
        """Get booking ID."""
        return self._booking_id

    @booking_id.setter
    def booking_id(self, value: int):
        """Set booking ID."""
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Booking ID must be a positive integer")
        self._booking_id = value

    @property
    def resource_id(self) -> int:
        """Get resource ID."""
        return self._resource_id

    @resource_id.setter
    def resource_id(self, value: int):
        """Set resource ID."""
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Resource ID must be a positive integer")
        self._resource_id = value

    @property
    def reviewer_id(self) -> int:
        """Get reviewer ID."""
        return self._reviewer_id

    @reviewer_id.setter
    def reviewer_id(self, value: int):
        """Set reviewer ID."""
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Reviewer ID must be a positive integer")
        self._reviewer_id = value

    @property
    def rating(self) -> int:
        """Get rating."""
        return self._rating

    @rating.setter
    def rating(self, value: int):
        """Set rating with validation."""
        if not isinstance(value, int) or value < 1 or value > 5:
            raise ValueError("Rating must be an integer between 1 and 5")
        self._rating = value

    @property
    def comment(self) -> Optional[str]:
        """Get comment."""
        return self._comment

    @comment.setter
    def comment(self, value: Optional[str]):
        """Set comment."""
        self._comment = value.strip() if value else None

    @property
    def is_visible(self) -> bool:
        """Get visibility status."""
        return self._is_visible

    @is_visible.setter
    def is_visible(self, value: bool):
        """Set visibility status."""
        self._is_visible = bool(value)

    @property
    def flagged_count(self) -> int:
        """Get flagged count."""
        return self._flagged_count

    @flagged_count.setter
    def flagged_count(self, value: int):
        """Set flagged count."""
        if not isinstance(value, int) or value < 0:
            raise ValueError("Flagged count must be a non-negative integer")
        self._flagged_count = value

    @property
    def host_response(self) -> Optional[str]:
        """Get host response."""
        return self._host_response

    @host_response.setter
    def host_response(self, value: Optional[str]):
        """Set host response."""
        self._host_response = value.strip() if value else None

    @property
    def host_responded_at(self):
        """Get host response timestamp."""
        return self._host_responded_at

    @host_responded_at.setter
    def host_responded_at(self, value):
        """Set host response timestamp."""
        self._host_responded_at = value

    @property
    def helpful_count(self) -> int:
        """Get helpful count."""
        return self._helpful_count

    @helpful_count.setter
    def helpful_count(self, value: int):
        """Set helpful count."""
        if not isinstance(value, int) or value < 0:
            raise ValueError("Helpful count must be a non-negative integer")
        self._helpful_count = value

    @property
    def created_at(self):
        """Get creation timestamp."""
        return self._created_at

    @created_at.setter
    def created_at(self, value):
        """Set creation timestamp."""
        self._created_at = value

    @property
    def updated_at(self):
        """Get update timestamp."""
        return self._updated_at

    @updated_at.setter
    def updated_at(self, value):
        """Set update timestamp."""
        self._updated_at = value

    @property
    def reviewer_name(self) -> Optional[str]:
        """Get reviewer name."""
        return self._reviewer_name

    @reviewer_name.setter
    def reviewer_name(self, value: Optional[str]):
        """Set reviewer name."""
        self._reviewer_name = value

    @property
    def resource_title(self) -> Optional[str]:
        """Get resource title."""
        return self._resource_title

    @resource_title.setter
    def resource_title(self, value: Optional[str]):
        """Set resource title."""
        self._resource_title = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert review to dictionary for JSON serialization.

        Returns:
            Dictionary representation of review
        """
        return {
            'review_id': self.review_id,
            'booking_id': self.booking_id,
            'resource_id': self.resource_id,
            'reviewer_id': self.reviewer_id,
            'rating': self.rating,
            'comment': self.comment,
            'is_visible': self.is_visible,
            'flagged_count': self.flagged_count,
            'host_response': self.host_response,
            'host_responded_at': self.host_responded_at,
            'helpful_count': self.helpful_count,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'reviewer_name': self.reviewer_name,
            'resource_title': self.resource_title,
            'star_rating': self.get_star_display()
        }

    @property
    def has_host_response(self) -> bool:
        """Check if host has responded to this review."""
        return bool(self._host_response)

    @property
    def is_flagged(self) -> bool:
        """Check if review has been flagged."""
        return self._flagged_count > 0

    @property
    def is_highly_flagged(self) -> bool:
        """Check if review has been flagged multiple times."""
        return self._flagged_count >= 3

    def get_star_display(self) -> str:
        """
        Get star rating as string of filled/empty stars.

        Returns:
            String with star symbols (e.g., "★★★★☆")
        """
        filled = '★' * self._rating
        empty = '☆' * (5 - self._rating)
        return filled + empty

    def get_rating_class(self) -> str:
        """
        Get CSS class based on rating.

        Returns:
            CSS class name for styling
        """
        if self._rating >= 4:
            return 'rating-good'
        elif self._rating >= 3:
            return 'rating-ok'
        else:
            return 'rating-bad'

    def get_rating_color(self) -> str:
        """
        Get Bootstrap color class for rating.

        Returns:
            Bootstrap color class
        """
        if self._rating >= 4:
            return 'success'
        elif self._rating >= 3:
            return 'warning'
        else:
            return 'danger'

    def get_time_ago(self) -> str:
        """
        Get human-readable time since review was posted.

        Returns:
            Time ago string (e.g., "2 weeks ago")
        """
        if not self._created_at:
            return ''

        # Parse created_at if it's a string (stored in UTC)
        if isinstance(self._created_at, str):
            try:
                created_datetime = datetime.strptime(self._created_at, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return self._created_at
        else:
            created_datetime = self._created_at

        # Use UTC time for comparison since database stores UTC timestamps
        now = datetime.utcnow()
        delta = now - created_datetime
        days = delta.days

        # Handle negative delta (future timestamps or timezone issues)
        if delta.total_seconds() < 0:
            return 'Just now'

        if days < 1:
            hours = delta.seconds // 3600
            if hours < 1:
                minutes = delta.seconds // 60
                if minutes < 1:
                    return 'Just now'
                return f'{minutes} minute{"s" if minutes != 1 else ""} ago'
            return f'{hours} hour{"s" if hours != 1 else ""} ago'
        elif days < 7:
            return f'{days} day{"s" if days != 1 else ""} ago'
        elif days < 30:
            weeks = days // 7
            return f'{weeks} week{"s" if weeks != 1 else ""} ago'
        elif days < 365:
            months = days // 30
            return f'{months} month{"s" if months != 1 else ""} ago'
        else:
            years = days // 365
            return f'{years} year{"s" if years != 1 else ""} ago'

    def can_be_edited_by(self, user_id: int) -> bool:
        """
        Check if user can edit this review.

        Args:
            user_id: User ID to check

        Returns:
            True if user can edit
        """
        return user_id == self._reviewer_id

    def can_respond(self, user_id: int, resource_owner_id: int) -> bool:
        """
        Check if user can respond to this review (must be resource owner).

        Args:
            user_id: User ID to check
            resource_owner_id: ID of resource owner

        Returns:
            True if user can respond
        """
        return user_id == resource_owner_id

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f'<Review {self._review_id}: {self._rating}★ for Resource {self._resource_id}>'


class ContentReport:
    """
    Content report model for flagging inappropriate content.

    Attributes:
        report_id: Unique identifier
        reporter_id: User who reported
        target_type: Type of content (review, message, resource, user)
        target_id: ID of reported content
        reason: Report reason
        status: Report status (open, in_review, resolved, dismissed)
        resolved_by: Admin who resolved
        resolved_at: When resolved
        resolution_notes: Resolution notes
        created_at: Creation timestamp
    """

    # Target types
    TARGET_REVIEW = 'review'
    TARGET_MESSAGE = 'message'
    TARGET_RESOURCE = 'resource'
    TARGET_USER = 'user'

    # Status values
    STATUS_OPEN = 'open'
    STATUS_IN_REVIEW = 'in_review'
    STATUS_RESOLVED = 'resolved'
    STATUS_DISMISSED = 'dismissed'

    def __init__(self, report_data: Dict[str, Any]):
        """Initialize ContentReport from database row."""
        self._report_id = report_data['report_id']
        self._reporter_id = report_data['reporter_id']
        self._target_type = report_data['target_type']
        self._target_id = report_data['target_id']
        self._reason = report_data['reason']
        self._status = report_data['status']
        self._resolved_by = report_data.get('resolved_by')
        self._resolved_at = report_data.get('resolved_at')
        self._resolution_notes = report_data.get('resolution_notes')
        self._created_at = report_data.get('created_at')

        # Additional properties from joins
        self._reporter_name = report_data.get('reporter_name')
        self._resolver_name = report_data.get('resolver_name')

    # Property getters and setters
    @property
    def report_id(self) -> int:
        """Get report ID."""
        return self._report_id

    @report_id.setter
    def report_id(self, value: int):
        """Set report ID."""
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Report ID must be a positive integer")
        self._report_id = value

    @property
    def reporter_id(self) -> int:
        """Get reporter ID."""
        return self._reporter_id

    @reporter_id.setter
    def reporter_id(self, value: int):
        """Set reporter ID."""
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Reporter ID must be a positive integer")
        self._reporter_id = value

    @property
    def target_type(self) -> str:
        """Get target type."""
        return self._target_type

    @target_type.setter
    def target_type(self, value: str):
        """Set target type with validation."""
        valid_types = (self.TARGET_REVIEW, self.TARGET_MESSAGE, self.TARGET_RESOURCE, self.TARGET_USER)
        if value not in valid_types:
            raise ValueError(f"Target type must be one of {valid_types}")
        self._target_type = value

    @property
    def target_id(self) -> int:
        """Get target ID."""
        return self._target_id

    @target_id.setter
    def target_id(self, value: int):
        """Set target ID."""
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Target ID must be a positive integer")
        self._target_id = value

    @property
    def reason(self) -> str:
        """Get report reason."""
        return self._reason

    @reason.setter
    def reason(self, value: str):
        """Set report reason with validation."""
        if not value or not value.strip():
            raise ValueError("Reason cannot be empty")
        self._reason = value.strip()

    @property
    def status(self) -> str:
        """Get report status."""
        return self._status

    @status.setter
    def status(self, value: str):
        """Set report status with validation."""
        valid_statuses = (self.STATUS_OPEN, self.STATUS_IN_REVIEW, self.STATUS_RESOLVED, self.STATUS_DISMISSED)
        if value not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        self._status = value

    @property
    def resolved_by(self) -> Optional[int]:
        """Get resolver ID."""
        return self._resolved_by

    @resolved_by.setter
    def resolved_by(self, value: Optional[int]):
        """Set resolver ID."""
        self._resolved_by = value

    @property
    def resolved_at(self):
        """Get resolution timestamp."""
        return self._resolved_at

    @resolved_at.setter
    def resolved_at(self, value):
        """Set resolution timestamp."""
        self._resolved_at = value

    @property
    def resolution_notes(self) -> Optional[str]:
        """Get resolution notes."""
        return self._resolution_notes

    @resolution_notes.setter
    def resolution_notes(self, value: Optional[str]):
        """Set resolution notes."""
        self._resolution_notes = value.strip() if value else None

    @property
    def created_at(self):
        """Get creation timestamp."""
        return self._created_at

    @created_at.setter
    def created_at(self, value):
        """Set creation timestamp."""
        self._created_at = value

    @property
    def reporter_name(self) -> Optional[str]:
        """Get reporter name."""
        return self._reporter_name

    @reporter_name.setter
    def reporter_name(self, value: Optional[str]):
        """Set reporter name."""
        self._reporter_name = value

    @property
    def resolver_name(self) -> Optional[str]:
        """Get resolver name."""
        return self._resolver_name

    @resolver_name.setter
    def resolver_name(self, value: Optional[str]):
        """Set resolver name."""
        self._resolver_name = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'report_id': self.report_id,
            'reporter_id': self.reporter_id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'reason': self.reason,
            'status': self.status,
            'resolved_by': self.resolved_by,
            'resolved_at': self.resolved_at,
            'resolution_notes': self.resolution_notes,
            'created_at': self.created_at,
            'reporter_name': self.reporter_name,
            'resolver_name': self.resolver_name
        }

    @property
    def is_open(self) -> bool:
        """Check if report is open."""
        return self._status == self.STATUS_OPEN

    @property
    def is_resolved(self) -> bool:
        """Check if report is resolved."""
        return self._status == self.STATUS_RESOLVED

    def get_status_badge_class(self) -> str:
        """Get Bootstrap badge class for status."""
        status_classes = {
            self.STATUS_OPEN: 'danger',
            self.STATUS_IN_REVIEW: 'warning',
            self.STATUS_RESOLVED: 'success',
            self.STATUS_DISMISSED: 'secondary'
        }
        return status_classes.get(self._status, 'secondary')

    def __repr__(self) -> str:
        """String representation."""
        return f'<ContentReport {self._report_id}: {self._target_type} #{self._target_id} ({self._status})>'
