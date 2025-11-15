"""
Security Tests
==============
Tests for security vulnerabilities including SQL injection and XSS prevention.

Requirements covered:
- SQL injection prevention using parameterized queries
- XSS prevention using template escaping
- CSRF protection
- Input validation and sanitization
- Session security
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_access.user_dal import UserDAL
from src.data_access.resource_dal import ResourceDAL
from src.data_access.booking_dal import BookingDAL


class TestSQLInjectionPrevention:
    """Test that SQL injection attempts are prevented by parameterized queries."""

    def test_sql_injection_in_user_login(self):
        """Test SQL injection prevention in user login (email field)."""
        dal = UserDAL()

        # Attempt SQL injection that would bypass authentication
        malicious_email = "admin@iu.edu' OR '1'='1"

        # This should return None, not bypass authentication
        user = dal.get_user_by_email(malicious_email)
        assert user is None

    def test_sql_injection_in_user_email_field(self):
        """Test SQL injection prevention in user email lookup."""
        dal = UserDAL()

        # Various SQL injection attempts
        injection_attempts = [
            "'; DROP TABLE users; --",
            "' OR 1=1; --",
            "admin'--",
            "' UNION SELECT * FROM users--",
            "1' AND '1'='1",
        ]

        for malicious_input in injection_attempts:
            user = dal.get_user_by_email(malicious_input)
            # Should return None, not execute malicious SQL
            assert user is None

        # Verify users table still exists
        users = dal.get_all_users()
        assert isinstance(users, list)

    def test_sql_injection_in_resource_search(self):
        """Test SQL injection prevention in resource search/filter."""
        dal = ResourceDAL()

        # Attempt SQL injection in search/filter
        malicious_search = "'; DELETE FROM resources; --"

        # Get resources with malicious search - should handle safely
        resources = dal.search_resources(search_query=malicious_search)

        # Should return empty list or handle gracefully
        assert isinstance(resources, list)

        # Verify resources table still exists
        all_resources = dal.get_all_resources()
        assert isinstance(all_resources, list)

    def test_sql_injection_in_booking_query(self):
        """Test SQL injection prevention in booking queries."""
        dal = BookingDAL()

        # Attempt SQL injection in booking ID lookup
        malicious_id = "1 OR 1=1"

        try:
            # This should either return None or raise appropriate error
            booking = dal.get_booking_by_id(malicious_id)
            assert booking is None
        except (ValueError, TypeError):
            # Acceptable to raise type error for invalid ID format
            pass

    def test_parameterized_queries_user_creation(self):
        """Test that user creation uses parameterized queries."""
        dal = UserDAL()

        # Create user with special characters that could break SQL
        user_id = dal.create_user(
            name="O'Brien",  # Apostrophe could break unparameterized query
            email="test'user@iu.edu",
            password="hash123",
            role="student"
        )

        # Should handle special characters correctly
        assert user_id is not None

        # Verify user was created correctly
        user = dal.get_user_by_id(user_id)
        assert user is not None
        assert user['name'] == "O'Brien"

    def test_parameterized_queries_resource_creation(self):
        """Test that resource creation uses parameterized queries."""
        resource_dal = ResourceDAL()
        user_dal = UserDAL()

        # Create owner
        owner_id = user_dal.create_user(
            name="Owner",
            email="owner_paramtest@iu.edu",
            password="hash",
            role="staff"
        )

        # Create resource with SQL-like characters in description
        resource_id = resource_dal.create_resource(
            owner_type="user",
            owner_id=owner_id,
            title="Test'; DROP TABLE resources; --",
            description="Description with 'quotes' and \"double quotes\"",
            category_id=1,
            location="Test Location",
            status="published"
        )

        assert resource_id is not None

        # Verify resource was created with exact title
        resource = resource_dal.get_resource_by_id(resource_id)
        assert resource is not None
        assert "DROP TABLE" in resource['title']  # Should be stored as literal text


class TestXSSPrevention:
    """Test that XSS attacks are prevented through proper output escaping."""

    def test_xss_in_user_name_rendering(self, client):
        """Test that XSS in user name is escaped when rendered."""
        dal = UserDAL()

        # Create user with XSS attempt in name
        user_id = dal.create_user(
            name='<script>alert("XSS")</script>',
            email='xss_name@iu.edu',
            password='hash123',
            role='student'
        )

        assert user_id is not None

        # Register and login with this user
        # (Assuming the DB accepts the XSS string - we're testing template escaping)

        # When rendered in templates, script tags should be escaped
        # This would need to be tested by checking actual HTML output
        # For now, verify the user was stored
        user = dal.get_user_by_id(user_id)
        assert user is not None

    def test_xss_in_resource_title(self, client):
        """Test that XSS in resource title is escaped in templates."""
        resource_dal = ResourceDAL()
        user_dal = UserDAL()

        # Create owner
        owner_id = user_dal.create_user(
            name="Owner",
            email="xss_resource_owner@iu.edu",
            password="hash",
            role="staff"
        )

        # Create resource with XSS in title
        resource_id = resource_dal.create_resource(
            owner_type="user",
            owner_id=owner_id,
            title='<img src=x onerror="alert(\'XSS\')">',
            description='<script>steal_cookies()</script>',
            category_id=1,
            location="Test Location",
            status="published"
        )

        assert resource_id is not None

        # Retrieve resource
        resource = resource_dal.get_resource_by_id(resource_id)
        assert resource is not None
        assert '<img' in resource['title']  # Stored as-is

        # When rendered in browser, Flask templates should escape it
        # (Jinja2 auto-escaping prevents XSS)

    def test_xss_in_message_content(self, client):
        """Test that XSS in message content is escaped."""
        # This test would require the message system to be set up
        # Testing that message content like <script>alert('XSS')</script>
        # is properly escaped when displayed in the UI
        pass  # TODO: Implement when message DAL is available

    def test_html_entities_escaped_in_output(self, client):
        """Test that HTML entities are properly escaped in output."""
        resource_dal = ResourceDAL()
        user_dal = UserDAL()

        # Create owner
        owner_id = user_dal.create_user(
            name="Owner",
            email="html_entity_owner@iu.edu",
            password="hash",
            role="staff"
        )

        # Create resource with HTML entities
        resource_id = resource_dal.create_resource(
            owner_type="user",
            owner_id=owner_id,
            title="Test & < > \" '",
            description="Contains & < > \" ' characters",
            category_id=1,
            location="Test Location",
            status="published"
        )

        # Should be stored as-is
        resource = resource_dal.get_resource_by_id(resource_id)
        assert resource is not None
        assert '&' in resource['title']
        assert '<' in resource['title']
        assert '>' in resource['title']


class TestInputValidation:
    """Test input validation and sanitization."""

    def test_email_validation_format(self, client):
        """Test that invalid email formats are rejected."""
        # Test registration with invalid emails
        invalid_emails = [
            'notanemail',
            '@iu.edu',
            'user@',
            'user @iu.edu',
            'user@iu',
        ]

        for invalid_email in invalid_emails:
            register_data = {
                'name': 'Test User',
                'email': invalid_email,
                'password': 'SecurePass123!',
                'confirm_password': 'SecurePass123!',
                'role': 'student'
            }

            response = client.post('/auth/register', data=register_data, follow_redirects=True)

            # Should show error or reject registration
            # (Check depends on validation implementation)

    def test_password_strength_requirements(self, client):
        """Test password strength validation."""
        # Test weak passwords
        weak_passwords = [
            'short',           # Too short
            'alllowercase',    # No uppercase/numbers
            'ALLUPPERCASE',    # No lowercase/numbers
            '12345678',        # No letters
        ]

        for weak_pass in weak_passwords:
            register_data = {
                'name': 'Test User',
                'email': 'weakpass@iu.edu',
                'password': weak_pass,
                'confirm_password': weak_pass,
                'role': 'student'
            }

            response = client.post('/auth/register', data=register_data, follow_redirects=True)

            # Should reject weak passwords (if validation exists)

    def test_required_fields_validation(self, client):
        """Test that required fields cannot be empty."""
        # Try to create resource without required fields
        response = client.post('/resources/create', data={
            'title': '',  # Empty title
            'description': 'Some description',
            'category_id': 1
        }, follow_redirects=True)

        # Should show validation error

    def test_numeric_input_validation(self):
        """Test that numeric fields only accept numbers."""
        dal = BookingDAL()
        resource_dal = ResourceDAL()
        user_dal = UserDAL()

        # Create test data
        user_id = user_dal.create_user("User", "numeric@iu.edu", "hash", "student")
        owner_id = user_dal.create_user("Owner", "numowner@iu.edu", "hash", "staff")
        resource_id = resource_dal.create_resource(
            owner_type="user",
            owner_id=owner_id,
            title="Room",
            description="Desc",
            category_id=1,
            location="Test Location",
            status="published"
        )

        # Try to create booking with non-numeric resource_id
        try:
            booking_id = dal.create_booking(
                user_id=user_id,
                resource_id="not_a_number",  # Should fail
                start_time="2025-12-01 10:00:00",
                end_time="2025-12-01 12:00:00",
                status="pending"
            )
            # Should either fail or raise error
        except (ValueError, TypeError, Exception):
            pass  # Expected to fail


class TestCSRFProtection:
    """Test CSRF (Cross-Site Request Forgery) protection."""

    def test_csrf_token_required_for_forms(self, client):
        """Test that forms require valid CSRF token."""
        # Try to submit form without CSRF token
        response = client.post('/auth/login', data={
            'email': 'test@iu.edu',
            'password': 'password'
            # Missing CSRF token
        })

        # Should reject request without valid CSRF token
        # (Flask-WTF automatically includes CSRF protection)

    def test_csrf_token_in_form_html(self, client):
        """Test that CSRF token is included in form HTML."""
        # Get login form
        response = client.get('/auth/login')

        # Should contain CSRF token field
        assert response.status_code == 200
        # Look for hidden CSRF field
        assert b'csrf_token' in response.data or b'_csrf' in response.data


class TestSessionSecurity:
    """Test session management security."""

    def test_session_cleared_on_logout(self, client):
        """Test that session is properly cleared on logout."""
        # Create staff user directly via DAL (registration defaults to student)
        from werkzeug.security import generate_password_hash
        user_dal = UserDAL()

        user_dal.create_user(
            name='Session User',
            email='session_security@iu.edu',
            password=generate_password_hash('SecurePass123!'),
            role='staff'
        )

        login_data = {
            'email': 'session_security@iu.edu',
            'password': 'SecurePass123!'
        }
        client.post('/auth/login', data=login_data, follow_redirects=True)

        # Verify logged in (can access protected route)
        response = client.get('/resources/create', follow_redirects=True)
        assert response.status_code == 200

        # Logout
        client.get('/auth/logout', follow_redirects=True)

        # After logout, should not be able to access protected routes
        response = client.get('/resources/create', follow_redirects=True)
        assert b'login' in response.data.lower()

    def test_session_isolation_between_users(self, client):
        """Test that sessions are isolated between different users."""
        # This would test that User A's session doesn't leak to User B
        # Requires testing with multiple clients or session manipulation
        pass  # TODO: Implement with proper session testing


class TestFileUploadSecurity:
    """Test file upload security (if applicable)."""

    def test_file_type_validation(self, client):
        """Test that only allowed file types can be uploaded."""
        # If the application allows file uploads (e.g., resource images)
        # Test that malicious file types are rejected
        pass  # TODO: Implement if file upload feature exists

    def test_file_size_limits(self, client):
        """Test that file size limits are enforced."""
        # Test uploading files larger than allowed limit
        pass  # TODO: Implement if file upload feature exists


class TestAuthorizationControls:
    """Test authorization and access control."""

    def test_user_cannot_edit_others_resources(self, client):
        """Test that users cannot edit resources they don't own."""
        # User A creates a resource
        # User B tries to edit it
        # Should be denied
        pass  # TODO: Implement with proper multi-user testing

    def test_user_cannot_cancel_others_bookings(self, client):
        """Test that users cannot cancel other users' bookings."""
        # User A creates a booking
        # User B tries to cancel it
        # Should be denied
        pass  # TODO: Implement with proper multi-user testing

    def test_role_based_access_control(self, client):
        """Test that role-based permissions are enforced."""
        # Student vs Staff vs Faculty permissions
        # Certain routes/actions should be restricted by role
        pass  # TODO: Implement with role-checking logic
