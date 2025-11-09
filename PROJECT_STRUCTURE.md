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
```python
# models/user.py
class User:
    """
    Represents a user in the system.
    Maps to users table.
    """
    # Define user attributes and methods
```

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
- [ ] Project structure setup
- [ ] Flask app initialization
- [ ] Base templates (layout, navbar, footer)
- [ ] Configuration management

### Phase 2: Authentication (Days 4-6)
- [ ] User registration with email verification
- [ ] Login/logout with sessions
- [ ] Password reset flow
- [ ] CSRF protection
- [ ] Role-based access control decorators

### Phase 3: Resources (Days 7-9)
- [ ] Resource CRUD operations
- [ ] Image upload handling
- [ ] Category filtering
- [ ] Search functionality
- [ ] Availability rules management

### Phase 4: Bookings (Days 10-12)
- [ ] Booking creation with conflict detection
- [ ] Calendar view
- [ ] Approval workflow
- [ ] Waitlist system (Advanced)
- [ ] Email notifications

### Phase 5: Communication (Days 13-14)
- [ ] Message threads
- [ ] Notifications system
- [ ] Reviews and ratings

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

- [ ] Password hashing with bcrypt (≥12 rounds)
- [ ] CSRF tokens on all forms
- [ ] SQL injection protection (parameterized queries)
- [ ] XSS protection (template escaping)
- [ ] File upload validation and scanning
- [ ] Rate limiting
- [ ] Session management with expiry
- [ ] Email verification required
- [ ] Input validation (server-side)
- [ ] Secure cookie settings

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
✓ [ ] .prompt/dev_notes.md
✓ [ ] Test results

---

## End of Project Structure Documentation
