"""
Campus Resource Hub - Data Access Layer (DAL)
=============================================
MVC Role: Data Access Layer (separates data operations from controllers)
MCP Role: Database interaction boundary for AI-assisted query generation

This package encapsulates ALL database operations.

KEY PRINCIPLE: Controllers should NEVER write raw SQL.
All database interactions MUST go through DAL classes.

Each DAL class provides:
1. CRUD operations (Create, Read, Update, Delete)
2. Specialized queries for business logic
3. Transaction management
4. Error handling

Architecture:
- base_dal.py: Common database connection and utilities
- user_dal.py: User management operations
- resource_dal.py: Resource CRUD and search
- booking_dal.py: Booking management and conflict detection
- message_dal.py: Messaging operations
- review_dal.py: Review and rating operations
- analytics_dal.py: Reporting and analytics queries

Security:
- ALL queries use parameterized statements (prevents SQL injection)
- Input validation at DAL level
- Connection pooling for performance
"""

__all__ = [
    'BaseDAL',
    'UserDAL',
    # Add other DAL classes as they are implemented
]
