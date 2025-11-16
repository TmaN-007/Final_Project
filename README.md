# Campus Resource Hub

> **AI-Driven Development (AiDD) 2025 Capstone Project**
> Kelley School of Business - Indiana University
> **Project Duration:** 18 Days (November 2025)

A full-stack web application enabling university departments, student organizations, and individuals to list, share, and reserve campus resources including study rooms, AV equipment, lab instruments, event spaces, and tutoring time.

---

## Table of Contents

- [Executive Summary](#executive-summary)
- [Quick Start](#quick-start)
- [Project Status](#project-status)
- [Core Features](#core-features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Testing & Quality Assurance](#testing--quality-assurance)
- [Security Implementation](#security-implementation)
- [AI-First Development](#ai-first-development)
- [Database Design](#database-design)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Team & Roles](#team--roles)
- [Documentation](#documentation)
- [Project Timeline](#project-timeline)
- [Known Issues & Resolutions](#known-issues--resolutions)

---

## Executive Summary

The Campus Resource Hub is a production-quality web application built using AI-first development practices. The system supports role-based access control (Student, Staff, Admin), calendar-integrated booking with conflict detection, approval workflows, messaging, reviews, and administrative dashboards.

**Key Metrics:**
- 20-table optimized relational database schema (11 unused tables removed)
- 59 RESTful API endpoints
- 49 automated tests (100% pass rate)
- 15 manual test cases
- ~85% AI-assisted development with human validation

---

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd Final_Project

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python3 run.py
```

The application will be available at `http://localhost:5000`

### Default Admin Credentials

```
Email: admin@iu.edu
Password: admin123
```

---

## Project Status

**Current Phase:** Testing & Documentation Complete
**Completion:** 95%
**Due Date:** November 15, 2025

| Component | Status | Completion |
|-----------|--------|------------|
| Database Schema | ✅ Complete | 100% |
| Model Layer (OOP) | ✅ Complete | 100% |
| Data Access Layer | ✅ Complete | 100% |
| Authentication System | ✅ Complete | 100% |
| Resources Module | ✅ Complete | 100% |
| Booking System | ✅ Complete | 100% |
| Messaging System | ✅ Complete | 100% |
| Review System | ✅ Complete | 100% |
| Admin Dashboard | ✅ Complete | 100% |
| Frontend Templates | ✅ Complete | 100% |
| **Testing Suite** | ✅ **Complete** | **100%** |
| Security Hardening | ✅ Complete | 100% |
| API Documentation | ✅ Complete | 100% |
| Deployment Prep | 🔄 In Progress | 80% |

---

## Core Features

### ✅ Implemented Features

#### 1. User Management & Authentication
- Registration with email verification
- Secure login/logout (bcrypt password hashing)
- Role-based access control (Student, Staff, Admin)
- Remember Me functionality (365-day persistent cookies)
- Password strength validation
- Profile management

#### 2. Resource Listings
- Full CRUD operations for resources
- Resource categories: Study Rooms, Equipment, Lab Instruments, Event Spaces, Tutoring
- Image uploads with validation
- Availability rules configuration
- Status lifecycle: Draft → Published → Archived
- Owner/Staff/Admin access controls

#### 3. Search & Filter
- Keyword search across title, description, location
- Filter by category, availability, capacity
- Sort by: Recent, Most Booked, Top Rated
- Real-time search results

#### 4. Booking & Scheduling
- Calendar-based booking interface
- Conflict detection (prevents double-booking)
- Booking approval workflows
- Status transitions: Pending → Approved/Rejected → Completed/Cancelled
- Email notifications (console logging in development)
- Past booking history

#### 5. Messaging System
- Threaded message conversations
- User-to-user messaging
- Resource owner communication
- Unread message indicators
- Message history tracking

#### 6. Reviews & Ratings
- Star rating system (1-5 stars)
- Written reviews with feedback
- Aggregate rating calculation
- Review moderation (admin)
- Host response capability
- Review history

#### 7. Admin Dashboard
- User management (ban/unban, role changes)
- Resource oversight and moderation
- Booking approval queue
- Review moderation
- System analytics and statistics
- Audit log tracking

#### 8. Advanced Features
- **Waitlist System:** Users can join waitlists for fully booked resources
- **Theme Toggle:** Light/Dark mode with localStorage persistence
- **Custom Icons:** Theme-aware PNG icons for all resource categories

---

## Technology Stack

### Backend
- **Framework:** Flask 2.3.0 (Python 3.10+)
- **Database:** SQLite (development) / PostgreSQL-ready (production)
- **ORM:** Direct SQL with Data Access Layer pattern
- **Authentication:** Flask-Login, Flask-Security
- **Password Hashing:** bcrypt (12 rounds minimum)
- **CSRF Protection:** Flask-WTF
- **Input Validation:** Custom validators + WTForms
- **XSS Prevention:** Jinja2 auto-escaping + bleach sanitization

### Frontend
- **Template Engine:** Jinja2
- **CSS Framework:** Bootstrap 5
- **Icons:** Custom PNG theme-aware icons
- **JavaScript:** Vanilla JS for interactivity
- **Theme System:** CSS variables with localStorage

### Testing
- **Framework:** pytest 7.4.3
- **Test Types:** Unit tests, Integration tests, Manual tests
- **Coverage:** pytest-cov
- **Test Client:** Flask test client

### Development Tools
- **Version Control:** Git + GitHub
- **AI Tools:** Claude (Anthropic), GitHub Copilot
- **Code Editor:** Cursor AI, VS Code
- **Package Manager:** pip

---

## Architecture

The application follows a strict **Model-View-Controller (MVC)** pattern with a dedicated **Data Access Layer (DAL)**.

### Project Structure

```
Final_Project/
├── src/
│   ├── controllers/          # Flask blueprints & routes
│   │   ├── auth_controller.py
│   │   ├── resources_controller.py
│   │   ├── bookings_controller.py
│   │   ├── messages_controller.py
│   │   ├── reviews_controller.py
│   │   └── admin_controller.py
│   ├── models/               # ORM classes with @property encapsulation
│   │   ├── user.py
│   │   ├── resource.py
│   │   ├── booking.py
│   │   ├── message.py
│   │   └── review.py
│   ├── data_access/          # DAL - encapsulated CRUD operations
│   │   ├── base_dal.py
│   │   ├── user_dal.py
│   │   ├── resource_dal.py
│   │   ├── booking_dal.py
│   │   ├── message_dal.py
│   │   └── review_dal.py
│   ├── templates/            # Jinja2 HTML templates
│   │   ├── auth/
│   │   ├── resources/
│   │   ├── bookings/
│   │   ├── messages/
│   │   ├── reviews/
│   │   └── admin/
│   ├── static/               # CSS, JS, images
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── utils/                # Helper functions
│       ├── validators.py
│       └── security.py
├── tests/                    # Test suite
│   ├── test_validators_unit.py       # 36 unit tests
│   ├── test_endpoints_integration.py # 12 integration tests
│   └── conftest.py
├── .prompt/                  # AI-first development logs
│   ├── dev_notes.md          # All AI interactions (2,126 lines)
│   └── golden_prompts.md     # High-impact prompts (787 lines)
├── docs/context/             # Context Pack for AI tools
│   ├── APA/                  # Agility & Process artifacts
│   ├── DT/                   # Design Thinking artifacts
│   ├── PM/                   # Product Management artifacts
│   └── shared/               # Shared resources
├── campus_resource_hub.db    # SQLite database
├── schema.sql                # Database schema
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

### Architectural Layers

#### 1. Model Layer (`src/models/`)
- ORM classes with **@property getters/setters** for encapsulation
- 80+ properties across 8 model classes
- Private attributes with domain-specific validation
- Example: Rating validation (1-5), email format, datetime logic
- Backward compatible with existing DAL code

#### 2. View Layer (`src/templates/`)
- Jinja2 templates with Bootstrap 5
- Theme-aware design (light/dark mode)
- Responsive layouts
- CSRF token integration
- XSS-safe template rendering

#### 3. Controller Layer (`src/controllers/`)
- Flask blueprints for modular routing
- Request/response handling
- Form validation
- Session management
- Authorization checks (@login_required, @admin_required)

#### 4. Data Access Layer (`src/data_access/`)
- Encapsulated CRUD operations
- **No raw SQL in controllers**
- Parameterized queries (SQL injection prevention)
- BaseDAL pattern with common methods
- Transaction management

---

## Testing & Quality Assurance

### Test Suite Overview

**Total Tests:** 49
**Pass Rate:** 100%
**Execution Time:** 0.43 seconds

| Test Type | Count | Coverage |
|-----------|-------|----------|
| Unit Tests | 36 | Validators, Input Sanitization, Password Matching |
| Integration Tests | 12 | API Endpoints, Authentication, E2E Flows |
| Manual Test Cases | 15 | User Journeys, Security, Usability |

### Running Tests

```bash
# Run all tests
python3 -m pytest tests/test_validators_unit.py tests/test_endpoints_integration.py -v

# Run unit tests only
python3 -m pytest tests/test_validators_unit.py -v

# Run integration tests only
python3 -m pytest tests/test_endpoints_integration.py -v

# Run with coverage report
python3 -m pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

### Test Documentation

- **[MANUAL_TEST_PLAN.md](MANUAL_TEST_PLAN.md)** - 15 manual test cases with step-by-step instructions
- **[TESTING_REFLECTION.md](TESTING_REFLECTION.md)** - 289-word reflection on testing methodologies and AI assistance
- **[TESTING_ASSIGNMENT_SUMMARY.md](TESTING_ASSIGNMENT_SUMMARY.md)** - Comprehensive testing assignment summary
- **[SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md)** - Pre-submission verification checklist

### Unit Tests (36 tests)

**Test Coverage:**
- **Email Validation (8 tests):** Valid formats, invalid formats, edge cases (empty, None, too long)
- **Password Validation (8 tests):** OWASP compliance, missing requirements, length validation
- **Name Validation (7 tests):** Valid names, SQL injection prevention, length constraints
- **Input Sanitization (5 tests):** XSS prevention (script/HTML tag removal), whitespace handling
- **Password Matching (3 tests):** Identical passwords, case sensitivity, mismatch detection
- **Edge Cases (5 tests):** Complex emails, special characters, whitespace-only input

**Key Test File:** [tests/test_validators_unit.py](tests/test_validators_unit.py)

### Integration Tests (12 tests)

**Test Coverage:**
- **Resource Endpoints (3 tests):** Browse, search, detail view
- **Booking Endpoints (2 tests):** Authentication requirements, access control
- **Authentication Endpoints (2 tests):** Registration, login page loading
- **Invalid Endpoints (2 tests):** 404 handling, error responses
- **Complete User Journeys (2 tests):** Registration → Login, Browse → Detail E2E
- **Security Testing (1 test):** CSRF protection validation

**Key Test File:** [tests/test_endpoints_integration.py](tests/test_endpoints_integration.py)

### Manual Test Cases (15 cases)

**Test Categories:**
- **Positive Tests (6 cases):** Registration, search, booking, viewing, cancellation, approval
- **Negative Tests (6 cases):** Duplicate email, booking conflicts, unauthorized access, invalid dates, missing fields, SQL injection
- **Exploratory Tests (3 cases):** XSS prevention, CSRF validation, session timeout

**Key Test File:** [MANUAL_TEST_PLAN.md](MANUAL_TEST_PLAN.md)

---

## Security Implementation

### OWASP Top 10 Compliance

#### 1. Injection Prevention
- ✅ **Parameterized SQL Queries:** All DAL methods use parameterized queries
- ✅ **Input Validation:** Server-side validation for all user inputs
- ✅ **SQL Injection Tests:** Automated tests verify injection protection

#### 2. Broken Authentication
- ✅ **Bcrypt Password Hashing:** 12 rounds minimum
- ✅ **Session Management:** Flask-Login with secure session cookies
- ✅ **Remember Me:** Secure 365-day persistent cookies with httponly/secure flags
- ✅ **Password Strength:** 8+ chars, uppercase, lowercase, digit, special character

#### 3. Sensitive Data Exposure
- ✅ **No Plaintext Passwords:** All passwords hashed before storage
- ✅ **Secure Cookie Flags:** httponly, secure, samesite
- ✅ **Minimal PII Storage:** Only essential user information stored

#### 4. XML External Entities (XXE)
- ✅ **No XML Processing:** Application does not process XML

#### 5. Broken Access Control
- ✅ **Role-Based Access Control:** Student, Staff, Admin roles
- ✅ **@login_required Decorator:** Protects authenticated routes
- ✅ **@admin_required Decorator:** Protects admin-only routes
- ✅ **Owner Checks:** Users can only edit their own resources/bookings

#### 6. Security Misconfiguration
- ✅ **Debug Mode Off:** Debug=False in production
- ✅ **Secret Key Management:** Environment variable configuration
- ✅ **Error Handling:** Generic error messages (no stack traces to users)

#### 7. Cross-Site Scripting (XSS)
- ✅ **Jinja2 Auto-Escaping:** Enabled by default
- ✅ **Bleach Sanitization:** `bleach.clean()` for user-generated content
- ✅ **XSS Tests:** Automated tests verify script tag removal

#### 8. Insecure Deserialization
- ✅ **No Deserialization:** Application does not deserialize untrusted data

#### 9. Using Components with Known Vulnerabilities
- ✅ **Dependency Management:** Regular `pip list --outdated` checks
- ✅ **Requirements Pinning:** Specific version numbers in requirements.txt

#### 10. Insufficient Logging & Monitoring
- ✅ **Audit Logs:** Admin actions logged in `audit_logs` table
- ✅ **Error Logging:** Flask logging configured for errors
- ✅ **User Activity:** Login attempts, booking actions tracked

### CSRF Protection
- ✅ **Flask-WTF:** CSRF tokens on all forms
- ✅ **Token Validation:** Server-side token verification
- ✅ **CSRF Tests:** Automated tests verify POST protection

### File Upload Security
- ✅ **Type Validation:** Whitelist allowed file extensions (.jpg, .png, .pdf)
- ✅ **Size Limits:** Maximum file size enforced
- ✅ **Path Traversal Prevention:** Filename sanitization
- ✅ **Storage Location:** Uploads stored in safe directory outside webroot

---

## AI-First Development

This project was developed using **AI-first practices** with full transparency and documentation.

### AI Tools Used

- **Claude (Anthropic):** Primary AI assistant for code generation, debugging, testing
- **GitHub Copilot:** Code completion and suggestion
- **Cursor AI:** Context-aware code editing

### AI Contribution Breakdown

- **AI-Generated:** ~85% of codebase (with human review and validation)
- **Human-Written:** ~15% of codebase (critical business logic, security decisions)
- **Human Validation:** 100% of AI-generated code reviewed and tested

### AI-First Folder Structure

#### `.prompt/` Directory

**Purpose:** Document all AI interactions and prompt engineering

- **[dev_notes.md](.prompt/dev_notes.md)** (2,126 lines)
  - 40+ AI interactions from 12 development sessions (11/08 - 11/15/2025)
  - Context, prompts, outcomes, lessons learned
  - Code attribution and ethical AI usage
  - Testing and validation procedures

- **[golden_prompts.md](.prompt/golden_prompts.md)** (787 lines)
  - 11 high-impact prompts with 5-star effectiveness ratings
  - Database schema design, Flask MVC setup, OOP refactoring
  - Security implementation, debugging, documentation generation
  - Prompt engineering principles and best practices

#### `docs/context/` Directory (Context Pack)

**Purpose:** Provide context to AI tools for accurate code generation

```
docs/context/
├── APA/          # Agility, Processes & Automation artifacts
├── DT/           # Design Thinking artifacts (personas, journey maps)
├── PM/           # Product Management materials (PRDs, OKRs)
└── shared/       # Common items (glossary, personas)
```

### AI Integration Philosophy

1. **Transparency:** All AI usage documented in `.prompt/dev_notes.md`
2. **Validation:** All AI-generated code tested and validated by humans
3. **Attribution:** Code comments mark AI-contributed sections
4. **Ethical Use:** AI as tool to augment human capabilities, not replace judgment
5. **Context Grounding:** Reference specific files and line numbers in prompts
6. **Security First:** Explicitly request OWASP compliance in all AI prompts

### Lessons Learned

**What Worked:**
- AI dramatically accelerated test creation (36 unit tests in < 1 hour)
- AI suggested edge cases not initially considered
- AI provided excellent scaffolding for boilerplate code

**What Didn't Work:**
- AI made incorrect assumptions about error messages
- AI-generated tests required validation against actual implementation
- AI couldn't know specific implementation details without seeing code

**Key Takeaway:** AI is a powerful pair-programmer, but human judgment is essential for validating correctness and understanding failure root causes.

---

## Database Design

### Schema Overview

- **Total Tables:** 20 (optimized - unused tables removed)
- **Indexes:** 25+ for optimal performance
- **Foreign Keys:** 50+ relationships
- **Seed Data:** 8 categories, 8 departments, 1 admin user

### Table Groups

1. **User Management (4 tables):** users, user_sessions, password_reset_tokens, login_attempts
2. **Groups (2 tables):** groups, group_members
3. **Resources (6 tables):** resources, resource_categories, resource_images, resource_availability, resource_equipment, departments
4. **Bookings (4 tables):** bookings, booking_conflicts, booking_approval_logs, waitlists
5. **Calendar Integration (2 tables):** calendar_sync, calendar_events
6. **Messaging (3 tables):** message_threads, messages, message_participants
7. **Reviews (1 table):** reviews
8. **Content Moderation (1 table):** content_reports
9. **Admin & Analytics (3 tables):** audit_logs, analytics_events, system_settings
10. **Security (2 tables):** security_logs, rate_limiting
11. **AI Features (1 table):** ai_concierge_requests
12. **Rate Limiting (1 table):** rate_limits

### Entity Relationship Diagram

See [ERD_DIAGRAM.md](ERD_DIAGRAM.md) for complete entity relationships with Mermaid diagram.

### Database Files

- **[schema.sql](schema.sql)** - Complete SQL schema with constraints and indexes
- **[DATABASE_TABLES.txt](DATABASE_TABLES.txt)** - Detailed table documentation
- **[campus_resource_hub.db](campus_resource_hub.db)** - Initialized SQLite database

---

## API Documentation

### API Overview

- **Total Endpoints:** 59
- **Public Endpoints:** 3 (no authentication required)
- **Authenticated Endpoints:** 36 (login required)
- **Role-Based Endpoints:** 20 (admin/staff/owner only)

### Endpoint Categories

| Category | Endpoints | Description |
|----------|-----------|-------------|
| Authentication | 7 | Registration, login, profile |
| Resources | 7 | CRUD, search, listing |
| Bookings | 11 | Create, approve, calendar |
| Messages | 7 | Threads, send, inbox |
| Reviews | 7 | Submit, moderate, respond |
| Admin | 20 | User, resource, booking management |

### Quick Reference

```
# Authentication
POST   /auth/register
POST   /auth/login
GET    /auth/logout
POST   /auth/profile/edit

# Resources
GET    /resources/                  # Browse/search (public)
GET    /resources/<id>              # View details
POST   /resources/create            # Create (staff/admin)
POST   /resources/<id>/edit         # Edit (owner/admin)
DELETE /resources/<id>/delete       # Delete (owner/admin)

# Bookings
GET    /bookings/                   # View user bookings
POST   /bookings/resource/<id>/create  # Create booking
POST   /bookings/<id>/approve       # Approve (owner/admin)
POST   /bookings/<id>/cancel        # Cancel booking

# Messages
GET    /messages/                   # Inbox
POST   /messages/send               # Send message
GET    /messages/thread/<id>        # View thread

# Reviews
POST   /reviews/create/<booking_id> # Create review
POST   /reviews/<id>/respond        # Host response (owner)

# Admin
GET    /admin/dashboard             # Admin overview
GET    /admin/users                 # User management
POST   /admin/users/<id>/ban        # Ban user
GET    /admin/bookings              # Booking oversight
```

**Complete API Documentation:** [API.md](API.md)

---

## Deployment

### Local Development

```bash
# Run development server
python3 run.py

# Run with specific port
FLASK_RUN_PORT=5001 python3 run.py

# Enable debug mode
FLASK_ENV=development python3 run.py
```

### Production Deployment (Ready)

The application is configured for deployment to:
- AWS Elastic Beanstalk
- Heroku
- Google Cloud Run
- Microsoft Azure App Service

**Deployment Requirements:**
- PostgreSQL database (migrate from SQLite)
- Environment variable configuration
- HTTPS/TLS certificates
- Static file CDN (optional)

### Environment Variables

```bash
# Required for production
SECRET_KEY=<secure-random-key>
DATABASE_URL=<postgresql-url>
FLASK_ENV=production
MAIL_SERVER=<smtp-server>
MAIL_USERNAME=<email>
MAIL_PASSWORD=<password>
```

---

## Documentation

### Complete Documentation Set

| Document | Description | Lines/Size | Status |
|----------|-------------|-----------|--------|
| [README.md](README.md) | Project overview (this file) | 600+ | ✅ Complete |
| [schema.sql](schema.sql) | Database schema | 1,500+ | ✅ Complete |
| [DATABASE_TABLES.txt](DATABASE_TABLES.txt) | Table documentation | 800+ | ✅ Complete |
| [ERD_DIAGRAM.md](ERD_DIAGRAM.md) | Entity relationships | 300+ | ✅ Complete |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Architecture guide | 400+ | ✅ Complete |
| [API.md](API.md) | Endpoint documentation | 1,090+ | ✅ Complete |
| [.prompt/dev_notes.md](.prompt/dev_notes.md) | AI development log | 2,126 | ✅ Complete |
| [.prompt/golden_prompts.md](.prompt/golden_prompts.md) | High-impact prompts | 787 | ✅ Complete |

---

## Project Timeline

### 18-Day Development Schedule

- **Days 1-3:** ✅ Planning, database schema, project structure
- **Days 4-6:** ✅ Database & authentication implementation
- **Days 7-9:** ✅ Resource CRUD & search implementation
- **Days 10-12:** ✅ Booking logic & messaging system
- **Days 13-14:** ✅ Frontend polish & client validation
- **Days 15:** ✅ Testing & security sweep (49 tests, 100% pass rate)
- **Days 16:** ✅ Documentation finalization
- **Days 17:** 🔄 Deployment preparation (in progress)
- **Days 18:** 📋 Demo & presentation (scheduled)

---

## Known Issues & Resolutions

### Resolved Issues (2025-11-14)

| Issue | Status | Resolution |
|-------|--------|------------|
| Timezone offset in bookings | ✅ Fixed | Bookings preserve local time without UTC conversion |
| Datetime parsing errors | ✅ Fixed | System handles both ISO and SQLite datetime formats |
| Cancelled bookings blocking slots | ✅ Fixed | Calendar correctly shows cancelled slots as available |
| Past slots showing as booked | ✅ Fixed | Past time slots display grey (unavailable) |
| Booking submission crashes | ✅ Fixed | Resolved import scoping issue |

### Current Known Issues

None. All critical bugs resolved.

---

## Academic Integrity Statement

This project was developed using AI-assisted tools (Claude, GitHub Copilot) following course guidelines for AI-first development. All AI-generated code has been reviewed, validated, and tested by human developers. The `.prompt/dev_notes.md` file contains a complete audit trail of AI contributions, demonstrating transparent and ethical use of AI in software development.

**Code Attribution:**
- AI-Generated: ~85% (with human review)
- Human-Written: ~15% (critical business logic)
- Human Validation: 100% (all code tested)

---

## Project Metrics Summary

| Metric | Value |
|--------|-------|
| **Total Lines of Code** | ~15,000 |
| **Database Tables** | 20 |
| **API Endpoints** | 59 |
| **Test Cases** | 49 (automated) + 15 (manual) |
| **Test Pass Rate** | 100% |
| **Code Coverage** | 85%+ |
| **AI Contribution** | ~85% (with validation) |
| **Development Time** | 18 days |
| **Documentation Pages** | 12 major documents |

---

## Appendix: Running the Application

### First-Time Setup

```bash
# 1. Ensure Python 3.10+ is installed
python3 --version

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify database exists
ls -lh campus_resource_hub.db

# 6. Run application
python3 run.py
```

### Accessing the Application

1. Open browser to `http://localhost:5000`
2. Register a new account or use admin credentials:
   - Email: `admin@iu.edu`
   - Password: `admin123`
3. Explore features: Resources, Bookings, Messages, Reviews
4. Admin users have access to `/admin/dashboard`

### Troubleshooting

**Port already in use:**
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Run on different port
FLASK_RUN_PORT=5001 python3 run.py
```

**Database errors:**
```bash
# Reinitialize database
python3 run.py --reset-db
```

**Import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

---

**End of README**

For detailed technical documentation, see the files referenced throughout this document.
