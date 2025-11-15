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

---

## 🧪 BOOKING SYSTEM TESTING (Added 2025-11-14)

### Critical Test Cases for Timezone Handling

#### Test Case 1: Local Time Preservation
**Objective:** Verify booking times match user-selected local time without UTC conversion

**Steps:**
1. Navigate to a resource detail page with calendar
2. Select a specific time slot (e.g., 6:00 AM - 8:00 AM)
3. Submit the booking form
4. Navigate to "My Bookings" page
5. Verify the displayed time matches the selected time (6:00 AM - 8:00 AM)

**Expected Result:** Booking shows exact time selected, no 6-hour offset or timezone conversion

**Database Verification:**
```bash
sqlite3 campus_resource_hub.db "SELECT booking_id, start_datetime, end_datetime FROM bookings ORDER BY booking_id DESC LIMIT 1;"
```
Should show: `2025-11-14 06:00:00` (not UTC-converted time)

---

#### Test Case 2: Cancelled Booking Calendar Update
**Objective:** Verify cancelled bookings no longer block time slots

**Steps:**
1. Create a booking for 2:00 PM - 4:00 PM on a future date
2. Verify the time slot shows as red (booked) on calendar
3. Navigate to "My Bookings" and cancel the booking
4. Return to the resource calendar
5. Refresh the page if necessary

**Expected Result:**
- Time slot changes from red (booked) to green (available)
- Slot can be booked again by same or different user

**API Verification:**
```bash
curl http://localhost:5001/bookings/calendar-data/<resource_id>
```
Cancelled bookings should NOT appear in response

---

#### Test Case 3: Past Slot Color Coding
**Objective:** Verify past time slots show as grey (unavailable), not red (booked)

**Steps:**
1. Navigate to a resource detail page
2. Use week navigation to go back to previous weeks
3. Observe color coding of past time slots
4. Note: Some past slots may have had bookings

**Expected Result:**
- All past slots show grey color (class: `unavailable`)
- Past slots are disabled (not clickable)
- No past slots show red (booked) color
- Hover text shows "This time has passed" or similar

**Visual Check:**
```
Grey slot = Unavailable (past or beyond max window)
Red slot = Booked (future/current active booking)
Green slot = Available for booking
Amber slot = Beyond maximum booking window
```

---

#### Test Case 4: Booking Conflict Detection
**Objective:** Verify system correctly detects and prevents overlapping bookings

**Test 4a: Exact Overlap**
1. Create booking: 2:00 PM - 4:00 PM
2. Try to create another booking: 2:00 PM - 4:00 PM
3. Expected: Error message "Selected time slot is not available"

**Test 4b: Partial Overlap (Start)**
1. Existing booking: 2:00 PM - 4:00 PM
2. Try to book: 1:00 PM - 3:00 PM (overlaps end)
3. Expected: Conflict detected, booking rejected

**Test 4c: Partial Overlap (End)**
1. Existing booking: 2:00 PM - 4:00 PM
2. Try to book: 3:00 PM - 5:00 PM (overlaps start)
3. Expected: Conflict detected, booking rejected

**Test 4d: Complete Enclosure**
1. Existing booking: 2:00 PM - 4:00 PM
2. Try to book: 1:00 PM - 5:00 PM (completely contains existing)
3. Expected: Conflict detected, booking rejected

**Test 4e: Adjacent Slots (Should Succeed)**
1. Existing booking: 2:00 PM - 4:00 PM
2. Try to book: 4:00 PM - 6:00 PM (starts when other ends)
3. Expected: Booking succeeds (no overlap)

**Test 4f: Different Days (Should Succeed)**
1. Existing booking: Monday 2:00 PM - 4:00 PM
2. Try to book: Tuesday 2:00 PM - 4:00 PM
3. Expected: Booking succeeds (different days)

---

#### Test Case 5: Multi-Week Calendar Navigation
**Objective:** Verify calendar correctly displays bookings across multiple weeks

