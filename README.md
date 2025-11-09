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

**Model Layer** (`src/models/`)
- Database models and business logic

**View Layer** (`src/views/`)
- Jinja2 templates + Bootstrap 5

**Controller Layer** (`src/controllers/`)
- Flask blueprints and routes

**Data Access Layer** (`src/data_access/`)
- Encapsulated CRUD operations
- No raw SQL in controllers

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for complete architecture details.

---

## 🔐 Security Features Implemented

- ✅ Bcrypt password hashing required
- ✅ Email verification tokens
- ✅ CSRF token management
- ✅ Session tracking
- ✅ SQL injection prevention (parameterized queries)
- ✅ File upload validation
- ✅ Rate limiting support
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

| Component | Status |
|-----------|--------|
| Database Schema | ✅ Complete |
| Database Created | ✅ Complete |
| Documentation | ✅ 60% Complete |
| Flask App Structure | 📋 Next |
| Authentication | 📋 Pending |
| Resources Module | 📋 Pending |
| Booking Module | 📋 Pending |
| Testing | 📋 Pending |

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
✅ Security features
✅ AI-first folder structure
⏳ Bootstrap 5 frontend
⏳ pytest test suite
⏳ AI-powered feature

---

**Project Status:** 🟢 Foundation Complete - Ready for Development
**Last Updated:** 2025-11-08
**Next Milestone:** Create Flask application structure
