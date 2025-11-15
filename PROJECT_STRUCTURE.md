# Campus Resource Hub - Project Structure & Tech Stack Analysis

## Tech Stack (Required by Project Brief)

### Backend
- **Python 3.10+** with **Flask**
- **SQLite** for local development (PostgreSQL optional for deployment)
- **Flask-Login** / Flask-Security for authentication
- **bcrypt** for password hashing
- **Flask-WTF** for CSRF protection

### Frontend
- **Jinja2 templates** (Flask)
- **Bootstrap 5** for responsive UI

### Testing
- **pytest** for unit and integration tests

### Version Control
- **GitHub** with branching and Pull Requests

### Architecture Pattern
- **Model-View-Controller (MVC)**
  - Model Layer: ORM/SQL classes
  - View Layer: HTML/Jinja templates
  - Controller Layer: Flask routes/blueprints
  - Data Access Layer (DAL): Encapsulated CRUD operations

---

## Recommended Project Directory Structure

```
Final_Project/
│
├── .prompt/                          # AI-First Development (Required)
│   ├── dev_notes.md                 # Log of AI interactions
│   └── golden_prompts.md            # High-impact prompts
│
├── docs/                            # Context Pack (Required)
│   ├── context/
│   │   ├── APA/                    # Agility, Processes & Automation artifacts
│   │   ├── DT/                     # Design Thinking artifacts
│   │   ├── PM/                     # Product Management artifacts
│   │   └── shared/                 # Common items (personas, glossary, OKRs)
│   ├── PRD.md                      # Product Requirements Document
│   ├── wireframes/                 # UI wireframes
│   └── API.md                      # API documentation
│
├── src/                             # Main application code
│   ├── __init__.py
│   │
│   ├── static/                      # Static assets
│   │   ├── css/
│   │   │   ├── main.css
│   │   │   ├── home.css            # Includes theme-aware icon styles
│   │   │   └── admin.css
│   │   ├── js/
│   │   │   ├── main.js
│   │   │   ├── home.js             # Theme toggle functionality
│   │   │   ├── booking_calendar.js
│   │   │   └── form_validation.js
│   │   ├── images/
│   │   │   └── icons/              # ✅ Theme-aware PNG icons (Added 2025-11-11)
│   │   │       ├── Study_Room_Icon_Light.png
│   │   │       ├── Study_Room_Icon_Dark.png
│   │   │       ├── AV_Equip_Light.png
│   │   │       ├── AV_Equip_Dark.png
│   │   │       ├── Lab_Light.png
│   │   │       ├── Lab_Dark.png
│   │   │       ├── Event_Light.png
│   │   │       ├── Event_Dark.png
│   │   │       ├── Computer_light.png
│   │   │       └── Computer_Dark.png
│   │   └── uploads/                # User-uploaded files (secure)
│   │
│   ├── controllers/                 # Flask routes and blueprints
│   │   ├── __init__.py
│   │   ├── auth_controller.py      # /auth/* routes
│   │   ├── resource_controller.py  # /resources/* routes
│   │   ├── booking_controller.py   # /bookings/* routes
│   │   ├── message_controller.py   # /messages/* routes
│   │   ├── review_controller.py    # /reviews/* routes
│   │   ├── admin_controller.py     # /admin/* routes
│   │   └── api_controller.py       # /api/* RESTful endpoints
│   │
│   ├── models/                      # ORM/Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── resource.py
│   │   ├── booking.py
│   │   ├── message.py
│   │   ├── review.py
│   │   └── analytics.py
│   │
│   ├── data_access/                 # Data Access Layer (Required)
│   │   ├── __init__.py
│   │   ├── base_dal.py             # Base CRUD operations
│   │   ├── user_dal.py
│   │   ├── resource_dal.py
│   │   ├── booking_dal.py
│   │   ├── message_dal.py
│   │   ├── review_dal.py
│   │   └── analytics_dal.py
│   │
│   ├── services/                    # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py         # Authentication & authorization
│   │   ├── booking_service.py      # Booking conflict detection
│   │   ├── notification_service.py # Email/notification sending
│   │   ├── search_service.py       # Search and filtering
│   │   ├── ai_service.py           # AI concierge/assistant
│   │   └── calendar_service.py     # Calendar integration
│   │
│   ├── utils/                       # Utility functions
│   │   ├── __init__.py
│   │   ├── validators.py           # Server-side validation
│   │   ├── security.py             # XSS, CSRF, injection protection
│   │   ├── file_upload.py          # Secure file handling
│   │   └── helpers.py              # General helper functions
│   │
│   ├── forms/                       # Flask-WTF forms
│   │   ├── __init__.py
│   │   ├── auth_forms.py
│   │   ├── resource_forms.py
│   │   ├── booking_forms.py
│   │   └── review_forms.py
│   │
│   ├── views/                       # HTML/Jinja templates
│   │   ├── layout.html             # Base template
│   │   ├── components/             # Reusable components
│   │   │   ├── navbar.html
│   │   │   ├── footer.html
│   │   │   ├── resource_card.html
│   │   │   └── booking_calendar.html
│   │   │
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   └── reset_password.html
│   │   │
│   │   ├── resources/
│   │   │   ├── index.html          # Browse/search
│   │   │   ├── detail.html         # Resource detail page
│   │   │   ├── create.html
│   │   │   └── edit.html
│   │   │
│   │   ├── bookings/
│   │   │   ├── create.html
│   │   │   ├── detail.html
│   │   │   └── my_bookings.html
│   │   │
│   │   ├── dashboard/
│   │   │   ├── user_dashboard.html
│   │   │   └── admin_dashboard.html
│   │   │
│   │   ├── messages/
│   │   │   ├── inbox.html
│   │   │   └── thread.html
│   │   │
│   │   └── home.html               # Landing page
│   │
│   ├── static/                      # Static assets
│   │   ├── css/
│   │   │   ├── main.css
│   │   │   └── admin.css
│   │   ├── js/
│   │   │   ├── main.js
│   │   │   ├── booking_calendar.js
│   │   │   └── form_validation.js
│   │   ├── images/
│   │   └── uploads/                # User-uploaded files (secure)
│   │
│   ├── config.py                    # Configuration management
│   └── app.py                       # Flask app initialization
│
├── tests/                           # Test suite (Required)
│   ├── __init__.py
│   ├── conftest.py                 # Pytest fixtures
│   ├── unit/
│   │   ├── test_user_dal.py
│   │   ├── test_booking_service.py
│   │   └── test_validators.py
│   ├── integration/
│   │   ├── test_auth_flow.py
│   │   ├── test_booking_flow.py
│   │   └── test_api_endpoints.py
│   └── ai_eval/                    # AI feature validation (Optional)
│       └── test_ai_concierge.py
│
├── migrations/                      # Database migrations (if using Flask-Migrate)
│   └── versions/
│
├── deployment/                      # Deployment scripts (Optional)
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── aws/
│
├── .gitignore
├── requirements.txt                 # Python dependencies
├── README.md                        # Setup and run instructions
├── schema.sql                       # Database schema (✓ Created)
├── DATABASE_TABLES.txt              # Table documentation (✓ Created)
├── ERD_DIAGRAM.md                   # ERD visualization (✓ Created)
├── campus_resource_hub.db           # SQLite database (✓ Created)
└── run.py                           # Application entry point
```

