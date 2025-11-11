"""
Campus Resource Hub - Models Package
====================================
MVC Role: Model Layer (data representation and business rules)
MCP Role: Data structure definitions for AI-assisted object mapping

This package contains model classes that represent database entities.

Models provide:
1. Object-oriented interface to database rows
2. Business logic and validation
3. Relationships between entities
4. Helper methods for common operations

Architecture:
- user.py: User model with Flask-Login integration
- resource.py: Resource model
- booking.py: Booking model with conflict detection
- message.py: Message model
- review.py: Review model

Models work WITH DAL (not instead of):
- DAL handles database operations (SQL)
- Models provide OO interface and business logic
"""

from .user import User
from .resource import Resource, ResourceCategory
from .booking import Booking, BookingWaitlist
from .message import Message, MessageThread, Notification
from .review import Review, ContentReport

__all__ = [
    'User',
    'Resource',
    'ResourceCategory',
    'Booking',
    'BookingWaitlist',
    'Message',
    'MessageThread',
    'Notification',
    'Review',
    'ContentReport',
]
