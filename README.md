# Campus Resource Hub 🎓

> AI Driven Development (AiDD) 2025 Capstone Project
> Kelley School of Business - Indiana University
> **Team 13**

A full-stack web application enabling university departments, student organizations, and individuals to list, share, and reserve campus resources (study rooms, AV equipment, lab instruments, event spaces, tutoring time, etc.).

---

## 🎯 Project Overview

**Duration:** 18 days (November 2025)
**Team Size:** Core Team (4 students)
**Instructor:** Prof. Jay Newquist
**Tech Stack:** Python + Flask + SQLite + Bootstrap 5

### Key Features
- ✅ Role-based access control (Student, Staff, Admin)
- ✅ Resource listing and search
- ✅ Calendar-based booking with conflict detection
- ✅ Approval workflows
- ✅ Messaging system
- ✅ Reviews and ratings
- ✅ Admin dashboard
- ✅ AI-powered resource concierge (Advanced Feature)
- ✅ Waitlist system (Advanced Feature)

---

## 🗄️ Database Schema

- **30 tables** implementing full resource booking system
- SQLite for development (PostgreSQL-ready for production)
- Complete with indexes, constraints, and seed data
- See [DATABASE_TABLES.txt](DATABASE_TABLES.txt) for full documentation
- See [ERD_DIAGRAM.md](ERD_DIAGRAM.md) for entity relationships

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Final_Project
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database is already initialized** ✅
   - `campus_resource_hub.db` contains the complete schema with 30 tables

5. **Run the application** (Coming soon)
   ```bash
   python run.py
   ```

---

## 📁 Project Files Created

✅ **Completed:**
- `schema.sql` - Complete database schema with 30 tables
- `campus_resource_hub.db` - Initialized SQLite database
- `DATABASE_TABLES.txt` - Full table documentation
- `ERD_DIAGRAM.md` - Entity relationship diagram with Mermaid
- `PROJECT_STRUCTURE.md` - Architecture and folder structure guide
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore rules
- `README.md` - This file

📋 **Next Steps:**
- Create Flask application structure
- Build authentication module
- Implement MVC pattern
- Create templates and static files

---

## 🏗️ Architecture (MVC Pattern - Required)

**Model Layer** (`src/models/`) ✅ **Updated 2025-11-11**
- Database models with OOP encapsulation
- **All models use @property getters/setters** with validation
- 80+ properties across 8 model classes
- Private attributes with domain-specific validation
- Example: Rating validation (1-5), email format, datetime logic

**View Layer** (`src/templates/`)
- Jinja2 templates + Bootstrap 5
- **Theme-aware design** (light/dark mode toggle)
- Custom PNG icons for all 5 resource categories
- Responsive layouts with gradient backgrounds

**Controller Layer** (`src/controllers/`)
- Flask blueprints and routes
- Authentication (login, register, password reset) ✅
- Home page and dashboard ✅
- Resources, bookings, reviews (in progress)

**Data Access Layer** (`src/data_access/`)
- Encapsulated CRUD operations
- No raw SQL in controllers
- BaseDAL pattern with parameterized queries
- UserDAL, ResourceDAL, BookingDAL, MessageDAL, ReviewDAL ✅

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for complete architecture details.

---

## 🔐 Security Features Implemented

- ✅ Bcrypt password hashing (12 rounds minimum)
- ✅ Email verification tokens
- ✅ CSRF token management (Flask-WTF)
- ✅ Session tracking with Flask-Login
- ✅ **Remember Me** functionality (365-day cookies with security flags)
- ✅ SQL injection prevention (parameterized queries in all DAL methods)
- ✅ XSS protection (Jinja2 auto-escaping + bleach sanitization)
- ✅ File upload validation (type, size, path traversal checks)
- ✅ Password strength requirements (8+ chars, uppercase, lowercase, digit)
- ✅ Rate limiting support (database tables ready)
- ✅ Admin audit logs

---

## 📚 Documentation

| Document | Description | Status |
|----------|-------------|--------|
| [schema.sql](schema.sql) | Database schema | ✅ Complete |
| [DATABASE_TABLES.txt](DATABASE_TABLES.txt) | Table documentation | ✅ Complete |
| [ERD_DIAGRAM.md](ERD_DIAGRAM.md) | Entity relationships | ✅ Complete |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Architecture guide | ✅ Complete |

---

## 📊 Database Statistics

- **Total Tables:** 30
- **Indexes:** 25+ for optimal performance
- **Foreign Keys:** 50+ relationships
- **Seed Data:** 8 categories, 8 departments, 1 admin user

### Table Groups:
1. User Management (4 tables)
2. Groups (2 tables)
3. Resources (6 tables)
4. Bookings (4 tables)
5. Calendar Integration (2 tables)
6. Messaging (3 tables)
7. Reviews (1 table)
8. Content Moderation (1 table)
9. Admin & Analytics (3 tables)
10. Security (2 tables)
11. AI Features (1 table)
12. Rate Limiting (1 table)

