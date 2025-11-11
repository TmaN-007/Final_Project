"""
Message Model for Campus Resource Hub.

Represents messages and message threads between users.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class MessageThread:
    """
    Message thread model containing related messages.

    Attributes:
        thread_id: Unique identifier
        resource_id: Related resource (optional)
        booking_id: Related booking (optional)
        subject: Thread subject
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    def __init__(self, thread_data: Dict[str, Any]):
        """
        Initialize MessageThread from database row.

        Args:
            thread_data: Dictionary containing thread fields from database
        """
        self._thread_id = thread_data['thread_id']
        self._resource_id = thread_data.get('resource_id')
        self._booking_id = thread_data.get('booking_id')
        self._subject = thread_data.get('subject')
        self._created_at = thread_data.get('created_at')
        self._updated_at = thread_data.get('updated_at')

        # Additional properties from joins
        self._resource_title = thread_data.get('resource_title')
        self._last_message_at = thread_data.get('last_message_at')
        self._unread_count = thread_data.get('unread_count', 0)
        self._participant_names = thread_data.get('participant_names', [])

    # Property getters and setters
    @property
    def thread_id(self) -> int:
        """Get thread ID."""
        return self._thread_id

    @thread_id.setter
    def thread_id(self, value: int):
        """Set thread ID."""
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Thread ID must be a positive integer")
        self._thread_id = value

    @property
    def resource_id(self) -> Optional[int]:
        """Get resource ID."""
        return self._resource_id

    @resource_id.setter
    def resource_id(self, value: Optional[int]):
        """Set resource ID."""
        self._resource_id = value

    @property
    def booking_id(self) -> Optional[int]:
        """Get booking ID."""
        return self._booking_id

    @booking_id.setter
    def booking_id(self, value: Optional[int]):
        """Set booking ID."""
        self._booking_id = value

    @property
    def subject(self) -> Optional[str]:
        """Get thread subject."""
        return self._subject

    @subject.setter
    def subject(self, value: Optional[str]):
        """Set thread subject."""
        self._subject = value.strip() if value else None

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
    def last_message_at(self):
        """Get last message timestamp."""
        return self._last_message_at

    @last_message_at.setter
    def last_message_at(self, value):
        """Set last message timestamp."""
        self._last_message_at = value

    @property
    def unread_count(self) -> int:
        """Get unread message count."""
        return self._unread_count

    @unread_count.setter
    def unread_count(self, value: int):
        """Set unread message count."""
        self._unread_count = int(value) if value else 0

    @property
    def participant_names(self) -> List[str]:
        """Get participant names."""
        return self._participant_names

    @participant_names.setter
    def participant_names(self, value: List[str]):
        """Set participant names."""
        self._participant_names = value if value else []

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert thread to dictionary for JSON serialization.

        Returns:
            Dictionary representation of thread
        """
        return {
            'thread_id': self.thread_id,
            'resource_id': self.resource_id,
            'booking_id': self.booking_id,
            'subject': self.subject,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'resource_title': self.resource_title,
            'last_message_at': self.last_message_at,
            'unread_count': self.unread_count,
            'participant_names': self.participant_names
        }

    @property
    def has_unread_messages(self) -> bool:
        """Check if thread has unread messages."""
        return self._unread_count > 0

    def get_display_subject(self) -> str:
        """
        Get display subject (use resource title if no subject).

        Returns:
            Subject string for display
        """
        if self._subject:
            return self._subject
        elif self._resource_title:
            return f'RE: {self._resource_title}'
        else:
            return 'Conversation'

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f'<MessageThread {self._thread_id}: {self.get_display_subject()}>'


class Message:
    """
    Individual message model.

    Attributes:
        message_id: Unique identifier
        thread_id: Parent thread ID
        sender_id: User who sent the message
        receiver_id: User who receives the message (optional)
        content: Message content
        is_read: Whether message has been read
        sent_at: Timestamp when sent
    """

    def __init__(self, message_data: Dict[str, Any]):
        """
        Initialize Message from database row.

        Args:
            message_data: Dictionary containing message fields from database
        """
        self._message_id = message_data['message_id']
        self._thread_id = message_data['thread_id']
        self._sender_id = message_data['sender_id']
        self._receiver_id = message_data.get('receiver_id')
        self._content = message_data['content']
        self._is_read = bool(message_data.get('is_read', False))
        self._sent_at = message_data.get('sent_at')

        # Additional properties from joins
        self._sender_name = message_data.get('sender_name')
        self._sender_email = message_data.get('sender_email')
        self._receiver_name = message_data.get('receiver_name')

    # Property getters and setters
    @property
    def message_id(self) -> int:
        """Get message ID."""
        return self._message_id

    @message_id.setter
    def message_id(self, value: int):
        """Set message ID."""
        self._message_id = value

    @property
    def thread_id(self) -> int:
        """Get thread ID."""
        return self._thread_id

    @thread_id.setter
    def thread_id(self, value: int):
        """Set thread ID."""
        self._thread_id = value

    @property
    def sender_id(self) -> int:
        """Get sender ID."""
        return self._sender_id

    @sender_id.setter
    def sender_id(self, value: int):
        """Set sender ID."""
        self._sender_id = value

    @property
    def receiver_id(self) -> Optional[int]:
        """Get receiver ID."""
        return self._receiver_id

    @receiver_id.setter
    def receiver_id(self, value: Optional[int]):
        """Set receiver ID."""
        self._receiver_id = value

    @property
    def content(self) -> str:
        """Get message content."""
        return self._content

    @content.setter
    def content(self, value: str):
        """Set message content with validation."""
        if not value or not value.strip():
            raise ValueError("Message content cannot be empty")
        self._content = value.strip()

    @property
    def is_read(self) -> bool:
        """Get read status."""
        return self._is_read

    @is_read.setter
    def is_read(self, value: bool):
        """Set read status."""
        self._is_read = bool(value)

    @property
    def sent_at(self):
        """Get sent timestamp."""
        return self._sent_at

    @sent_at.setter
    def sent_at(self, value):
        """Set sent timestamp."""
        self._sent_at = value

    @property
    def sender_name(self) -> Optional[str]:
        """Get sender name."""
        return self._sender_name

    @sender_name.setter
    def sender_name(self, value: Optional[str]):
        """Set sender name."""
        self._sender_name = value

    @property
    def sender_email(self) -> Optional[str]:
        """Get sender email."""
        return self._sender_email

    @sender_email.setter
    def sender_email(self, value: Optional[str]):
        """Set sender email."""
        self._sender_email = value

    @property
    def receiver_name(self) -> Optional[str]:
        """Get receiver name."""
        return self._receiver_name

    @receiver_name.setter
    def receiver_name(self, value: Optional[str]):
        """Set receiver name."""
        self._receiver_name = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert message to dictionary for JSON serialization.

        Returns:
            Dictionary representation of message
        """
        return {
            'message_id': self.message_id,
            'thread_id': self.thread_id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'is_read': self.is_read,
            'sent_at': self.sent_at,
            'sender_name': self.sender_name,
            'sender_email': self.sender_email,
            'receiver_name': self.receiver_name,
            'time_ago': self.get_time_ago()
        }

    @property
    def is_unread(self) -> bool:
        """Check if message is unread."""
        return not self.is_read

    def get_time_ago(self) -> str:
        """
        Get human-readable time since message was sent.

        Returns:
            Time ago string (e.g., "2 hours ago")
        """
        if not self.sent_at:
            return ''

        # Parse sent_at if it's a string
        if isinstance(self.sent_at, str):
            try:
                sent_datetime = datetime.strptime(self.sent_at, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return self.sent_at
        else:
            sent_datetime = self.sent_at

        now = datetime.now()
        delta = now - sent_datetime

        # Calculate time difference
        seconds = delta.total_seconds()
        minutes = seconds / 60
        hours = minutes / 60
        days = hours / 24

        if seconds < 60:
            return 'Just now'
        elif minutes < 60:
            m = int(minutes)
            return f'{m} minute{"s" if m != 1 else ""} ago'
        elif hours < 24:
            h = int(hours)
            return f'{h} hour{"s" if h != 1 else ""} ago'
        elif days < 7:
            d = int(days)
            return f'{d} day{"s" if d != 1 else ""} ago'
        elif days < 30:
            w = int(days / 7)
            return f'{w} week{"s" if w != 1 else ""} ago'
        elif days < 365:
            mo = int(days / 30)
            return f'{mo} month{"s" if mo != 1 else ""} ago'
        else:
            y = int(days / 365)
            return f'{y} year{"s" if y != 1 else ""} ago'

    def get_content_preview(self, max_length: int = 100) -> str:
        """
        Get preview of message content.

        Args:
            max_length: Maximum length of preview

        Returns:
            Truncated content with ellipsis if needed
        """
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + '...'

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f'<Message {self.message_id}: From {self.sender_name} ({self.sent_at})>'


class Notification:
    """
    Notification model for user notifications.

    Attributes:
        notification_id: Unique identifier
        user_id: User receiving notification
        notification_type: Type of notification
        payload_json: JSON payload with notification data
        delivery_method: How notification was delivered
        delivery_status: Status of delivery
        is_read: Whether user has read notification
        sent_at: When notification was sent
        created_at: Creation timestamp
    """

    # Notification types
    TYPE_BOOKING_REQUESTED = 'booking_requested'
    TYPE_BOOKING_APPROVED = 'booking_approved'
    TYPE_BOOKING_REJECTED = 'booking_rejected'
    TYPE_BOOKING_CANCELLED = 'booking_cancelled'
    TYPE_WAITLIST_NOTIFIED = 'waitlist_notified'
    TYPE_MESSAGE_RECEIVED = 'message_received'
    TYPE_REVIEW_POSTED = 'review_posted'
    TYPE_RESOURCE_AVAILABLE = 'resource_available'

    def __init__(self, notification_data: Dict[str, Any]):
        """Initialize Notification from database row."""
        self._notification_id = notification_data['notification_id']
        self._user_id = notification_data['user_id']
        self._notification_type = notification_data['notification_type']
        self._payload_json = notification_data.get('payload_json')
        self._delivery_method = notification_data.get('delivery_method', 'in_app')
        self._delivery_status = notification_data.get('delivery_status', 'pending')
        self._is_read = bool(notification_data.get('is_read', False))
        self._sent_at = notification_data.get('sent_at')
        self._created_at = notification_data.get('created_at')

    # Property getters and setters
    @property
    def notification_id(self) -> int:
        """Get notification ID."""
        return self._notification_id

    @notification_id.setter
    def notification_id(self, value: int):
        """Set notification ID."""
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Notification ID must be a positive integer")
        self._notification_id = value

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
    def notification_type(self) -> str:
        """Get notification type."""
        return self._notification_type

    @notification_type.setter
    def notification_type(self, value: str):
        """Set notification type with validation."""
        valid_types = (
            self.TYPE_BOOKING_REQUESTED, self.TYPE_BOOKING_APPROVED, self.TYPE_BOOKING_REJECTED,
            self.TYPE_BOOKING_CANCELLED, self.TYPE_WAITLIST_NOTIFIED, self.TYPE_MESSAGE_RECEIVED,
            self.TYPE_REVIEW_POSTED, self.TYPE_RESOURCE_AVAILABLE
        )
        if value not in valid_types:
            raise ValueError(f"Notification type must be one of {valid_types}")
        self._notification_type = value

    @property
    def payload_json(self) -> Optional[str]:
        """Get payload JSON."""
        return self._payload_json

    @payload_json.setter
    def payload_json(self, value: Optional[str]):
        """Set payload JSON."""
        self._payload_json = value

    @property
    def delivery_method(self) -> str:
        """Get delivery method."""
        return self._delivery_method

    @delivery_method.setter
    def delivery_method(self, value: str):
        """Set delivery method."""
        self._delivery_method = value

    @property
    def delivery_status(self) -> str:
        """Get delivery status."""
        return self._delivery_status

    @delivery_status.setter
    def delivery_status(self, value: str):
        """Set delivery status."""
        self._delivery_status = value

    @property
    def is_read(self) -> bool:
        """Get read status."""
        return self._is_read

    @is_read.setter
    def is_read(self, value: bool):
        """Set read status."""
        self._is_read = bool(value)

    @property
    def sent_at(self):
        """Get sent timestamp."""
        return self._sent_at

    @sent_at.setter
    def sent_at(self, value):
        """Set sent timestamp."""
        self._sent_at = value

    @property
    def created_at(self):
        """Get creation timestamp."""
        return self._created_at

    @created_at.setter
    def created_at(self, value):
        """Set creation timestamp."""
        self._created_at = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'notification_id': self.notification_id,
            'user_id': self.user_id,
            'notification_type': self.notification_type,
            'payload_json': self.payload_json,
            'delivery_method': self.delivery_method,
            'delivery_status': self.delivery_status,
            'is_read': self.is_read,
            'sent_at': self.sent_at,
            'created_at': self.created_at
        }

    @property
    def is_unread(self) -> bool:
        """Check if notification is unread."""
        return not self._is_read

    def get_icon_class(self) -> str:
        """Get Font Awesome icon class for notification type."""
        icon_classes = {
            self.TYPE_BOOKING_REQUESTED: 'fa-calendar-plus',
            self.TYPE_BOOKING_APPROVED: 'fa-check-circle',
            self.TYPE_BOOKING_REJECTED: 'fa-times-circle',
            self.TYPE_BOOKING_CANCELLED: 'fa-ban',
            self.TYPE_WAITLIST_NOTIFIED: 'fa-bell',
            self.TYPE_MESSAGE_RECEIVED: 'fa-envelope',
            self.TYPE_REVIEW_POSTED: 'fa-star',
            self.TYPE_RESOURCE_AVAILABLE: 'fa-unlock'
        }
        return icon_classes.get(self._notification_type, 'fa-info-circle')

    def __repr__(self) -> str:
        """String representation."""
        return f'<Notification {self._notification_id}: {self._notification_type} for User {self._user_id}>'
