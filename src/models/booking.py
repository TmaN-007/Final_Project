"""
Booking Model for Campus Resource Hub.

Represents a resource booking/reservation.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class Booking:
    """
    Booking model representing a resource reservation.

    Attributes:
        booking_id: Unique identifier
        resource_id: Resource being booked
        requester_id: User who made the booking
        start_datetime: Booking start time
        end_datetime: Booking end time
        status: 'pending', 'approved', 'rejected', 'cancelled', or 'completed'
        approval_required: Whether approval was needed
        notes: Optional booking notes
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    # Status constants
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CANCELLED = 'cancelled'
    STATUS_COMPLETED = 'completed'

    def __init__(self, booking_data: Dict[str, Any]):
        """
        Initialize Booking from database row.

        Args:
            booking_data: Dictionary containing booking fields from database
        """
        self._booking_id = booking_data['booking_id']
        self._resource_id = booking_data['resource_id']
        self._requester_id = booking_data['requester_id']
        self._start_datetime = self._parse_datetime(booking_data['start_datetime'])
        self._end_datetime = self._parse_datetime(booking_data['end_datetime'])
        self._status = booking_data['status']
        self._approval_required = bool(booking_data.get('approval_required', False))
        self._notes = booking_data.get('notes')
        self._created_at = booking_data.get('created_at')
        self._updated_at = booking_data.get('updated_at')

        # Additional properties from joins
        self._resource_title = booking_data.get('resource_title')
        self._requester_name = booking_data.get('requester_name')
        self._requester_email = booking_data.get('requester_email')

    def _parse_datetime(self, dt_string: str) -> datetime:
        """Parse datetime string from database."""
        if isinstance(dt_string, datetime):
            return dt_string
        # Try ISO format first (with 'T' separator): 'YYYY-MM-DDTHH:MM:SS'
        try:
            return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            # Fall back to SQLite format: 'YYYY-MM-DD HH:MM:SS'
            return datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')

    # Property getters and setters
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
    def requester_id(self) -> int:
        """Get requester ID."""
        return self._requester_id

    @requester_id.setter
    def requester_id(self, value: int):
        """Set requester ID."""
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Requester ID must be a positive integer")
        self._requester_id = value

    @property
    def start_datetime(self) -> datetime:
        """Get start datetime."""
        return self._start_datetime

    @start_datetime.setter
    def start_datetime(self, value: datetime):
        """Set start datetime with validation."""
        if not isinstance(value, datetime):
            raise ValueError("Start datetime must be a datetime object")
        self._start_datetime = value

    @property
    def end_datetime(self) -> datetime:
        """Get end datetime."""
        return self._end_datetime

    @end_datetime.setter
    def end_datetime(self, value: datetime):
        """Set end datetime with validation."""
        if not isinstance(value, datetime):
            raise ValueError("End datetime must be a datetime object")
        if hasattr(self, '_start_datetime') and value <= self._start_datetime:
            raise ValueError("End datetime must be after start datetime")
        self._end_datetime = value

    @property
    def status(self) -> str:
        """Get booking status."""
        return self._status

    @status.setter
    def status(self, value: str):
        """Set booking status with validation."""
        valid_statuses = (self.STATUS_PENDING, self.STATUS_APPROVED, self.STATUS_REJECTED,
                         self.STATUS_CANCELLED, self.STATUS_COMPLETED)
        if value not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        self._status = value

    @property
    def approval_required(self) -> bool:
        """Get approval required flag."""
        return self._approval_required

    @approval_required.setter
    def approval_required(self, value: bool):
        """Set approval required flag."""
        self._approval_required = bool(value)

    @property
    def notes(self) -> Optional[str]:
        """Get booking notes."""
        return self._notes

    @notes.setter
    def notes(self, value: Optional[str]):
        """Set booking notes."""
        self._notes = value.strip() if value else None

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
    def resource_title(self) -> Optional[str]:
        """Get resource title."""
        return self._resource_title

    @resource_title.setter
    def resource_title(self, value: Optional[str]):
        """Set resource title."""
        self._resource_title = value

    @property
    def requester_name(self) -> Optional[str]:
        """Get requester name."""
        return self._requester_name

    @requester_name.setter
    def requester_name(self, value: Optional[str]):
        """Set requester name."""
        self._requester_name = value

    @property
    def requester_email(self) -> Optional[str]:
        """Get requester email."""
        return self._requester_email

    @requester_email.setter
    def requester_email(self, value: Optional[str]):
        """Set requester email."""
        self._requester_email = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert booking to dictionary for JSON serialization.

        Returns:
            Dictionary representation of booking
        """
        return {
            'booking_id': self.booking_id,
            'resource_id': self.resource_id,
            'requester_id': self.requester_id,
            'start_datetime': self.start_datetime.isoformat() if self.start_datetime else None,
            'end_datetime': self.end_datetime.isoformat() if self.end_datetime else None,
            'status': self.status,
            'approval_required': self.approval_required,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'resource_title': self.resource_title,
            'requester_name': self.requester_name,
            'requester_email': self.requester_email,
            'duration_hours': self.get_duration_hours()
        }

    @property
    def is_pending(self) -> bool:
        """Check if booking is pending approval."""
        return self._status == self.STATUS_PENDING

    @property
    def is_approved(self) -> bool:
        """Check if booking is approved."""
        return self._status == self.STATUS_APPROVED

    @property
    def is_rejected(self) -> bool:
        """Check if booking was rejected."""
        return self._status == self.STATUS_REJECTED

    @property
    def is_cancelled(self) -> bool:
        """Check if booking was cancelled."""
        return self._status == self.STATUS_CANCELLED

    @property
    def is_completed(self) -> bool:
        """Check if booking is completed."""
        return self._status == self.STATUS_COMPLETED

    @property
    def is_active(self) -> bool:
        """Check if booking is currently active."""
        now = datetime.now()
        return (
            self._status in (self.STATUS_PENDING, self.STATUS_APPROVED) and
            self._start_datetime <= now <= self._end_datetime
        )

    @property
    def is_upcoming(self) -> bool:
        """Check if booking is upcoming."""
        return (
            self._status in (self.STATUS_PENDING, self.STATUS_APPROVED) and
            self._start_datetime > datetime.now()
        )

    @property
    def is_past(self) -> bool:
        """Check if booking is in the past."""
        return self._end_datetime < datetime.now()

    def get_duration_hours(self) -> float:
        """
        Calculate booking duration in hours.

        Returns:
            Duration in hours
        """
        if self._start_datetime and self._end_datetime:
            delta = self._end_datetime - self._start_datetime
            return delta.total_seconds() / 3600
        return 0.0

    def get_duration_string(self) -> str:
        """
        Get human-readable duration string.

        Returns:
            Formatted duration string
        """
        hours = self.get_duration_hours()
        if hours < 1:
            minutes = int(hours * 60)
            return f'{minutes} minute{"s" if minutes != 1 else ""}'
        elif hours < 24:
            return f'{hours:.1f} hour{"s" if hours != 1.0 else ""}'
        else:
            days = hours / 24
            return f'{days:.1f} day{"s" if days != 1.0 else ""}'

    def get_status_badge_class(self) -> str:
        """
        Get Bootstrap badge class for status.

        Returns:
            Bootstrap badge class name
        """
        status_classes = {
            self.STATUS_PENDING: 'warning',
            self.STATUS_APPROVED: 'success',
            self.STATUS_REJECTED: 'danger',
            self.STATUS_CANCELLED: 'secondary',
            self.STATUS_COMPLETED: 'info'
        }
        return status_classes.get(self._status, 'secondary')

    def can_be_cancelled(self, current_user_id: int) -> bool:
        """
        Check if booking can be cancelled by user.

        Args:
            current_user_id: ID of user attempting to cancel

        Returns:
            True if booking can be cancelled
        """
        # Can cancel if:
        # 1. User is the requester
        # 2. Booking is not already cancelled/rejected/completed
        # 3. Booking hasn't started yet
        return (
            current_user_id == self._requester_id and
            self._status not in (self.STATUS_CANCELLED, self.STATUS_REJECTED, self.STATUS_COMPLETED) and
            self._start_datetime > datetime.now()
        )

    def can_be_approved(self) -> bool:
        """
        Check if booking can be approved.

        Returns:
            True if booking can be approved
        """
        return self._status == self.STATUS_PENDING and self._approval_required

    def conflicts_with(self, other_start: datetime, other_end: datetime) -> bool:
        """
        Check if this booking conflicts with another time period.

        Args:
            other_start: Start time of other booking
            other_end: End time of other booking

        Returns:
            True if there is a conflict
        """
        # Two bookings conflict if they overlap in time
        return (
            self._start_datetime < other_end and
            self._end_datetime > other_start
        )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f'<Booking {self._booking_id}: {self._resource_title} ({self._status})>'


class BookingWaitlist:
    """Waitlist entry model."""

    def __init__(self, waitlist_data: Dict[str, Any]):
        """Initialize waitlist entry from database row."""
        self._waitlist_id = waitlist_data['waitlist_id']
        self._resource_id = waitlist_data['resource_id']
        self._user_id = waitlist_data['user_id']
        self._desired_start_datetime = self._parse_datetime(waitlist_data['desired_start_datetime'])
        self._desired_end_datetime = self._parse_datetime(waitlist_data['desired_end_datetime'])
        self._status = waitlist_data['status']
        self._converted_booking_id = waitlist_data.get('converted_booking_id')
        self._created_at = waitlist_data.get('created_at')
        self._notified_at = waitlist_data.get('notified_at')

    def _parse_datetime(self, dt_string: str) -> datetime:
        """Parse datetime string from database."""
        if isinstance(dt_string, datetime):
            return dt_string
        # Try ISO format first (with 'T' separator): 'YYYY-MM-DDTHH:MM:SS'
        try:
            return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            # Fall back to SQLite format: 'YYYY-MM-DD HH:MM:SS'
            return datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')

    # Property getters and setters
    @property
    def waitlist_id(self) -> int:
        """Get waitlist ID."""
        return self._waitlist_id

    @waitlist_id.setter
    def waitlist_id(self, value: int):
        """Set waitlist ID."""
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Waitlist ID must be a positive integer")
        self._waitlist_id = value

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
    def desired_start_datetime(self) -> datetime:
        """Get desired start datetime."""
        return self._desired_start_datetime

    @desired_start_datetime.setter
    def desired_start_datetime(self, value: datetime):
        """Set desired start datetime."""
        if not isinstance(value, datetime):
            raise ValueError("Desired start datetime must be a datetime object")
        self._desired_start_datetime = value

    @property
    def desired_end_datetime(self) -> datetime:
        """Get desired end datetime."""
        return self._desired_end_datetime

    @desired_end_datetime.setter
    def desired_end_datetime(self, value: datetime):
        """Set desired end datetime."""
        if not isinstance(value, datetime):
            raise ValueError("Desired end datetime must be a datetime object")
        self._desired_end_datetime = value

    @property
    def status(self) -> str:
        """Get waitlist status."""
        return self._status

    @status.setter
    def status(self, value: str):
        """Set waitlist status with validation."""
        valid_statuses = ('waiting', 'converted', 'expired')
        if value not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        self._status = value

    @property
    def converted_booking_id(self) -> Optional[int]:
        """Get converted booking ID."""
        return self._converted_booking_id

    @converted_booking_id.setter
    def converted_booking_id(self, value: Optional[int]):
        """Set converted booking ID."""
        self._converted_booking_id = value

    @property
    def created_at(self):
        """Get creation timestamp."""
        return self._created_at

    @created_at.setter
    def created_at(self, value):
        """Set creation timestamp."""
        self._created_at = value

    @property
    def notified_at(self):
        """Get notification timestamp."""
        return self._notified_at

    @notified_at.setter
    def notified_at(self, value):
        """Set notification timestamp."""
        self._notified_at = value

    @property
    def is_waiting(self) -> bool:
        """Check if still waiting."""
        return self._status == 'waiting'

    @property
    def is_converted(self) -> bool:
        """Check if converted to booking."""
        return self._status == 'converted'

    def __repr__(self) -> str:
        """String representation."""
        return f'<BookingWaitlist {self._waitlist_id}: User {self._user_id} for Resource {self._resource_id}>'
