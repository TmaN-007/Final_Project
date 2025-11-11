"""
Campus Resource Hub - Controllers Package
=========================================
MVC Role: Controller Layer
MCP Role: Request handling and routing coordination

This package contains Flask blueprints that act as controllers in the MVC pattern.
Each controller handles routes for a specific feature area.

Controllers are responsible for:
1. Receiving HTTP requests
2. Validating input (with forms)
3. Calling business logic (services) or data access (DAL)
4. Returning HTTP responses (templates or JSON)

IMPORTANT: Controllers should NOT contain:
- Raw SQL queries (use DAL)
- Complex business logic (use services)
- Direct database access

Architecture:
- auth_controller.py: Login, registration, password reset
- resource_controller.py: Resource CRUD operations
- booking_controller.py: Booking management
- message_controller.py: Messaging system
- review_controller.py: Reviews and ratings
- admin_controller.py: Admin dashboard and management
- api_controller.py: RESTful API endpoints
"""

__all__ = [
    'main_bp',
    'auth_bp',
    # Add other blueprints here as they are implemented
]
