"""
Unit Tests for Booking Logic
============================
Tests booking conflict detection, status transitions, and business rules.

Requirements covered:
- Unit tests for booking logic (conflict detection, status transitions)
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_access.user_dal import UserDAL
from src.data_access.resource_dal import ResourceDAL
from src.data_access.booking_dal import BookingDAL


class TestBookingConflictDetection:
    """Test booking conflict detection logic."""

    def test_no_conflict_with_non_overlapping_bookings(self):
        """Test that non-overlapping bookings don't conflict."""
        booking_dal = BookingDAL()
        resource_dal = ResourceDAL()
        user_dal = UserDAL()

        # Create user and resource
        user_id = user_dal.create_user("User", "conflict1@iu.edu", "pass", "student")
        owner_id = user_dal.create_user("Owner", "conflict_owner1@iu.edu", "pass", "staff")
        resource_id = resource_dal.create_resource(
            owner_type="user",
            owner_id=owner_id,
            title="Room",
            description="Desc",
            category_id=1,
            location="Test Location",
            status="published"
        )

        # Create first booking: 10:00-12:00
        booking1_id = booking_dal.create_booking(
            requester_id=user_id,
            resource_id=resource_id,
            start_datetime=datetime.strptime("2025-12-15 10:00:00", "%Y-%m-%d %H:%M:%S"),
            end_datetime=datetime.strptime("2025-12-15 12:00:00", "%Y-%m-%d %H:%M:%S")
        )

        # Try to create second booking: 12:00-14:00 (starts exactly when first ends)
        # This should NOT conflict
        has_conflict = booking_dal.has_booking_conflict(
            resource_id=resource_id,
            start_datetime=datetime.strptime("2025-12-15 12:00:00", "%Y-%m-%d %H:%M:%S"),
            end_datetime=datetime.strptime("2025-12-15 14:00:00", "%Y-%m-%d %H:%M:%S")
        )

        assert has_conflict is False

    def test_conflict_with_overlapping_start_time(self):
        """Test that overlapping bookings are detected (overlap at start)."""
        booking_dal = BookingDAL()
        resource_dal = ResourceDAL()
        user_dal = UserDAL()

        user_id = user_dal.create_user("User", "conflict2@iu.edu", "pass", "student")
        owner_id = user_dal.create_user("Owner", "conflict_owner2@iu.edu", "pass", "staff")
        resource_id = resource_dal.create_resource(
            owner_type="user",
            owner_id=owner_id,
            title="Room",
            description="Desc",
            category_id=1,
            location="Test Location",
            status="published"
        )

        # Create first booking: 10:00-12:00
        booking_dal.create_booking(
            requester_id=user_id,
            resource_id=resource_id,
            start_datetime=datetime.strptime("2025-12-15 10:00:00", "%Y-%m-%d %H:%M:%S"),
            end_datetime=datetime.strptime("2025-12-15 12:00:00", "%Y-%m-%d %H:%M:%S")
        )

        # Try to create booking that starts during first: 11:00-13:00
        has_conflict = booking_dal.has_booking_conflict(
            resource_id=resource_id,
            start_datetime=datetime.strptime("2025-12-15 11:00:00", "%Y-%m-%d %H:%M:%S"),
            end_datetime=datetime.strptime("2025-12-15 13:00:00", "%Y-%m-%d %H:%M:%S")
        )

        assert has_conflict is True

    def test_conflict_with_overlapping_end_time(self):
        """Test that overlapping bookings are detected (overlap at end)."""
        booking_dal = BookingDAL()
        resource_dal = ResourceDAL()
        user_dal = UserDAL()

        user_id = user_dal.create_user("User", "conflict3@iu.edu", "pass", "student")
        owner_id = user_dal.create_user("Owner", "conflict_owner3@iu.edu", "pass", "staff")
        resource_id = resource_dal.create_resource(
            owner_type="user",
            owner_id=owner_id,
            title="Room",
            description="Desc",
            category_id=1,
            location="Test Location",
            status="published"
        )

        # Create first booking: 10:00-12:00
        booking_dal.create_booking(
            requester_id=user_id,
            resource_id=resource_id,
            start_datetime=datetime.strptime("2025-12-15 10:00:00", "%Y-%m-%d %H:%M:%S"),
            end_datetime=datetime.strptime("2025-12-15 12:00:00", "%Y-%m-%d %H:%M:%S")
        )

        # Try to create booking that ends during first: 09:00-11:00
        has_conflict = booking_dal.has_booking_conflict(
            resource_id=resource_id,
            start_datetime=datetime.strptime("2025-12-15 09:00:00", "%Y-%m-%d %H:%M:%S"),
            end_datetime=datetime.strptime("2025-12-15 11:00:00", "%Y-%m-%d %H:%M:%S")
        )

        assert has_conflict is True

    def test_conflict_with_completely_overlapping_booking(self):
        """Test conflict when new booking completely overlaps existing."""
        booking_dal = BookingDAL()
        resource_dal = ResourceDAL()
        user_dal = UserDAL()

        user_id = user_dal.create_user("User", "conflict4@iu.edu", "pass", "student")
        owner_id = user_dal.create_user("Owner", "conflict_owner4@iu.edu", "pass", "staff")
        resource_id = resource_dal.create_resource(
            owner_type="user",
            owner_id=owner_id,
            title="Room",
            description="Desc",
            category_id=1,
            location="Test Location",
            status="published"
        )

        # Create first booking: 10:00-12:00
        booking_dal.create_booking(
            requester_id=user_id,
            resource_id=resource_id,
            start_datetime=datetime.strptime("2025-12-15 10:00:00", "%Y-%m-%d %H:%M:%S"),
            end_datetime=datetime.strptime("2025-12-15 12:00:00", "%Y-%m-%d %H:%M:%S")
        )

        # Try to create booking that completely encompasses first: 09:00-13:00
        has_conflict = booking_dal.has_booking_conflict(
            resource_id=resource_id,
            start_datetime=datetime.strptime("2025-12-15 09:00:00", "%Y-%m-%d %H:%M:%S"),
            end_datetime=datetime.strptime("2025-12-15 13:00:00", "%Y-%m-%d %H:%M:%S")
        )

        assert has_conflict is True

    def test_conflict_with_exact_same_time(self):
        """Test conflict when booking has exact same time slot."""
        booking_dal = BookingDAL()
        resource_dal = ResourceDAL()
        user_dal = UserDAL()

        user_id = user_dal.create_user("User", "conflict5@iu.edu", "pass", "student")
        owner_id = user_dal.create_user("Owner", "conflict_owner5@iu.edu", "pass", "staff")
        resource_id = resource_dal.create_resource(
            owner_type="user",
            owner_id=owner_id,
            title="Room",
            description="Desc",
            category_id=1,
            location="Test Location",
            status="published"
        )

        # Create first booking: 10:00-12:00
        booking_dal.create_booking(
            requester_id=user_id,
            resource_id=resource_id,
            start_datetime=datetime.strptime("2025-12-15 10:00:00", "%Y-%m-%d %H:%M:%S"),
            end_datetime=datetime.strptime("2025-12-15 12:00:00", "%Y-%m-%d %H:%M:%S")
        )

        # Try to create booking with exact same time: 10:00-12:00
        has_conflict = booking_dal.has_booking_conflict(
            resource_id=resource_id,
            start_datetime=datetime.strptime("2025-12-15 10:00:00", "%Y-%m-%d %H:%M:%S"),
            end_datetime=datetime.strptime("2025-12-15 12:00:00", "%Y-%m-%d %H:%M:%S")
        )

        assert has_conflict is True

    def test_no_conflict_different_resources(self):
        """Test that bookings for different resources don't conflict."""
        booking_dal = BookingDAL()
        resource_dal = ResourceDAL()
        user_dal = UserDAL()

        user_id = user_dal.create_user("User", "conflict6@iu.edu", "pass", "student")
        owner_id = user_dal.create_user("Owner", "conflict_owner6@iu.edu", "pass", "staff")
        resource1_id = resource_dal.create_resource(
            owner_type="user",
            owner_id=owner_id,
            title="Room 1",
            description="Desc",
            category_id=1,
            location="Test Location",
            status="published"
        )
        resource2_id = resource_dal.create_resource(
            owner_type="user",
            owner_id=owner_id,
            title="Room 2",
            description="Desc",
            category_id=1,
            location="Test Location",
            status="published"
        )

        # Create booking for resource 1: 10:00-12:00
        booking_dal.create_booking(
            requester_id=user_id,
            resource_id=resource1_id,
            start_datetime=datetime.strptime("2025-12-15 10:00:00", "%Y-%m-%d %H:%M:%S"),
            end_datetime=datetime.strptime("2025-12-15 12:00:00", "%Y-%m-%d %H:%M:%S")
        )

        # Check for conflict on resource 2 (different resource): 10:00-12:00
        has_conflict = booking_dal.has_booking_conflict(
            resource_id=resource2_id,
            start_datetime=datetime.strptime("2025-12-15 10:00:00", "%Y-%m-%d %H:%M:%S"),
            end_datetime=datetime.strptime("2025-12-15 12:00:00", "%Y-%m-%d %H:%M:%S")
        )

        assert has_conflict is False

    def test_cancelled_bookings_dont_cause_conflict(self):
        """Test that cancelled bookings don't cause conflicts."""
        booking_dal = BookingDAL()
        resource_dal = ResourceDAL()
        user_dal = UserDAL()

        user_id = user_dal.create_user("User", "conflict7@iu.edu", "pass", "student")
        owner_id = user_dal.create_user("Owner", "conflict_owner7@iu.edu", "pass", "staff")
        resource_id = resource_dal.create_resource(
            owner_type="user",
            owner_id=owner_id,
            title="Room",
            description="Desc",
            category_id=1,
            location="Test Location",
            status="published"
        )

        # Create booking and then cancel it
        booking_id = booking_dal.create_booking(
            requester_id=user_id,
            resource_id=resource_id,
            start_datetime=datetime.strptime("2025-12-15 10:00:00", "%Y-%m-%d %H:%M:%S"),
            end_datetime=datetime.strptime("2025-12-15 12:00:00", "%Y-%m-%d %H:%M:%S")
        )
        booking_dal.cancel_booking(booking_id)

        # Check for conflict at same time - should be no conflict
        has_conflict = booking_dal.has_booking_conflict(
            resource_id=resource_id,
            start_datetime=datetime.strptime("2025-12-15 10:00:00", "%Y-%m-%d %H:%M:%S"),
            end_datetime=datetime.strptime("2025-12-15 12:00:00", "%Y-%m-%d %H:%M:%S")
        )

        assert has_conflict is False


