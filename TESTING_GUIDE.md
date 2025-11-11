# Testing Guide - Campus Resource Hub

## 🚀 Quick Start (First Time Setup)

### 1. Create Virtual Environment
```bash
cd /Users/hii/Desktop/AiDD\ Final\ Project/Final_Project
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Create .env File
```bash
cp .env.example .env
```

Edit `.env` and set:
```
SECRET_KEY=your-secret-key-here-change-me
FLASK_ENV=development
```

Generate a secure SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Verify Database Exists
```bash
ls -lh campus_resource_hub.db
# Should show the database file (30 tables already created)
```

### 5. Run the Application
```bash
python3 run.py
```

Expected output:
```
 * Serving Flask app 'src.app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

---

## ✅ What's Currently Working

### 1. Homepage (/)
- **Status:** ✅ Working
- **Features:**
  - Bootstrap 5 responsive navigation
  - Hero section with search bar
  - Category cards

**Test:**
```bash
curl http://127.0.0.1:5000/
# Should return HTML with "Campus Resource Hub"
```

### 2. Login Page (/auth/login)
- **Status:** ✅ Form displays
- **Features:**
  - Email and password fields
  - CSRF protection
  - "Remember me" checkbox

**Test:**
```bash
curl http://127.0.0.1:5000/auth/login
# Should return login form HTML
```

### 3. Register Page (/auth/register)
- **Status:** ✅ Form displays
- **Features:**
  - Name, email, password fields
  - Role selection (student/staff)
  - Password confirmation
  - Server-side validation

**Test:**
```bash
curl http://127.0.0.1:5000/auth/register
# Should return registration form HTML
```

### 4. Forgot Password (/auth/forgot-password)
- **Status:** ✅ Form displays
- **Features:**
  - Email input
  - Token generation ready

**Test:**
```bash
curl http://127.0.0.1:5000/auth/forgot-password
# Should return password reset request form
```

---

## ⚠️ What's NOT Working Yet

### 1. Actual Login Functionality
**Issue:** Form displays but POST handler needs integration

**To Fix:**
```python
# In src/controllers/auth_controller.py
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = UserDAL.verify_password(form.email.data, form.password.data)
        if user:
            login_user(User(user), remember=form.remember_me.data)
            return redirect(url_for('main.index'))
        flash('Invalid email or password', 'danger')
    return render_template('auth/login.html', form=form)
```

### 2. User Registration
**Issue:** Form validation works but POST handler is stub

**To Fix:** Integrate RegisterForm with UserDAL.create_user()

### 3. Resource Browsing
**Issue:** No resource_controller.py yet

**What's Ready:**
- ✅ ResourceDAL with full CRUD
- ✅ ResourceForm for create/edit
- ✅ Resource and ResourceCategory models
- ❌ Missing: Controller and templates

**To Test When Done:**
```
GET  /resources           - Browse all resources
GET  /resources/<id>      - View resource detail
GET  /resources/create    - Create form
POST /resources/create    - Save new resource
GET  /resources/<id>/edit - Edit form
POST /resources/<id>/edit - Update resource
```

### 4. Booking System
**Issue:** No BookingDAL or booking_controller.py yet

**What's Ready:**
- ✅ BookingForm, BookingApprovalForm
- ✅ Booking and BookingWaitlist models
- ❌ Missing: BookingDAL, controller, templates

### 5. Messaging System
**Issue:** No MessageDAL or message_controller.py yet

**What's Ready:**
- ✅ Message, MessageThread, Notification models
- ❌ Missing: MessageDAL, controller, templates

---

## 🧪 Manual Testing Checklist

### Phase 1: Basic Functionality
- [ ] Homepage loads at http://127.0.0.1:5000
- [ ] Navigation bar shows all links
- [ ] Login page displays form
- [ ] Register page displays form
- [ ] Forms have CSRF tokens (check HTML source)
- [ ] Bootstrap CSS is loaded (page is styled)

### Phase 2: Form Validation
- [ ] Login form requires email and password
- [ ] Register form validates email format
- [ ] Register form checks password strength
- [ ] Register form checks password confirmation match
- [ ] CSRF token validation works

### Phase 3: Authentication (Once Integrated)
- [ ] User can register new account
- [ ] Email verification token is generated
- [ ] User can login with valid credentials
- [ ] Invalid credentials show error message
- [ ] Logged-in user sees profile menu
- [ ] User can logout
- [ ] Password reset request works
- [ ] Password reset token is valid

### Phase 4: Resources (Once Created)
- [ ] Browse all published resources
- [ ] Search resources by keyword
- [ ] Filter by category
- [ ] Filter by location
- [ ] View resource detail page
- [ ] Create new resource (logged in)
- [ ] Upload resource images
- [ ] Edit own resources
- [ ] Delete own resources

### Phase 5: Bookings (Once Created)
- [ ] View resource availability calendar
- [ ] Create booking for available slot
- [ ] System detects booking conflicts
- [ ] Receive confirmation message
- [ ] View my bookings list
- [ ] Cancel upcoming booking
- [ ] Approve booking (staff/admin)
- [ ] Reject booking with reason

### Phase 6: Messaging (Once Created)
- [ ] View inbox
- [ ] Read message thread
- [ ] Send message
- [ ] Mark message as read
- [ ] View unread count badge

### Phase 7: Reviews (Once Created)
- [ ] Leave review after booking
- [ ] Rating 1-5 stars required
- [ ] Host can respond to review
- [ ] View resource average rating

---

## 🐛 Known Issues