---

## Required Python Dependencies (requirements.txt)

```txt
# Core Framework
Flask==3.0.0
python-dotenv==1.0.0

# Database
Flask-SQLAlchemy==3.1.1  # ORM (optional - can use raw SQL)

# Authentication & Security
Flask-Login==0.6.3
Flask-WTF==1.2.1
bcrypt==4.1.2
PyJWT==2.8.0

# Email
Flask-Mail==0.9.1

# Forms & Validation
WTForms==3.1.1
email-validator==2.1.0

# Testing
pytest==7.4.3
pytest-flask==1.3.0
pytest-cov==4.1.0

# AI Features (Optional - for advanced features)
openai==1.6.1
anthropic==0.8.1

# Calendar Integration (Advanced Feature)
google-auth==2.25.2
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.111.0

# Utilities
python-dateutil==2.8.2
Pillow==10.1.0  # Image handling
bleach==6.1.0   # XSS protection

# Development
black==23.12.1
flake8==7.0.0
```

---

## MVC Architecture Implementation

### 1. Model Layer (models/)

**IMPORTANT: All models use property-based encapsulation (Updated 2025-11-11)**

```python
# models/user.py
class User:
    """
    Represents a user in the system.
    Maps to users table.

    All attributes are private (underscore prefix) with @property getters/setters.
    Setters include validation appropriate to each field.
    """

    def __init__(self, user_data: dict):
        """Initialize with private attributes."""
        self._user_id = user_data['user_id']
        self._email = user_data['email']
        # ... other private attributes

    @property
    def email(self) -> str:
        """Get email address."""
        return self._email

    @email.setter
    def email(self, value: str):
        """Set email with validation."""
        if not value or '@' not in value:
            raise ValueError("Invalid email format")
        self._email = value.lower()
```

