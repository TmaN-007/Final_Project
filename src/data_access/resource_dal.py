"""
Resource Data Access Layer for Campus Resource Hub.

Handles all database operations for resources and resource categories.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from .base_dal import BaseDAL


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
        requires_approval: bool = False
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

        Returns:
            New resource_id
        """
        query = """
            INSERT INTO resources (
                owner_type, owner_id, title, description, category_id, location,
                capacity, status, availability_mode, requires_approval,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """
        return cls.execute_insert(query, (
            owner_type, owner_id, title, description, category_id, location,
            capacity, status, availability_mode, int(requires_approval)
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

        if owner_type and owner_id:
            query += " AND r.owner_type = ? AND r.owner_id = ?"
            params.extend([owner_type, owner_id])

        query += " ORDER BY r.created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        return cls.execute_query(query, tuple(params))

    @classmethod
    def search_resources(
        cls,
        search_query: Optional[str] = None,
        category_id: Optional[int] = None,
        location: Optional[str] = None,
        min_capacity: Optional[int] = None,
        availability_mode: Optional[str] = None,
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

        # Sort order
        sort_map = {
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
        requires_approval: Optional[bool] = None
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

    @classmethod
    def delete_resource(cls, resource_id: int) -> int:
        """
        Delete a resource (CASCADE will delete related records).

        Args:
            resource_id: Resource ID

        Returns:
            Number of rows affected
        """
        query = "DELETE FROM resources WHERE resource_id = ?"
        return cls.execute_update(query, (resource_id,))

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
        return cls.execute_insert(query, (resource_id, image_path, int(is_primary), sort_order))

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
