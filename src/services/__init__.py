"""
Campus Resource Hub - Services Package
======================================
MVC Role: Business Logic Layer
MCP Role: Service orchestration for AI-assisted business rules

This package contains service classes that implement business logic.

Services layer sits between controllers and DAL:
- Controllers call services (not DAL directly for complex operations)
- Services orchestrate multiple DAL operations
- Services implement business rules and validations

Architecture:
- auth_service.py: Authentication and authorization logic
- booking_service.py: Booking conflict detection and management
- notification_service.py: Email and notification sending
- search_service.py: Advanced search and filtering
- ai_service.py: AI concierge and assistant features
- calendar_service.py: External calendar integration
"""

__all__ = []