**Model Classes with Property Encapsulation:**
- ✅ User (9 properties) - Email validation, role validation
- ✅ Resource (15+ properties) - Capacity validation, status validation
- ✅ ResourceCategory (5 properties) - Basic getters/setters
- ✅ Booking (12+ properties) - DateTime logic validation
- ✅ BookingWaitlist (9 properties) - Position validation
- ✅ Review (13 properties) - Rating range 1-5 validation
- ✅ ContentReport (10 properties) - Status validation
- ✅ Message (9 properties) - Content non-empty validation
- ✅ MessageThread (10 properties) - Participant validation
- ✅ Notification (9 properties) - Type validation

**Total: 80+ properties across 8 model classes**

### 2. Data Access Layer (data_access/)
```python
# data_access/user_dal.py
class UserDAL:
    """
    Encapsulates all database operations for users.
    Controllers should NEVER write raw SQL.
    """
    @staticmethod
    def create_user(name, email, password_hash, role):
        # INSERT INTO users...

    @staticmethod
    def get_user_by_email(email):
        # SELECT * FROM users WHERE email = ?
```

### 3. Controller Layer (controllers/)
```python
# controllers/auth_controller.py
from flask import Blueprint, request, render_template
from data_access.user_dal import UserDAL
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Handle login logic
    # Uses UserDAL for database
    # Uses AuthService for business logic
    # Returns template (View)
```

### 4. View Layer (views/)
```html
<!-- views/auth/login.html -->
{% extends "layout.html" %}
{% block content %}
<form method="POST">
    {{ form.csrf_token }}
    <!-- Login form -->
</form>
{% endblock %}
```

---

## Key Features Implementation Checklist

### Phase 1: Foundation (Days 1-3)
- [x] Database schema created
- [x] Project structure setup
- [x] Flask app initialization
- [x] Base templates (layout, navbar, footer)
- [x] Configuration management

### Phase 2: Authentication (Days 4-6)
- [x] User registration with email verification (forms + DAL ready)
- [x] Login/logout with sessions (forms ready, needs controller integration)
- [x] Password reset flow (forms + DAL ready)
- [x] CSRF protection (Flask-WTF enabled)
- [ ] Role-based access control decorators (TODO: implement)

### Phase 3: Resources (Days 7-9)
- [x] Resource CRUD operations (ResourceDAL complete)
- [x] Image upload handling (forms + DAL methods ready)
- [x] Category filtering (search functionality in DAL)
- [x] Search functionality (ResourceDAL.search_resources complete)
- [ ] Availability rules management (TODO: controller + templates)

### Phase 4: Bookings (Days 10-12)
- [x] Booking creation with conflict detection (forms + models ready)
- [ ] Calendar view (TODO: BookingDAL + templates)
- [x] Approval workflow (forms ready)
- [x] Waitlist system (Advanced) (forms + models ready)
- [ ] Email notifications (TODO: email service integration)

### Phase 5: Communication (Days 13-14)
- [x] Message threads (models ready)
- [x] Notifications system (models ready)
- [x] Reviews and ratings (forms + models ready)

### Phase 6: Admin & AI (Days 15-16)
- [ ] Admin dashboard
- [ ] Content moderation
- [ ] Analytics views
- [ ] AI concierge feature (Required)

### Phase 7: Testing & Polish (Days 17-18)
- [ ] Unit tests
- [ ] Integration tests
- [ ] Security audit
- [ ] Documentation finalization
- [ ] Demo preparation

---

## Security Implementation Checklist

- [x] Password hashing with bcrypt (≥12 rounds) - UserDAL implements generate_password_hash
- [x] CSRF tokens on all forms - Flask-WTF enabled globally
- [x] SQL injection protection (parameterized queries) - All DAL methods use ? placeholders
- [x] XSS protection (template escaping) - Jinja2 auto-escaping + bleach sanitization
- [x] File upload validation and scanning - security.py validates extensions, size, filenames
- [ ] Rate limiting - Database table ready, middleware TODO
- [x] Session management with expiry - Flask-Login + user_sessions table
- [x] Email verification required - tokens + expiration in users table
- [x] Input validation (server-side) - WTForms validators on all forms
- [x] Secure cookie settings - config.py sets SESSION_COOKIE_SECURE for production

---

## AI-First Development Integration

### Required AI Feature (Pick One)

1. **Resource Concierge** (Recommended)
   - Natural language queries about available resources
   - Uses /docs/context/ for grounding
   - Example: "Find me a study room near Kelley tomorrow afternoon"

2. **Booking Assistant**
   - AI suggests optimal booking times
   - Conflict resolution suggestions
   - Based on historical usage data

3. **Auto-Summary Reporter**
   - Weekly usage summaries
   - Top resources report
   - Analytics insights

