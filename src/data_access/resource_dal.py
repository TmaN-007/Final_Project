"""
Resource Data Access Layer for Campus Resource Hub.

Handles all database operations for resources and resource categories.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from .base_dal import BaseDAL
import logging

logger = logging.getLogger(__name__)


class ResourceDAL(BaseDAL):
    """Data Access Layer for resources."""

    @classmethod
    def create_resource(
        cls,
        owner_type: str,
        owner_id: int,
        title: str,
        description: str,
        category_id: int,
        location: str,
        capacity: Optional[int] = None,
        status: str = 'draft',
        availability_mode: str = 'rules',
        requires_approval: bool = False,
        images: Optional[str] = None,
        availability_rules: Optional[str] = None
    ) -> int:
        """
        Create a new resource.

        Args:
            owner_type: 'user' or 'group'
            owner_id: ID of owner
            title: Resource title
            description: Resource description
            category_id: Category ID
            location: Physical location
            capacity: Max capacity (None for single items)
            status: 'draft', 'published', or 'archived'
            availability_mode: 'rules', 'open', or 'by-request'
            requires_approval: Whether bookings need approval
            images: Comma-separated image paths or JSON array
            availability_rules: JSON blob describing recurring availability

        Returns:
            New resource_id
        """
        query = """
            INSERT INTO resources (
                owner_type, owner_id, title, description, category_id, location,
                capacity, status, availability_mode, requires_approval, images,
                availability_rules, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """
        return cls.execute_update(query, (
            owner_type, owner_id, title, description, category_id, location,
            capacity, status, availability_mode, int(requires_approval), images,
            availability_rules
        ))

    @classmethod
    def get_resource_by_id(cls, resource_id: int) -> Optional[Dict[str, Any]]:
        """
        Get resource by ID with category and owner information.

        Args:
            resource_id: Resource ID

        Returns:
            Resource dict or None
        """
        query = """
            SELECT
                r.*,
                rc.name as category_name,
                CASE
                    WHEN r.owner_type = 'user' THEN u.name
                    WHEN r.owner_type = 'group' THEN g.name
                    ELSE NULL
                END as owner_name,
                (SELECT AVG(rating) FROM reviews WHERE resource_id = r.resource_id AND is_visible = 1) as avg_rating,
                (SELECT COUNT(*) FROM reviews WHERE resource_id = r.resource_id AND is_visible = 1) as review_count,
                (SELECT image_path FROM resource_images WHERE resource_id = r.resource_id AND is_primary = 1 LIMIT 1) as primary_image
            FROM resources r
            LEFT JOIN resource_categories rc ON r.category_id = rc.category_id
            LEFT JOIN users u ON r.owner_type = 'user' AND r.owner_id = u.user_id
            LEFT JOIN groups g ON r.owner_type = 'group' AND r.owner_id = g.group_id
            WHERE r.resource_id = ?
        """
        results = cls.execute_query(query, (resource_id,))
        return results[0] if results else None

    @classmethod
    def get_all_resources(
        cls,
        status: Optional[str] = None,
        category_id: Optional[int] = None,
        owner_type: Optional[str] = None,
        owner_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all resources with filters.

        Args:
            status: Filter by status ('published', 'draft', 'archived')
            category_id: Filter by category
            owner_type: Filter by owner type
            owner_id: Filter by owner ID
            limit: Max results
            offset: Pagination offset

        Returns:
            List of resource dicts
        """
        query = """
            SELECT
                r.*,
                rc.name as category_name,
                CASE
                    WHEN r.owner_type = 'user' THEN u.name
                    WHEN r.owner_type = 'group' THEN g.name
                    ELSE NULL
                END as owner_name,
                (SELECT AVG(rating) FROM reviews WHERE resource_id = r.resource_id AND is_visible = 1) as avg_rating,
                (SELECT COUNT(*) FROM reviews WHERE resource_id = r.resource_id AND is_visible = 1) as review_count,
                (SELECT image_path FROM resource_images WHERE resource_id = r.resource_id AND is_primary = 1 LIMIT 1) as primary_image
            FROM resources r
            LEFT JOIN resource_categories rc ON r.category_id = rc.category_id
            LEFT JOIN users u ON r.owner_type = 'user' AND r.owner_id = u.user_id
            LEFT JOIN groups g ON r.owner_type = 'group' AND r.owner_id = g.group_id
            WHERE 1=1
        """
        params = []

        if status:
            query += " AND r.status = ?"
            params.append(status)

        if category_id:
            query += " AND r.category_id = ?"
            params.append(category_id)

        if owner_type and owner_id is not None:
            query += " AND r.owner_type = ? AND r.owner_id = ?"
            params.extend([owner_type, owner_id])

        query += " ORDER BY r.created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"ResourceDAL.get_all_resources: query={query}, params={params}")

        results = cls.execute_query(query, tuple(params))
        logger.info(f"ResourceDAL.get_all_resources: returned {len(results)} results")
        return results

    @classmethod
    def search_resources(
        cls,
        search_query: Optional[str] = None,
        category_id: Optional[int] = None,
        location: Optional[str] = None,
        min_capacity: Optional[int] = None,
        availability_mode: Optional[str] = None,
        availability_date: Optional[str] = None,
        availability_time: Optional[str] = None,
        sort_by: str = 'created_desc',
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search resources with multiple filters.

        Args:
            search_query: Text search in title/description
            category_id: Filter by category
            location: Filter by location (partial match)
            min_capacity: Minimum capacity
            availability_mode: Filter by availability mode
            availability_date: Filter by available date (YYYY-MM-DD)
            availability_time: Filter by available time (HH:MM)
            sort_by: Sort order (created_desc, created_asc, title_asc, title_desc, rating_desc, capacity_desc)
            limit: Max results
            offset: Pagination offset

        Returns:
            List of matching resource dicts
        """
        query = """
            SELECT
                r.*,
                rc.name as category_name,
                CASE
                    WHEN r.owner_type = 'user' THEN u.name
                    WHEN r.owner_type = 'group' THEN g.name
                    ELSE NULL
                END as owner_name,
                (SELECT AVG(rating) FROM reviews WHERE resource_id = r.resource_id AND is_visible = 1) as avg_rating,
                (SELECT COUNT(*) FROM reviews WHERE resource_id = r.resource_id AND is_visible = 1) as review_count,
                (SELECT COUNT(*) FROM bookings WHERE resource_id = r.resource_id AND status IN ('confirmed', 'pending')) as booking_count,
                (SELECT image_path FROM resource_images WHERE resource_id = r.resource_id AND is_primary = 1 LIMIT 1) as primary_image
            FROM resources r
            LEFT JOIN resource_categories rc ON r.category_id = rc.category_id
            LEFT JOIN users u ON r.owner_type = 'user' AND r.owner_id = u.user_id
            LEFT JOIN groups g ON r.owner_type = 'group' AND r.owner_id = g.group_id
            WHERE r.status = 'published'
        """
        params = []

        if search_query:
            query += " AND (r.title LIKE ? OR r.description LIKE ?)"
            search_pattern = f'%{search_query}%'
            params.extend([search_pattern, search_pattern])

        if category_id:
            query += " AND r.category_id = ?"
            params.append(category_id)

        if location:
            query += " AND r.location LIKE ?"
            params.append(f'%{location}%')

        if min_capacity:
            query += " AND r.capacity >= ?"
            params.append(min_capacity)

        if availability_mode:
            query += " AND r.availability_mode = ?"
            params.append(availability_mode)

        # Filter by availability (check for conflicting bookings)
        if availability_date and availability_time:
            # Combine date and time into datetime format
            datetime_str = f"{availability_date} {availability_time}:00"

            # Exclude resources that have confirmed/pending bookings at this date/time
            query += """
                AND r.resource_id NOT IN (
                    SELECT b.resource_id
                    FROM bookings b
                    WHERE b.status IN ('confirmed', 'pending')
                    AND ? BETWEEN b.start_datetime AND b.end_datetime
                )
            """
            params.append(datetime_str)

        # Sort order
        sort_map = {
            'recent': 'r.created_at DESC',
            'most_booked': 'booking_count DESC NULLS LAST',
            'top_rated': 'avg_rating DESC NULLS LAST',
            'created_desc': 'r.created_at DESC',
            'created_asc': 'r.created_at ASC',
            'title_asc': 'r.title ASC',
            'title_desc': 'r.title DESC',
            'rating_desc': 'avg_rating DESC NULLS LAST',
            'capacity_desc': 'r.capacity DESC NULLS LAST'
        }
        order_by = sort_map.get(sort_by, 'r.created_at DESC')
        query += f" ORDER BY {order_by} LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        return cls.execute_query(query, tuple(params))

    @classmethod
    def count_search_resources(
        cls,
        search_query: Optional[str] = None,
        category_id: Optional[int] = None,
        location: Optional[str] = None,
        min_capacity: Optional[int] = None,
        availability_mode: Optional[str] = None,
        availability_date: Optional[str] = None,
        availability_time: Optional[str] = None
    ) -> int:
        """
        Count resources matching search criteria.
        Uses same filters as search_resources() but returns count instead of results.

        Args:
            search_query: Search term for title/description
            category_id: Filter by category
            location: Filter by location (partial match)
            min_capacity: Minimum capacity required
            availability_mode: Filter by availability mode
            availability_date: Check availability on date (YYYY-MM-DD)
            availability_time: Check availability at time (HH:MM)

        Returns:
            int: Total count of matching resources
        """
        query = """
            SELECT COUNT(DISTINCT r.resource_id) as count
            FROM resources r
            WHERE r.status = 'published'
        """
        params = []

        if search_query:
            query += " AND (r.title LIKE ? OR r.description LIKE ?)"
            search_pattern = f'%{search_query}%'
            params.extend([search_pattern, search_pattern])

        if category_id:
            query += " AND r.category_id = ?"
            params.append(category_id)

        if location:
            query += " AND r.location LIKE ?"
            params.append(f'%{location}%')

        if min_capacity:
            query += " AND r.capacity >= ?"
            params.append(min_capacity)

        if availability_mode:
            query += " AND r.availability_mode = ?"
            params.append(availability_mode)

        if availability_date and availability_time:
            datetime_str = f"{availability_date} {availability_time}:00"
            query += """
                AND r.resource_id NOT IN (
                    SELECT b.resource_id
                    FROM bookings b
                    WHERE b.status IN ('confirmed', 'pending')
                    AND ? BETWEEN b.start_datetime AND b.end_datetime
                )
            """
            params.append(datetime_str)

        results = cls.execute_query(query, tuple(params))
        return results[0]['count'] if results else 0

    @classmethod
    def update_resource(
        cls,
        resource_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        category_id: Optional[int] = None,
        location: Optional[str] = None,
        capacity: Optional[int] = None,
        status: Optional[str] = None,
        availability_mode: Optional[str] = None,
        requires_approval: Optional[bool] = None,
        images: Optional[str] = None,
        availability_rules: Optional[str] = None
    ) -> int:
        """
        Update resource fields.

        Args:
            resource_id: Resource ID
            title: New title (optional)
            description: New description (optional)
            category_id: New category (optional)
            location: New location (optional)
            capacity: New capacity (optional)
            status: New status (optional)
            availability_mode: New availability mode (optional)
            requires_approval: New approval requirement (optional)
            images: New images (optional)
            availability_rules: New availability rules (optional)

        Returns:
            Number of rows affected
        """
        fields = []
        params = []

        if title is not None:
            fields.append("title = ?")
            params.append(title)
        if description is not None:
            fields.append("description = ?")
            params.append(description)
        if category_id is not None:
            fields.append("category_id = ?")
            params.append(category_id)
        if location is not None:
            fields.append("location = ?")
            params.append(location)
        if capacity is not None:
            fields.append("capacity = ?")
            params.append(capacity)
        if status is not None:
            fields.append("status = ?")
            params.append(status)
        if availability_mode is not None:
            fields.append("availability_mode = ?")
            params.append(availability_mode)
        if requires_approval is not None:
            fields.append("requires_approval = ?")
            params.append(int(requires_approval))
        if images is not None:
            fields.append("images = ?")
            params.append(images)
        if availability_rules is not None:
            fields.append("availability_rules = ?")
            params.append(availability_rules)

        if not fields:
            return 0

        fields.append("updated_at = datetime('now')")
        params.append(resource_id)

        query = f"""
            UPDATE resources
            SET {', '.join(fields)}
            WHERE resource_id = ?
        """

        return cls.execute_update(query, tuple(params))

    # ===== RESOURCE CATEGORIES =====

    @classmethod
    def get_all_categories(cls) -> List[Dict[str, Any]]:
        """
        Get all resource categories.

        Returns:
            List of category dicts
        """
        query = """
            SELECT category_id, name, description, icon, created_at
            FROM resource_categories
            ORDER BY name ASC
        """
        return cls.execute_query(query)

    @classmethod
    def get_category_by_id(cls, category_id: int) -> Optional[Dict[str, Any]]:
        """
        Get category by ID.

        Args:
            category_id: Category ID

        Returns:
            Category dict or None
        """
        query = """
            SELECT category_id, name, description, icon, created_at
            FROM resource_categories
            WHERE category_id = ?
        """
        results = cls.execute_query(query, (category_id,))
        return results[0] if results else None

    # ===== RESOURCE IMAGES =====

    @classmethod
    def add_resource_image(
        cls,
        resource_id: int,
        image_path: str,
        is_primary: bool = False,
        sort_order: int = 0
    ) -> int:
        """
        Add an image to a resource.

        Args:
            resource_id: Resource ID
            image_path: Path to image file
            is_primary: Whether this is the primary image
            sort_order: Display order

        Returns:
            New image_id
        """
        # If setting as primary, unset other primary images
        if is_primary:
            cls.execute_update(
                "UPDATE resource_images SET is_primary = 0 WHERE resource_id = ?",
                (resource_id,)
            )

        query = """
            INSERT INTO resource_images (resource_id, image_path, is_primary, sort_order, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        """
        return cls.execute_update(query, (resource_id, image_path, int(is_primary), sort_order))

    @classmethod
    def get_resource_images(cls, resource_id: int) -> List[Dict[str, Any]]:
        """
        Get all images for a resource.

        Args:
            resource_id: Resource ID

        Returns:
            List of image dicts
        """
        query = """
            SELECT image_id, resource_id, image_path, is_primary, sort_order, created_at
            FROM resource_images
            WHERE resource_id = ?
            ORDER BY is_primary DESC, sort_order ASC
        """
        return cls.execute_query(query, (resource_id,))

    @classmethod
    def delete_resource_image(cls, image_id: int) -> int:
        """
        Delete a resource image.

        Args:
            image_id: Image ID

        Returns:
            Number of rows affected
        """
        query = "DELETE FROM resource_images WHERE image_id = ?"
        return cls.execute_update(query, (image_id,))

    # =============================================================================
    # ADMIN PANEL METHODS
    # =============================================================================

    @classmethod
    def count_all_resources(cls) -> int:
        """
        Count total number of resources.

        Returns:
            Total count of resources
        """
        query = "SELECT COUNT(*) as count FROM resources"
        result = cls.execute_query(query)
        return result[0]['count'] if result else 0

    @classmethod
    def count_pending_resources(cls) -> int:
        """
        Count resources with pending or draft status.

        Returns:
            Count of pending/draft resources
        """
        query = "SELECT COUNT(*) as count FROM resources WHERE status IN ('draft', 'pending')"
        result = cls.execute_query(query)
        return result[0]['count'] if result else 0

    @classmethod
    def get_recent_resources(cls, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recently created resources.

        Args:
            limit: Maximum number of resources to return

        Returns:
            List of resource dicts
        """
        query = """
            SELECT r.resource_id, r.title, c.name as category, r.status, r.owner_id,
                   r.created_at, u.name as owner_name
            FROM resources r
            LEFT JOIN users u ON r.owner_id = u.user_id
            LEFT JOIN resource_categories c ON r.category_id = c.category_id
            ORDER BY r.created_at DESC
            LIMIT ?
        """
        return cls.execute_query(query, (limit,))

    @classmethod
    def get_all_resources_paginated(cls, page: int = 1, per_page: int = 20,
                                     status_filter: str = '', category_filter: str = '',
                                     search_query: str = '', owner_filter: str = '') -> Dict[str, Any]:
        """
        Get paginated list of resources with optional filters.

        Args:
            page: Page number (1-indexed)
            per_page: Number of items per page
            status_filter: Filter by status ('draft', 'published', 'archived')
            category_filter: Filter by category
            search_query: Search in title or description
            owner_filter: Filter by owner name

        Returns:
            Dict with 'resources' list and 'pagination' info
        """
        offset = (page - 1) * per_page

        # Build WHERE clause dynamically
        where_clauses = []
        params = []

        if status_filter:
            where_clauses.append("r.status = ?")
            params.append(status_filter)

        if category_filter:
            where_clauses.append("c.name = ?")
            params.append(category_filter)

        if search_query:
            where_clauses.append("(r.title LIKE ? OR r.description LIKE ?)")
            search_pattern = f'%{search_query}%'
            params.extend([search_pattern, search_pattern])

        if owner_filter:
            where_clauses.append("u.name LIKE ?")
            owner_pattern = f'%{owner_filter}%'
            params.append(owner_pattern)

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        # Get total count
        count_query = f"""
            SELECT COUNT(*) as count
            FROM resources r
            LEFT JOIN users u ON r.owner_id = u.user_id
            LEFT JOIN resource_categories c ON r.category_id = c.category_id
            WHERE {where_sql}
        """
        total_result = cls.execute_query(count_query, tuple(params))
        total_count = total_result[0]['count'] if total_result else 0

        # Get resources
        query = f"""
            SELECT r.resource_id, r.title, c.name as category, r.status, r.owner_id,
                   r.created_at, r.updated_at, u.name as owner_name,
                   (SELECT image_path FROM resource_images
                    WHERE resource_id = r.resource_id AND is_primary = 1
                    LIMIT 1) as primary_image
            FROM resources r
            LEFT JOIN users u ON r.owner_id = u.user_id
            LEFT JOIN resource_categories c ON r.category_id = c.category_id
            WHERE {where_sql}
            ORDER BY r.created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([per_page, offset])
        resources = cls.execute_query(query, tuple(params))

        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page

        return {
            'resources': resources,
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
    def update_resource_status(cls, resource_id: int, status: str) -> bool:
        """
        Update resource status (admin only).

        Args:
            resource_id: Resource ID
            status: New status ('draft', 'published', 'archived')

        Returns:
            True if update successful, False otherwise
        """
        query = """
            UPDATE resources
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE resource_id = ?
        """
        rows_affected = cls.execute_update(query, (status, resource_id))
        return rows_affected > 0

    @classmethod
    def get_category_availability_counts(cls) -> Dict[int, int]:
        """
        Get the count of available resources for each category.
        A resource is considered "available" if it's published and not currently booked
        (doesn't have an active approved booking where current time is between start and end).

        Returns:
            Dict mapping category_id to count of available resources
        """
        query = """
            SELECT
                r.category_id,
                COUNT(DISTINCT r.resource_id) as available_count
            FROM resources r
            WHERE r.status = 'published'
              AND r.resource_id NOT IN (
                  SELECT DISTINCT b.resource_id
                  FROM bookings b
                  WHERE b.status = 'approved'
                    AND datetime('now') BETWEEN datetime(b.start_datetime) AND datetime(b.end_datetime)
              )
            GROUP BY r.category_id
        """
        results = cls.execute_query(query, ())

        # Convert to dict for easy lookup
        availability_dict = {}
        for row in results:
            availability_dict[row['category_id']] = row['available_count']

        return availability_dict

    @classmethod
    def delete_resource(cls, resource_id: int) -> bool:
        """
        Delete a resource (admin only).
        Also deletes all associated records from related tables.

        Args:
            resource_id: Resource ID

        Returns:
            True if deletion successful, False otherwise
        """
        try:
            # Delete in order to respect foreign key constraints
            # Since foreign keys are disabled, we must manually delete from all related tables

            # 1. Delete reviews (references bookings and resources)
            cls.execute_update("DELETE FROM reviews WHERE resource_id = ?", (resource_id,))

            # 2. Delete bookings (other tables reference this)
            cls.execute_update("DELETE FROM bookings WHERE resource_id = ?", (resource_id,))

            # 3. Delete booking waitlist
            cls.execute_update("DELETE FROM booking_waitlist WHERE resource_id = ?", (resource_id,))

            # 4. Delete resource images
            cls.execute_update("DELETE FROM resource_images WHERE resource_id = ?", (resource_id,))

            # 5. Delete resource equipment
            cls.execute_update("DELETE FROM resource_equipment WHERE resource_id = ?", (resource_id,))

            # 6. Delete resource availability rules (table)
            cls.execute_update("DELETE FROM resource_availability_rules WHERE resource_id = ?", (resource_id,))

            # 7. Delete resource unavailable slots
            cls.execute_update("DELETE FROM resource_unavailable_slots WHERE resource_id = ?", (resource_id,))

            # 8. Delete resource analytics
            cls.execute_update("DELETE FROM resource_analytics WHERE resource_id = ?", (resource_id,))

            # 9. Update message threads to set resource_id to NULL
            cls.execute_update("UPDATE message_threads SET resource_id = NULL WHERE resource_id = ?", (resource_id,))

            # 10. Finally delete the resource itself
            rows_affected = cls.execute_update("DELETE FROM resources WHERE resource_id = ?", (resource_id,))

            return rows_affected > 0
        except Exception as e:
            logger.error(f"Error deleting resource {resource_id}: {str(e)}", exc_info=True)
            return False

    @classmethod
    def get_featured_resources(cls, user_id: int, limit: int = 4) -> List[Dict[str, Any]]:
        """
        Get featured resources for the home page.
        Returns 2 highest-rated and 2 most-booked resources.
        Prioritizes categories the user has previously booked from.

        Args:
            user_id: User ID to personalize recommendations
            limit: Total number of featured resources (default 4)

        Returns:
            List of featured resource dicts
        """
        # Get categories the user has booked from before
        user_categories_query = """
            SELECT DISTINCT r.category_id
            FROM bookings b
            JOIN resources r ON b.resource_id = r.resource_id
            WHERE b.requester_id = ?
            ORDER BY b.created_at DESC
            LIMIT 3
        """
        user_categories = cls.execute_query(user_categories_query, (user_id,))
        user_category_ids = [cat['category_id'] for cat in user_categories]

        # Build category filter
        category_filter = ""
        if user_category_ids:
            placeholders = ','.join('?' * len(user_category_ids))
            category_filter = f"AND r.category_id IN ({placeholders})"

        # Get 2 highest-rated resources (prioritizing user's categories)
        top_rated_query = f"""
            SELECT
                r.*,
                rc.name as category_name,
                (SELECT AVG(rating) FROM reviews WHERE resource_id = r.resource_id AND is_visible = 1) as avg_rating,
                (SELECT COUNT(*) FROM reviews WHERE resource_id = r.resource_id AND is_visible = 1) as review_count,
                (SELECT image_path FROM resource_images WHERE resource_id = r.resource_id AND is_primary = 1 LIMIT 1) as primary_image
            FROM resources r
            LEFT JOIN resource_categories rc ON r.category_id = rc.category_id
            WHERE r.status = 'published'
              {category_filter}
            ORDER BY avg_rating DESC NULLS LAST, review_count DESC
            LIMIT 2
        """

        if user_category_ids:
            top_rated = cls.execute_query(top_rated_query, tuple(user_category_ids))
        else:
            # If no user categories, get globally top-rated
            top_rated_query = top_rated_query.replace(category_filter, "")
            top_rated = cls.execute_query(top_rated_query, ())

        # Get 2 most-booked resources (prioritizing user's categories, excluding already selected)
        excluded_ids = [r['resource_id'] for r in top_rated]
        exclusion_filter = ""
        if excluded_ids:
            exclusion_placeholders = ','.join('?' * len(excluded_ids))
            exclusion_filter = f"AND r.resource_id NOT IN ({exclusion_placeholders})"

        most_booked_query = f"""
            SELECT
                r.*,
                rc.name as category_name,
                COUNT(b.booking_id) as booking_count,
                (SELECT AVG(rating) FROM reviews WHERE resource_id = r.resource_id AND is_visible = 1) as avg_rating,
                (SELECT COUNT(*) FROM reviews WHERE resource_id = r.resource_id AND is_visible = 1) as review_count,
                (SELECT image_path FROM resource_images WHERE resource_id = r.resource_id AND is_primary = 1 LIMIT 1) as primary_image
            FROM resources r
            LEFT JOIN resource_categories rc ON r.category_id = rc.category_id
            LEFT JOIN bookings b ON r.resource_id = b.resource_id AND b.status IN ('approved', 'completed')
            WHERE r.status = 'published'
              {category_filter}
              {exclusion_filter}
            GROUP BY r.resource_id
            ORDER BY booking_count DESC, r.created_at DESC
            LIMIT 2
        """

        most_booked_params = []
        if user_category_ids:
            most_booked_params.extend(user_category_ids)
        if excluded_ids:
            most_booked_params.extend(excluded_ids)

        if most_booked_params:
            most_booked = cls.execute_query(most_booked_query, tuple(most_booked_params))
        else:
            # If no filters, remove the filter placeholders
            most_booked_query = most_booked_query.replace(category_filter, "").replace(exclusion_filter, "")
            most_booked = cls.execute_query(most_booked_query, ())

        # Combine and return
        featured = top_rated + most_booked
        return featured[:limit]