### Issue 1: Dependencies Not Installed
**Symptom:** `ModuleNotFoundError: No module named 'flask_wtf'`

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue 2: SECRET_KEY Not Set
**Symptom:** `RuntimeError: The session is unavailable because no secret key was set.`

**Solution:** Create `.env` file with SECRET_KEY

### Issue 3: Database Not Found
**Symptom:** `sqlite3.OperationalError: unable to open database file`

**Solution:** Verify `campus_resource_hub.db` exists in project root

### Issue 4: Templates Not Found
**Symptom:** `jinja2.exceptions.TemplateNotFound: auth/login.html`

**Solution:** Check templates are in `src/templates/` (not `src/views/` yet)

### Issue 5: Static Files Not Loading
**Symptom:** CSS/JS files return 404

**Solution:** Verify files are in `src/static/css/` and `src/static/js/`

---

## 🔍 Debugging Tips

### Check Flask Routes
```bash
export FLASK_APP=run.py
flask routes
```

Expected output:
```
Endpoint             Methods  Rule
-------------------  -------  --------------------------
auth.forgot_password GET,POST /auth/forgot-password
auth.login           GET,POST /auth/login
auth.logout          GET      /auth/logout
auth.register        GET,POST /auth/register
auth.reset_password  GET,POST /auth/reset-password/<token>
auth.verify_email    GET      /auth/verify-email/<token>
main.about           GET      /about
main.index           GET      /
main.search          GET      /search
static               GET      /static/<path:filename>
```

### Check Database Tables
```bash
sqlite3 campus_resource_hub.db "SELECT name FROM sqlite_master WHERE type='table';"
```

Should show 30 tables.

### Check Database Contents
```bash
# View categories
sqlite3 campus_resource_hub.db "SELECT * FROM resource_categories;"

# View departments
sqlite3 campus_resource_hub.db "SELECT * FROM departments;"

# View users (should have 1 admin)
sqlite3 campus_resource_hub.db "SELECT user_id, name, email, role FROM users;"
```

### Test Form Validation
```python
# In Python shell
python3
>>> from src.forms.auth_forms import LoginForm, RegisterForm
>>> form = LoginForm(data={'email': 'test@example.com', 'password': 'pass'})
>>> form.validate()
True
>>> form.email.data
'test@example.com'
```

### Check Model Instantiation
```python
# In Python shell
python3
>>> from src.models import User, Resource, Booking
>>> user_data = {'user_id': 1, 'name': 'Test', 'email': 'test@test.com', 'role': 'student', 'email_verified': 1}
>>> user = User(user_data)
>>> user.name
'Test'
>>> user.is_admin
False
```

### Test DAL Methods
```python
# In Python shell
python3
>>> from src.data_access.user_dal import UserDAL
>>> users = UserDAL.get_all_users()
>>> len(users)
1  # Should have admin user
>>> UserDAL.get_user_by_email('admin@campus.edu')
{'user_id': 1, 'name': 'System Admin', ...}
```

---

## 📊 Current Component Status

| Component | Code Ready | Tested | Working |
|-----------|------------|--------|---------|
| **Homepage** | ✅ | ⏳ | ❓ |
| **Login Form** | ✅ | ⏳ | ❓ |
| **Register Form** | ✅ | ⏳ | ❓ |
| **Login POST** | ⚠️ Stub | ❌ | ❌ |
| **Register POST** | ⚠️ Stub | ❌ | ❌ |
| **Resources Browse** | ❌ | ❌ | ❌ |
| **Resource Detail** | ❌ | ❌ | ❌ |
| **Resource Create** | ❌ | ❌ | ❌ |
| **Bookings** | ❌ | ❌ | ❌ |
| **Messages** | ❌ | ❌ | ❌ |
| **Reviews** | ❌ | ❌ | ❌ |

---

## 🎯 Next Testing Milestones

### Milestone 1: Authentication Works
**Goal:** User can register and login

**Requirements:**
- [x] Forms created
- [x] UserDAL created
- [ ] Controllers integrated with forms
- [ ] Email service sends verification
- [ ] Sessions work correctly

**Test:** Create account → Login → See dashboard

---

### Milestone 2: Resources Work
**Goal:** User can browse and create resources

**Requirements:**
- [x] Forms created
- [x] ResourceDAL created
- [ ] resource_controller.py created
- [ ] Templates created
- [ ] Image upload works

**Test:** Create resource → Browse list → View detail → Edit

---

### Milestone 3: Bookings Work
**Goal:** User can book resources

**Requirements:**
- [x] Forms created
- [x] Models created
- [ ] BookingDAL created
- [ ] booking_controller.py created
- [ ] Conflict detection works
- [ ] Templates created

**Test:** View calendar → Create booking → Approve → Cancel

---

## 🚀 Quick Commands Reference

```bash
# Start Flask app
python3 run.py

# Run with specific port
FLASK_RUN_PORT=8000 python3 run.py

# Run in production mode
FLASK_ENV=production python3 run.py

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Check code style
flake8 src/ --max-line-length=120

# Format code
black src/ tests/

# View database
sqlite3 campus_resource_hub.db

# Create .env from example
cp .env.example .env
```

---

## 📝 Test Results Log

Add test results here as you test:

### Test Run 1: [Date]
- **Tester:** [Name]
- **Environment:** Development
- **Results:**
  - ✅ Homepage loads
  - ✅ Forms display
  - ❌ Login doesn't work (expected)
  - ❌ Resources page not found (expected)

---

**Last Updated:** 2025-11-08
**Status:** Ready for local testing (after pip install)