### Implementation Location
- Service: `src/services/ai_service.py`
- Controller: `src/controllers/api_controller.py` (endpoint: `/api/ai/ask`)
- Template: Add AI chat widget to dashboard

---

## Next Steps

1. **Set up virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create .env file**
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///campus_resource_hub.db
   ```

4. **Initialize Flask app structure**

5. **Start with authentication module**

---

## Git Workflow (Required)

All major changes MUST use:
1. Feature branches (`git checkout -b feature/booking-system`)
2. Pull Requests with reviews
3. Meaningful commit messages
4. Document AI usage in commits

---

## Documentation Requirements

✓ [x] README.md - Setup instructions
✓ [x] PRD (Product Requirements Document)
✓ [ ] Wireframes
✓ [x] Database schema + ERD
✓ [ ] API documentation
✓ [x] .prompt/dev_notes.md - AI interaction logs
✓ [x] .prompt/golden_prompts.md - Effective prompts library
✓ [x] PROGRESS_REPORT.md - Current status and next steps
✓ [x] IMPLEMENTATION_LOG.txt - Detailed technical documentation
✓ [ ] Test results

---

## Frontend Theme System (Added 2025-11-11)

### Theme Toggle Implementation

**JavaScript (home.js):**
- `toggleTheme()` - Switches between light and dark modes
- `loadTheme()` - Restores user's theme preference from localStorage
- Theme stored as data attribute on `<html>` element: `data-theme="dark"` or `data-theme="light"`

**Theme-Aware Icon System:**

**Pattern:** Dual image approach with CSS visibility toggle

```html
<!-- Each icon has two versions -->
<div class="category-icon">
    <img src="/static/images/icons/Study_Room_Icon_Light.png" class="icon-light">
    <img src="/static/images/icons/Study_Room_Icon_Dark.png" class="icon-dark">
</div>
```

**CSS (home.css):**
```css
/* Dark mode: Show light icons (for contrast) */
.category-icon .icon-light { display: block !important; }
.category-icon .icon-dark { display: none !important; }

