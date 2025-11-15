# Campus Resource Hub - Acceptance Criteria
**AI-First Development Project**
**Last Updated:** 2025-11-14

## Purpose
This document defines acceptance criteria for key features. AI assistants reference these criteria to ensure generated code meets project requirements.

---

## 1. User Authentication

### Registration
**Given** a new user visits the registration page
**When** they submit valid credentials
**Then**
- Account is created with hashed password
- User receives email verification (if configured)
- User is redirected to login page
- Password must meet strength requirements (8+ chars, uppercase, lowercase, digit, special char)

**Security Requirements:**
- Passwords hashed with bcrypt (12 rounds minimum)
- Email validation (RFC 5322 compliant)
- CSRF protection on form submission
- XSS prevention via input sanitization

---

## 2. Resource Browsing

### Search and Filter
**Given** a logged-in user is on the resources page
**When** they enter a search term or select filters
**Then**
- Results update dynamically
- Show only published resources
- Display resource image, title, category, rating
- Pagination with 12 items per page

**Performance:**
- Search results load within 500ms
- Database queries use indexes

---

## 3. Booking System

### Request Booking
**Given** a user views an available resource
**When** they select a time slot and submit booking request
**Then**
- System checks for conflicts
- Booking created with 'pending' status
- Resource owner receives notification
- User sees confirmation message

**Validation:**
- Start time must be in the future
- End time must be after start time
- No overlapping bookings for same resource
- User cannot book their own resources

### Approve Booking
**Given** a resource owner receives a booking request
**When** they approve the request
**Then**
- Booking status changes to 'approved'
- Requester receives notification
- Time slot marked as unavailable
- Calendar updates in real-time

---

## 4. Messaging System

### Send Message
**Given** two users need to communicate about a resource
**When** they send messages
**Then**
- Thread created if doesn't exist
- Message content sanitized for XSS
- Sender and recipient marked as participants
- Unread count updated

**Character Limits:**
- Subject: 200 characters max
- Message: 2000 characters max

---

## 5. Reviews and Ratings

### Submit Review
**Given** a user has completed a booking
**When** they submit a review
**Then**
- Review associated with resource and booking
- Rating validated (1-5 integer)
- Average rating recalculated
- Resource owner can reply to review

**Requirements:**
- One review per booking
- Must have completed booking
- Review visible to all users
- Owner reply shows "Response from owner"

---

## 6. Admin Panel

### User Management
**Given** an admin accesses the admin panel
**When** they view user list  **Then**
- All users displayed with role badges
- Can search by name/email
- Can filter by role or status
- Can change user roles
- Can deactivate accounts

**Audit Trail:**
- All admin actions logged
- Logs include: admin user, target user, action, timestamp, reason

### Resource Moderation
**Given** an admin reviews reported content
**When** they take action
**Then**
- Can mark resource as 'draft' (unpublish)
- Can delete resource (archive)
- Owner notified of moderation action
- Moderation reason recorded

---

## 7. AI Context Grounding (This Document!)

### Personalized Welcome
**Given** an AI assistant loads user context
**When** generating welcome message
**Then**
- References user role from `/docs/context/DT/personas.json`
- Suggests typical resources for that role
- Mentions relevant pain points
- Provides role-specific quick actions

**Example:**
> "Welcome back, Sarah! As a **student**, I can help you find **study rooms** and **AV equipment**. I see there are 5 study rooms available during your preferred time. Would you like to book one?"

**Context Sources:**
- `/docs/context/DT/personas.json` - User role characteristics
- `/docs/context/APA/acceptance_criteria.md` - Feature requirements
- `/docs/context/shared/` - System-wide rules

---

## 8. Security Requirements

### Input Validation
**Given** any user input
**When** submitted to server
**Then**
- Server-side validation always runs
- HTML stripped or sanitized
- SQL injection prevented (parameterized queries)
- File uploads validated (type, size, path)

### Session Management
**Given** a user logs in
**When** session created
**Then**
- HttpOnly cookie set
- Secure flag enabled in production
- SameSite=Lax for CSRF protection
- 24-hour session timeout
- Remember Me: 365-day token with security flags

---

## 9. Accessibility

**Given** any page in the application
**When** rendered
**Then**
- Semantic HTML5 elements used
- Form labels properly associated
- Keyboard navigation supported
- Color contrast ratio ≥ 4.5:1
- Alt text on all images

---

## Testing Notes for AI Agents

When generating code for these features, ensure:
1. Server-side validation **always** runs (never trust client)
2. Database queries use **parameterized** statements
3. User input **sanitized** before storage or display
4. Error messages are **generic** (security best practice)
5. Success actions include **user feedback** (flash messages)

---

**AI Usage:**
This document serves as ground truth for feature implementation. When an AI generates code for Campus Resource Hub, it should reference these criteria to ensure compliance with project requirements.
