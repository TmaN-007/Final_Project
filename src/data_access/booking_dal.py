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
                b.booking_id,
                b.resource_id,
                b.requester_id,
                b.start_datetime,
                b.end_datetime,
                b.start_datetime as start_time,
                b.end_datetime as end_time,
                b.status,
                b.created_at,
                b.updated_at,
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
            # Use local time for comparison since bookings are stored in local time
            from datetime import datetime
            current_local = datetime.now().isoformat()
            query += " AND b.end_datetime > ? AND b.status NOT IN ('completed', 'cancelled')"
            params.append(current_local)

        # Order by status first (approved, then completed), then by latest bookings within each status
        query += """
            ORDER BY
                CASE b.status
                    WHEN 'approved' THEN 1
                    WHEN 'completed' THEN 2
                    WHEN 'pending' THEN 3
                    WHEN 'cancelled' THEN 4
                    ELSE 5
                END,
                b.created_at DESC
            LIMIT ? OFFSET ?
        """
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

    # =============================================================================
    # ADMIN PANEL METHODS
    # =============================================================================

    @classmethod
    def count_all_bookings(cls) -> int:
        """
        Count total number of bookings.

        Returns:
            Total count of bookings
        """
        query = "SELECT COUNT(*) as count FROM bookings"
        result = cls.execute_query(query)
        return result[0]['count'] if result else 0

    @classmethod
    def count_pending_bookings(cls) -> int:
        """
        Count bookings with pending status.

        Returns:
            Count of pending bookings
        """
        query = "SELECT COUNT(*) as count FROM bookings WHERE status = 'pending'"
        result = cls.execute_query(query)
        return result[0]['count'] if result else 0

    @classmethod
    def count_bookings_by_user(
        cls,
        user_id: int,
        status: Optional[str] = None,
        upcoming_only: bool = False
    ) -> int:
        """
        Count total bookings for a user with optional filters.

        Args:
            user_id (int): User ID
            status (Optional[str]): Filter by status
            upcoming_only (bool): Only count future bookings

        Returns:
            int: Total count of matching bookings
        """
        query = "SELECT COUNT(*) as count FROM bookings WHERE requester_id = ?"
        params = [user_id]

        if status:
            query += " AND status = ?"
            params.append(status)

        if upcoming_only:
            # Use local time for comparison since bookings are stored in local time
            from datetime import datetime
            current_local = datetime.now().isoformat()
            query += " AND end_datetime > ? AND status NOT IN ('completed', 'cancelled')"
            params.append(current_local)

        result = cls.execute_query(query, tuple(params))
        return result[0]['count'] if result else 0

    @classmethod
    def get_recent_bookings(cls, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recently created bookings.

        Args:
            limit: Maximum number of bookings to return

        Returns:
            List of booking dicts with user and resource info
        """
        query = """
            SELECT b.booking_id, b.status, b.start_datetime as start_time,
                   b.end_datetime as end_time, b.created_at, b.requester_id as user_id,
                   b.resource_id, u.name as user_name, u.email as user_email,
                   r.title as resource_title, rc.name as resource_category
            FROM bookings b
            LEFT JOIN users u ON b.requester_id = u.user_id
            LEFT JOIN resources r ON b.resource_id = r.resource_id
            LEFT JOIN resource_categories rc ON r.category_id = rc.category_id
            ORDER BY b.created_at DESC
            LIMIT ?
        """
        return cls.execute_query(query, (limit,))

    @classmethod
    def get_all_bookings_paginated(cls, page: int = 1, per_page: int = 20,
                                    status_filter: str = '', user_id: int = None,
                                    resource_id: int = None, search_query: str = '',
                                    booking_id: str = '') -> Dict[str, Any]:
        """
        Get paginated list of bookings with optional filters.

        Args:
            page: Page number (1-indexed)
            per_page: Number of items per page
            status_filter: Filter by status ('pending', 'confirmed', 'completed', 'cancelled')
            user_id: Filter by user ID
            resource_id: Filter by resource ID
            search_query: Search in user name, email, or resource title
            booking_id: Filter by exact booking ID

        Returns:
            Dict with 'bookings' list and 'pagination' info
        """
        offset = (page - 1) * per_page

        # Build WHERE clause dynamically
        where_clauses = []
        params = []

        if status_filter:
            where_clauses.append("b.status = ?")
            params.append(status_filter)

        if user_id:
            where_clauses.append("b.requester_id = ?")
            params.append(user_id)

        if resource_id:
            where_clauses.append("b.resource_id = ?")
            params.append(resource_id)

        # Exact booking ID filter takes priority
        if booking_id:
            where_clauses.append("b.booking_id = ?")
            params.append(int(booking_id))
        elif search_query:
            # General search in user name, email, or resource title
            where_clauses.append("(u.name LIKE ? OR u.email LIKE ? OR r.title LIKE ?)")
            search_pattern = f'%{search_query}%'
            params.extend([search_pattern, search_pattern, search_pattern])

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        # Get total count
        count_query = f"""
            SELECT COUNT(*) as count
            FROM bookings b
            LEFT JOIN users u ON b.requester_id = u.user_id
            LEFT JOIN resources r ON b.resource_id = r.resource_id
            WHERE {where_sql}
        """
        total_result = cls.execute_query(count_query, tuple(params))
        total_count = total_result[0]['count'] if total_result else 0

        # Get bookings
        query = f"""
            SELECT b.booking_id, b.status, b.start_datetime as start_time,
                   b.end_datetime as end_time, b.created_at, b.updated_at,
                   b.requester_id as user_id, b.resource_id,
                   u.name as user_name, u.email as user_email,
                   r.title as resource_title, rc.name as resource_category
            FROM bookings b
            LEFT JOIN users u ON b.requester_id = u.user_id
            LEFT JOIN resources r ON b.resource_id = r.resource_id
            LEFT JOIN resource_categories rc ON r.category_id = rc.category_id
            WHERE {where_sql}
            ORDER BY b.created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([per_page, offset])
        bookings = cls.execute_query(query, tuple(params))

        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page

        return {
            'bookings': bookings,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_prev': page > 1,
                'has_next': page < total_pages
            }
        }

    @classmethod
    def admin_cancel_booking(cls, booking_id: int, admin_notes: str = '') -> bool:
        """
        Cancel a booking (admin only).

        Args:
            booking_id: Booking ID
            admin_notes: Optional notes about the cancellation

        Returns:
            True if cancellation successful, False otherwise
        """
        query = """
            UPDATE bookings
            SET status = 'cancelled',
                updated_at = CURRENT_TIMESTAMP
            WHERE booking_id = ?
        """
        rows_affected = cls.execute_update(query, (booking_id,))

        # If admin_notes provided, you might want to log it somewhere
        # For now, just return success status
        return rows_affected > 0

    @classmethod
    def auto_complete_past_bookings(cls) -> int:
        """
        Automatically mark approved bookings as completed if their end time has passed.
        Sends system notifications to users for completed bookings.

        Returns:
            int: Number of bookings updated
        """
        # Get current local time as ISO string to compare with stored local time dates
        from datetime import datetime
        current_local = datetime.now().isoformat()

        # First, get the bookings that will be completed
        select_query = """
            SELECT b.booking_id, b.requester_id, b.resource_id, r.title as resource_title
            FROM bookings b
            LEFT JOIN resources r ON b.resource_id = r.resource_id
            WHERE b.status = 'approved'
              AND b.end_datetime < ?
        """
        completed_bookings = cls.execute_query(select_query, (current_local,))

        # Update their status
        update_query = """
            UPDATE bookings
            SET status = 'completed',
                updated_at = CURRENT_TIMESTAMP
            WHERE status = 'approved'
              AND end_datetime < ?
        """
        rows_affected = cls.execute_update(update_query, (current_local,))

        # Send system notifications for each completed booking
        if completed_bookings:
            try:
                from src.utils import system_messaging
                for booking_data in completed_bookings:
                    try:
                        system_messaging.notify_booking_completed(
                            booking_id=booking_data['booking_id'],
                            user_id=booking_data['requester_id'],
                            resource_title=booking_data.get('resource_title', 'Resource'),
                            resource_id=booking_data['resource_id']
                        )
                    except Exception as e:
                        print(f"Failed to send completion notification for booking {booking_data['booking_id']}: {e}")
            except Exception as e:
                print(f"Failed to import system_messaging: {e}")

        return rows_affected

    @classmethod
    def cancel_bookings_by_resource(cls, resource_id: int) -> int:
        """
        Delete all active (pending and approved) bookings for a specific resource.
        Used when a resource is archived or deleted.
        Sends system notifications to affected users.

        Args:
            resource_id: Resource ID whose bookings should be deleted

        Returns:
            int: Number of bookings deleted
        """
        # First, get affected bookings grouped by user for notifications
        select_query = """
            SELECT b.requester_id, COUNT(*) as booking_count, r.title as resource_title
            FROM bookings b
            LEFT JOIN resources r ON b.resource_id = r.resource_id
            WHERE b.resource_id = ?
              AND b.status IN ('pending', 'approved')
            GROUP BY b.requester_id, r.title
        """
        affected_users = cls.execute_query(select_query, (resource_id,))

        # Delete ALL bookings for this resource (not just active ones)
        # This is necessary because the bookings table has ON DELETE RESTRICT on resource_id
        # We must delete ALL booking records, including completed and cancelled ones
        delete_query = """
            DELETE FROM bookings
            WHERE resource_id = ?
        """
        rows_affected = cls.execute_update(delete_query, (resource_id,))

        # Send system notifications to affected users
        if affected_users:
            try:
                from src.utils import system_messaging
                for user_data in affected_users:
                    try:
                        system_messaging.notify_resource_archived(
                            user_id=user_data['requester_id'],
                            resource_title=user_data.get('resource_title', 'Resource'),
                            affected_bookings_count=user_data['booking_count']
                        )
                    except Exception as e:
                        logger.error(f"Failed to send archival notification to user {user_data['requester_id']}: {e}")
            except Exception as e:
                logger.error(f"Failed to import system_messaging: {e}")

        return rows_affected

    @classmethod
    def cancel_bookings_by_user(cls, user_id: int) -> int:
        """
        Cancel all active (pending and approved) bookings for a specific user.
        Used when a user is banned.

        Args:
            user_id: User ID whose bookings should be cancelled

        Returns:
            int: Number of bookings cancelled
        """
        query = """
            UPDATE bookings
            SET status = 'cancelled',
                updated_at = CURRENT_TIMESTAMP
            WHERE requester_id = ?
              AND status IN ('pending', 'approved')
        """
        rows_affected = cls.execute_update(query, (user_id,))
        return rows_affected

    # TODO: Implement additional methods as needed:
    # - get_booking_statistics()
    # - get_user_booking_history()
    # - get_resource_utilization()
    # - handle_recurrence_rules()