/* Light mode: Show dark icons (for contrast) */
[data-theme="light"] .category-icon .icon-light { display: none !important; }
[data-theme="light"] .category-icon .icon-dark { display: block !important; }
```

**Benefits:**
- Instant theme switching without image reload
- Proper contrast in both themes
- Scalable pattern for other themed assets
- No JavaScript required for icon switching

**Icon Assets:**
- 10 PNG files total (5 categories × 2 themes)
- Naming convention: `{Category}_Icon_{Light|Dark}.png`
- Used in: Category carousel and featured resources section

---

## Key Architecture Patterns (Summary)

### 1. Property-Based Encapsulation (Models)
**When:** All model classes
**Pattern:** Private attributes + @property decorators with validation
**Benefits:** Data integrity, type safety, documentation, backward compatibility

### 2. Theme-Aware Assets (Frontend)
**When:** Icons, logos, illustrations that need theme adaptation
**Pattern:** Dual images with CSS visibility control via `[data-theme]` selector
**Benefits:** No JavaScript logic, instant switching, clean separation of concerns

### 3. Factory Pattern (Application Initialization)
**When:** Flask app creation
**Pattern:** `create_app()` function in `src/app.py`
**Benefits:** Multiple instances for testing, configuration isolation

### 4. Data Access Layer (Database Operations)
**When:** All database interactions
**Pattern:** BaseDAL with specialized DAL classes, parameterized queries
**Benefits:** SQL injection prevention, reusable operations, separation of concerns

### 5. Blueprint Pattern (Routing)
**When:** Feature-based route organization
**Pattern:** Separate blueprints for auth, resources, bookings, etc.
**Benefits:** Modular routes, clear URL structure, easier testing

---

---

## Implementation Roadmap (TODO)

**Current Status: ~55% Complete**

### Phase 1: Resource Management (High Priority) ⚠️ IN PROGRESS
**What:** Resource browsing, creation, editing, deletion
**Why Critical:** Core feature - users need to see and staff need to create resources

**Tasks:**
- [ ] Complete `resource_controller.py`
  - [x] Browse/search route (ResourceDAL.search_resources ready)
  - [ ] Resource detail page route
  - [ ] Create resource route (forms ready)
  - [ ] Edit resource route (forms ready)
  - [ ] Delete resource route
- [ ] Create resource templates
  - [ ] `resources/index.html` - Browse page with search/filters
  - [ ] `resources/detail.html` - Resource detail with booking CTA
  - [ ] `resources/create.html` - Staff-only form
  - [ ] `resources/edit.html` - Staff/admin form

**Dependencies:** ResourceDAL (✅ Complete), forms (✅ Ready)
**Estimated Time:** 2-3 hours

---

### Phase 2: Booking System (High Priority) ⚠️ IN PROGRESS
**What:** Users can create bookings, view calendar, staff approves bookings
**Why Critical:** Primary value proposition of the app

**Tasks:**
- [ ] Complete `booking_controller.py`
  - [x] Booking models ready
  - [ ] Create booking route with conflict detection
  - [ ] Approve/reject booking route (staff/admin)
  - [ ] Cancel booking route
  - [ ] My bookings list route
- [ ] Create booking templates
  - [ ] `bookings/create.html` with calendar widget
  - [ ] `bookings/detail.html` - Booking confirmation
  - [ ] `bookings/my_bookings.html` - User's bookings list
- [ ] Implement calendar JavaScript
  - [ ] `booking_calendar.js` - Date/time picker
  - [ ] Availability checking via API
  - [ ] Conflict validation feedback

**Dependencies:** BookingDAL (✅ Complete), forms (✅ Ready)
**Estimated Time:** 3-4 hours

---

### Phase 3: Dashboard & User Management 📊
**What:** Personalized dashboard showing my resources, bookings, messages
**Why Critical:** Central hub for user interaction

**Tasks:**
- [ ] Build user dashboard
  - [ ] `dashboard/user_dashboard.html`
  - [ ] My active bookings widget
  - [ ] My listed resources (if staff)
  - [ ] Unread messages count
  - [ ] Recent notifications
- [ ] Add profile management
  - [ ] View/edit profile route
  - [ ] Change password route
  - [ ] Email preferences

**Dependencies:** All DAL classes (✅ Complete)
**Estimated Time:** 2 hours

---

### Phase 4: Messaging System 💬
**What:** Users can message resource owners, staff can message students
**Why Critical:** Communication required for booking questions

**Tasks:**
- [ ] Complete `message_controller.py`
  - [x] MessageDAL ready with thread support
  - [ ] Inbox route (list threads)
  - [ ] View thread route
  - [ ] Send message route
  - [ ] Mark as read route
- [ ] Create message templates
  - [ ] `messages/inbox.html` - Thread list
  - [ ] `messages/thread.html` - Conversation view

**Dependencies:** MessageDAL (✅ Complete), Notification system (✅ Ready)
**Estimated Time:** 2-3 hours

---

### Phase 5: Review System ⭐
**What:** Users can review resources and rate them
**Why Important:** Trust and quality control

**Tasks:**
- [ ] Complete `review_controller.py`
  - [x] ReviewDAL ready with voting support
  - [ ] Submit review route
  - [ ] Vote on review route (helpful/not helpful)
  - [ ] Report review route
  - [ ] Display reviews on resource detail page
- [ ] Create review templates
  - [ ] Review submission form (modal or inline)
  - [ ] Review display component

**Dependencies:** ReviewDAL (✅ Complete)
**Estimated Time:** 1-2 hours

---

### Phase 6: Admin Panel 👑
**What:** Admin dashboard for system management
**Why Critical:** Staff approval workflow, content moderation

**Tasks:**
- [ ] Build admin dashboard
  - [ ] `dashboard/admin_dashboard.html`
  - [ ] Pending approvals queue (bookings + resources)
  - [ ] User management (list, view, suspend)
  - [ ] Reported content queue (reviews/messages)
  - [ ] System analytics (usage stats)
- [ ] Complete `admin_controller.py`
  - [ ] User management routes
  - [ ] Approval queue routes
  - [ ] Content moderation routes
  - [ ] Analytics data routes

**Dependencies:** All DAL classes (✅ Complete), RBAC decorators (TODO)
**Estimated Time:** 3-4 hours

---

### Phase 7: Testing 🧪
**What:** Automated tests for critical functionality
**Why Critical:** Academic requirement + catch bugs

**Tasks:**
- [ ] Unit tests
  - [ ] `test_booking_service.py` - Conflict detection logic
  - [ ] `test_validators.py` - Form validation
  - [ ] `test_security.py` - XSS/injection protection
- [ ] Integration tests
  - [ ] `test_auth_flow.py` - Register → verify → login
  - [ ] `test_booking_flow.py` - Browse → book → approve
  - [ ] `test_api_endpoints.py` - API security
- [ ] Security tests
  - [ ] SQL injection attempts
  - [ ] XSS attempts
  - [ ] CSRF token validation

**Dependencies:** All features (Phases 1-6)
**Estimated Time:** 2-3 hours

---

### Phase 8: Advanced Feature (Pick ONE) 🚀
**Required:** AI-First Development feature

**Option A: AI Resource Concierge (RECOMMENDED)**
- [ ] Implement `ai_service.py`
  - [ ] Natural language query parsing
  - [ ] Context grounding from `docs/context/`
  - [ ] Resource recommendation algorithm
  - [ ] Example: "Find me a study room near Kelley tomorrow afternoon"
- [ ] Add AI chat widget to dashboard
- [ ] API endpoint: `/api/ai/ask`

**Option B: Waitlist System (Already 80% Done)**
- [x] BookingWaitlist model (✅ Complete)
- [x] BookingDAL waitlist methods (✅ Complete)
- [ ] Waitlist controller routes
- [ ] Waitlist notification when spot opens
- [ ] Auto-promote from waitlist

**Option C: Google Calendar Integration**
- [ ] OAuth2 setup for Google Calendar API
- [ ] Export booking to user's calendar
- [ ] Sync cancellations/changes
- [ ] Require API key setup

**Dependencies:** Core features (Phases 1-6)
**Estimated Time:** 3-4 hours

---

### Phase 9: Polish & Documentation 🎨
**What:** Final UI/UX improvements and demo prep
**Why Critical:** Academic presentation + user experience

**Tasks:**
- [ ] Responsive design testing
  - [ ] Mobile layout (Bootstrap breakpoints)
  - [ ] Tablet layout
  - [ ] Desktop optimization
- [ ] Accessibility audit
  - [ ] ARIA labels
  - [ ] Keyboard navigation
  - [ ] Screen reader testing
- [ ] Documentation finalization
  - [ ] API.md documentation
  - [ ] User guide (how to book a resource)
  - [ ] Admin guide
- [ ] Demo preparation
  - [ ] Seed database with demo data
  - [ ] Prepare demo script
  - [ ] Screenshots for presentation

**Dependencies:** All features complete
**Estimated Time:** 2-3 hours

---

## Total Estimated Time Remaining: ~20-28 hours

**Critical Path:** Phases 1-2 (Resource + Booking) must be done first
**Parallel Work Possible:** Phase 3-5 (Dashboard, Messages, Reviews) can be done in any order
**Final Sprint:** Phases 6-9 (Admin, Testing, Advanced, Polish)

---

## Role-Based Access Control (RBAC)

**Authorization Hierarchy:**
```
Admin (Full System Access)
  ↓ inherits all capabilities from Staff
