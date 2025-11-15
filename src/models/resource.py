"""
Resource Model for Campus Resource Hub.

Represents a resource that can be booked (room, equipment, service, etc.).
"""

from typing import Dict, Any, Optional, List
from datetime import datetime


class Resource:
    """
    Resource model representing a bookable campus resource.

    Attributes:
        resource_id: Unique identifier
        owner_type: 'user' or 'group'
        owner_id: ID of the owner (user_id or group_id)
        title: Resource title
        description: Detailed description
        category_id: Category identifier
        location: Physical location
        capacity: Maximum capacity (None for single items)
        status: 'draft', 'published', or 'archived'
        availability_mode: 'rules', 'open', or 'by-request'
        requires_approval: Whether bookings need approval
        images: Comma-separated image paths or JSON array
        availability_rules: JSON blob describing recurring availability
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    def __init__(self, resource_data: Dict[str, Any]):
        """
        Initialize Resource from database row.

        Args:
            resource_data: Dictionary containing resource fields from database
        """
        self._resource_id = resource_data['resource_id']
        self._owner_type = resource_data['owner_type']
        self._owner_id = resource_data['owner_id']
        self._title = resource_data['title']
        self._description = resource_data.get('description')
        self._category_id = resource_data.get('category_id')
        self._location = resource_data.get('location')
        self._capacity = resource_data.get('capacity')
        self._status = resource_data['status']
        self._availability_mode = resource_data['availability_mode']
        self._requires_approval = bool(resource_data.get('requires_approval', False))
        self._images = resource_data.get('images')
        self._availability_rules = resource_data.get('availability_rules')
        self._created_at = resource_data.get('created_at')
        self._updated_at = resource_data.get('updated_at')

        # Additional properties that might be joined from other tables
        self._category_name = resource_data.get('category_name')
        self._owner_name = resource_data.get('owner_name')
        self._avg_rating = resource_data.get('avg_rating')
        self._review_count = resource_data.get('review_count', 0)
        self._primary_image = resource_data.get('primary_image')

    # Property getters and setters
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
    def owner_type(self) -> str:
        """Get owner type."""
        return self._owner_type

    @owner_type.setter
    def owner_type(self, value: str):
        """Set owner type with validation."""
        valid_types = ('user', 'group')
        if value not in valid_types:
            raise ValueError(f"Owner type must be one of {valid_types}")
        self._owner_type = value

    @property
    def owner_id(self) -> int:
        """Get owner ID."""
        return self._owner_id

    @owner_id.setter
    def owner_id(self, value: int):
        """Set owner ID."""
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Owner ID must be a positive integer")
        self._owner_id = value

    @property
    def title(self) -> str:
        """Get resource title."""
        return self._title

    @title.setter
    def title(self, value: str):
        """Set resource title with validation."""
        if not value or not value.strip():
            raise ValueError("Title cannot be empty")
        self._title = value.strip()

    @property
    def description(self) -> Optional[str]:
        """Get resource description."""
        return self._description

    @description.setter
    def description(self, value: Optional[str]):
        """Set resource description."""
        self._description = value.strip() if value else None

    @property
    def category_id(self) -> Optional[int]:
        """Get category ID."""
        return self._category_id

    @category_id.setter
    def category_id(self, value: Optional[int]):
        """Set category ID."""
        self._category_id = value

    @property
    def location(self) -> Optional[str]:
        """Get location."""
        return self._location

    @location.setter
    def location(self, value: Optional[str]):
        """Set location."""
        self._location = value.strip() if value else None

    @property
    def capacity(self) -> Optional[int]:
        """Get capacity."""
        return self._capacity

    @capacity.setter
    def capacity(self, value: Optional[int]):
        """Set capacity with validation."""
        if value is not None and (not isinstance(value, int) or value < 0):
            raise ValueError("Capacity must be a non-negative integer")
        self._capacity = value

    @property
    def status(self) -> str:
        """Get status."""
        return self._status

    @status.setter
    def status(self, value: str):
        """Set status with validation."""
        valid_statuses = ('draft', 'published', 'archived')
        if value not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        self._status = value

    @property
    def availability_mode(self) -> str:
        """Get availability mode."""
        return self._availability_mode

    @availability_mode.setter
    def availability_mode(self, value: str):
        """Set availability mode with validation."""
        valid_modes = ('rules', 'open', 'by-request')
        if value not in valid_modes:
            raise ValueError(f"Availability mode must be one of {valid_modes}")
        self._availability_mode = value

    @property
    def requires_approval(self) -> bool:
        """Get requires approval flag."""
        return self._requires_approval

    @requires_approval.setter
    def requires_approval(self, value: bool):
        """Set requires approval flag."""
        self._requires_approval = bool(value)

    @property
    def images(self) -> Optional[str]:
        """Get images."""
        return self._images

    @images.setter
    def images(self, value: Optional[str]):
        """Set images."""
        self._images = value

    @property
    def availability_rules(self) -> Optional[str]:
        """Get availability rules."""
        return self._availability_rules

    @availability_rules.setter
    def availability_rules(self, value: Optional[str]):
        """Set availability rules."""
        self._availability_rules = value

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
    def category_name(self) -> Optional[str]:
        """Get category name."""
        return self._category_name

    @category_name.setter
    def category_name(self, value: Optional[str]):
        """Set category name."""
        self._category_name = value

    @property
    def owner_name(self) -> Optional[str]:
        """Get owner name."""
        return self._owner_name

    @owner_name.setter
    def owner_name(self, value: Optional[str]):
        """Set owner name."""
        self._owner_name = value

    @property
    def avg_rating(self) -> Optional[float]:
        """Get average rating."""
        return self._avg_rating

    @avg_rating.setter
    def avg_rating(self, value: Optional[float]):
        """Set average rating."""
        self._avg_rating = value

    @property
    def review_count(self) -> int:
        """Get review count."""
        return self._review_count

    @review_count.setter
    def review_count(self, value: int):
        """Set review count."""
        self._review_count = int(value) if value else 0

    @property
    def primary_image(self) -> Optional[str]:
        """Get primary image."""
        return self._primary_image

    @primary_image.setter
    def primary_image(self, value: Optional[str]):
        """Set primary image."""
        self._primary_image = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert resource to dictionary for JSON serialization.

        Returns:
            Dictionary representation of resource
        """
        return {
            'resource_id': self.resource_id,
            'owner_type': self.owner_type,
            'owner_id': self.owner_id,
            'title': self.title,
            'description': self.description,
            'category_id': self.category_id,
            'category_name': self.category_name,
            'location': self.location,
            'capacity': self.capacity,
            'status': self.status,
            'availability_mode': self.availability_mode,
            'requires_approval': self.requires_approval,
            'images': self.images,
            'availability_rules': self.availability_rules,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'owner_name': self.owner_name,
            'avg_rating': self.avg_rating,
            'review_count': self.review_count,
            'primary_image': self.primary_image
        }

    @property
    def is_published(self) -> bool:
        """Check if resource is published."""
        return self._status == 'published'

    @property
    def is_draft(self) -> bool:
        """Check if resource is draft."""
        return self._status == 'draft'

    @property
    def is_archived(self) -> bool:
        """Check if resource is archived."""
        return self._status == 'archived'

    @property
    def is_bookable(self) -> bool:
        """Check if resource accepts bookings."""
        return self._availability_mode in ('rules', 'by-request')

    @property
    def is_open_access(self) -> bool:
        """Check if resource is open access (no booking needed)."""
        return self._availability_mode == 'open'

    @property
    def has_capacity_limit(self) -> bool:
        """Check if resource has a capacity limit."""
        return self._capacity is not None and self._capacity > 0

    def is_owned_by_user(self, user_id: int) -> bool:
        """
        Check if resource is owned by specific user.

        Args:
            user_id: User ID to check

        Returns:
            True if user owns this resource
        """
        return self._owner_type == 'user' and self._owner_id == user_id

    def is_owned_by_group(self, group_id: int) -> bool:
        """
        Check if resource is owned by specific group.

        Args:
            group_id: Group ID to check

        Returns:
            True if group owns this resource
        """
        return self._owner_type == 'group' and self._owner_id == group_id

    def get_display_capacity(self) -> str:
        """
        Get human-readable capacity string.

        Returns:
            Formatted capacity string
        """
        if not self.has_capacity_limit:
            return 'No limit'
        return f'{self._capacity} person{"s" if self._capacity != 1 else ""}'

    def get_status_badge_class(self) -> str:
        """
        Get Bootstrap badge class for status.

        Returns:
            Bootstrap badge class name
        """
        status_classes = {
            'draft': 'secondary',
            'published': 'success',
            'archived': 'warning'
        }
        return status_classes.get(self._status, 'secondary')

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f'<Resource {self._resource_id}: {self._title}>'


