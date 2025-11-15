# Campus Resource Hub - Development Notes

## Session Log

### 2025-11-14 - Reviews & Ratings + Booking Approval

**Tasks Completed:**
1. Fixed star rating hover behavior in review creation form
2. Fixed rating distribution display (field name mismatch)
3. Fixed review time display (UTC timezone issue)
4. Implemented custom booking order (approved → completed → cancelled)
5. Added auto-submit filters for bookings page
6. Added "Write Review" button on completed booking cards

**User Request:**
"Booking approval workflow: automatic approval for open resources, staff/admin approval for restricted resources"

**Investigation Results:**

The booking approval workflow is **already fully implemented**:

1. **Automatic Approval for Open Resources:**
   - Resources with `requires_approval = False` (or NULL) automatically get "approved" status when booked
   - Check in `src/controllers/booking_controller.py:250`

2. **Staff/Admin Approval for Restricted Resources:**
   - Resources with `requires_approval = True` get "pending" status when booked
   - Staff/admin users can approve/reject via `/bookings/pending` route
   - Route has `@role_required(['staff', 'admin'])` decorator (line 467)

3. **Approvals Link Visibility:**
   - "Approvals" link in navbar only shows for staff/admin users
   - Template: `src/templates/base.html:138`
   - Currently logged in as: nick@nick.edu (student role) - cannot see link

4. **To Access Approvals:**
   - Log in as **gajaya@iu.edu** (admin) or **gauthamjk8@gmail.com** (staff)
   - Then navigate to Home and the "Approvals" link will appear in navbar

**Issues Found & Fixed:**

1. **Missing 403 Error Template:**
   - When accessing `/bookings/pending` without proper permissions, `TemplateNotFound: errors/403.html` error occurred
   - **Fix:** Created `/src/templates/errors/` directory and `403.html` template
   - Fixed incorrect blueprint name: changed `url_for('home.index')` to `url_for('main.index')`

2. **Decorator Bug - Role Required:**
   - `@role_required(['staff', 'admin'])` was passing a list instead of separate arguments
   - This caused ALL users (including admin) to be denied access
   - **Root Cause:** Decorator expects `*roles` but was receiving `(['staff', 'admin'],)` - a tuple with one list
   - **Fix:** Changed to `@role_required('staff', 'admin')` in booking_controller.py lines 374 and 455

3. **Navbar Active State:**
   - "My Bookings" was showing as active when on "Approvals" page
   - "Approvals" link wasn't showing active state
   - **Fix:** Updated base.html to exclude `pending_approvals` from "My Bookings" active check and added active state to "Approvals"

**Continuing Investigation:**

4. **User Model Verification:**
   - Checked User model at `src/models/user.py`
   - Role property (line 105-107) is correctly implemented
   - Returns `self._role` which is initialized from database `user_data['role']`

5. **Added Debug Output:**
   - Added HTML comment in `base.html:137` to show `current_user.role` value
   - This will help diagnose if issue is browser caching, session, or template rendering
   - Debug comment: `<!-- Debug: User Role = {{ current_user.role }} -->`

**Root Cause Found & Fixed:**

6. **Home Page Has Separate Navbar:**
   - User reported: "Approvals" link visible on all pages EXCEPT home page
   - **Root Cause:** Home page (`src/templates/index.html`) has its own hardcoded navbar (lines 98-202)
   - Other pages extend `base.html` which has the updated navbar with "Approvals" link
   - Home page navbar at lines 122-123 had hardcoded `#` placeholders for "My Bookings" and "Messages"
   - **Fix:** Updated home page navbar (lines 119-129) to:
     - Match base.html structure
     - Use proper `url_for()` for My Bookings and Messages
     - Add "Approvals" link with role check: `{% if current_user.role in ['staff', 'admin'] %}`
     - Wrap all nav links in `{% if current_user.is_authenticated %}` check

**Issue Resolved:**
- "Approvals" link now visible in navbar on home page for admin/staff users
- All navbar links now functional on home page (were placeholders before)

---

### 2025-11-14 - Email Notifications for Booking Workflow

**User Request:**
"When someone books something or submits a request, we have to send an email to them saying the details saying its booked or pending in review and then if the admin or staff approves it or denies it, that should also send the user an email saying the status and book confirmation or denial"

**Implementation Completed:**

1. **Email Service Setup:**
   - Created `/src/utils/email_service.py` with comprehensive email sending functionality
   - Initialized Flask-Mail in `src/app.py` (line 123-124)
   - Leveraged existing Flask-Mail configuration in `config.py` (lines 51-57)
   - Implemented async email sending using background threads to avoid blocking requests

2. **Email Templates Created:**
   - `src/templates/emails/booking_confirmation.html` - For auto-approved bookings
   - `src/templates/emails/booking_pending.html` - For bookings requiring approval
   - `src/templates/emails/booking_approved.html` - When staff/admin approves
   - `src/templates/emails/booking_denied.html` - When staff/admin denies
   - All templates styled with modern, responsive HTML/CSS