Staff (Resource Management)
  ↓ inherits all capabilities from Student
Student (Basic User)
```

### Student Role Capabilities

**Authentication:**
- ✅ Register account with email verification
- ✅ Login/logout with "Remember Me"
- ✅ Reset password via email
- ✅ Update profile (name, email, password)

**Resource Browsing:**
- ✅ View all active resources
- ✅ Search/filter resources by category, location, features
- ✅ View resource details, availability, reviews
- ✅ View resource images and descriptions

**Booking Management:**
- ✅ Create booking requests for available resources
- ✅ View own bookings (pending, approved, past)
- ✅ Cancel own bookings (if approved)
- ✅ Join waitlist when resource unavailable
- ❌ Cannot approve bookings
- ❌ Cannot modify other users' bookings

**Communication:**
- ✅ Send messages to resource owners
- ✅ Reply to messages in threads
- ✅ View own inbox and message history
- ✅ Receive notifications for booking status changes
- ❌ Cannot message all users (no broadcast)

**Review System:**
- ✅ Submit reviews for resources they've booked (after booking completed)
- ✅ Rate resources (1-5 stars)
- ✅ Vote on review helpfulness
- ✅ Report inappropriate reviews
- ❌ Cannot delete or edit reviews after submission

**Restrictions:**
- ❌ Cannot create or manage resources
- ❌ Cannot approve/reject booking requests
- ❌ Cannot access admin panel
- ❌ Cannot moderate content
- ❌ Cannot view other users' booking details
- ❌ Cannot suspend or manage other users

---

### Staff Role Capabilities

**Inherits All Student Capabilities PLUS:**

**Resource Management:**
- ✅ Create new resources with details, images, availability rules
- ✅ Edit own resources (details, images, availability)
- ✅ Deactivate/reactivate own resources
- ✅ View booking calendar for own resources
- ❌ Cannot edit resources owned by other staff
- ❌ Cannot delete resources (only deactivate)

**Booking Approval:**
- ✅ View pending booking requests for own resources
- ✅ Approve booking requests
- ✅ Reject booking requests with reason
- ✅ Cancel approved bookings with notification
- ✅ Manage waitlist for own resources
- ❌ Cannot approve bookings for resources they don't own

**Analytics:**
- ✅ View usage statistics for own resources
- ✅ View booking history for own resources
- ✅ View review summaries for own resources
- ❌ Cannot view system-wide analytics

**Communication:**
- ✅ Receive booking request notifications
- ✅ Message students about bookings
- ✅ Respond to resource inquiries
- ✅ Access dedicated "Resource Owner" inbox

**Ownership Rules:**
- A staff member can only manage resources they created
- Cannot transfer resource ownership
- Resources remain even if staff account downgraded

**Restrictions:**
- ❌ Cannot access admin panel
- ❌ Cannot manage other staff's resources
- ❌ Cannot suspend users
- ❌ Cannot moderate content (only report)
- ❌ Cannot change system settings

---

### Admin Role Capabilities

**Inherits All Staff Capabilities PLUS:**

**User Management:**
- ✅ View all users with search/filter
- ✅ View user details and activity history
- ✅ Suspend/unsuspend user accounts
- ✅ Change user roles (student ↔ staff, promote to admin)
- ✅ Reset user passwords (with email notification)
- ✅ View user login history and session data
- ❌ Cannot delete users (soft delete only - set inactive)

**Resource Management (System-Wide):**
- ✅ Edit ANY resource regardless of owner
- ✅ Deactivate/archive problematic resources
- ✅ Transfer resource ownership between staff
- ✅ Create resources on behalf of staff
- ✅ View all resources (active, inactive, archived)
- ✅ Bulk operations (archive old resources)

**Booking Management (System-Wide):**
- ✅ View all bookings system-wide
- ✅ Approve/reject any booking request
- ✅ Cancel any booking with notification
- ✅ Override booking conflicts (manual approval)
- ✅ View booking analytics and trends
- ✅ Manage waitlists for any resource

**Content Moderation:**
- ✅ Review reported content (reviews, messages)
- ✅ Remove inappropriate reviews
- ✅ Hide/show reviews (soft delete)
- ✅ View moderation queue with filters
- ✅ Ban users from reviewing
- ✅ View reported content history

**System Administration:**
- ✅ Access admin dashboard with system metrics
- ✅ View system-wide analytics:
  - Total users, resources, bookings
  - Usage trends over time
  - Popular resources and categories
  - User engagement metrics
- ✅ Manage resource categories (create, edit, delete)
- ✅ View audit logs (admin_logs table)
- ✅ Export data for reporting
- ✅ System configuration (future: booking rules, policies)

**Communication:**
- ✅ Send system-wide notifications
- ✅ Message any user
- ✅ View any message thread (for moderation)
- ✅ Access all notification logs

**Security & Compliance:**
- ✅ View security logs (failed logins, suspicious activity)
- ✅ Review CSRF token usage
- ✅ Monitor rate limits
- ✅ Access uploaded files for review

---

## Authorization Rules Implementation

### Database-Level Authorization

**users.role Column:**
```sql
role TEXT DEFAULT 'student' CHECK(role IN ('student', 'staff', 'admin'))
```

**Ownership Tracking:**
```sql
-- resources table
owner_id INTEGER NOT NULL  -- Links to users.user_id
owner_type TEXT DEFAULT 'user' CHECK(owner_type IN ('user', 'group'))
```

### Controller-Level Authorization

**Implementation Pattern:**

```python
# utils/decorators.py
from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(*roles):
    """
    Decorator to restrict access based on user role.
    Usage: @role_required('staff', 'admin')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # Unauthorized
            if current_user.role not in roles:
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def owner_required(resource_type='resource'):
    """
    Decorator to restrict access to resource owners.
    Usage: @owner_required('resource')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resource_id = kwargs.get('resource_id')
            # Check ownership logic
            if not is_owner(current_user.user_id, resource_id, resource_type):
                if current_user.role != 'admin':
                    abort(403)  # Forbidden unless admin
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