---

## 👥 Team Roles

- **Product Lead:** PRD, features, demo
- **Backend Engineer:** Database, API, auth, deployment
- **Frontend Engineer:** Templates, UI/UX, responsive design
- **Quality/DevOps:** Tests, CI, security, documentation

---

## 📅 Timeline (18 Days)

- **Days 1-3:** ✅ Planning, database schema, project structure
- **Days 4-6:** 🔄 Authentication & user management
- **Days 7-9:** Resource CRUD & search
- **Days 10-12:** Booking system & messaging
- **Days 13-14:** Frontend polish & validation
- **Days 15:** Testing & security
- **Days 16:** Documentation finalization
- **Days 17:** Deployment preparation
- **Days 18:** Demo & presentation

---

## ✅ Project Status

| Component | Status | Notes |
|-----------|--------|-------|
| Database Schema | ✅ Complete | 30 tables with relationships |
| Database Created | ✅ Complete | SQLite initialized |
| **Model Layer** | ✅ **Complete** | **All models with @property encapsulation** |
| **Data Access Layer** | ✅ **Complete** | **5 DAL classes with validation** |
| Flask App Structure | ✅ Complete | Factory pattern, blueprints |
| **Authentication** | ✅ **Complete** | **Login, register, password reset, Remember Me** |
| **Home Page** | ✅ **Complete** | **Theme toggle, custom icons** |
| Documentation | ✅ 85% Complete | AI logs, architecture docs |
| Resources Module | 🔄 In Progress | DAL complete, controller partial |
| Booking Module | 🔄 In Progress | DAL complete, controller pending |
| Message/Review System | ✅ Complete | Models and DAL ready |
| Frontend Templates | 🔄 60% Complete | Auth + home done, resources pending |
| Testing | 📋 Pending | Unit and integration tests |

---

## 🤝 Git Workflow

All major changes use:
1. Feature branches (`git checkout -b feature/auth`)
2. Pull Requests with reviews
3. Document AI usage in commits

---

## 🔗 Key Project Requirements

✅ Flask + Python 3.10+
✅ SQLite database
✅ MVC architecture
✅ Data Access Layer (DAL)
✅ 30-table schema
✅ Security features (CSRF, XSS, SQL injection, password hashing)
✅ AI-first folder structure (.prompt/ docs)
✅ Bootstrap 5 frontend with theme support
✅ **OOP Encapsulation** (property getters/setters with validation)
⏳ pytest test suite
⏳ AI-powered feature

---

## 🎨 Recent Updates

### 2025-11-14: Booking System Bug Fixes
- ✅ Fixed critical timezone conversion bug (6-hour offset)
- ✅ Fixed datetime format parsing (ISO vs SQLite formats)
- ✅ Cancelled bookings no longer block time slots
- ✅ Past time slots now correctly show as grey (unavailable)
- ✅ Enhanced calendar display with proper color coding
- ✅ Added debugging console logs for conflict detection
- ✅ See [PROGRESS_REPORT.md](PROGRESS_REPORT.md) for detailed fix documentation

### 2025-11-11: OOP Refactoring
- ✅ All 8 model classes refactored with @property encapsulation
- ✅ 80+ properties with validation (email format, rating ranges, datetime logic)
- ✅ Private attributes with getters/setters
- ✅ Backward compatible with existing DAL code

### 2025-11-11: Theme System
- ✅ Light/Dark mode toggle with localStorage persistence
- ✅ Theme-aware custom PNG icons (10 files, 5 categories)
- ✅ Dual-image CSS pattern for instant switching

### 2025-11-11: Authentication
- ✅ Remember Me functionality verified (365-day persistent cookies)
- ✅ Password strength validation
- ✅ Security flags (httponly, secure) on cookies

---

## 🐛 Known Issues Resolved (2025-11-14)

| Issue | Status | Description |
|-------|--------|-------------|
| Timezone offset in bookings | ✅ Fixed | Bookings now preserve local time without UTC conversion |
| Datetime parsing errors | ✅ Fixed | System handles both ISO and SQLite datetime formats |
| Cancelled bookings blocking slots | ✅ Fixed | Calendar correctly shows cancelled slots as available |
| Past slots showing as booked | ✅ Fixed | Past time slots display grey (unavailable) color |
| Booking submission crashes | ✅ Fixed | Resolved import scoping issue |

For detailed testing procedures, see [TESTING_GUIDE.md](TESTING_GUIDE.md).

---

**Project Status:** 🟢 Booking System Stable - Testing & Polish Phase
**Last Updated:** 2025-11-14
**Next Milestone:** Comprehensive testing and additional feature polish