**Steps:**
1. Navigate to resource detail page
2. Current week displays by default
3. Click "Next Week" button multiple times
4. Create booking 3 weeks in future
5. Navigate back to current week
6. Navigate forward again to week with booking

**Expected Result:**
- Week navigation updates URL parameter (?week=YYYY-MM-DD)
- Booking shows correctly in its week
- Past weeks show grey slots
- Future weeks show availability correctly
- Browser back/forward buttons work with week navigation

---

#### Test Case 6: Datetime Format Parsing
**Objective:** Verify system handles both ISO and SQLite datetime formats

**Database Setup:**
```bash
# Insert booking with ISO format
sqlite3 campus_resource_hub.db "INSERT INTO bookings (user_id, resource_id, start_datetime, end_datetime, status, created_at, updated_at) VALUES (1, 1, '2025-11-20T10:00:00', '2025-11-20T12:00:00', 'approved', datetime('now'), datetime('now'));"

# Insert booking with SQLite format
sqlite3 campus_resource_hub.db "INSERT INTO bookings (user_id, resource_id, start_datetime, end_datetime, status, created_at, updated_at) VALUES (1, 1, '2025-11-21 14:00:00', '2025-11-21 16:00:00', 'approved', datetime('now'), datetime('now'));"
```

**Steps:**
1. Navigate to "My Bookings" page
2. Verify both bookings display without errors
3. Check that datetime parsing doesn't crash

**Expected Result:**
- Both bookings display correctly
- No ValueError exceptions
- Times display in readable format

---

### Debugging Console Logs

When testing booking availability, open browser Developer Tools (F12) and check Console for:

**Booking Fetch Log:**
```javascript
Fetched bookings: [{booking_id: 3, start_datetime: "2025-11-15T14:00:00", ...}]
```

**Conflict Detection Log:**
```javascript
Slot marked as booked: {
  slotStart: "2025-11-15T14:00:00.000Z",
  slotEnd: "2025-11-15T14:30:00.000Z",
  bookingStart: "2025-11-15T14:00:00.000Z",
  bookingEnd: "2025-11-15T18:00:00.000Z"
}
```

These logs help diagnose issues with:
- API returning wrong data
- Timezone conversion problems
- Overlap detection logic errors

---

### Known Issues Resolved (2025-11-14)

| Issue | Status | Fix Location |
|-------|--------|--------------|
| ValueError: datetime format mismatch | ✅ Fixed | [src/models/booking.py:58-67](src/models/booking.py#L58-L67) |
| 6-hour timezone offset in bookings | ✅ Fixed | [src/templates/resources/detail.html:989-996](src/templates/resources/detail.html#L989-L996) |
| Cancelled bookings block slots | ✅ Fixed | [src/controllers/booking_controller.py:567-569](src/controllers/booking_controller.py#L567-L569) |
| Past slots show as red (booked) | ✅ Fixed | [src/templates/resources/detail.html:1090-1104](src/templates/resources/detail.html#L1090-L1104) |
| UnboundLocalError in booking submission | ✅ Fixed | [src/controllers/resource_controller.py:202](src/controllers/resource_controller.py#L202) |

---

### Regression Testing Checklist

After any changes to booking system, verify:

- [ ] User can create bookings without errors
- [ ] Booking times match selected slots (no timezone conversion)
- [ ] Cancelled bookings no longer show as "booked" on calendar
- [ ] Past time slots show grey (unavailable), not red (booked)
- [ ] Conflict detection prevents overlapping bookings
- [ ] Adjacent time slots can be booked separately
- [ ] Week navigation works forward and backward
- [ ] "My Bookings" page displays all user bookings
- [ ] Booking cancellation updates calendar immediately
- [ ] Multiple bookings for same resource on different days work
- [ ] Browser console shows no JavaScript errors
- [ ] Database stores datetime in correct format

---

**Last Updated:** 2025-11-14
**Status:** Ready for local testing with booking system fixes verified
