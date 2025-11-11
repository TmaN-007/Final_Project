"""
Campus Resource Hub - Booking Data Access Layer
================================================
MVC Role: Data access for booking management
MCP Role: Booking data queries for AI-assisted scheduling

This module handles all database operations for bookings including:
- Booking CRUD operations
- Conflict detection
- Availability checking
- Booking status management
- Approval workflows
- Waitlist management

All queries use parameterized statements for SQL injection prevention.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging

from src.data_access.base_dal import BaseDAL

logger = logging.getLogger(__name__)


class BookingDAL(BaseDAL):
    """
    Booking Data Access Layer.

    Handles all database operations for the bookings table and related tables.
    Includes critical conflict detection logic to prevent double-booking.
    """

    @classmethod
    def create_booking(
        cls,
        resource_id: int,
        requester_id: int,
        start_datetime: datetime,
        end_datetime: datetime,
        notes: Optional[str] = None,
        approval_required: bool = False
    ) -> Optional[int]:
        """
        Create a new booking after checking for conflicts.

        Args:
            resource_id (int): Resource to book
            requester_id (int): User making the booking
            start_datetime (datetime): Booking start time
            end_datetime (datetime): Booking end time
            notes (Optional[str]): Additional notes
            approval_required (bool): Whether this booking requires approval

        Returns:
            Optional[int]: New booking ID if successful, None if conflict exists

        Raises:
            ValueError: If end_datetime is not after start_datetime

        Example:
            >>> booking_id = BookingDAL.create_booking(
            ...     resource_id=5,
            ...     requester_id=123,
            ...     start_datetime=datetime(2025, 11, 15, 10, 0),
            ...     end_datetime=datetime(2025, 11, 15, 12, 0),
            ...     approval_required=True
            ... )
        """
        # Validate datetime order
        if end_datetime <= start_datetime:
            raise ValueError("end_datetime must be after start_datetime")

        # Check for conflicts
        if cls.has_booking_conflict(resource_id, start_datetime, end_datetime):
            logger.warning(
                f"Booking conflict detected for resource {resource_id} "
                f"between {start_datetime} and {end_datetime}"
            )
            return None

        # Determine initial status
        status = 'pending' if approval_required else 'approved'

        query = """
            INSERT INTO bookings (
                resource_id, requester_id, start_datetime, end_datetime,
                status, approval_required, notes, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """

        return cls.execute_update(query, (
            resource_id,
            requester_id,
            start_datetime.isoformat(),
            end_datetime.isoformat(),
            status,
            int(approval_required),
            notes
        ))

    @classmethod
    def has_booking_conflict(
        cls,
        resource_id: int,
        start_datetime: datetime,
        end_datetime: datetime,
        exclude_booking_id: Optional[int] = None
    ) -> bool:
        """
        Check if a booking would conflict with existing bookings.

        A conflict exists if there is any overlap with:
        1. Approved or pending bookings for the same resource
        2. Resource unavailable slots

        Args:
            resource_id (int): Resource to check
            start_datetime (datetime): Proposed start time
            end_datetime (datetime): Proposed end time
            exclude_booking_id (Optional[int]): Booking ID to exclude (for updates)

        Returns:
            bool: True if conflict exists, False otherwise

        Example:
            >>> has_conflict = BookingDAL.has_booking_conflict(
            ...     resource_id=5,
            ...     start_datetime=datetime(2025, 11, 15, 10, 0),
            ...     end_datetime=datetime(2025, 11, 15, 12, 0)
            ... )
        """
        # Check for overlapping bookings
        # Two time ranges overlap if: start1 < end2 AND start2 < end1
        query = """
            SELECT COUNT(*) as count
            FROM bookings
            WHERE resource_id = ?
              AND status IN ('approved', 'pending')
              AND start_datetime < ?
              AND end_datetime > ?
        """
        params = [resource_id, end_datetime.isoformat(), start_datetime.isoformat()]

        if exclude_booking_id:
            query += " AND booking_id != ?"
            params.append(exclude_booking_id)

        results = cls.execute_query(query, tuple(params))
        booking_conflicts = results[0]['count'] if results else 0

        if booking_conflicts > 0:
            return True

        # Check for unavailable slots
        unavailable_query = """
            SELECT COUNT(*) as count
            FROM resource_unavailable_slots
            WHERE resource_id = ?
              AND start_datetime < ?
              AND end_datetime > ?
        """
        unavailable_results = cls.execute_query(
            unavailable_query,
            (resource_id, end_datetime.isoformat(), start_datetime.isoformat())
        )
        unavailable_conflicts = unavailable_results[0]['count'] if unavailable_results else 0

        return unavailable_conflicts > 0

    @classmethod
    def get_booking_by_id(cls, booking_id: int) -> Optional[Dict[str, Any]]:
        """
        Get booking by ID with resource and user information.

        Args:
            booking_id (int): Booking ID

        Returns:
            Optional[Dict]: Booking data or None if not found

        Example:
            >>> booking = BookingDAL.get_booking_by_id(123)
            >>> print(booking['resource_title'])
        """
        query = """
            SELECT
                b.*,
                r.title as resource_title,
                r.location as resource_location,
                r.owner_type as resource_owner_type,
                r.owner_id as resource_owner_id,
                u.name as requester_name,
                u.email as requester_email
            FROM bookings b
            JOIN resources r ON b.resource_id = r.resource_id
            JOIN users u ON b.requester_id = u.user_id
            WHERE b.booking_id = ?
        """
        results = cls.execute_query(query, (booking_id,))
        return results[0] if results else None

    @classmethod
    def get_bookings_by_user(
        cls,
        user_id: int,
        status: Optional[str] = None,
        upcoming_only: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all bookings for a user.

        Args:
            user_id (int): User ID
            status (Optional[str]): Filter by status
            upcoming_only (bool): Only show future bookings
            limit (int): Max results
            offset (int): Pagination offset

        Returns:
            List[Dict]: List of bookings

        Example:
            >>> upcoming = BookingDAL.get_bookings_by_user(
            ...     user_id=123,
            ...     upcoming_only=True
            ... )
        """
        query = """
            SELECT
                b.*,
                r.title as resource_title,
                r.location as resource_location,
                r.category_id
            FROM bookings b
            JOIN resources r ON b.resource_id = r.resource_id
            WHERE b.requester_id = ?
        """
        params = [user_id]

        if status:
            query += " AND b.status = ?"
            params.append(status)

        if upcoming_only:
            query += " AND b.end_datetime > datetime('now')"

        query += " ORDER BY b.start_datetime DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        return cls.execute_query(query, tuple(params))

    @classmethod
    def get_bookings_by_resource(
        cls,
        resource_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all bookings for a resource within a date range.

        Args:
            resource_id (int): Resource ID
            start_date (Optional[datetime]): Start of date range
            end_date (Optional[datetime]): End of date range
            status (Optional[str]): Filter by status
            limit (int): Max results
            offset (int): Pagination offset

        Returns:
            List[Dict]: List of bookings

        Example:
            >>> bookings = BookingDAL.get_bookings_by_resource(
            ...     resource_id=5,
            ...     start_date=datetime(2025, 11, 1),
            ...     end_date=datetime(2025, 11, 30),
            ...     status='approved'
            ... )
        """
        query = """
            SELECT
                b.*,
                u.name as requester_name,
                u.email as requester_email
            FROM bookings b
            JOIN users u ON b.requester_id = u.user_id
            WHERE b.resource_id = ?
        """
        params = [resource_id]

        if start_date:
            query += " AND b.end_datetime >= ?"
            params.append(start_date.isoformat())

        if end_date:
            query += " AND b.start_datetime <= ?"
            params.append(end_date.isoformat())

        if status:
            query += " AND b.status = ?"
            params.append(status)

        query += " ORDER BY b.start_datetime ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        return cls.execute_query(query, tuple(params))

    @classmethod
    def update_booking_status(
        cls,
        booking_id: int,
        new_status: str,
        approver_id: Optional[int] = None,
        comment: Optional[str] = None
    ) -> bool:
        """
        Update booking status.

        Args:
            booking_id (int): Booking ID
            new_status (str): New status ('approved', 'rejected', 'cancelled', 'completed')
            approver_id (Optional[int]): User ID of approver (for approval/rejection)
            comment (Optional[str]): Approval/rejection comment

        Returns:
            bool: True if updated successfully, False otherwise

        Example:
            >>> success = BookingDAL.update_booking_status(
            ...     booking_id=123,
            ...     new_status='approved',
            ...     approver_id=456,
            ...     comment='Approved for academic use'
            ... )
        """
        if new_status not in ('pending', 'approved', 'rejected', 'cancelled', 'completed'):
            raise ValueError(f"Invalid status: {new_status}")

        # Update booking status
        query = """
            UPDATE bookings
            SET status = ?,
                updated_at = datetime('now')
            WHERE booking_id = ?
        """
        rows_affected = cls.execute_update(query, (new_status, booking_id))

        # Log approval action if applicable
        if new_status in ('approved', 'rejected') and approver_id:
            approval_query = """
                INSERT INTO booking_approval_actions (
                    booking_id, approver_id, action, comment, created_at
                ) VALUES (?, ?, ?, ?, datetime('now'))
            """
            cls.execute_update(approval_query, (booking_id, approver_id, new_status, comment))

        return rows_affected > 0

    @classmethod
    def update_booking(
        cls,
        booking_id: int,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
        notes: Optional[str] = None
    ) -> bool:
        """
        Update booking details (time or notes).

        Args:
            booking_id (int): Booking ID
            start_datetime (Optional[datetime]): New start time
            end_datetime (Optional[datetime]): New end time
            notes (Optional[str]): New notes

        Returns:
            bool: True if updated successfully, False otherwise

        Note:
            If changing times, this will check for conflicts.
        """
        # Get current booking
        booking = cls.get_booking_by_id(booking_id)
        if not booking:
            return False

        # If updating times, check for conflicts
        if start_datetime or end_datetime:
            new_start = start_datetime or datetime.fromisoformat(booking['start_datetime'])
            new_end = end_datetime or datetime.fromisoformat(booking['end_datetime'])

            if new_end <= new_start:
                raise ValueError("end_datetime must be after start_datetime")

            if cls.has_booking_conflict(
                booking['resource_id'],
                new_start,
                new_end,
                exclude_booking_id=booking_id
            ):
                logger.warning(
                    f"Cannot update booking {booking_id}: conflict detected"
                )
                return False

        fields = []
        params = []

        if start_datetime:
            fields.append("start_datetime = ?")
            params.append(start_datetime.isoformat())

        if end_datetime:
            fields.append("end_datetime = ?")
            params.append(end_datetime.isoformat())

        if notes is not None:
            fields.append("notes = ?")
            params.append(notes)

        if not fields:
            return False

        fields.append("updated_at = datetime('now')")
        params.append(booking_id)

        query = f"""
            UPDATE bookings
            SET {', '.join(fields)}
            WHERE booking_id = ?
        """

        rows_affected = cls.execute_update(query, tuple(params))
        return rows_affected > 0

    @classmethod
    def cancel_booking(cls, booking_id: int) -> bool:
        """
        Cancel a booking.

        Args:
            booking_id (int): Booking ID

        Returns:
            bool: True if cancelled successfully, False otherwise

        Example:
            >>> success = BookingDAL.cancel_booking(123)
        """
        return cls.update_booking_status(booking_id, 'cancelled')

    @classmethod
    def delete_booking(cls, booking_id: int) -> bool:
        """
        Delete a booking (hard delete).

        Args:
            booking_id (int): Booking ID

        Returns:
            bool: True if deleted successfully, False otherwise

        Note:
            Prefer cancel_booking() for soft delete in most cases.
        """
        query = "DELETE FROM bookings WHERE booking_id = ?"
        rows_affected = cls.execute_update(query, (booking_id,))
        return rows_affected > 0

    @classmethod
    def get_pending_approvals(
        cls,
        resource_owner_id: int,
        owner_type: str = 'user',
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get bookings pending approval for resources owned by a user/group.

        Args:
            resource_owner_id (int): Owner ID
            owner_type (str): 'user' or 'group'
            limit (int): Max results
            offset (int): Pagination offset

        Returns:
            List[Dict]: List of pending bookings

        Example:
            >>> pending = BookingDAL.get_pending_approvals(
            ...     resource_owner_id=456,
            ...     owner_type='user'
            ... )
        """
        query = """
            SELECT
                b.*,
                r.title as resource_title,
                r.location as resource_location,
                u.name as requester_name,
                u.email as requester_email
            FROM bookings b
            JOIN resources r ON b.resource_id = r.resource_id
            JOIN users u ON b.requester_id = u.user_id
            WHERE b.status = 'pending'
              AND b.approval_required = 1
              AND r.owner_type = ?
              AND r.owner_id = ?
            ORDER BY b.created_at ASC
            LIMIT ? OFFSET ?
        """
        return cls.execute_query(query, (owner_type, resource_owner_id, limit, offset))

    @classmethod
    def get_available_slots(
        cls,
        resource_id: int,
        start_date: datetime,
        end_date: datetime,
        slot_duration_minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Get available time slots for a resource within a date range.

        This is a helper method for calendar views showing open slots.

        Args:
            resource_id (int): Resource ID
            start_date (datetime): Start of range
            end_date (datetime): End of range
            slot_duration_minutes (int): Duration of each slot to check

        Returns:
            List[Dict]: List of available slots with start/end times

        Note:
            This returns potential slots. Actual availability depends on
            resource availability rules which should be checked separately.
        """
        # Get all bookings in the range
        bookings = cls.get_bookings_by_resource(
            resource_id,
            start_date,
            end_date,
            status='approved'
        )

        # Get unavailable slots
        unavailable_query = """
            SELECT start_datetime, end_datetime
            FROM resource_unavailable_slots
            WHERE resource_id = ?
              AND start_datetime < ?
              AND end_datetime > ?
        """
        unavailable_slots = cls.execute_query(
            unavailable_query,
            (resource_id, end_date.isoformat(), start_date.isoformat())
        )

        # Combine all blocked times
        blocked_times = []
        for booking in bookings:
            blocked_times.append({
                'start': datetime.fromisoformat(booking['start_datetime']),
                'end': datetime.fromisoformat(booking['end_datetime'])
            })
        for slot in unavailable_slots:
            blocked_times.append({
                'start': datetime.fromisoformat(slot['start_datetime']),
                'end': datetime.fromisoformat(slot['end_datetime'])
            })

        # Sort blocked times by start time
        blocked_times.sort(key=lambda x: x['start'])

        # Find available slots
        available_slots = []
        current_time = start_date
        slot_duration = timedelta(minutes=slot_duration_minutes)

        while current_time + slot_duration <= end_date:
            slot_end = current_time + slot_duration

            # Check if this slot conflicts with any blocked time
            is_available = True
            for blocked in blocked_times:
                if current_time < blocked['end'] and slot_end > blocked['start']:
                    is_available = False
                    # Skip to end of this blocked period
                    current_time = blocked['end']
                    break

            if is_available:
                available_slots.append({
                    'start_datetime': current_time,
                    'end_datetime': slot_end
                })
                current_time = slot_end
            elif current_time >= end_date:
                break

        return available_slots

    @classmethod
    def add_to_waitlist(
        cls,
        resource_id: int,
        user_id: int,
        desired_start_datetime: datetime,
        desired_end_datetime: datetime
    ) -> int:
        """
        Add user to waitlist for a resource.

        Args:
            resource_id (int): Resource ID
            user_id (int): User ID
            desired_start_datetime (datetime): Desired start time
            desired_end_datetime (datetime): Desired end time

        Returns:
            int: Waitlist ID

        Example:
            >>> waitlist_id = BookingDAL.add_to_waitlist(
            ...     resource_id=5,
            ...     user_id=123,
            ...     desired_start_datetime=datetime(2025, 11, 15, 10, 0),
            ...     desired_end_datetime=datetime(2025, 11, 15, 12, 0)
            ... )
        """
        query = """
            INSERT INTO booking_waitlist (
                resource_id, user_id, desired_start_datetime, desired_end_datetime,
                status, created_at
            ) VALUES (?, ?, ?, ?, 'waiting', datetime('now'))
        """
        return cls.execute_update(query, (
            resource_id,
            user_id,
            desired_start_datetime.isoformat(),
            desired_end_datetime.isoformat()
        ))

    @classmethod
    def get_waitlist_by_resource(cls, resource_id: int) -> List[Dict[str, Any]]:
        """
        Get waitlist entries for a resource.

        Args:
            resource_id (int): Resource ID

        Returns:
            List[Dict]: List of waitlist entries

        Example:
            >>> waitlist = BookingDAL.get_waitlist_by_resource(5)
        """
        query = """
            SELECT
                w.*,
                u.name as user_name,
                u.email as user_email
            FROM booking_waitlist w
            JOIN users u ON w.user_id = u.user_id
            WHERE w.resource_id = ?
              AND w.status = 'waiting'
            ORDER BY w.created_at ASC
        """
        return cls.execute_query(query, (resource_id,))

    # TODO: Implement additional methods as needed:
    # - get_booking_statistics()
    # - get_user_booking_history()
    # - get_resource_utilization()
    # - handle_recurrence_rules()