**Usage in Controllers:**

```python
# controllers/resource_controller.py
from utils.decorators import role_required, owner_required

@resource_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('staff', 'admin')
def create_resource():
    """Only staff and admin can create resources."""
    # Create resource logic
    pass

@resource_bp.route('/<int:resource_id>/edit', methods=['GET', 'POST'])
@login_required
@owner_required('resource')
def edit_resource(resource_id):
    """Only resource owner or admin can edit."""
    # Edit resource logic
    pass

@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    """Admin-only access."""
    # Admin dashboard logic
    pass
```

### UI-Level Authorization

**Template Conditional Rendering:**

```html
<!-- views/resources/detail.html -->
{% if current_user.is_authenticated %}
    {% if current_user.role in ['staff', 'admin'] %}
        <!-- Staff can see "Edit Resource" button -->
        <a href="{{ url_for('resource.edit', resource_id=resource.resource_id) }}"
           class="btn btn-warning">Edit Resource</a>
    {% endif %}

    {% if current_user.role == 'admin' %}
        <!-- Admin-only controls -->
        <a href="{{ url_for('admin.delete_resource', resource_id=resource.resource_id) }}"
           class="btn btn-danger">Delete Resource</a>
    {% endif %}

    <!-- All authenticated users can book -->
    <a href="{{ url_for('booking.create', resource_id=resource.resource_id) }}"
       class="btn btn-primary">Book This Resource</a>
{% endif %}
```