class ResourceCategory:
    """Resource category model."""

    def __init__(self, category_data: Dict[str, Any]):
        """Initialize category from database row."""
        self._category_id = category_data['category_id']
        self._name = category_data['name']
        self._description = category_data.get('description')
        self._icon = category_data.get('icon')
        self._created_at = category_data.get('created_at')

    # Property getters and setters
    @property
    def category_id(self) -> int:
        """Get category ID."""
        return self._category_id

    @category_id.setter
    def category_id(self, value: int):
        """Set category ID."""
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Category ID must be a positive integer")
        self._category_id = value

    @property
    def name(self) -> str:
        """Get category name."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Set category name with validation."""
        if not value or not value.strip():
            raise ValueError("Category name cannot be empty")
        self._name = value.strip()

    @property
    def description(self) -> Optional[str]:
        """Get category description."""
        return self._description

    @description.setter
    def description(self, value: Optional[str]):
        """Set category description."""
        self._description = value.strip() if value else None

    @property
    def icon(self) -> Optional[str]:
        """Get category icon."""
        return self._icon

    @icon.setter
    def icon(self, value: Optional[str]):
        """Set category icon."""
        self._icon = value

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
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'created_at': self.created_at
        }

    def __repr__(self) -> str:
        """String representation."""
        return f'<ResourceCategory {self._category_id}: {self._name}>'
