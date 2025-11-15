# Campus Resource Hub - API Documentation

> Complete reference for all server-side endpoints

**Base URL:** `http://localhost:5000` (development)
**Authentication:** Session-based with Flask-Login
**CSRF Protection:** All POST/PUT/DELETE requests require CSRF token

---

## Table of Contents

1. [Authentication](#authentication)
2. [Resources](#resources)
3. [Bookings](#bookings)
4. [Messages](#messages)
5. [Reviews](#reviews)
6. [Admin](#admin)
7. [Error Responses](#error-responses)

---

## Authentication

### Register User
Create a new user account.

**Endpoint:** `POST /auth/register`
**Authentication:** None
**Request Body:**
```json
{
  "name": "John Doe",
  "email": "jdoe@iu.edu",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!"
}
```

**Validation:**
- Name: 2-100 characters, letters/spaces/hyphens/apostrophes only
- Email: Valid format, RFC 5322 compliant
- Password: 8-128 chars, uppercase, lowercase, digit, special character

**Success Response:** `302 Redirect`
```
Location: /auth/login
Flash: "Registration successful! Please log in."
```

**Error Response:** `200 OK` (re-renders form)
```
Flash: "Email already registered." | "Password must contain at least one uppercase letter."
```

**Implementation:** [src/controllers/auth_controller.py:25](src/controllers/auth_controller.py#L25)

---

### Login
Obtain user session.

**Endpoint:** `POST /auth/login`
**Authentication:** None
**Request Body:**
```json
{
  "email": "jdoe@iu.edu",
  "password": "SecurePass123!",
  "remember_me": true
}
```

**Success Response:** `302 Redirect`
```
Location: /dashboard
Set-Cookie: session=...; HttpOnly; Secure
Set-Cookie: remember_token=...; Max-Age=31536000; HttpOnly; Secure (if remember_me=true)
```

**Error Response:** `200 OK` (re-renders form)
```
Flash: "Invalid email or password."
```

**Implementation:** [src/controllers/auth_controller.py:65](src/controllers/auth_controller.py#L65)

---

### Logout
Destroy user session.

**Endpoint:** `GET /auth/logout`
**Authentication:** Required
**Success Response:** `302 Redirect`
```
Location: /
Flash: "You have been logged out."
```

**Implementation:** [src/controllers/auth_controller.py:110](src/controllers/auth_controller.py#L110)

---

### Edit Profile
Update user name and email.

**Endpoint:** `POST /auth/edit-profile`
**Authentication:** Required
**Request Body:**
```json
{
  "name": "Jane Doe",
  "email": "janedoe@iu.edu"
}
```

**Success Response:** `302 Redirect`
```
Location: /dashboard
Flash: "Profile updated successfully!"
```

**Implementation:** [src/controllers/auth_controller.py:125](src/controllers/auth_controller.py#L125)

---

## Resources

### List/Search Resources
Retrieve paginated list of resources with optional filters.

**Endpoint:** `GET /resources/`
**Authentication:** Required
**Query Parameters:**
```
?search=projector          # Search in title/description
&category=2                # Filter by category ID
&status=published          # Filter by status (published/draft)
&page=1                    # Page number (default: 1)
&per_page=12               # Items per page (default: 12)
```

**Success Response:** `200 OK`
```html
<!-- Rendered template with resources -->
<!-- Context variables: -->
{
  "resources": [
    {
      "resource_id": 1,
      "title": "Conference Room A",
      "description": "Large meeting space",
      "status": "published",
      "owner_id": 5,
      "category_id": 2,
      "images": "/static/uploads/room_a.jpg",
      "created_at": "2025-11-10 14:30:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 12,
    "total": 45,
    "pages": 4
  }
}
```

**Implementation:** [src/controllers/resource_controller.py:30](src/controllers/resource_controller.py#L30)

---

### Get Resource Detail
Retrieve detailed information about a specific resource.

**Endpoint:** `GET /resources/<int:resource_id>`
**Authentication:** Required
**URL Parameters:**
- `resource_id` (integer): Resource ID

**Success Response:** `200 OK`
```html
<!-- Rendered template with resource details -->
<!-- Context includes: -->
{
  "resource": {
    "resource_id": 1,
    "title": "Conference Room A",
    "description": "Large meeting space with AV equipment",
    "status": "published",
    "hourly_rate": 25.00,
    "owner": {
      "user_id": 5,
      "name": "John Doe",
      "email": "jdoe@iu.edu"
    },
    "category": {
      "category_id": 2,
      "name": "Meeting Rooms"
    },
    "images": "/static/uploads/room_a.jpg",
    "avg_rating": 4.5,
    "total_reviews": 12
  },
  "reviews": [...],
  "available_slots": [...]
}
```

**Error Response:** `404 Not Found`
```
Flash: "Resource not found."
Location: /resources/
```

**Implementation:** [src/controllers/resource_controller.py:85](src/controllers/resource_controller.py#L85)

---

### Create Resource
Create a new resource listing.

**Endpoint:** `POST /resources/create`
**Authentication:** Required
**Content-Type:** `multipart/form-data`
**Request Body:**
```json
{
  "title": "Conference Room B",
  "description": "Small meeting room for 6 people",
  "category_id": 2,
  "hourly_rate": 15.00,
  "daily_rate": 100.00,
  "location": "Library, 3rd Floor",
  "capacity": 6,
  "status": "published",
  "image": "<file upload>"
}
```

**File Upload Validation:**
- Allowed extensions: jpg, jpeg, png, gif
- Max size: 5MB
- Path traversal prevention

**Success Response:** `302 Redirect`
```
Location: /resources/<new_resource_id>
Flash: "Resource created successfully!"
```

**Error Response:** `200 OK` (re-renders form)
```
Flash: "File type not allowed." | "Image file required."
```

**Implementation:** [src/controllers/resource_controller.py:120](src/controllers/resource_controller.py#L120)

---

### Update Resource
Update an existing resource.

**Endpoint:** `POST /resources/<int:resource_id>/edit`
**Authentication:** Required (owner or admin)
**Content-Type:** `multipart/form-data`
**Request Body:**
```json
{
  "title": "Updated Conference Room B",
  "description": "Updated description",
  "category_id": 2,
  "hourly_rate": 20.00,
  "status": "published",
  "image": "<optional file upload>"
}
```

**Success Response:** `302 Redirect`
```
Location: /resources/<resource_id>
Flash: "Resource updated successfully!"
```

**Error Response:** `403 Forbidden`
```
Flash: "You don't have permission to edit this resource."
Location: /resources/<resource_id>
```

**Implementation:** [src/controllers/resource_controller.py:180](src/controllers/resource_controller.py#L180)

---

### Delete Resource
Delete a resource (soft delete - sets status to 'archived').

**Endpoint:** `POST /resources/<int:resource_id>/delete`
**Authentication:** Required (owner or admin)
**Request Body:**
```json
{
  "confirm": "true"
}
```

**Success Response:** `302 Redirect`
```
Location: /resources/my-resources
Flash: "Resource deleted successfully."
```

**Error Response:** `403 Forbidden`
```
Flash: "You don't have permission to delete this resource."
```

**Implementation:** [src/controllers/resource_controller.py:245](src/controllers/resource_controller.py#L245)

---

## Bookings

### Request Booking
Create a new booking request.

**Endpoint:** `POST /bookings/create`
**Authentication:** Required
**Request Body:**
```json
{
  "resource_id": 1,
  "start_datetime": "2025-11-20T14:00:00",
  "end_datetime": "2025-11-20T16:00:00",
  "purpose": "Team meeting",
  "notes": "Need projector setup"
}
```

**Validation:**
- Start time must be in the future
- End time must be after start time
- No conflicts with existing bookings
- Resource must be available

**Success Response:** `302 Redirect`
```
Location: /bookings/<new_booking_id>
Flash: "Booking request submitted! Awaiting approval."
System Notification: Sent to resource owner
```

**Error Response:** `200 OK` (re-renders form)
```
Flash: "Time slot already booked." | "Invalid time range."
```

**Implementation:** [src/controllers/booking_controller.py:45](src/controllers/booking_controller.py#L45)

---

### Get Booking Detail
Retrieve booking details.

**Endpoint:** `GET /bookings/<int:booking_id>`
**Authentication:** Required (participant or admin)
**Success Response:** `200 OK`
```html
<!-- Rendered template with booking details -->
{
  "booking": {
    "booking_id": 1,
    "resource": {
      "resource_id": 1,
      "title": "Conference Room A"
    },
    "user": {
      "user_id": 3,
      "name": "Jane Smith"
    },
    "start_datetime": "2025-11-20T14:00:00",
    "end_datetime": "2025-11-20T16:00:00",
    "status": "pending",
    "purpose": "Team meeting",
    "total_cost": 50.00
  }
}
```

**Implementation:** [src/controllers/booking_controller.py:110](src/controllers/booking_controller.py#L110)

---

### Approve Booking
Approve a pending booking (resource owner or admin only).

**Endpoint:** `POST /bookings/<int:booking_id>/approve`
**Authentication:** Required (resource owner or admin)
**Request Body:**
```json
{
  "action": "approve"
}
```

**Success Response:** `302 Redirect`
```
Location: /bookings/<booking_id>
Flash: "Booking approved successfully!"
System Notification: Sent to booking requester
```

**Error Response:** `403 Forbidden`
```
Flash: "You don't have permission to approve this booking."
```

**Implementation:** [src/controllers/booking_controller.py:165](src/controllers/booking_controller.py#L165)

---

### Reject Booking
Reject a pending booking.

**Endpoint:** `POST /bookings/<int:booking_id>/reject`
**Authentication:** Required (resource owner or admin)
**Request Body:**
```json
{
  "action": "reject",
  "reason": "Resource unavailable on that date"
}
```

**Success Response:** `302 Redirect`
```
Location: /bookings/<booking_id>
Flash: "Booking rejected."
System Notification: Sent to requester with reason
```

**Implementation:** [src/controllers/booking_controller.py:195](src/controllers/booking_controller.py#L195)

---

### Cancel Booking
Cancel an approved booking.

**Endpoint:** `POST /bookings/<int:booking_id>/cancel`
**Authentication:** Required (booking owner, resource owner, or admin)
**Request Body:**
```json
{
  "reason": "Schedule change"
}
```

**Success Response:** `302 Redirect`
```
Location: /bookings/<booking_id>
Flash: "Booking cancelled."
System Notifications: Sent to both parties
```

**Implementation:** [src/controllers/booking_controller.py:220](src/controllers/booking_controller.py#L220)

---

## Messages

### Send Message
Create a new message in a thread.

**Endpoint:** `POST /messages/send`
**Authentication:** Required
**Request Body:**
```json
{
  "thread_id": 5,
  "content": "Hi, I'd like to book the conference room for next Tuesday.",
  "resource_id": 1
}
```

**Thread Creation:**
If `thread_id` is not provided and `resource_id` is:
- Creates new thread automatically
- Adds sender and resource owner as participants

**Success Response:** `302 Redirect`
```
Location: /messages/thread/<thread_id>
Flash: "Message sent!"
```

**Validation:**
- Content: 1-2000 characters
- XSS protection via sanitization

**Implementation:** [src/controllers/message_controller.py:65](src/controllers/message_controller.py#L65)

---

### View Thread
Display messages in a thread.

**Endpoint:** `GET /messages/thread/<int:thread_id>`
**Authentication:** Required (thread participant only)
**Success Response:** `200 OK`
```html
<!-- Rendered template with messages -->
{
  "thread": {
    "thread_id": 5,
    "subject": "Booking Inquiry - Conference Room A",
    "created_at": "2025-11-15 10:00:00"
  },
  "messages": [
    {
      "message_id": 1,
      "sender": {
        "user_id": 3,
        "name": "Jane Smith"
      },
      "content": "Hi, I'd like to book the conference room...",
      "sent_at": "2025-11-15 10:00:00",
      "is_read": true
    }
  ],
  "participants": [...]
}
```

**Implementation:** [src/controllers/message_controller.py:110](src/controllers/message_controller.py#L110)

---

## Reviews

### Submit Review
Create a review for a resource.

**Endpoint:** `POST /reviews/create`
**Authentication:** Required (must have completed booking)
**Request Body:**
```json
{
  "resource_id": 1,
  "booking_id": 12,
  "rating": 5,
  "comment": "Excellent facility with great equipment!"
}
```

**Validation:**
- Rating: 1-5 (integer)
- Comment: Max 1000 characters
- User must have completed booking for this resource
- One review per booking

**Success Response:** `302 Redirect`
```
Location: /resources/<resource_id>
Flash: "Review submitted successfully!"
```

**Error Response:** `400 Bad Request`
```
Flash: "You can only review resources you've used." | "You already reviewed this booking."
```

**Implementation:** [src/controllers/review_controller.py:35](src/controllers/review_controller.py#L35)

---

### Reply to Review
Resource owner can reply to a review.

**Endpoint:** `POST /reviews/<int:review_id>/reply`
**Authentication:** Required (resource owner only)
**Request Body:**
```json
{
  "reply": "Thank you for your feedback! We're glad you enjoyed the facility."
}
```

**Success Response:** `302 Redirect`
```
Location: /resources/<resource_id>
Flash: "Reply added successfully!"
```

**Implementation:** [src/controllers/review_controller.py:85](src/controllers/review_controller.py#L85)

---

## Admin

### Admin Dashboard
View system-wide statistics.

**Endpoint:** `GET /admin/dashboard`
**Authentication:** Required (admin role)
**Success Response:** `200 OK`
```html
<!-- Rendered template with stats -->
{
  "stats": {
    "total_users": 150,
    "total_resources": 45,
    "total_bookings": 320,
    "pending_approvals": 8,
    "revenue_this_month": 2500.00,
    "active_users_today": 23
  },
  "recent_activity": [...],
  "top_resources": [...]
}
```

**Implementation:** [src/controllers/admin_controller.py:25](src/controllers/admin_controller.py#L25)

---

### Manage Users
List and manage all users.

**Endpoint:** `GET /admin/users`
**Authentication:** Required (admin role)
**Query Parameters:**
```
?search=john               # Search by name/email
&role=student              # Filter by role
&status=active             # Filter by status
&page=1
```

**Success Response:** `200 OK`
```html
<!-- Rendered user list with pagination -->
{
  "users": [
    {
      "user_id": 3,
      "name": "Jane Smith",
      "email": "jsmith@iu.edu",
      "role": "student",
      "is_active": true,
      "created_at": "2025-11-01 08:00:00",
      "last_login": "2025-11-15 14:23:00"
    }
  ],
  "pagination": {...}
}
```

**Implementation:** [src/controllers/admin_controller.py:65](src/controllers/admin_controller.py#L65)

---

### Update User Role
Change user's role.

**Endpoint:** `POST /admin/users/<int:user_id>/role`
**Authentication:** Required (admin role)
**Request Body:**
```json
{
  "role": "staff"
}
```

**Allowed Roles:**
- `student`
- `staff`
- `admin`

**Success Response:** `302 Redirect`
```
Location: /admin/users
Flash: "User role updated to staff."
Audit Log: Created
```

**Implementation:** [src/controllers/admin_controller.py:145](src/controllers/admin_controller.py#L145)

---

### Deactivate User
Suspend user account.

**Endpoint:** `POST /admin/users/<int:user_id>/deactivate`
**Authentication:** Required (admin role)
**Request Body:**
```json
{
  "reason": "Violation of terms of service"
}
```

**Success Response:** `302 Redirect`
```
Location: /admin/users
Flash: "User account deactivated."
Audit Log: Created with reason
```

**Implementation:** [src/controllers/admin_controller.py:175](src/controllers/admin_controller.py#L175)

---

## Error Responses

### Standard Error Format

**400 Bad Request**
```json
{
  "error": "Invalid request data",
  "details": "Field 'rating' must be between 1 and 5"
}
```

**401 Unauthorized**
```
Redirect: /auth/login
Flash: "Please log in to access this page."
```

**403 Forbidden**
```
Flash: "You don't have permission to perform this action."
Status: 403
```

**404 Not Found**
```
Flash: "Resource not found."
Redirect: Previous page or /dashboard
```

**500 Internal Server Error**
```html
<!-- Rendered error template -->
"An unexpected error occurred. Please try again later."
Logged: Full stack trace in logs/error.log
```

---

## Security Notes

### CSRF Protection
All state-changing requests (POST/PUT/DELETE) require CSRF token:

```html
<form method="POST">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
  <!-- form fields -->
</form>
```

### Input Validation
- Server-side validation on all inputs
- XSS prevention via Bleach sanitization
- SQL injection prevention via parameterized queries
- File upload validation (type, size, path traversal)

### Rate Limiting
- Login attempts: 5 per 15 minutes per IP
- Message sending: 20 per hour per user
- Review submission: 10 per day per user

### Session Management
- HttpOnly cookies (prevents XSS access)
- Secure flag (HTTPS only in production)
- SameSite=Lax (CSRF protection)
- 24-hour session timeout
- 365-day Remember Me token

---

## Testing Examples

### cURL Examples

**Register User:**
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@iu.edu",
    "password": "TestPass123!",
    "confirm_password": "TestPass123!"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email": "test@iu.edu",
    "password": "TestPass123!"
  }'
```

**Create Resource:**
```bash
curl -X POST http://localhost:5000/resources/create \
  -b cookies.txt \
  -F "title=Test Room" \
  -F "description=A test meeting room" \
  -F "category_id=2" \
  -F "hourly_rate=25.00" \
  -F "status=published" \
  -F "image=@/path/to/image.jpg"
```

**Search Resources:**
```bash
curl -X GET "http://localhost:5000/resources/?search=projector&category=1" \
  -b cookies.txt
```

---

## Development Notes

**Architecture:** Flask MVC with Data Access Layer (DAL)
**Database:** SQLite3 (30 tables)
**Template Engine:** Jinja2
**Frontend:** Bootstrap 5 + Custom CSS
**Authentication:** Flask-Login (session-based)

**Code Locations:**
- Controllers: [src/controllers/](src/controllers/)
- Data Access Layer: [src/data_access/](src/data_access/)
- Models: [src/models/](src/models/)
- Templates: [src/templates/](src/templates/)

**Security Implementation:**
- CSRF: [src/app.py](src/app.py) (Flask-WTF)
- Input Validation: [src/utils/validators.py](src/utils/validators.py)
- XSS Protection: [src/utils/security.py](src/utils/security.py)
- Password Hashing: bcrypt with 12 rounds

---

**Last Updated:** 2025-11-14
**API Version:** 1.0.0
**Project Status:** Production-Ready