**Navbar Role-Based Links:**

```html
<!-- views/components/navbar.html -->
<nav class="navbar">
    {% if current_user.is_authenticated %}
        <!-- Everyone sees dashboard -->
        <a href="{{ url_for('main.dashboard') }}">Dashboard</a>

        {% if current_user.role in ['staff', 'admin'] %}
            <!-- Staff and admin see resource management -->
            <a href="{{ url_for('resource.my_resources') }}">My Resources</a>
            <a href="{{ url_for('resource.create') }}">Add Resource</a>
        {% endif %}

        {% if current_user.role == 'admin' %}
            <!-- Admin-only link -->
            <a href="{{ url_for('admin.dashboard') }}">Admin Panel</a>
        {% endif %}

        <a href="{{ url_for('auth.logout') }}">Logout</a>
    {% endif %}
</nav>
```

### Authorization Rules Matrix

| Action | Student | Staff | Admin | Notes |
|--------|---------|-------|-------|-------|
| **Resources** |
| Browse resources | ✅ | ✅ | ✅ | Public view |
| View resource detail | ✅ | ✅ | ✅ | Public view |
| Create resource | ❌ | ✅ | ✅ | Staff+ only |
| Edit own resource | ❌ | ✅ (own) | ✅ (any) | Ownership check |
| Edit others' resource | ❌ | ❌ | ✅ | Admin override |
| Delete resource | ❌ | ❌ | ✅ | Admin only (soft delete) |
| **Bookings** |
| Create booking | ✅ | ✅ | ✅ | All authenticated |
| View own bookings | ✅ | ✅ | ✅ | User sees own |
| View all bookings | ❌ | ✅ (own resources) | ✅ (all) | Context-dependent |
| Approve booking | ❌ | ✅ (own resources) | ✅ (any) | Ownership check |
| Cancel own booking | ✅ | ✅ | ✅ | User cancels own |
| Cancel others' booking | ❌ | ✅ (own resources) | ✅ (any) | Staff for their resources |
| **Users** |
| Edit own profile | ✅ | ✅ | ✅ | Self-service |
| View other profiles | ❌ | ❌ | ✅ | Admin only |
| Suspend user | ❌ | ❌ | ✅ | Admin only |
| Change user role | ❌ | ❌ | ✅ | Admin only |
| **Reviews** |
| Submit review | ✅ | ✅ | ✅ | After completed booking |
| Vote on review | ✅ | ✅ | ✅ | All authenticated |
| Report review | ✅ | ✅ | ✅ | All authenticated |
| Moderate review | ❌ | ❌ | ✅ | Admin only |
| **Messages** |
| Send message | ✅ | ✅ | ✅ | All authenticated |
| View own inbox | ✅ | ✅ | ✅ | User sees own |
| View others' messages | ❌ | ❌ | ✅ | Admin for moderation |
| **Admin** |
| Access admin panel | ❌ | ❌ | ✅ | Admin only |
| View analytics | ❌ | ✅ (own) | ✅ (all) | Context-dependent |
| Manage categories | ❌ | ❌ | ✅ | Admin only |
| View audit logs | ❌ | ❌ | ✅ | Admin only |

### Security Best Practices

**1. Never Trust Client-Side Checks**
- Always validate role on server-side
- UI hiding is UX, not security

**2. Ownership Verification**
```python
def verify_resource_ownership(user_id, resource_id):
    """Verify user owns resource."""
    resource = ResourceDAL.get_resource_by_id(resource_id)
    if not resource:
        abort(404)
    if resource.owner_id != user_id and current_user.role != 'admin':
        abort(403)
```

**3. Audit Logging**
```python
# All admin actions logged to admin_logs table
def log_admin_action(admin_id, action, target_type, target_id, details):
    """Log admin action for audit trail."""
    AdminDAL.create_log(
        admin_id=admin_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details
    )
```

**4. Role Hierarchy**
- Admin inherits all staff permissions
- Staff inherits all student permissions
- Check for highest needed role: `if role in ['staff', 'admin']`

---

## End of Project Structure Documentation
