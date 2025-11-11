"""
Campus Resource Hub - Message & Notification Data Access Layer
==============================================================
MVC Role: Data access for messaging and notifications
MCP Role: Message/notification queries for AI-assisted communication

This module handles all database operations for:
- Direct messages between users
- Message threads
- In-app notifications
- Notification delivery tracking

All queries use parameterized statements for SQL injection prevention.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import logging

from src.data_access.base_dal import BaseDAL

logger = logging.getLogger(__name__)


class MessageDAL(BaseDAL):
    """
    Message and Notification Data Access Layer.

    Handles all database operations for messages, message threads, and notifications.
    """

    # ========== MESSAGE THREADS ==========

    @classmethod
    def create_thread(
        cls,
        subject: Optional[str] = None,
        resource_id: Optional[int] = None,
        booking_id: Optional[int] = None
    ) -> int:
        """
        Create a new message thread.

        Args:
            subject (Optional[str]): Thread subject
            resource_id (Optional[int]): Related resource ID
            booking_id (Optional[int]): Related booking ID

        Returns:
            int: New thread ID

        Example:
            >>> thread_id = MessageDAL.create_thread(
            ...     subject='Question about Study Room A',
            ...     resource_id=5
            ... )
        """
        query = """
            INSERT INTO message_threads (
                resource_id, booking_id, subject, created_at, updated_at
            ) VALUES (?, ?, ?, datetime('now'), datetime('now'))
        """
        return cls.execute_update(query, (resource_id, booking_id, subject))

    @classmethod
    def get_thread_by_id(cls, thread_id: int) -> Optional[Dict[str, Any]]:
        """
        Get message thread by ID.

        Args:
            thread_id (int): Thread ID

        Returns:
            Optional[Dict]: Thread data or None if not found

        Example:
            >>> thread = MessageDAL.get_thread_by_id(123)
        """
        query = """
            SELECT
                mt.*,
                r.title as resource_title,
                b.booking_id
            FROM message_threads mt
            LEFT JOIN resources r ON mt.resource_id = r.resource_id
            LEFT JOIN bookings b ON mt.booking_id = b.booking_id
            WHERE mt.thread_id = ?
        """
        results = cls.execute_query(query, (thread_id,))
        return results[0] if results else None

    @classmethod
    def get_threads_by_user(
        cls,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all message threads involving a user.

        Args:
            user_id (int): User ID
            unread_only (bool): Only show threads with unread messages
            limit (int): Max results
            offset (int): Pagination offset

        Returns:
            List[Dict]: List of threads

        Example:
            >>> threads = MessageDAL.get_threads_by_user(
            ...     user_id=123,
            ...     unread_only=True
            ... )
        """
        query = """
            SELECT DISTINCT
                mt.*,
                r.title as resource_title,
                (SELECT COUNT(*) FROM messages m
                 WHERE m.thread_id = mt.thread_id
                   AND m.receiver_id = ?
                   AND m.is_read = 0) as unread_count,
                (SELECT m2.sent_at FROM messages m2
                 WHERE m2.thread_id = mt.thread_id
                 ORDER BY m2.sent_at DESC LIMIT 1) as last_message_at
            FROM message_threads mt
            LEFT JOIN resources r ON mt.resource_id = r.resource_id
            WHERE mt.thread_id IN (
                SELECT DISTINCT thread_id
                FROM messages
                WHERE sender_id = ? OR receiver_id = ?
            )
        """
        params = [user_id, user_id, user_id]

        if unread_only:
            query += " AND unread_count > 0"

        query += " ORDER BY last_message_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        return cls.execute_query(query, tuple(params))

    # ========== MESSAGES ==========

    @classmethod
    def send_message(
        cls,
        thread_id: int,
        sender_id: int,
        receiver_id: int,
        content: str
    ) -> int:
        """
        Send a message in a thread.

        Args:
            thread_id (int): Thread ID
            sender_id (int): Sender user ID
            receiver_id (int): Receiver user ID
            content (str): Message content

        Returns:
            int: New message ID

        Example:
            >>> message_id = MessageDAL.send_message(
            ...     thread_id=123,
            ...     sender_id=456,
            ...     receiver_id=789,
            ...     content='Is the study room available tomorrow?'
            ... )
        """
        # Insert message
        query = """
            INSERT INTO messages (
                thread_id, sender_id, receiver_id, content, is_read, sent_at
            ) VALUES (?, ?, ?, ?, 0, datetime('now'))
        """
        message_id = cls.execute_update(query, (thread_id, sender_id, receiver_id, content))

        # Update thread updated_at
        update_thread = """
            UPDATE message_threads
            SET updated_at = datetime('now')
            WHERE thread_id = ?
        """
        cls.execute_update(update_thread, (thread_id,))

        # Create notification for receiver
        NotificationDAL.create_notification(
            user_id=receiver_id,
            notification_type='message_received',
            payload={'thread_id': thread_id, 'message_id': message_id, 'sender_id': sender_id}
        )

        return message_id

    @classmethod
    def get_messages_by_thread(
        cls,
        thread_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all messages in a thread.

        Args:
            thread_id (int): Thread ID
            limit (int): Max results
            offset (int): Pagination offset

        Returns:
            List[Dict]: List of messages

        Example:
            >>> messages = MessageDAL.get_messages_by_thread(123)
        """
        query = """
            SELECT
                m.*,
                u_sender.name as sender_name,
                u_sender.profile_image as sender_image,
                u_receiver.name as receiver_name
            FROM messages m
            JOIN users u_sender ON m.sender_id = u_sender.user_id
            LEFT JOIN users u_receiver ON m.receiver_id = u_receiver.user_id
            WHERE m.thread_id = ?
            ORDER BY m.sent_at ASC
            LIMIT ? OFFSET ?
        """
        return cls.execute_query(query, (thread_id, limit, offset))

    @classmethod
    def mark_message_as_read(cls, message_id: int) -> bool:
        """
        Mark a message as read.

        Args:
            message_id (int): Message ID

        Returns:
            bool: True if marked as read, False otherwise

        Example:
            >>> success = MessageDAL.mark_message_as_read(123)
        """
        query = "UPDATE messages SET is_read = 1 WHERE message_id = ?"
        rows_affected = cls.execute_update(query, (message_id,))
        return rows_affected > 0

    @classmethod
    def mark_thread_as_read(cls, thread_id: int, user_id: int) -> bool:
        """
        Mark all messages in a thread as read for a user.

        Args:
            thread_id (int): Thread ID
            user_id (int): User ID

        Returns:
            bool: True if marked as read, False otherwise

        Example:
            >>> success = MessageDAL.mark_thread_as_read(
            ...     thread_id=123,
            ...     user_id=456
            ... )
        """
        query = """
            UPDATE messages
            SET is_read = 1
            WHERE thread_id = ?
              AND receiver_id = ?
              AND is_read = 0
        """
        rows_affected = cls.execute_update(query, (thread_id, user_id))
        return rows_affected > 0

    @classmethod
    def get_unread_message_count(cls, user_id: int) -> int:
        """
        Get count of unread messages for a user.

        Args:
            user_id (int): User ID

        Returns:
            int: Count of unread messages

        Example:
            >>> unread_count = MessageDAL.get_unread_message_count(123)
        """
        query = """
            SELECT COUNT(*) as count
            FROM messages
            WHERE receiver_id = ?
              AND is_read = 0
        """
        results = cls.execute_query(query, (user_id,))
        return results[0]['count'] if results else 0

    @classmethod
    def delete_message(cls, message_id: int) -> bool:
        """
        Delete a message.

        Args:
            message_id (int): Message ID

        Returns:
            bool: True if deleted, False otherwise

        Example:
            >>> success = MessageDAL.delete_message(123)
        """
        query = "DELETE FROM messages WHERE message_id = ?"
        rows_affected = cls.execute_update(query, (message_id,))
        return rows_affected > 0


class NotificationDAL(BaseDAL):
    """
    Notification Data Access Layer.

    Handles all database operations for user notifications.
    """

    @classmethod
    def create_notification(
        cls,
        user_id: int,
        notification_type: str,
        payload: Dict[str, Any],
        delivery_method: str = 'in_app'
    ) -> int:
        """
        Create a notification for a user.

        Args:
            user_id (int): User to notify
            notification_type (str): Type of notification
                ('booking_requested', 'booking_approved', 'booking_rejected',
                 'booking_cancelled', 'waitlist_notified', 'message_received',
                 'review_posted', 'resource_available')
            payload (Dict): Notification data (will be JSON encoded)
            delivery_method (str): 'in_app', 'email', 'sms', 'push'

        Returns:
            int: New notification ID

        Example:
            >>> notif_id = NotificationDAL.create_notification(
            ...     user_id=123,
            ...     notification_type='booking_approved',
            ...     payload={'booking_id': 456, 'resource_title': 'Study Room A'}
            ... )
        """
        valid_types = (
            'booking_requested', 'booking_approved', 'booking_rejected',
            'booking_cancelled', 'waitlist_notified', 'message_received',
            'review_posted', 'resource_available'
        )
        if notification_type not in valid_types:
            raise ValueError(f"Invalid notification_type: {notification_type}")

        payload_json = json.dumps(payload)

        query = """
            INSERT INTO notifications (
                user_id, notification_type, payload_json, delivery_method,
                delivery_status, is_read, created_at
            ) VALUES (?, ?, ?, ?, 'pending', 0, datetime('now'))
        """
        return cls.execute_update(query, (
            user_id,
            notification_type,
            payload_json,
            delivery_method
        ))

    @classmethod
    def get_notifications_by_user(
        cls,
        user_id: int,
        unread_only: bool = False,
        notification_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get notifications for a user.

        Args:
            user_id (int): User ID
            unread_only (bool): Only return unread notifications
            notification_type (Optional[str]): Filter by type
            limit (int): Max results
            offset (int): Pagination offset

        Returns:
            List[Dict]: List of notifications

        Example:
            >>> notifications = NotificationDAL.get_notifications_by_user(
            ...     user_id=123,
            ...     unread_only=True
            ... )
        """
        query = """
            SELECT
                notification_id,
                user_id,
                notification_type,
                payload_json,
                delivery_method,
                delivery_status,
                is_read,
                sent_at,
                error_message,
                created_at
            FROM notifications
            WHERE user_id = ?
        """
        params = [user_id]

        if unread_only:
            query += " AND is_read = 0"

        if notification_type:
            query += " AND notification_type = ?"
            params.append(notification_type)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        results = cls.execute_query(query, tuple(params))

        # Parse JSON payloads
        for notification in results:
            if notification['payload_json']:
                try:
                    notification['payload'] = json.loads(notification['payload_json'])
                except json.JSONDecodeError:
                    notification['payload'] = {}
            else:
                notification['payload'] = {}

        return results

    @classmethod
    def mark_notification_as_read(cls, notification_id: int) -> bool:
        """
        Mark a notification as read.

        Args:
            notification_id (int): Notification ID

        Returns:
            bool: True if marked as read, False otherwise

        Example:
            >>> success = NotificationDAL.mark_notification_as_read(123)
        """
        query = "UPDATE notifications SET is_read = 1 WHERE notification_id = ?"
        rows_affected = cls.execute_update(query, (notification_id,))
        return rows_affected > 0

    @classmethod
    def mark_all_as_read(cls, user_id: int) -> bool:
        """
        Mark all notifications as read for a user.

        Args:
            user_id (int): User ID

        Returns:
            bool: True if any notifications were marked as read

        Example:
            >>> success = NotificationDAL.mark_all_as_read(123)
        """
        query = """
            UPDATE notifications
            SET is_read = 1
            WHERE user_id = ?
              AND is_read = 0
        """
        rows_affected = cls.execute_update(query, (user_id,))
        return rows_affected > 0

    @classmethod
    def get_unread_notification_count(cls, user_id: int) -> int:
        """
        Get count of unread notifications for a user.

        Args:
            user_id (int): User ID

        Returns:
            int: Count of unread notifications

        Example:
            >>> unread_count = NotificationDAL.get_unread_notification_count(123)
        """
        query = """
            SELECT COUNT(*) as count
            FROM notifications
            WHERE user_id = ?
              AND is_read = 0
        """
        results = cls.execute_query(query, (user_id,))
        return results[0]['count'] if results else 0

    @classmethod
    def update_delivery_status(
        cls,
        notification_id: int,
        delivery_status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update notification delivery status.

        Args:
            notification_id (int): Notification ID
            delivery_status (str): 'pending', 'sent', or 'failed'
            error_message (Optional[str]): Error message if failed

        Returns:
            bool: True if updated, False otherwise

        Example:
            >>> success = NotificationDAL.update_delivery_status(
            ...     notification_id=123,
            ...     delivery_status='sent'
            ... )
        """
        if delivery_status not in ('pending', 'sent', 'failed'):
            raise ValueError(f"Invalid delivery_status: {delivery_status}")

        query = """
            UPDATE notifications
            SET delivery_status = ?,
                error_message = ?,
                sent_at = CASE
                    WHEN ? = 'sent' THEN datetime('now')
                    ELSE sent_at
                END
            WHERE notification_id = ?
        """
        rows_affected = cls.execute_update(
            query,
            (delivery_status, error_message, delivery_status, notification_id)
        )
        return rows_affected > 0

    @classmethod
    def get_pending_notifications(
        cls,
        delivery_method: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get notifications pending delivery.

        Used by background workers to process notification queue.

        Args:
            delivery_method (Optional[str]): Filter by delivery method
            limit (int): Max results

        Returns:
            List[Dict]: List of pending notifications

        Example:
            >>> pending = NotificationDAL.get_pending_notifications(
            ...     delivery_method='email'
            ... )
        """
        query = """
            SELECT
                n.*,
                u.name as user_name,
                u.email as user_email
            FROM notifications n
            JOIN users u ON n.user_id = u.user_id
            WHERE n.delivery_status = 'pending'
        """
        params = []

        if delivery_method:
            query += " AND n.delivery_method = ?"
            params.append(delivery_method)

        query += " ORDER BY n.created_at ASC LIMIT ?"
        params.append(limit)

        results = cls.execute_query(query, tuple(params))

        # Parse JSON payloads
        for notification in results:
            if notification['payload_json']:
                try:
                    notification['payload'] = json.loads(notification['payload_json'])
                except json.JSONDecodeError:
                    notification['payload'] = {}
            else:
                notification['payload'] = {}

        return results

    @classmethod
    def delete_notification(cls, notification_id: int) -> bool:
        """
        Delete a notification.

        Args:
            notification_id (int): Notification ID

        Returns:
            bool: True if deleted, False otherwise

        Example:
            >>> success = NotificationDAL.delete_notification(123)
        """
        query = "DELETE FROM notifications WHERE notification_id = ?"
        rows_affected = cls.execute_update(query, (notification_id,))
        return rows_affected > 0

    @classmethod
    def delete_old_notifications(cls, days_old: int = 90) -> int:
        """
        Delete old read notifications (cleanup task).

        Args:
            days_old (int): Delete notifications older than this many days

        Returns:
            int: Number of notifications deleted

        Example:
            >>> deleted = NotificationDAL.delete_old_notifications(days_old=90)
        """
        query = """
            DELETE FROM notifications
            WHERE is_read = 1
              AND created_at < datetime('now', '-' || ? || ' days')
        """
        return cls.execute_update(query, (days_old,))

    # TODO: Implement additional methods as needed:
    # - batch_create_notifications()
    # - get_notification_statistics()
