"""
Campus Resource Hub - Review & Content Moderation Data Access Layer
===================================================================
MVC Role: Data access for reviews and content reports
MCP Role: Review/moderation queries for AI-assisted content safety

This module handles all database operations for:
- Reviews and ratings
- Review helpfulness voting
- Host responses
- Content reports
- Moderation workflows

All queries use parameterized statements for SQL injection prevention.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from src.data_access.base_dal import BaseDAL

logger = logging.getLogger(__name__)


class ReviewDAL(BaseDAL):
    """
    Review Data Access Layer.

    Handles all database operations for reviews and ratings.
    """

    @classmethod
    def create_review(
        cls,
        booking_id: int,
        resource_id: int,
        reviewer_id: int,
        rating: int,
        comment: Optional[str] = None
    ) -> Optional[int]:
        """
        Create a review for a resource after a booking.

        Args:
            booking_id (int): Completed booking ID
            resource_id (int): Resource being reviewed
            reviewer_id (int): User writing the review
            rating (int): Rating (1-5 stars)
            comment (Optional[str]): Review text

        Returns:
            Optional[int]: New review ID if successful, None if validation fails

        Raises:
            ValueError: If rating is not between 1 and 5

        Example:
            >>> review_id = ReviewDAL.create_review(
            ...     booking_id=123,
            ...     resource_id=5,
            ...     reviewer_id=456,
            ...     rating=5,
            ...     comment='Excellent study space!'
            ... )
        """
        # Validate rating
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5")

        # Check if user has already reviewed this booking
        existing_query = """
            SELECT COUNT(*) as count
            FROM reviews
            WHERE booking_id = ? AND reviewer_id = ?
        """
        existing = cls.execute_query(existing_query, (booking_id, reviewer_id))
        if existing and existing[0]['count'] > 0:
            logger.warning(f"User {reviewer_id} already reviewed booking {booking_id}")
            return None

        query = """
            INSERT INTO reviews (
                booking_id, resource_id, reviewer_id, rating, comment,
                is_visible, flagged_count, helpful_count, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, 1, 0, 0, datetime('now'), datetime('now'))
        """
        return cls.execute_update(query, (
            booking_id,
            resource_id,
            reviewer_id,
            rating,
            comment
        ))

    @classmethod
    def get_review_by_id(cls, review_id: int) -> Optional[Dict[str, Any]]:
        """
        Get review by ID with reviewer and resource information.

        Args:
            review_id (int): Review ID

        Returns:
            Optional[Dict]: Review data or None if not found

        Example:
            >>> review = ReviewDAL.get_review_by_id(123)
        """
        query = """
            SELECT
                r.*,
                u.name as reviewer_name,
                u.profile_image as reviewer_image,
                res.title as resource_title,
                b.start_datetime,
                b.end_datetime
            FROM reviews r
            JOIN users u ON r.reviewer_id = u.user_id
            JOIN resources res ON r.resource_id = res.resource_id
            JOIN bookings b ON r.booking_id = b.booking_id
            WHERE r.review_id = ?
        """
        results = cls.execute_query(query, (review_id,))
        return results[0] if results else None

    @classmethod
    def get_reviews_by_resource(
        cls,
        resource_id: int,
        visible_only: bool = True,
        min_rating: Optional[int] = None,
        sort_by: str = 'recent',
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all reviews for a resource.

        Args:
            resource_id (int): Resource ID
            visible_only (bool): Only show visible reviews
            min_rating (Optional[int]): Minimum rating filter
            sort_by (str): Sort order ('recent', 'rating_high', 'rating_low', 'helpful')
            limit (int): Max results
            offset (int): Pagination offset

        Returns:
            List[Dict]: List of reviews

        Example:
            >>> reviews = ReviewDAL.get_reviews_by_resource(
            ...     resource_id=5,
            ...     sort_by='helpful'
            ... )
        """
        query = """
            SELECT
                r.*,
                u.name as reviewer_name,
                u.profile_image as reviewer_image,
                b.start_datetime
            FROM reviews r
            JOIN users u ON r.reviewer_id = u.user_id
            JOIN bookings b ON r.booking_id = b.booking_id
            WHERE r.resource_id = ?
        """
        params = [resource_id]

        if visible_only:
            query += " AND r.is_visible = 1"

        if min_rating:
            query += " AND r.rating >= ?"
            params.append(min_rating)

        # Sort order
        sort_map = {
            'recent': 'r.created_at DESC',
            'rating_high': 'r.rating DESC, r.created_at DESC',
            'rating_low': 'r.rating ASC, r.created_at DESC',
            'helpful': 'r.helpful_count DESC, r.created_at DESC'
        }
        order_by = sort_map.get(sort_by, 'r.created_at DESC')
        query += f" ORDER BY {order_by} LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        return cls.execute_query(query, tuple(params))

    @classmethod
    def get_reviews_by_user(
        cls,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all reviews written by a user.

        Args:
            user_id (int): User ID
            limit (int): Max results
            offset (int): Pagination offset

        Returns:
            List[Dict]: List of reviews

        Example:
            >>> my_reviews = ReviewDAL.get_reviews_by_user(123)
        """
        query = """
            SELECT
                r.*,
                res.title as resource_title,
                b.start_datetime
            FROM reviews r
            JOIN resources res ON r.resource_id = res.resource_id
            JOIN bookings b ON r.booking_id = b.booking_id
            WHERE r.reviewer_id = ?
            ORDER BY r.created_at DESC
            LIMIT ? OFFSET ?
        """
        return cls.execute_query(query, (user_id, limit, offset))

    @classmethod
    def update_review(
        cls,
        review_id: int,
        rating: Optional[int] = None,
        comment: Optional[str] = None
    ) -> bool:
        """
        Update review content.

        Args:
            review_id (int): Review ID
            rating (Optional[int]): New rating (1-5)
            comment (Optional[str]): New comment text

        Returns:
            bool: True if updated, False otherwise

        Example:
            >>> success = ReviewDAL.update_review(
            ...     review_id=123,
            ...     rating=4,
            ...     comment='Updated: Still good but a bit noisy'
            ... )
        """
        fields = []
        params = []

        if rating is not None:
            if not (1 <= rating <= 5):
                raise ValueError("Rating must be between 1 and 5")
            fields.append("rating = ?")
            params.append(rating)

        if comment is not None:
            fields.append("comment = ?")
            params.append(comment)

        if not fields:
            return False

        fields.append("updated_at = datetime('now')")
        params.append(review_id)

        query = f"""
            UPDATE reviews
            SET {', '.join(fields)}
            WHERE review_id = ?
        """

        rows_affected = cls.execute_update(query, tuple(params))
        return rows_affected > 0

    @classmethod
    def add_host_response(
        cls,
        review_id: int,
        host_response: str
    ) -> bool:
        """
        Add host response to a review.

        Args:
            review_id (int): Review ID
            host_response (str): Host's response text

        Returns:
            bool: True if added, False otherwise

        Example:
            >>> success = ReviewDAL.add_host_response(
            ...     review_id=123,
            ...     host_response='Thank you for your feedback!'
            ... )
        """
        query = """
            UPDATE reviews
            SET host_response = ?,
                host_responded_at = datetime('now'),
                updated_at = datetime('now')
            WHERE review_id = ?
        """
        rows_affected = cls.execute_update(query, (host_response, review_id))
        return rows_affected > 0

    @classmethod
    def increment_helpful_count(cls, review_id: int) -> bool:
        """
        Increment the helpful count for a review.

        Args:
            review_id (int): Review ID

        Returns:
            bool: True if incremented, False otherwise

        Example:
            >>> success = ReviewDAL.increment_helpful_count(123)
        """
        query = """
            UPDATE reviews
            SET helpful_count = helpful_count + 1
            WHERE review_id = ?
        """
        rows_affected = cls.execute_update(query, (review_id,))
        return rows_affected > 0

    @classmethod
    def hide_review(cls, review_id: int) -> bool:
        """
        Hide a review (content moderation).

        Args:
            review_id (int): Review ID

        Returns:
            bool: True if hidden, False otherwise

        Example:
            >>> success = ReviewDAL.hide_review(123)
        """
        query = """
            UPDATE reviews
            SET is_visible = 0,
                updated_at = datetime('now')
            WHERE review_id = ?
        """
        rows_affected = cls.execute_update(query, (review_id,))
        return rows_affected > 0

    @classmethod
    def show_review(cls, review_id: int) -> bool:
        """
        Show a previously hidden review.

        Args:
            review_id (int): Review ID

        Returns:
            bool: True if shown, False otherwise

        Example:
            >>> success = ReviewDAL.show_review(123)
        """
        query = """
            UPDATE reviews
            SET is_visible = 1,
                updated_at = datetime('now')
            WHERE review_id = ?
        """
        rows_affected = cls.execute_update(query, (review_id,))
        return rows_affected > 0

    @classmethod
    def delete_review(cls, review_id: int) -> bool:
        """
        Delete a review (hard delete).

        Args:
            review_id (int): Review ID

        Returns:
            bool: True if deleted, False otherwise

        Example:
            >>> success = ReviewDAL.delete_review(123)
        """
        query = "DELETE FROM reviews WHERE review_id = ?"
        rows_affected = cls.execute_update(query, (review_id,))
        return rows_affected > 0

    @classmethod
    def get_resource_rating_summary(cls, resource_id: int) -> Dict[str, Any]:
        """
        Get rating summary statistics for a resource.

        Args:
            resource_id (int): Resource ID

        Returns:
            Dict: Summary with avg_rating, total_reviews, rating distribution

        Example:
            >>> summary = ReviewDAL.get_resource_rating_summary(5)
            >>> print(f"Average: {summary['avg_rating']}")
        """
        query = """
            SELECT
                AVG(rating) as avg_rating,
                COUNT(*) as total_reviews,
                SUM(CASE WHEN rating = 5 THEN 1 ELSE 0 END) as five_star,
                SUM(CASE WHEN rating = 4 THEN 1 ELSE 0 END) as four_star,
                SUM(CASE WHEN rating = 3 THEN 1 ELSE 0 END) as three_star,
                SUM(CASE WHEN rating = 2 THEN 1 ELSE 0 END) as two_star,
                SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as one_star
            FROM reviews
            WHERE resource_id = ?
              AND is_visible = 1
        """
        results = cls.execute_query(query, (resource_id,))
        return results[0] if results else {
            'avg_rating': None,
            'total_reviews': 0,
            'five_star': 0,
            'four_star': 0,
            'three_star': 0,
            'two_star': 0,
            'one_star': 0
        }


class ContentModerationDAL(BaseDAL):
    """
    Content Moderation Data Access Layer.

    Handles content reports and moderation workflows.
    """

    @classmethod
    def create_report(
        cls,
        reporter_id: int,
        target_type: str,
        target_id: int,
        reason: str
    ) -> int:
        """
        Create a content report.

        Args:
            reporter_id (int): User reporting the content
            target_type (str): Type of content ('review', 'message', 'resource', 'user')
            target_id (int): ID of the reported content
            reason (str): Reason for reporting

        Returns:
            int: New report ID

        Example:
            >>> report_id = ContentModerationDAL.create_report(
            ...     reporter_id=123,
            ...     target_type='review',
            ...     target_id=456,
            ...     reason='Contains inappropriate language'
            ... )
        """
        valid_types = ('review', 'message', 'resource', 'user')
        if target_type not in valid_types:
            raise ValueError(f"Invalid target_type: {target_type}")

        query = """
            INSERT INTO content_reports (
                reporter_id, target_type, target_id, reason,
                status, created_at
            ) VALUES (?, ?, ?, ?, 'open', datetime('now'))
        """
        report_id = cls.execute_update(query, (reporter_id, target_type, target_id, reason))

        # If this is a review, increment flagged_count
        if target_type == 'review':
            increment_query = """
                UPDATE reviews
                SET flagged_count = flagged_count + 1
                WHERE review_id = ?
            """
            cls.execute_update(increment_query, (target_id,))

        return report_id

    @classmethod
    def get_report_by_id(cls, report_id: int) -> Optional[Dict[str, Any]]:
        """
        Get report by ID with reporter information.

        Args:
            report_id (int): Report ID

        Returns:
            Optional[Dict]: Report data or None if not found

        Example:
            >>> report = ContentModerationDAL.get_report_by_id(123)
        """
        query = """
            SELECT
                cr.*,
                u.name as reporter_name,
                u.email as reporter_email,
                resolver.name as resolver_name
            FROM content_reports cr
            JOIN users u ON cr.reporter_id = u.user_id
            LEFT JOIN users resolver ON cr.resolved_by = resolver.user_id
            WHERE cr.report_id = ?
        """
        results = cls.execute_query(query, (report_id,))
        return results[0] if results else None

    @classmethod
    def get_open_reports(
        cls,
        target_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all open content reports.

        Args:
            target_type (Optional[str]): Filter by content type
            limit (int): Max results
            offset (int): Pagination offset

        Returns:
            List[Dict]: List of open reports

        Example:
            >>> open_reports = ContentModerationDAL.get_open_reports(
            ...     target_type='review'
            ... )
        """
        query = """
            SELECT
                cr.*,
                u.name as reporter_name
            FROM content_reports cr
            JOIN users u ON cr.reporter_id = u.user_id
            WHERE cr.status IN ('open', 'in_review')
        """
        params = []

        if target_type:
            query += " AND cr.target_type = ?"
            params.append(target_type)

        query += " ORDER BY cr.created_at ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        return cls.execute_query(query, tuple(params))

    @classmethod
    def update_report_status(
        cls,
        report_id: int,
        new_status: str,
        resolved_by: Optional[int] = None,
        resolution_notes: Optional[str] = None
    ) -> bool:
        """
        Update report status.

        Args:
            report_id (int): Report ID
            new_status (str): New status ('open', 'in_review', 'resolved', 'dismissed')
            resolved_by (Optional[int]): Admin/moderator user ID
            resolution_notes (Optional[str]): Resolution details

        Returns:
            bool: True if updated, False otherwise

        Example:
            >>> success = ContentModerationDAL.update_report_status(
            ...     report_id=123,
            ...     new_status='resolved',
            ...     resolved_by=456,
            ...     resolution_notes='Content removed'
            ... )
        """
        valid_statuses = ('open', 'in_review', 'resolved', 'dismissed')
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}")

        fields = ["status = ?"]
        params = [new_status]

        if new_status in ('resolved', 'dismissed'):
            fields.append("resolved_at = datetime('now')")
            if resolved_by:
                fields.append("resolved_by = ?")
                params.append(resolved_by)
            if resolution_notes:
                fields.append("resolution_notes = ?")
                params.append(resolution_notes)

        params.append(report_id)

        query = f"""
            UPDATE content_reports
            SET {', '.join(fields)}
            WHERE report_id = ?
        """

        rows_affected = cls.execute_update(query, tuple(params))
        return rows_affected > 0

    @classmethod
    def get_reports_by_target(
        cls,
        target_type: str,
        target_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get all reports for a specific piece of content.

        Args:
            target_type (str): Content type
            target_id (int): Content ID

        Returns:
            List[Dict]: List of reports

        Example:
            >>> reports = ContentModerationDAL.get_reports_by_target(
            ...     target_type='review',
            ...     target_id=123
            ... )
        """
        query = """
            SELECT
                cr.*,
                u.name as reporter_name
            FROM content_reports cr
            JOIN users u ON cr.reporter_id = u.user_id
            WHERE cr.target_type = ?
              AND cr.target_id = ?
            ORDER BY cr.created_at DESC
        """
        return cls.execute_query(query, (target_type, target_id))

    @classmethod
    def get_report_count_by_status(cls) -> Dict[str, int]:
        """
        Get count of reports grouped by status.

        Returns:
            Dict: Status counts

        Example:
            >>> counts = ContentModerationDAL.get_report_count_by_status()
            >>> print(f"Open reports: {counts.get('open', 0)}")
        """
        query = """
            SELECT status, COUNT(*) as count
            FROM content_reports
            GROUP BY status
        """
        results = cls.execute_query(query)
        return {row['status']: row['count'] for row in results}

    @classmethod
    def delete_report(cls, report_id: int) -> bool:
        """
        Delete a content report.

        Args:
            report_id (int): Report ID

        Returns:
            bool: True if deleted, False otherwise

        Example:
            >>> success = ContentModerationDAL.delete_report(123)
        """
        query = "DELETE FROM content_reports WHERE report_id = ?"
        rows_affected = cls.execute_update(query, (report_id,))
        return rows_affected > 0

    # TODO: Implement additional methods as needed:
    # - get_frequently_reported_content()
    # - get_moderation_statistics()
    # - auto_hide_heavily_flagged_content()