3. **Email Functions Implemented:**
   - `send_booking_confirmation_email()` - Auto-approved bookings
   - `send_booking_pending_email()` - Bookings awaiting approval
   - `send_booking_approved_email()` - Approval notifications
   - `send_booking_denied_email()` - Denial notifications with optional reason
   - All emails include booking details, resource info, booking ID, and relevant links

4. **Integration into Booking Controller:**

   **Booking Creation Flow** (`booking_controller.py` lines 293-331):
   - Added email notification after successful booking creation
   - Sends `booking_confirmation_email` if resource doesn't require approval
   - Sends `booking_pending_email` if resource requires staff/admin approval
   - Emails include formatted date/time, resource details, and booking ID

   **Approval/Denial Flow** (`booking_controller.py` lines 493-539):
   - Added email notification after approval/denial action
   - Gets requester information from UserDAL
   - Sends `booking_approved_email` when approved by staff/admin
   - Sends `booking_denied_email` when denied, includes denial reason if provided
   - Includes approver/denier name in email

5. **Error Handling:**
   - All email operations wrapped in try-except blocks
   - Email failures logged but don't block booking operations
   - If MAIL_USERNAME not configured, logs warning instead of failing

6. **Email Configuration:**
   - Email credentials are loaded from environment variables
   - Default sender: `noreply@campusresourcehub.edu`
   - SMTP server defaults to Gmail (configurable via environment)
   - For development, emails will log warnings if credentials not set

**Files Modified:**
- `/src/utils/email_service.py` (created)
- `/src/app.py` (lines 122-124)
- `/src/controllers/booking_controller.py` (lines 293-331, 493-539)
- `/src/templates/emails/booking_confirmation.html` (created)
- `/src/templates/emails/booking_pending.html` (created)
- `/src/templates/emails/booking_approved.html` (created)
- `/src/templates/emails/booking_denied.html` (created)

**Testing Notes:**
- To enable actual email sending, set environment variables:
  - `MAIL_USERNAME` - SMTP username
  - `MAIL_PASSWORD` - SMTP password
  - `MAIL_SERVER` - SMTP server (default: smtp.gmail.com)
  - `MAIL_PORT` - SMTP port (default: 587)
- Without credentials, emails will log warnings but app will continue to function
- Email templates are responsive and work well on mobile devices

**Workflow Summary:**
1. User books a resource:
   - If auto-approved → Email: "Booking Confirmed"
   - If requires approval → Email: "Booking Pending Review"
2. Staff/Admin reviews booking:
   - If approved → Email: "Booking Approved" (includes approver name)
   - If denied → Email: "Booking Denied" (includes denier name and optional reason)

---

### 2025-11-14 - iMessage-Style Messaging Interface Implementation

#### Primary Requests Completed:
1. **Split-Screen Messaging Interface**: Transformed messaging from separate pages to unified split-screen layout
   - Left sidebar (350px) for thread list
   - Right panel for active conversation
   - Fixed positioning below navbar (80px from top)
   - Consistent height using `calc(100vh - 80px)`

2. **Solid Background Implementation**: Replaced translucent backgrounds with solid colors
   - Dark mode: `#1a1a1a` main, `#2a2a2a` sidebar
   - Light mode: `#f5f5f5` main, `#ffffff` sidebar

3. **Reliable Messaging**: Maintained working form submission with page reload after failed AJAX attempt

#### Files Modified:
- [src/controllers/message_controller.py](../src/controllers/message_controller.py): Added dual route support with optional thread_id
- [src/templates/messages/inbox.html](../src/templates/messages/inbox.html): Complete redesign for split-screen layout
- [src/templates/messages/inbox_old.html](../src/templates/messages/inbox_old.html): Backup of original design

#### Key Technical Solutions:
- Fixed positioning: `position: fixed; top: 80px; height: calc(100vh - 80px)`
- Flex layout: `display: flex` for horizontal split with separate overflow handling
- Theme-specific CSS: `[data-theme="light"]` selectors for dual theme support
- State management: URL parameter for active thread identification

#### Issues Resolved:
1. Background gradient visibility - Implemented solid opaque colors
2. Interface behind navbar - Changed from `top: 0` with padding to `top: 80px`
3. Inconsistent height - Used fixed viewport calculation
4. AJAX messaging failure - Reverted to reliable form submission

#### Database Schema Reviewed:
- `reviews` table exists with all necessary fields for upcoming feature
- `ai_interactions` table available for logging

---

### Next Tasks:
1. **Reviews & Ratings Implementation** (Current Priority)
   - User rating and feedback after completed bookings
   - Aggregate rating calculation
   - Top-rated badges
   - Host response functionality

2. **Future Enhancements**
   - Real-time messaging (when stable solution found)
   - Additional logging infrastructure

---

*Last Updated: 2025-11-14*