class TestBookingStatusTransitions:
    """Test booking status transition logic."""

    def test_status_transition_pending_to_approved(self):
        """Test valid transition from pending to approved."""
        booking_dal = BookingDAL()
        resource_dal = ResourceDAL()
        user_dal = UserDAL()

        user_id = user_dal.create_user("User", "status1@iu.edu", "pass", "student")
        owner_id = user_dal.create_user("Owner", "status_owner1@iu.edu", "pass", "staff")
        resource_id = resource_dal.create_resource(
            owner_type="user",
            owner_id=owner_id,
            title="Room",
            description="Desc",
            category_id=1,
            location="Test Location",
            status="published"
        )

        # Create booking with pending status
        booking_id = booking_dal.create_booking(
            requester_id=user_id,
            resource_id=resource_id,
            start_datetime=datetime.strptime("2025-12-20 10:00:00", "%Y-%m-%d %H:%M:%S"),
            end_datetime=datetime.strptime("2025-12-20 12:00:00", "%Y-%m-%d %H:%M:%S"),
            approval_required=True
        )

        # Transition to approved
        success = booking_dal.update_booking_status(booking_id, "approved")
        assert success is True

        # Verify status changed
        booking = booking_dal.get_booking_by_id(booking_id)
        assert booking['status'] == "approved"

    def test_status_transition_pending_to_rejected(self):
        """Test valid transition from pending to rejected."""
        booking_dal = BookingDAL()
        resource_dal = ResourceDAL()
        user_dal = UserDAL()

        user_id = user_dal.create_user("User", "status2@iu.edu", "pass", "student")
        owner_id = user_dal.create_user("Owner", "status_owner2@iu.edu", "pass", "staff")
        resource_id = resource_dal.create_resource(
            owner_type="user",
            owner_id=owner_id,
            title="Room",
            description="Desc",
            category_id=1,
            location="Test Location",
            status="published"
        )

        # Create pending booking
        booking_id = booking_dal.create_booking(
            requester_id=user_id,
            resource_id=resource_id,
            start_datetime=datetime.strptime("2025-12-20 14:00:00", "%Y-%m-%d %H:%M:%S"),
            end_datetime=datetime.strptime("2025-12-20 16:00:00", "%Y-%m-%d %H:%M:%S"),
            approval_required=True
        )

        # Transition to rejected
        success = booking_dal.update_booking_status(booking_id, "rejected")
        assert success is True

        # Verify status
        booking = booking_dal.get_booking_by_id(booking_id)
        assert booking['status'] == "rejected"

    def test_status_transition_approved_to_cancelled(self):
        """Test valid transition from approved to cancelled."""
        booking_dal = BookingDAL()
        resource_dal = ResourceDAL()
        user_dal = UserDAL()

        user_id = user_dal.create_user("User", "status3@iu.edu", "pass", "student")
        owner_id = user_dal.create_user("Owner", "status_owner3@iu.edu", "pass", "staff")
        resource_id = resource_dal.create_resource(
            owner_type="user",
            owner_id=owner_id,
            title="Room",
            description="Desc",
            category_id=1,
            location="Test Location",
            status="published"
        )

        # Create approved booking
        booking_id = booking_dal.create_booking(
            requester_id=user_id,
            resource_id=resource_id,
            start_datetime=datetime.strptime("2025-12-21 10:00:00", "%Y-%m-%d %H:%M:%S"),
            end_datetime=datetime.strptime("2025-12-21 12:00:00", "%Y-%m-%d %H:%M:%S")
        )

        # Cancel booking
        success = booking_dal.cancel_booking(booking_id)
        assert success is True

        # Verify status
        booking = booking_dal.get_booking_by_id(booking_id)
        assert booking['status'] == "cancelled"

    def test_status_transition_approved_to_completed(self):
        """Test valid transition from approved to completed."""
        booking_dal = BookingDAL()
        resource_dal = ResourceDAL()
        user_dal = UserDAL()

        user_id = user_dal.create_user("User", "status4@iu.edu", "pass", "student")
        owner_id = user_dal.create_user("Owner", "status_owner4@iu.edu", "pass", "staff")
        resource_id = resource_dal.create_resource(
            owner_type="user",
            owner_id=owner_id,
            title="Room",
            description="Desc",
            category_id=1,
            location="Test Location",
            status="published"
        )

        # Create approved booking
        booking_id = booking_dal.create_booking(
            requester_id=user_id,
            resource_id=resource_id,
            start_datetime=datetime.strptime("2025-12-21 14:00:00", "%Y-%m-%d %H:%M:%S"),
            end_datetime=datetime.strptime("2025-12-21 16:00:00", "%Y-%m-%d %H:%M:%S")
        )

        # Mark as completed
        success = booking_dal.update_booking_status(booking_id, "completed")
        assert success is True

        # Verify status
        booking = booking_dal.get_booking_by_id(booking_id)
        assert booking['status'] == "completed"
