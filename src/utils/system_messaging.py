"""
System Messaging Utility
========================
Handles automated messages sent from the system to users for booking-related events.

This module provides a centralized way to send system notifications for:
- Booking status changes (approved, rejected, cancelled)
- Resource status changes (archived)
- User account changes (banned)
"""

from datetime import datetime
from typing import Optional
from src.data_access.message_dal import MessageDAL


# System User ID (special user ID for system messages)
SYSTEM_USER_ID = 0


def send_system_message(recipient_id: int, subject: str, content: str) -> bool:
    """
    Send a system message to a user.

    Args:
        recipient_id: User ID of the message recipient
        subject: Message subject line (used only when creating new thread)
        content: Message body content

    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    try:
        # Find existing system notification thread for this user
        import sqlite3
        import os

        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'campus_resource_hub.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT mt.thread_id
            FROM message_threads mt
            JOIN message_thread_participants mtp1 ON mt.thread_id = mtp1.thread_id
            JOIN message_thread_participants mtp2 ON mt.thread_id = mtp2.thread_id
            WHERE mtp1.user_id = ?
            AND mtp2.user_id = ?
            AND mt.resource_id IS NULL
            AND mt.subject = 'System Notifications'
            LIMIT 1
        """, [SYSTEM_USER_ID, recipient_id])

        existing_thread = cursor.fetchone()
        conn.close()

        if existing_thread:
            thread_id = existing_thread['thread_id']
        else:
            # Create a new message thread with standard subject
            thread_id = MessageDAL.create_thread(
                subject='System Notifications',
                resource_id=None
            )

            if not thread_id:
                return False

            # Add both system user and recipient as participants
            MessageDAL.add_thread_participant(thread_id, SYSTEM_USER_ID)
            MessageDAL.add_thread_participant(thread_id, recipient_id)

        # Send the actual message
        message_id = MessageDAL.send_message(
            thread_id=thread_id,
            sender_id=SYSTEM_USER_ID,
            receiver_id=recipient_id,
            content=content
        )

        return message_id is not None

    except Exception as e:
        print(f"Error sending system message: {e}")
        return False


def notify_booking_approved(booking_id: int, user_id: int, resource_title: str,
                            start_datetime: datetime, end_datetime: datetime) -> bool:
    """
    Send notification when a booking is approved.

    Args:
        booking_id: ID of the booking
        user_id: User who made the booking
        resource_title: Title of the resource
        start_datetime: Booking start time
        end_datetime: Booking end time

    Returns:
        bool: True if notification sent successfully
    """
    subject = f"Booking Approved - {resource_title}"
    content = f"""Good news! Your booking request has been approved.

Resource: {resource_title}
Booking ID: {booking_id}
Date: {start_datetime.strftime('%B %d, %Y')}
Time: {start_datetime.strftime('%I:%M %p')} - {end_datetime.strftime('%I:%M %p')}

Your booking is now confirmed. Please arrive on time and follow any resource-specific guidelines.

If you need to cancel or modify your booking, please visit the booking details page."""

    return send_system_message(user_id, subject, content)


def notify_booking_rejected(booking_id: int, user_id: int, resource_title: str,
                            rejection_reason: Optional[str] = None) -> bool:
    """
    Send notification when a booking is rejected.

    Args:
        booking_id: ID of the booking
        user_id: User who made the booking
        resource_title: Title of the resource
        rejection_reason: Optional reason for rejection

    Returns:
        bool: True if notification sent successfully
    """
    subject = f"Booking Request Update - {resource_title}"

    reason_text = f"\n\nReason: {rejection_reason}" if rejection_reason else ""

    content = f"""Your booking request has been reviewed.

Resource: {resource_title}
Booking ID: {booking_id}
Status: Not Approved

Unfortunately, your booking request could not be approved at this time.{reason_text}

You may try booking a different time slot or contact the resource owner for more information."""

    return send_system_message(user_id, subject, content)


def notify_booking_cancelled(booking_id: int, user_id: int, resource_title: str,
                            reason: str, cancelled_by: str = "system") -> bool:
    """
    Send notification when a booking is cancelled.

    Args:
        booking_id: ID of the booking
        user_id: User who made the booking
        resource_title: Title of the resource
        reason: Reason for cancellation
        cancelled_by: Who cancelled it ("system", "admin", "resource owner")

    Returns:
        bool: True if notification sent successfully
    """
    subject = f"Booking Cancelled - {resource_title}"
    content = f"""This is to inform you that your booking has been cancelled.

Resource: {resource_title}
Booking ID: {booking_id}
Cancelled by: {cancelled_by.title()}

Reason: {reason}

We apologize for any inconvenience. You can browse other available resources or rebook this resource for a different time."""

    return send_system_message(user_id, subject, content)


def notify_resource_archived(user_id: int, resource_title: str,
                             affected_bookings_count: int) -> bool:
    """
    Send notification when a resource user booked is archived.

    Args:
        user_id: User who had bookings for this resource
        resource_title: Title of the archived resource
        affected_bookings_count: Number of bookings that were cancelled

    Returns:
        bool: True if notification sent successfully
    """
    subject = f"Resource No Longer Available - {resource_title}"

    bookings_text = "booking has" if affected_bookings_count == 1 else f"{affected_bookings_count} bookings have"

    content = f"""We regret to inform you that a resource you had booked is no longer available.

Resource: {resource_title}

Your {bookings_text} been automatically cancelled as the resource has been archived by the resource owner or administrator.

We apologize for any inconvenience this may cause. Please explore our other available resources that might meet your needs."""

    return send_system_message(user_id, subject, content)


def notify_user_banned(user_id: int, cancelled_bookings_count: int) -> bool:
    """
    Send notification when a user's account is banned.

    Args:
        user_id: User who was banned
        cancelled_bookings_count: Number of bookings that were cancelled

    Returns:
        bool: True if notification sent successfully
    """
    subject = "Account Access Restricted"

    bookings_text = ""
    if cancelled_bookings_count > 0:
        booking_word = "booking" if cancelled_bookings_count == 1 else "bookings"
        bookings_text = f"\n\nAll your active bookings ({cancelled_bookings_count} {booking_word}) have been cancelled."

    content = f"""Your account access has been restricted by an administrator.

You will no longer be able to access the Campus Resource Hub or make new bookings.{bookings_text}

If you believe this is an error, please contact the system administrator."""

    return send_system_message(user_id, subject, content)


def notify_booking_completed(booking_id: int, user_id: int, resource_title: str, resource_id: int) -> bool:
    """
    Send notification when a booking is marked as completed.

    Args:
        booking_id: ID of the booking
        user_id: User who made the booking
        resource_title: Title of the resource
        resource_id: ID of the resource

    Returns:
        bool: True if notification sent successfully
    """
    subject = f"Booking Completed - {resource_title}"
    content = f"""Your booking has been completed.

Resource: {resource_title}
Booking ID: {booking_id}

We hope you had a great experience! If you'd like, you can leave a review to help other users make informed decisions.

Thank you for using Campus Resource Hub!"""

    return send_system_message(user_id, subject, content)
